#!/usr/bin/env python3.5
import sys
from operator import itemgetter
import time

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# My imports
sys.path.append('..')
import db_utils.dao as dao_f
from db_utils.dao import Dao
from db_utils.dao import GeoDao
import models.topic_clustering_matrix as m
from models.topic_clustering_matrix import Matrix
import models.topics_tree as tt
from models.topics_tree import TopicsTree
sys.path.remove('..')

# 1 get the maximum coordinates for the map
# 2 get the s from the user and generate the grid
# 3 for each cell of the grid query the db and take the biggest topic that are 
#   big enaugh for the cell dimension

# PLOT=======================================================================================

def initMap(mainBl, mainTr):

	lat_min = mainBl[0]
	lat_max = mainTr[0]
	lon_min = mainBl[1]
	lon_max = mainTr[1]

	# Select the map
	m = Basemap(projection='mill',llcrnrlat=lat_min,urcrnrlat=lat_max,llcrnrlon=lon_min,urcrnrlon=lon_max,resolution='h')

	m.drawcoastlines()
	m.drawcountries()
	m.drawstates()
	m.fillcontinents(color='#04BAE3',lake_color='#FFFFFF')
	m.drawmapboundary(fill_color='#FFFFFF')

	ax = plt.axes()

	return m,ax

def addCell(m, ax, loc,text):
		
	x,y = m(loc[1],loc[0])
	point, = m.plot(x,y, 'ro')
	
	annotation = plt.text(x,y, text,fontsize=12,fontweight='bold',ha='left',va='bottom',color='k')
	annotation.set_visible(False)

	return [point,annotation]

#globalvar
points_with_annotation = []
def on_move(event):
	
	visibility_changed = False
	for point, annotation in points_with_annotation:
		should_be_visible = (point.contains(event)[0] == True)

		if should_be_visible != annotation.get_visible():
			visibility_changed = True
			annotation.set_visible(should_be_visible)

	if visibility_changed:		
		plt.draw()

# ===========================================================================================================


# return all the topic that are bounded into the cell (bl, tr)
def getGoodTopics(topics, bl, tr):
	cell_topics = []	

	for topic in topics:
		d_topic = dict(topic)
		# get the center and the diameter of that topic and decide if the
		# topic is into the cell
		topic_loc = d_topic['loc']
		topic_s = d_topic['s']

		if m.isIntoTheCell(topic_loc, topic_s, bl, tr):
			cell_topics.append(topic)

	return cell_topics


# create the bag of topic that contains the big topics as possible for cover all the space
def getBestTopics(topics):
	topics = sorted(topics, key=itemgetter('s'), reverse=True)		
	areas = [] # list that contains all the areas covered by the topic
	final_topics = [] # list that contains the result topics		
	for topic in topics:
		t_locs = m.getBox(topic['loc'], topic['s'])			

		#check if t_locs is already inside area[]
		guard = False
		for area in areas:
			if guard == False:
				guard = m.cellIsIntoTheCell(t_locs[0],t_locs[1], area[0],area[1])	

		if guard == False:
			final_topics.append(topic)
			areas.append(t_locs)		
	return final_topics

