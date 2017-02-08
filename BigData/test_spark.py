"""SimpleApp.py"""
import sys


from pyspark import SparkConf, SparkContext

sys.path.append('../libraries')
import M1_geoIndexing.geo_indexing as m1 # module 1
sys.path.remove('../libraries')

def fun(x, y):
	return x,y+1

def getConf():
	with open('conf.json') as data_file:    
		data = json.load(data_file)
	return data
		
def main(args):


	# get conf
	conf = getConf()
	
	db_host = conf['host']
	db_port = int(conf['port'])
	directory = conf['txt_directory']
	db_name = conf['db_name']
	collection_name_urls = conf['url_collection']
	collection_name_dbstat = conf['dbstat_collection']


	# links extraction
	logs['m1'] = m1.run(db_host, db_port, directory, db_name, collection_name_urls, collection_name_dbstat, phase1_n_threads)	


	conf = SparkConf()
	conf.setMaster("local")
	conf.setAppName("Test Spark")
	conf.set("spark.executor.memory", "1g")
	sc = SparkContext(conf = conf)

	rdd = sc.parallelize(["b", "a", "c"])
	a = rdd.map(lambda x: fun(x, 1)).collect()

	print('\n\n\n\n\n'+str(a)+'\n\n\n\n\n\n')

if __name__ == '__main__':
	sys.exit(main(sys.argv))
