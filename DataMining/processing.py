#!/usr/bin/env python3.5
import sys
import json
import datetime
import json
from pprint import pprint

# my imports
sys.path.append('../libraries')
import M1_geoIndexing.geo_indexing as m1 # module 1
import M2_topicsClustering.topics_clustering_mt as m2 # module 2
import M3_resultsApproximation.topics_merging as m3 # module 3
import M4_mapVisualtization as m4 # module 4
sys.path.remove('../libraries')

# 1 get the conf file
# call phase 1
# call phase 2
# call phase 3


def getConf(conffile):
	with open(conffile) as data_file:    
		data = json.load(data_file)
	return data

def main(args):

	if len(args) < 3:
		print('Error, insert parameters [conf_file_path][out_file_path]')
		return 0

	conf_file = args[1]
	out_file = args[2]

	if len(args) == 4:
		execution = int(args[3])

	conf = getConf(conf_file)
	
	db_host = conf['host']
	db_port = int(conf['port'])

	#exit data name
	test_name = conf['test_name']

	# phase 1 conf : db_host_name, db_port, directory, db_name, collection_name, collection_name_dbstat, n_threads
	directory = conf['txt_directory']
	db_name = conf['db_name']
	collection_name_urls = conf['url_collection']
	collection_name_dbstat = conf['dbstat_collection']
	phase1_n_threads = int(conf['geo_indexing_nthread'])

	# phase 2 conf
	text_processing_func = int(conf['junk_function'])
	low_treshold = int(conf['junk_low_threshold'])
	high_treshold = int(conf['junk_high_threshold'])

	collection_name_topics = collection_approximation_in = conf['collection_topics']
	s = int(conf['s'])
	if conf['bounded_locs'] != "":
		bounded_locs = conf['bounded_locs']
	else:
		bounded_locs = None
	phase2_n_threads = int(conf['topicsClustering_nthread'])
	maximize_links = conf['maximize_links']
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
	logs = {}
	logs['date'] = str(datetime.datetime.now())
	logs['params'] = conf

	if execution == 123 or execution == 12 or execution == 1 or execution == 13:
		logs['m1'] = m1.run(db_host, db_port, directory, db_name, collection_name_urls, collection_name_dbstat, phase1_n_threads)

	if execution == 123 or execution ==12 or execution == 2 or execution == 23:
		logs['m2'] = m2.run(db_host, db_port, db_name, collection_name_urls, collection_name_dbstat, collection_name_topics, s, text_processing_func, low_treshold, high_treshold, bounded_locs, phase2_n_threads, maximize_links, max_waiting_time_http, log, lda_ntopics, lda_npasses, lda_nwords)

	if execution == 123 or execution ==13 or execution == 3 or execution == 23:
		logs['m3'] = m3.run(db_host, db_port, db_name, collection_name_dbstat, collection_approximation_in, collection_approximation_out, bounded_locs, npartitions, nlevels, merge_selector, ntopics, nwords, s)

	print(out_file)	

	# write logs	
	if out_file[len(out_file)-1] == '/':
		out_logs_file_name = out_file+test_name+'_'+str(logs['date'])+'.json'
	else:
		out_logs_file_name = out_file+'/'+test_name+'_'+str(logs['date'])+'.json'

	print('Writing logs into a file called '+ out_logs_file_name +'...')

	with open(out_logs_file_name, 'w') as outfile:
		json.dump(logs, outfile)

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
