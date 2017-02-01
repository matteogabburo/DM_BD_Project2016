#!/usr/bin/env python3.5
import sys

# My imports
sys.path.append('..')
from models.topics_tree import TopicsTree
sys.path.remove('..')

# WHAT TOPICS TREE HAS TO DO
# 1. Take the min s
# 2. Using the min s, divide the db (topics db) into sectors that are multiple of s (for now 4*s) for a fixed num of levels
# 3. Merge the topics using a merge function
# 4. Save the computed topics into the db


def main(args):

	if len(args) == 1 or args[1] == '--h':
		print('Parameters : [ hostname, port, s ]')
		return 0

	host = args[1]
	port = int(args[2])
	s = int(args[3])

	#parameters 
	db_name = 'db_geo_index'
	collection_in = 'topics_trentino_test'
	collection_out = 'topics_trentino_test_approximated'

	# TEST ========================================
	# coordinate trentino	
	min_loc = [45.690270, 10.399488]
	max_loc = [46.569637, 12.008985]

	print("ATTENZIONE : COORINATE TEST INSERITE")
	# =============================================


	# tree generation
	tree = TopicsTree(min_loc, max_loc, s, 4)
	tree.generate_cluster(host, port, db_name, collection_in, collection_out)
	


	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
