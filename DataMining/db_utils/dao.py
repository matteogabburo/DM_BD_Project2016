import sys
import pymongo
from pymongo import MongoClient, GEO2D

# TODO readme
# it return the max lat max lon min lat min lon from the db
def getBoundaries(host, port, db_name, collection_name):
	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)
	c_list = list(dao.query(collection_name, ''))
	c_dict = dict(c_list[0])
	dao.close()	
	return (float(c_dict['lat_max']),float(c_dict['lon_max'])),(float(c_dict['lat_min']),float(c_dict['lon_min']))


# Connect to a database, parameters are the host of the db, the port
# where the db is waiting and the name of the database. It returns a 
# description of the opened database
def connectDB(host, port, db_name):

	client = MongoClient(HOST, PORT)
	db = client[db_name]
	return db	


# This function add to the db (parameter 1 is the descriptor of the
# db) a given document to a collection (parameter 2 is the name of 
# the desired collection ). REMEMBER this row MUST be the JSON of 
# an element. This function returns an instances of the insert_one
# result
# Example : result = addOneRow(db_descriptor, collection_name , {'loc':[1,1]} )
def addOneRow(db, collection_name, document):

	result = db[collection_name].insert_one(document)
	return result


# This function add to the db (parameter 1 is the descriptor of the
# db) a given list of documents to a collection (parameter 2 is the 
# name of the desired collection ). If the collection does not exist,
# it create neuer oneREMEMBER this row MUST be a list containing the 
# JSON of the elements. This function returns an instance of the 
# insert_many result
# Example : result = addMoreRows(db_descriptor, collection_name , [{'loc':[1,1]},{'loc':[1,1]}] )
def addMoreRows(db, collection_name, documents):

	result = db[collection_name].insert_many(documents)
	return result
	

# Simple class that manage the db
# Example of workflow :
#
# dao = Dao(HOST, PORT)
# dao.connect('geo_example')
# res = dao.addOne('places',{"loc": [1, 1]})
# res = dao.addMany('places',[{"loc": [1, 1]},{"loc": [1, 1]}])
# dao.close()
class Dao:

	def __init__(self, host, port):
		self.client = None
		self.db	= None
		self.host = host
		self.port = port

	def connect(self, db_name):
		self.client = MongoClient(self.host, self.port)
		self.db = self.client[db_name]
	
	def addOne(self, collection_name, document):
		result = self.db[collection_name].insert_one(document)
		return result

	def addMany(self, collection_name, documents):
		result = self.db[collection_name].insert_many(documents)
		return result

	def query(self, collection_name, query):
		if query != '':
			return self.db[collection_name].find(query)
		else:
			return self.db[collection_name].find()

	def bufferizzedQuery(self, collection_name, query, limit):
		if query != '':
			return self.db[collection_name].find(query).limit(limit)
		else:
			return self.db[collection_name].find().limit(limit)

	def aggregate(self, collection_name, query):
		return self.db[collection_name].aggregate(query)
	
	def updateOne(self, collection_name, id_doc, document):
		return self.db[collection_name].update_one(id_doc, document, upsert=False)

	def removeAll(self, collection_name):
		self.db[collection_name].remove({})

	def close(self):
		self.client.close()	

	def __del__(self):
		self.close()


# EXAMPLE
# host = 'localhost'
# port = 27017
# db_name = 'db_geo_index'	
# dao = GeoDao(host, port)
# dao.connect(db_name, 'clicks')
# locBl = [45.378154, 11.580687]
# locTr = [46.162651, 12.991187]
# res = dao.getUrlsByBox(locBl, locTr)
# print(list(res))
class GeoDao(Dao):

	def __init__(self, host, port):
		Dao.__init__(self,host,port)		
		self.collection = None		

	def connect(self, db_name, collection):
		Dao.connect(self, db_name)
		self.collection = collection
		self.db[collection].create_index([('loc', GEO2D)])


	def getUrlsByBox(self, locBl, locTr):
		query = {"loc": {"$within": {"$box": [locBl, locTr]}}}
		return self.query(self.collection, query)

	def __del__(self):
		self.close()
