#!/usr/bin/env python3.5
import sys
import numpy
from math import radians, cos, sin, asin, sqrt
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import threading
import time
from queue import Queue
import copy

# My imports
sys.path.append('..')
import db_utils.dao as d
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

# Definition of a class used for thread for parallelizing
class TopicClusteringThread(threading.Thread):
	def __init__(self, host_name, port, db_name, collection_name, collection_topics_name, bl, tr, s, max_waiting_time, q_fails):
		threading.Thread.__init__(self)
		self.host_name = host_name
		self.port = port
		self.db_name = db_name
		self.collection_name = collection_name
		self.collection_topics_name = collection_topics_name
		self.collection_corpuses_name = 'corpuses_trentino' # FOR TEST
		self.bl = bl 
		self.tr = tr
		self.max_waiting_time = max_waiting_time
		self.q_fails = q_fails
		# size of each cell of the grid
		self.s = s

		self.finish = False
	
	def run(self):

		# buffer size for insert in the db
		buffer_size = 20 # n of documents

		# connect to geo dao
		dao = GeoDao(self.host_name, self.port)
		dao.connect(self.db_name, self.collection_name)

		result = dao.getUrlsByBox(self.bl,self.tr)
	
		dao.close()

		#do something with result
		l_url = []
		l_res = list(result)

		#sets of things 
		#set_of_corpuses = []

		#dict for the topics of the cell 
		d_topics = {}

		n_corpuses = 0
	
		if len(l_res) > 0:

			# compute the coordinates for the center of the cell
			cluster_lon = self.bl[1] + (self.tr[1] - self.bl[1]) / 2
			cluster_lat = self.bl[0] + (self.tr[0] - self.bl[0]) / 2
			
			corpuses = []

			# extract url and put it in a list
			for row in l_res:
				d_row = dict(row)
				urls = d_row['urls']
				for url in urls:
					l_url.append(url)
	
				# extract all the fail urls from the shared queue
				l_fails = []
				
				
				# LOCK ===============================================
				lock = threading.Lock()
				lock.acquire() # will block if lock is already held
				while not self.q_fails.empty():
					l_fails.append(self.q_fails.get())
				
				# remove duplicates
				l_fails = list(set(l_fails))

				for e in l_fails:
					self.q_fails.put(e)
				lock.release()				
				# ====================================================
				
	
				# Get corpuses from of all the url into a cell
				http_ret = http.get_corpuses(l_url, self.max_waiting_time, l_fails, False)
				#corpuses = http_ret[0]		
				corpuses += http_ret[0]		
				
				for e in http_ret[1]:	
					self.q_fails.put(e)

				
				#Free memory	
				l_fails = None

				# remove empty sublist
				corpuses = [x for x in corpuses if x != []]

				
			n_corpuses = len(corpuses)
			if n_corpuses > 0:

				# ONLY FOR TEST : save all the corpus =============
				'''		
				d_corpuses = {}
				d_corpuses['loc'] = [cluster_lat,cluster_lon]
				d_corpuses['corpuses'] = corpuses

				set_of_corpuses.append(d_corpuses)

				# if the dimension of the query is really big store it
				# the db and free the memory
				if len(set_of_corpuses) >= buffer_size:
					print('[ Saving corpuses', end = '\r') # on DB for the coordinates : '+str(self.bl), end = '\r')
					dao = GeoDao(self.host_name, self.port)
					dao.connect(self.db_name, self.collection_corpuses_name)

					# save the sets
					dao.addMany(self.collection_corpuses_name, set_of_corpuses)

					dao.close()
											
					set_of_corpuses = []
				'''
				# =================================================		

				# Make lda on the corpuses
				'''print('[ LDA of '+str(len(corpuses))+' corpuses, '+
					str(size(sys.getsizeof(corpuses))), end = '\r') #for loc : \t '+str(self.bl[0])+'\t'+str(self.bl[0]), end = '\r')				'''
				# LDA with LOCK for increasing the performance and the memory consume ===========
				lock_lda = threading.Lock()
				lock_lda.acquire() # will block if lock is already held

				# nsteps, ntopics
				corpus,document_lda = lda.getTopicsFromDocs(corpuses,20,2)
				# 20 topics DA 20 word
				l_topics = lda.getTopicsRanking(document_lda,corpus,20,20)

				lock_lda.release()				
				# ===============================================================================

				# Save the topic list into the db
				d_topics['loc'] = [cluster_lat,cluster_lon]
				d_topics['topics'] = l_topics
				d_topics['s'] = self.s
				d_topics['ncorpuses'] = n_corpuses
				
				'''			
				set_of_topics.append(d_topics)

				# if the dimension of the query is really big store it
				# the db and free the memory
				if len(set_of_topics) >= buffer_size:
					print('[ Saving topics', end = '\r') #for loc : \t '+str(self.bl[0])+'\t'+str(self.bl[0]), end = '\r')
					dao = GeoDao(self.host_name, self.port)
					dao.connect(self.db_name, self.collection_topics_name)

					# save the sets
					dao.addMany(self.collection_topics_name, set_of_topics)

					dao.close()

					set_of_topics = []
				'''

		if len(d_topics) > 0: #or len(set_of_corpuses) > 0:
			# connect to geo dao
			dao = GeoDao(self.host_name, self.port)
			dao.connect(self.db_name, self.collection_name)

			# save the sets
			'''if len(set_of_corpuses) > 0:
				print('[ Saving corpuses', end = '\r') # for loc : \t '+str(self.bl[0])+'\t'+str(self.bl[0]), end = '\r')
				dao.addMany(self.collection_corpuses_name, set_of_corpuses)'''
			if len(d_topics) > 0:
				print('[ Saving topics  ', end = '\r') # for loc : \t '+str(self.bl[0])+'\t'+str(self.bl[0]), end = '\r')
				# dao.addMany(self.collection_topics_name, set_of_topics)			
				dao.addOne(self.collection_topics_name, d_topics)		

			dao.close()
			
		# close thread
		self.finish = True

