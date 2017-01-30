#!/usr/bin/env python3.5
import sys
from operator import itemgetter
import geopy
from geopy.distance import VincentyDistance

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
			guard = m.cellIsIntoTheCell(t_locs[0],t_locs[1], area[0],area[1])	
		
		if guard == False:
			final_topics.append(topic)
			areas.append(t_locs)		
	return final_topics

def main(args):

	if len(args) == 1 or args[1] == '--h':
		print('Parameters : [ hostname, port, s ]')
		return 0

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

	# dbs
	dao_topics = GeoDao(host, port)
	dao_topics.connect(db_name, collection_topics)
	dao_a_topics = GeoDao(host, port)
	dao_a_topics.connect(db_name, collection_a_topics)

	while(matrix.hasNext()):
		locs = matrix.next()

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]

		# get all the topics from the approximated collection and sort them using s
		a_topics = list(dao_a_topics.getUrlsByBox(bl, tr)) # approximated topics
		b_topics = list(dao_topics.getUrlsByBox(bl, tr)) # base topics, lowest level of the tree
		
		topics = getGoodTopics(a_topics, bl, tr)
		topics += getGoodTopics(b_topics, bl, tr)
		topics = getBestTopics(topics)	
	
		# merge the topics and take the first one
		if len(topics) > 0:
			cell_descriptor = tt.merge(topics, s)
		
			# take the highest topic into the cell descriptor
			final_topics = []
			d_cell_descriptor = dict(cell_descriptor)	
			topics = d_cell_descriptor['topics']
			
			best_topic = None
			best_coerence = 99999999 # an high number
			for topic in topics:		
				if(abs(topic[1]) < best_coerence):
					best_coerence = abs(topic[1])
					best_topic = topic[0]
			
			# extract the top 5 words from the best topic
			best_topic = sorted(best_topic, key=itemgetter(0), reverse=True)
			top_words = [w[1] for w in best_topic[:5]]
			
			print(top_words)

	dao_topics.close()
	dao_a_topics.close()
	
			


	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
