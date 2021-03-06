"""SimpleApp.py"""

import pyspark as ps
from pyspark import SparkContext, SparkConf
from pyspark.mllib.clustering import LDA
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.linalg import SparseVector
from pyspark.ml.feature import Word2Vec
from pyspark.sql import SparkSession
from numpy.testing import assert_almost_equal, assert_equal

#IMPORT to remove!!
from operator import add
################################################

conf = SparkConf()
conf.setMaster("local")
conf.setAppName("Test Spark")
conf.set("spark.executor.memory", "1g")
sc = SparkContext(conf = conf)

"""
spark = SparkSession\
        .builder\
        .appName("LDA example")\
        .getOrCreate()


"""
#x = sc.parallelize([(1,1),(1,2),(1,3),(1,4),(2,4),(2,3)])

#data = [
#	(1,[1, Vectors.dense([0.0, 1.0])]),
#	(2,[1, Vectors.dense([0.0, 1.0])]),
#	(1,[2, SparseVector(2, {0: 1.0})])
#	]

data = [
	(1,["ciao","come","stai", "ciao", "come", "va"]),
	(2,["goku","non","lo","sai"]),
	(1,["ciao","c","e","f","e","m","e","t","e","t"]),
	(2,["n","r"]),
	(1,["c","e","m"]),
	(3,["$","*","£","!","?","@","#",":",";","$","~","[","]","{","}","{","}","#"]),
	(4,["aa","aaaaaaa","aaaaa","aaaaaa","aaaa","aaaa","aaaaaaaaaaaaaaaa","aaaa","aaaaaaaaa"]),
	(3,["$","'",":",";","~","~","~","~","~"]),
	(4,["aaaa","aaaaaaaa","aaa","aa","aa","aaaaaaaa","aaaaaaaaa","a","aaaaaaaaaaaaaaaa","$","aaaaa","aaaaa","aaaaa","aaaaa","aaaaaaaa","aa","aa","aaaaaaaaaaaaaa"]),
	(5,["x","x","x","x","x","x","x","x","x"]),
	(3,["$",".","¬","|","+","`","!","^","^","$","[","]","%","%","%","(",")","="])
	]
rdd = sc.parallelize(data)

#print(x[1])

#print(x.map(lambda x: (x[0],[x[1]])).reduceByKey(lambda x,y: x+y).collect())

#the value element of a pair is converted into a list type
def mapTupleValueToList(element): 
	#def printMapping(x):
	#	print("\nMapping\n")
	#	return x
	#res = printMapping(x)
	return (element[0],[element[1]])

def concatenateList(listA, listB): 
	#print("\nconcatenation\n")
	return listA + listB

#run LDA on a RDD composed by RDD[x]=((ID,SparseVector(...)))
def runLDA(data,NumberOfTopics):
	#print("\n\n\n%")
	#print(data)
	data = sc.parallelize(data)
	#print("$")
	#print(data)
	#print("\n\n\n")
	model = LDA.train(data,k=NumberOfTopics,seed=1)
	return model

#convert a Topic(= ([word_0_ID,word_1_ID, ...] , [prob_0_ID, prob_1_ID, ...]) )
def mapTopicWithDictionary(Topic,Dictionary):
	topicMapped = []
	for i in range(len(Topic[0])):
		word = Topic[0][i]
		weight = Topic[1][i]
		#result=(weight,word)
		for key, value in Dictionary.items():
			if word == value:
				wtext = key
		result = [weight,wtext]
		topicMapped.append(result)
	return topicMapped

#converts the ID of a list of topics in a RDD produced by LDA into the mapped word
def mapSetTopicsWithDictionary(SetTopics,Dictionary):
	topics = []
	for topic in SetTopics:
		topics.append(mapTopicWithDictionary(topic, Dictionary))
	return topics

#extract topics from an LDA model, with the assigned Dictionary and a maximum number of words-per-topic
def getTopicsFromLDA(LDA, Dictionary, NumberOfTerms):
	result = LDA.describeTopics(NumberOfTerms)
	result = mapSetTopicsWithDictionary(result, Dictionary)
	return result

