#!/usr/bin/env python3.5
import sys
import json
from pprint import pprint

# my imports
import M1_geoIndexing.geo_indexing as m1 # module 1
import M2_topicsClustering.topics_clustering_mt as m2 # module 2
import M3_resultsApproximation.topics_merging as m3 # module 3
import M4_mapVisualtization as m4 # module 4

# 1 get the conf file
# call phase 1
# call phase 2
# call phase 3


def getConf():
	with open('conf.json') as data_file:    
		data = json.load(data_file)
	return data

def main(args):

	conf = getConf()
	
	db_host = conf['host']
	db_port = int(conf['port'])

	# phase 1 conf : db_host_name, db_port, directory, db_name, collection_name, collection_name_dbstat, n_threads
	directory = conf['txt_directory']
	db_name = conf['db_name']
	collection_name_urls = conf['url_collection']
	collection_name_dbstat = conf['dbstat_collection']
	phase1_n_threads = int(conf['geo_indexing_nthread'])

	# phase 2 conf
	collection_name_topics = collection_approximation_in = conf['collection_topics']
	s = int(conf['s'])
	if conf['bounded_locs'] != "":
		bounded_locs = conf['bounded_locs']
	else:
		bounded_locs = None
	phase2_n_threads = int(conf['topicsClustering_nthread'])
	max_waiting_time_http = float(conf['max_waiting_time_http'])
	if conf['log'] == "True" :
		log = True
	else:
		log = False 

	lda_ntopics = ntopics = int(conf['lda_ntopics'])
	lda_npasses = int(conf['lda_npasses'])
	lda_nwords = nwords = int(conf['lda_nwordsfortopic'])

	collection_approximation_out = conf['collection_approximation']
	merge_selector = conf['merge_algorithm']
	npartitions = conf['n_approximation_partition']
	nlevels = conf['n_approximation_levels']

	# runs
	m1.run(db_host, db_port, directory, db_name, collection_name_urls, collection_name_dbstat, phase1_n_threads)
	
	m2.run(db_host, db_port, db_name, collection_name_urls, collection_name_dbstat, collection_name_topics, s, bounded_locs, phase2_n_threads, max_waiting_time_http, log, lda_ntopics, lda_npasses, lda_nwords)

	m3.run(db_host, db_port, db_name, collection_name_dbstat, collection_approximation_in, collection_approximation_out, bounded_locs, npartitions, nlevels, merge_selector, ntopics, nwords, s)

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
