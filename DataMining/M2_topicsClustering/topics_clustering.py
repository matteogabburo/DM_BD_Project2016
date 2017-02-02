#!/usr/bin/env python3.5
import sys
import numpy
from math import radians, cos, sin, asin, sqrt
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# My imports
sys.path.append('..')
import db_utils.dao
from db_utils.dao import Dao
from db_utils.dao import GeoDao
import models.url
from models.url import Url
from models.topic_clustering_matrix import Matrix
import utils.http_requests as http
import utils.topic_processing as lda
import utils.print_tools as pt
sys.path.remove('..')

# Topic clustering must: 
# 1. Find the dimension of the grid, watching
#    the urls that are in the db
# 2. Make a logical grid
#	a. optimization for the memory finding the empty cells
# 3. Using the above grid for extract rows from
#    the db
# 4. For each url:
# 	a. Check the integrity
#	b. Make LDA on it (???)
# 5. Store the results into another db


# TODO readme
# it return the max lat max lon min lat min lon from the db
def getBoundaries(host, port, db_name):
	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)
	c_list = list(dao.query('globals', ''))
	c_dict = dict(c_list[0])
	dao.close()	
	return (float(c_dict['lat_max']),float(c_dict['lon_max'])),(float(c_dict['lat_min']),float(c_dict['lon_min']))

#TODO readme
def mapSpace():
	m = 10
	n = 10
	matr = a = numpy.zeros(shape=(m,n))

	print(matr)


def getPlotsMap(host, port, db_name, collection):
	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)

	c_list = list(dao.query(collection, ''))
	c_dict = dict(c_list[0])
	
	dao.close()

	# Select the map
	m = Basemap(projection='mill',llcrnrlat=int(c_dict['lat_min']),urcrnrlat=int(c_dict['lat_max']+1),llcrnrlon=int(c_dict['lon_min']),urcrnrlon=int(c_dict['lon_max']+1),resolution='i')

	m.drawcoastlines()
	m.drawcountries()
	m.drawstates()
	m.fillcontinents(color='#04BAE3',lake_color='#FFFFFF')
	m.drawmapboundary(fill_color='#FFFFFF')

	return m


def tmpLda(texts, ntopic = 30, niteration = 10):
	corpus,document_lda = lda.getTopicsFromDocs(texts,30,5)
	ranking = lda.getTopicsRanking(document_lda,corpus,30,10)

	return ranking

def main(args):
	
	if len(args) == 1 or args[1] == '--h':
		print('Parameters : [ hostname, port, s ]')
		return 0


	# Parameters for the db
	host = args[1]
	port = int(args[2])
	
	# Parameters for the matrix
	s = int(args[3])

	# Parameters for http requests
	max_waiting_time = 1 # 1s timeout for each request
	l_fails = [] #list containing the fails url	

	db_name = 'db_geo_index'	
	
	# geoindex collection
	collection_name = 'clicks'
	
	# topic collection
	collection_topics_name = 'topics_mini'

		
	max_loc, min_loc = getBoundaries(host, port, db_name)
	
	matrix = Matrix(min_loc, max_loc, s)
	matrix.toString()
	print('')

	# connect to geo dao
	dao = GeoDao(host, port)
	dao.connect(db_name, collection_name)

	# ===================================================================
	# Get the plot map
	m = getPlotsMap(host, port, db_name, 'globals')
	# ===================================================================

	empty_cell_counter = 0
	n_cells = 0
	while matrix.hasNext():
		# For the plotting		
		cell_full = False

		locs = matrix.next()

		#actual position of the iterator
		current = matrix.current
		print('Current cell : '+ str(current), end = '\r')

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]
		
		result = dao.getUrlsByBox(bl,tr)
	
		#do something with result
		l_url = []
		l_res = list(result)
		if len(l_res) == 0:
			empty_cell_counter = empty_cell_counter + 1
		elif len(l_res) > 0:

			# compute the coordinates for the center of the cell
			cluster_lon = bl[1] + (tr[1] - bl[1]) / 2
			cluster_lat = bl[0] + (tr[0] - bl[0]) / 2

			
			# extract url and put it in a list
			for row in l_res:
				d_row = dict(row)
				urls = d_row['urls']
				for url in urls:
					l_url.append(url)
					
				# Get corpuses from of all the url into a cell
				http_ret = http.get_corpuses(l_url, max_waiting_time, l_fails)
				corpuses = http_ret[0]				
				l_fails = list(set(l_fails + http_ret[1])) # merges fails list
				
				# remove empty sublist
				corpuses = [x for x in corpuses if x != []]

				if len(corpuses) > 0:
					'''
					# ONLY FOR TEST : save all the corpus =============
					print('Saving corpuses on DB ...', end = '\r')
					corpuses_collection_name= 'corpuses_mini'
							
					d_corpuses = {}
					d_corpuses['loc'] = [cluster_lat,cluster_lon]
					d_corpuses['corpuses'] = corpuses

					
					dao.addOne(corpuses_collection_name, d_corpuses)
					# =================================================

					# Make lda on the corpuses
					print('Doing LDA ...', end = '\r')
					l_topics = tmpLda(corpuses)					
				
					# Save the topic list into the db
					print('Saving topics on DB ...', end = '\r')
					d_topics = {}
					d_topics['loc'] = [cluster_lat,cluster_lon]
					d_topics['topics'] = l_topics
								
					dao.addOne(collection_topics_name, d_topics)
					
					# For plotting
					cell_full = True				
					'''
		# ===================================================================
		# Get the plot map
		if cell_full == True:
			x,y = m(cluster_lon,cluster_lat)
			m.plot(x,y, 'ro') 
		# ===================================================================

	
		n_cells = n_cells + 1

	dao.close()

	print('')
	print('# cells : '+str(n_cells))	
	print('# empty : '+str(empty_cell_counter))

	plt.title("Geo Plotting of the full cells")
	plt.show()

	

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))


