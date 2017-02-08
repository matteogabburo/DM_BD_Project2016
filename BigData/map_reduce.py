
import sys
import json

import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

from pyspark import SparkConf, SparkContext

sys.path.append('../libraries')
import M1_geoIndexing.geo_indexing as m1 # module 1
sys.path.remove('../libraries')

import requests
from bs4 import BeautifulSoup
from math import sqrt

import lxml
from lxml.html.clean import Cleaner

from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer

import geopy
from geopy.distance import VincentyDistance
from math import radians, sin, asin, cos, sqrt

from models.topic_clustering_matrix import Matrix


def fun(x, y):
	return x,y+1

def getConf():
	with open('conf.json') as data_file:    
		data = json.load(data_file)
	return data
		

def f_download(url, waiting_time):

	def getUpperLevel(url):
		try:
			s_url = url.split('/')[2]
		except:
			return None		

		if '?' in url:
			array = url.rpartition('?')
		elif len(url) > 8 and '/' in url:
			array = url.rpartition('/')
			if len(array[0]) <= 8:
				return None
		else :
			return None

		return array[0]

	def html2text(html):

		cleaner = Cleaner()
		cleaner.javascript = True # This is True because we want to activate the javascript filter
		cleaner.style = True 
		cleaner.scripts = True	
		cleaner.comments = True
		cleaner.links = True
		cleaner.meta = True
		cleaner.page_structure = True
		cleaner.processing_instructions = True
		cleaner.forms = True	
		cleaner.add_nofollow = True

		#html = unicodedata.normalize('NFKD', html).encode('ascii','ignore')

		try:
			document = lxml.html.document_fromstring(html)
			c = cleaner.clean_html(document)
			html = lxml.html.tostring(c)

			soup = BeautifulSoup(html, 'lxml')
			parsed_text = soup.get_text()		

			if(len(parsed_text) > 20):
				return parsed_text.lower()	
			else:
				return None
		except: 
			return None

	def stemm(document):
		ret = None
		if document != None:
			document = document.replace('\t',' ').replace('\n',' ')
			
			# Remove \n and separators
			tmp = ''
			oldc = ''
		
			for c in document:
				if c != '\n' and c != '\t':
					if c == ' ':
						if oldc != ' ':
							tmp = tmp + c									
					else :
						tmp = tmp + c
		
				oldc = c
			document = tmp

			tokenizer = RegexpTokenizer(r'\w+')

			# create English stop words list
			en_stop = get_stop_words('en')
			it_stop = get_stop_words('it')
			sp_stop = get_stop_words('es')
			ge_stop = get_stop_words('de')
			fr_stop = get_stop_words('fr')

			# Create p_stemmer of class PorterStemmer
			p_stemmer = PorterStemmer()
			
			# clean and tokenize document string
			raw = document.lower()
			tokens = tokenizer.tokenize(raw)
	
			# remove stop words from tokens
			stopped_tokens1 = [i for i in tokens if not i in en_stop]
			stopped_tokens2 = [i for i in stopped_tokens1 if not i in it_stop]
			stopped_tokens3 = [i for i in stopped_tokens2 if not i in sp_stop]
			stopped_tokens4 = [i for i in stopped_tokens3 if not i in ge_stop]
			stopped_tokens5 = [i for i in stopped_tokens4 if not i in fr_stop]
		
			# stem tokens
			stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens5]
	
			# remove all the word that are meaning less
			ret = []
			for word in stemmed_tokens:
				if not any(char.isdigit() for char in word):
					if len(word) > 1:
						ret.append(word)
		return ret

	def fallback(u, l_fails):
		u_res = getUpperLevel(u)
		if u_res == None:	
			try:		
				l_fails.append(u.split('/')[2])
			except:
				return (u_res,False, l_fails)

			return (u_res,True, l_fails)
		return (u_res,False, l_fails)

	# MAIN MAP =============================================	

	ret = []
	l_fails = []
	urls = url['urls']
	for u in urls:
		u_tmp = u
		guard = False
		while guard == False:		
			
			s_url = ''
			try:
				s_url = url.split('/')[2]
			except:
				guard = True
			
			if s_url not in l_fails:

				try:			
					# HTTP REQUEST
					print(u_tmp)
					response = requests.get(u_tmp, timeout=waiting_time)			
	
					# see if response is positive
					if response.status_code == 200 and 'text/html' in response.headers['content-type']:
						if len(response.text) > 20: # if the page is empty		
			
							text = response.text
							text = html2text(text)
							text = stemm(text)

							if text != None or len(text) > 20:
								ret.append(text)
								guard = True	
							else:
								u_tmp = getUpperLevel(u_tmp)
								if u_tmp == None:
									guard = True	

						else:		
							u_tmp, guard, l_fails = fallback(u_tmp,l_fails)
					else:				
						u_tmp, guard, l_fails  = fallback(u_tmp,l_fails)
				except:
					u_tmp, guard, l_fails = fallback(u_tmp,l_fails)
			else:
				guard = True

	return (url['loc'],ret)


