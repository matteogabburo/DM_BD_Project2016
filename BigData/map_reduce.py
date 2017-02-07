"""SimpleApp.py"""
import sys


from pyspark import SparkConf, SparkContext

def fun(x, y):
	return x,y+1
		
def main(args):

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