def main(args):
	
	start_time = time.time()

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

	# db parameters
	db_name = 'db_geo_index' # db name	
	collection_name = 'clicks' # geoindex collection
	collection_topics_name = 'topics_trentino_test' # topic collection

	# false and the pricipals print don't work
	log = True
		
	max_loc, min_loc = d.getBoundaries(host, port, db_name)
	
	# TEST ========================================
	# coordinate trentino	
	min_loc = [45.690270, 10.399488]
	max_loc = [46.569637, 12.008985]

	print("ATTENZIONE : COORDINATE TEST INSERITE")
	# =============================================


	matrix = Matrix(min_loc, max_loc, s)
	matrix.toString()
	print('')

	empty_cell_counter = 0
	n_cells = 0

	# Max number of thread
	n_thread = 80
	l_thread = []

	# shared queue	
	q_fails = Queue()

	#Checkpoint
	checkpoint = True

	while matrix.hasNext() :

		# For the plotting		
		cell_full = False

		locs = matrix.next()

		#actual position of the iterator
		#current = matrix.current
		#print('Current cell : '+ str(current), end = '\r')

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]
		
		# wait untill the thread numbers is equal to n_thread
		'''
		while threading.active_count() > n_thread:
			time.sleep(1) # delays for 1 seconds
		'''
		while len(l_thread) > n_thread - 1:
			time.sleep(1)
			l_thread = [t for t in l_thread if (t.isAlive() and t.finish == False)]

		if checkpoint == True :
			# connect to geo dao
			dao = GeoDao(host, port)
			dao.connect(db_name, collection_topics_name)
			if len(list(dao.getUrlsByBox(bl,tr))) > 0:			
				t = TopicClusteringThread(host, port, db_name, collection_name,
							 collection_topics_name, bl, tr, s, 
							max_waiting_time, q_fails)				
				t.deamon = True
				t.start()
				l_thread.append(t)
			dao.close()
		else:
			t = TopicClusteringThread(host, port, db_name, collection_name, 
						collection_topics_name, bl, tr, s,
						 max_waiting_time, q_fails)
			t.deamon = True
			t.start()
			l_thread.append(t)			


		n_cells = n_cells + 1	

		# print the state of the process
		pt.conditionalPrintCB(0,matrix.nX * matrix.nY,n_cells, str(n_cells)+ ' on '+str(matrix.numberOfCells) +
					 ' | Threads : ' + str(len(l_thread)), log)		

	# print the state of the process
	pt.conditionalPrintCB(0,matrix.nX * matrix.nY,n_cells, str(n_cells)+ ' on '+str(matrix.numberOfCells) +
				 ' | Threads : ' + str(len(l_thread)), log)		
	print('')


	while len(l_thread) > 0 :
		time.sleep(3)		
		print('I\'m working ... | Remaining threads open : '+str(len(l_thread))+'\t\t\t\t', end = '\r')
	
		l_thread = [t for t in l_thread if (t.isAlive() and t.finish == False)]

	print('')
	print('# cells : '+str(n_cells))	
	#print('# empty : '+str(empty_cell_counter))

	end_time = time.time()
	
	#get the time of the entire process
	final_time = end_time - start_time
	
	seconds_total = int(final_time)+1	
	minutes_total = int(int(final_time) / 60)
	hours_total = int(minutes_total / 60)

	if hours_total > 0 :
		minutes_total = hours_total % minutes_total
	if minutes_total > 0:
		seconds_total = minutes_total % seconds_total 

	print('')
	print('Execution time : '+ str(hours_total) +
		' hours, '+str(minutes_total)+
		' minutes and '+str(seconds_total) + ' seconds')

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))