def main(args):

	if len(args) == 1 or args[1] == '--h':
		print('Parameters : [ hostname, port, s ]')
		return 0

	# Globals
	N_WORDS_TOPICS = 20 
	N_TOPICS = 20

	# merge descriptor (1 = merge, 2 = mergeClusters)
	merge_selector = 1

	# Parameters for the db
	host = args[1]
	port = int(args[2])
	
	# Parameters for the matrix
	s = int(args[3])

	# db_parameters
	db_name = 'db_geo_index'
	collection_topics = 'topics_trentino_test' # topics with min s
	collection_a_topics = 'topics_trentino_test_approximated' # approximated topics

	# get the maximum map coordinates
	max_loc, min_loc = dao_f.getBoundaries(host, port, db_name)
		
	# TEST ========================================
	# coordinate trentino	
	min_loc = [45.690270, 10.399488]
	max_loc = [46.569637, 12.008985]

	print("ATTENZIONE : COORINATE TEST INSERITE")
	# =============================================

	# gen the matrix
	matrix = Matrix(min_loc, max_loc, s)
	matrix.toString()
	print('')

	# dbs
	dao_topics = GeoDao(host, port)
	dao_topics.connect(db_name, collection_topics)
	dao_a_topics = GeoDao(host, port)
	dao_a_topics.connect(db_name, collection_a_topics)

	cells_words = []

	#start timer
	start_time = time.time()

	while(matrix.hasNext()):
		locs = matrix.next()

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]

		# get all the topics from the approximated collection and sort them using s
		a_topics = list(dao_a_topics.getUrlsByBox(bl, tr)) # approximated topics
		b_topics = list(dao_topics.getUrlsByBox(bl, tr)) # base topics, lowest level of the tree
		b_topics = []

		topics = getGoodTopics(a_topics, bl, tr)
		topics += getGoodTopics(b_topics, bl, tr)		
		topics = getBestTopics(topics)

		# merge the topics and take the first one
		if len(topics) > 0:
			
			# merge selector 
			if merge_selector == 1:			
				cell_descriptor = tt.merge(topics, s)
			elif merge_selector == 2:
				cell_descriptor = tt.mergeClusters(topics,N_TOPICS,N_WORDS_TOPICS,s)
			# take the highest topic into the cell descriptor
			final_topics = []
			d_cell_descriptor = dict(cell_descriptor)	
			topics = d_cell_descriptor['topics']
			
			best_topic = None
			best_coerence = -1 # a low number

			for topic in topics:	
				#print(abs(topic[1]))
				if(abs(topic[1]) > best_coerence):
					best_coerence = abs(topic[1])
					best_topic = topic[0]
				#	print ('\t'+str(best_coerence))
			
			# extract the top 5 words from the best topic
			best_topic = sorted(best_topic, key=itemgetter(0), reverse=True)

			top_words = [w[1] for w in best_topic[:5]]

			# compute the coordinates for the center of the cell
			cluster_lon = bl[1] + (tr[1] - bl[1]) / 2
			cluster_lat = bl[0] + (tr[0] - bl[0]) / 2

			cells_words.append([[cluster_lat,cluster_lon], top_words])

			print(str(matrix.current) + ' : '+str(top_words))
	
	print('')
	print('# ' + str(len(cells_words))+ ' on '+str(matrix.numberOfCells))			

	#get the time of the entire process ==================================
	end_time = time.time()

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

	# ====================================================================

	dao_topics.close()
	dao_a_topics.close()
	
	
	# PLOT THE MAP========================================================

	m,ax = initMap(min_loc, max_loc)
	
	for cell in cells_words:
		points_with_annotation.append(addCell(m, ax, cell[0],cell[1]))
		
	#cursor = Cursor(ax)
	plt.connect('motion_notify_event', on_move)


	matrix.resetIterator()
	parallel_lats = []
	parallel_lons = []
	parallel_tlats = []
	parallel_tlons = []
	meridian_lats = []
	meridian_lons = []
	meridian_tlats = []
	meridian_tlons = []

	#initialize parallels
	for i in range(0,matrix.nY + 1):
		parallel_lats.append([])
		parallel_lons.append([])

	while matrix.hasNext():

		locs = matrix.next()		

		# for meridians
		if matrix.current[0] < matrix.nX:
			if matrix.current[0] == matrix.nX -1:
				meridian_tlats.append(locs[2])
				meridian_tlons.append(locs[1])
			else:
				meridian_tlats.append(locs[0])
				meridian_tlons.append(locs[1])
		else:	
			meridian_lats.append(meridian_tlats)
			meridian_lons.append(meridian_tlons)
			meridian_tlats = []	
			meridian_tlons = []
		
		# for parallels
		parallel_lats[matrix.current[0]].append(locs[0])
		parallel_lons[matrix.current[0]].append(locs[1])		

	# print meridian
	for i in range(0,len(meridian_lats)):
		x, y = m(meridian_lons[i], meridian_lats[i])
		m.plot(x,y, marker=None, color='b')	
	# print parallels
	for i in range(0,len(parallel_lats)):
		x, y = m(parallel_lons[i], parallel_lats[i])
		m.plot(x,y, marker=None, color='b')	

	#m.plot(y, x, marker=None, color='r')


	m.drawcoastlines()

	plt.title("Topics")
	plt.show()

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