def f_cellIndex(url, bottomLeftLoc, topRightLoc, s):

	class Matrix:
		# bottomLeftLoc is the coordinate (lat,lon) of the bottom
		# left margin of the map, topRightLoc is the coordinate 
		# (lat, lon) of the top right margin of the map, and s (km)
		# is the length of the x and y edge of each cell
		def __init__(self, bottomLeftLoc, topRightLoc, s):

			lenX,lenY = self.xyHaversine(bottomLeftLoc, topRightLoc)

			# converts the sizes fo the map into int
			lenX += 1
			lenY += 1
			lenX = int(lenX)
			lenY = int(lenY)

			# if the map length is not divisible from
			# s, it enlarge the size of the map finding
			# the first length divisible for s
			lenX = lenX + lenX % s
			lenY = lenY + lenY % s
	
			self.blLoc = bottomLeftLoc
			self.trLoc = topRightLoc
			self.brLoc = (self.trLoc[0], self.blLoc[1])
			self.tlLoc = (self.blLoc[0], self.trLoc[1])

			self.lenX = lenX
			self.lenY = lenY
			self.s = s

			# size of the matrix for X and Y
			self.nX = int(self.lenX / s) 
			self.nY = int(self.lenY / s) 

			# current is used by the iterator
			self.current = [-1,0]

			self.numberOfCells = (self.nY+1) * (self.nX+1)
	
		def haversine(self, loc1, loc2):

			lat1 = loc1[0]
			lon1 = loc1[1]
			lat2 = loc2[0]
			lon2 = loc2[1]

			"""
			Calculate the great circle distance between two points 
			on the earth (specified in decimal degrees)
			"""
			# convert decimal degrees to radians 
			lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
			# haversine formula 
			dlon = lon2 - lon1 
			dlat = lat2 - lat1 
			a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
			c = 2 * asin(sqrt(a)) 
			km = 6367 * c
			return km

		def xyHaversine(self, loc1, loc2):

			lat1 = loc1[0]
			lon1 = loc1[1]
			lat2 = loc2[0]
			lon2 = loc2[1]

			#return lat
			rlat = self.haversine((lat1,lon1),(lat2,lon1))

			#return lon
			rlon = self.haversine((lat1,lon1),(lat1,lon2))

			return (rlat,rlon)


		def resetIterator(self):
			self.current = [-1,0]

		# given the x and y matrix coordinates it return
		# the map coordinates of the bottom left and the 
		# top right of the cell as (latbl,lonbl,lattr,lontr)
		def getCellBT(self, x, y):

			xb,yb = self.getCellB(x,y)
			xt,yt = self.getCellB(x+1,y+1)
	
			return xb,yb,xt,yt
	
		# given the x and y matrix coordinates it return
		# the map coordinates of the bottom left of the 
		# selected cell
		def getCellB(self, x, y):

			ang90 = 90
			ang0 = 0

			# calculus of the X coordinate
			# dx = distance on x edge
			if x > 0:
				dx = self.s * x
				origin = geopy.Point(self.blLoc)
				destination = VincentyDistance(kilometers=dx).destination(origin, ang0)
				lata = destination.latitude
			elif x == 0:
				lata = self.blLoc[0]

			# calculus of the Y coordinate
			# dy = distance on y edge
			if y > 0:
				dy = self.s * y
				origin = geopy.Point(self.blLoc)
				destination = VincentyDistance(kilometers=dy).destination(origin, ang90)
				lona = destination.longitude
			elif y == 0:
				lona = self.blLoc[1]
		
		
			return (lata, lona)


		def __iter__(self):
			return self.getCellBT(self.current[0], self.current[1])

		def hasNext(self):
			if self.current[1] > self.nY:
				return False
			else:
				return True 

		def next(self):
			if self.hasNext():
				if self.current[0] >= self.nX:
					self.current[0] = 0
					self.current[1] = self.current[1] + 1
				else:
					self.current[0] = self.current[0] + 1	
			else:
				raise StopIteration

			return self.getCellBT(self.current[0], self.current[1])


	# GET CELL MAIN =========================================================


	url_loc = url[0]
	
	guard = False
	matrix = Matrix(bottomLeftLoc, topRightLoc, s)	
	
	while matrix.hasNext() and guard == False:
		locs = matrix.next()

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]
		
		if bl[0] < url_loc[0] and tr[0] > url_loc[0] and bl[1] < url_loc[1] and tr[1] > url_loc[1]:
			guard = True

	if guard == True:
		print('\t - > '+str(matrix.current)+' , '+str(url[1]))
		return (matrix.current, url[1])
	else:
		return (None, url[1])
		

def main(args):


	# get conf =============================================================================
	conf = getConf()
	
	db_host = conf['host']
	db_port = int(conf['port'])
	directory = conf['txt_directory']
	db_name = conf['db_name']
	collection_name_urls = conf['url_collection']
	collection_name_dbstat = conf['dbstat_collection']
	phase1_n_threads = int(conf['geo_indexing_nthread'])
	max_waiting_time = int(conf['max_waiting_time_http'])
	s = int(conf['s'])

	min_loc = None
	max_loc = None
	if conf['bounded_locs'] != "":
		bounded_locs = conf['bounded_locs']
		min_loc, max_loc = bounded_locs[0], bounded_locs[1]	
	else:
		min_loc, max_loc = d.getBoundaries(host, port, db_name, dbstat_collection_name)

	#========================================================================================

	logs = {}
	# links extraction

	#logs['m1'] = m1.run(db_host, db_port, directory, db_name, collection_name_urls, collection_name_dbstat, phase1_n_threads)

	# Spark context definition
	conf = SparkConf()
	conf.setMaster("local")
	conf.setAppName("Test Spark")
	conf.set("spark.executor.memory", "1g")
	sc = SparkContext(conf = conf)


	# get urls for the map
	
	# set up parameters for reading from MongoDB via Hadoop input format
	db_conf = "mongodb://"+db_host+":"+str(db_port)+"/"+db_name+"."
	db_conf_clicks = db_conf + collection_name_urls
	
	# Read from DB
	urlsRDD = sc.mongoRDD(db_conf_clicks)
	
	# Map Reduce
	a = urlsRDD.map(lambda x: f_download(x,max_waiting_time)).map(lambda x: f_cellIndex(x, min_loc, max_loc, s)).collect()
	
	print('\n\n\n\n\n\nFINITO\n\n\n\n\n\n\n')


if __name__ == '__main__':
	sys.exit(main(sys.argv))