#convert a Document(= (documentID, (word_0, word_1, ...)) ) into a SparseVector type
def documentToSparseVector(document, vocabulary):
	_id = document[1]
	doc = document[0]
	
	docMap = {}
	
	for word in doc:
		if(word not in vocabulary):
			continue
		key = vocabulary[word]
		if(key not in docMap):
			docMap[key] = 0
		docMap[key] = docMap[key] + 1
	
	return (_id,SparseVector(len(vocabulary),docMap))

#return a LDA model + its Dictionary, given a set of Documents(= [[word0, word1, ...] , [word0, word1, ...] , ... ] )
#if OnlineOptimizer (boolean) is set to True it uses OnlineLDAOptimizer, o.w. it uses EMLDAOptimizer
def getCellLDA(Documents, NumberOfTopics, OnlineOptimizer):
	#print("\n\n\n/////////////////////////////////////////////////////////////////////////////////////")
	#print("FUCK OFF")
	#print("docs:")
	#print(Documents.collect())
	corpus = Documents#.flatMap(lambda x: x[1])#sc.parallelize(Documents)
	#print("corpus:")
	#print(corpus.collect())
	term_counts = corpus.flatMap(lambda x: x).map(lambda x: (x,1)).reduceByKey(lambda x,y: x+y)
	#term_counts.cache()
	#print("term_counts:")
	#print(term_counts)
	#print(term_counts.collect())
	#print(term_counts.collect())
	#print("vocabulary:")
	vocabulary = term_counts.map(lambda x: x[0]).zipWithIndex().collectAsMap()
	#print(vocabulary)
	#print("______________________________________________________________________________________\n\n")
	#print("_____________________________________________________________________________________")
	#print(vocabulary)
	#print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	
	
	documents = corpus.zipWithIndex().map(lambda doc: documentToSparseVector(doc,vocabulary)).map(list)
	#print(documents.collect())
	#print("*************************************************************************************")
	
	Optimizer = "online" if OnlineOptimizer else "em"
	lda = LDA.train(documents, k=NumberOfTopics, maxIterations=20, optimizer=Optimizer)
	#print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	#print(result)
	#print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
	return lda, vocabulary#[lda.describeTopics(), vocabulary]

#given a set with cell tuples(= (CellID,Document)), return the list of (CellID, (lda, dictionary) )
def getMapLDA(GridRDD, NumberOfTopics):
	#each element [x] of GridRDD is a tuple (CellID,Corpus)
	
	#prepare data for LDA
	data = GridRDD \
		.groupByKey() \
		.map(lambda x : (x[0], list(x[1])))# \
	#	.collect()
	#print(data.collect())
	#print("$$$$$$$$$")
	keys = data.map(lambda x: x[0]).collect()
	#print("keys")
	#print(keys)
	#print("data")
	#print(data.collect())
	#data = [(cellID, data.filter(lambda x: x[0] == cellID).flatMap(lambda x: x[1])) for cellID in keys]
	
	new = []
	for cellID in keys:
		pair = (cellID, data.filter(lambda x: x[0] == cellID).flatMap(lambda x: x[1]).cache())
		new.append(pair)
		#print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		#print(cellID)
		#print(pair[1].collect())
		#print("££")
	
	data = new
	print("\n\n\n\n\n")
	
	
	l_lda = []
	for element in data:
		#print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		#print(element[0])
		#print(element[1])
		#print(element[1].collect())
		#print("\n\n\n")
		l_lda.append([element[0], getCellLDA(element[1], NumberOfTopics, False)])
	
	data = l_lda
	#print("end")
	#print(data)
	#print("\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n")
	return data


data = getMapLDA(rdd,20)#.describeTopics()

for ID,(lda,vocabulary) in data:#element in data:
	print("\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
	print(ID)
	#topics = element[0]
	#vocabulary = element[1]
	#print(mapSetTopicsWithDictionary(topics, vocabulary))
	print(getTopicsFromLDA(lda,vocabulary,10))#NumberOfWordsPerTopic=10
	print("\n\n")
	print(vocabulary)
	print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n")

