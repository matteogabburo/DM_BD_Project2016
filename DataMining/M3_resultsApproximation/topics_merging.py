#!/usr/bin/env python3.5
import sys
import time

# My imports
sys.path.append('..')
import db_utils.dao as d
from models.topics_tree import TopicsTree
sys.path.remove('..')

# WHAT TOPICS TREE HAS TO DO
# 1. Take the min s
# 2. Using the min s, divide the db (topics db) into sectors that are multiple of s (for now 4*s) for a fixed num of levels
# 3. Merge the topics using a merge function
# 4. Save the computed topics into the db


def run(host, port, db_name, dbstat_collection_name, collection_in, collection_out, bounded_locs, partitions, nlevels, merge_selector, ntopics, nwords, s):

	start_time = time.time()

	if bounded_locs != None:
		min_loc = bounded_locs[0]
		max_loc = bounded_locs[1]
	else:
		min_loc, max_loc = d.getBoundaries(host, port, db_name, dbstat_collection_name)

	# tree generation
	tree = TopicsTree(min_loc, max_loc, s, nlevels, partitions)

	if merge_selector == 1:
		tree.generate_cluster(host, port, db_name, collection_in, collection_out, ntopics, nwords)
	elif merge_selector == 2:
		tree.generate(host, port, db_name, collection_in, collection_out, ntopics)
	else :
		print('ERROR : Merge function undefined')

	end_time = time.time()

	logs = {}
	logs['time'] = end_time - start_time

	return logs

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
	
	run(host, port, db_name, 'globals', collection_in, collection_out, [min_loc, max_loc],4 ,4, 1, 20, 20, s)
	
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
