#!/usr/bin/env python3.5
import sys
import os
import time
import threading

# My imports
sys.path.append('..')
import db_utils.dao
from db_utils.dao import Dao
import models.url
from models.url import Url
from models.db_stat import Db_stat
sys.path.remove('..')

# Open a file passed for parameter and return the text. If the file does not exist it return 'None'
def openFile(filename):
	
	if os.path.isfile(filename):	
		in_file = open(filename ,"r")
		text = in_file.read()
		in_file.close()
		return text
	else : 
		return None

# Get a list of file into a directory ordered by name. If the directory does not exist it return 'None'
def getFilesList(directory):
	
	if os.path.isdir(directory):
		return [os.path.join(directory, f) for f in os.listdir(directory)]
	else :
		return None

# Get an array that contains the rows of the dataset in this order : 
# [GPS coordinates[Latitude, longitude], [url 1, url 2, ..., url n]].
# It returns None if the file does not exist
def getRowsList(filename):
	
	text = open_file(filename)
	if text == None:
		return None
	else :
		row_list = []
		rows = text.split('\n')
		for row in rows:
			parsed_row = parse_row(row)
			if  parsed_row != None :
				row_list.append(parsed_row)
		return row_list

# Parse a txt dataset row, and return an istance of an object Url defined in url.py.
# The actual format of each row in the text dataset is "gps_latitude, gps_longitude, {URL1|URL2|...|URLN}"
def parse_row(row):
	if len(row) > 0:
		
		arguments = row.split(',')
		
		# arguments are :
		# argument[0] = latitude
		# argument[1] = longitude
		# argument[2] = list of urls

		arguments[2] = arguments[2][1:-1]
		urls = arguments[2].split('|')

		return Url(arguments[0], arguments[1], urls)
	
	else :
		return None


# Persist the txt dataset row by row into a mongodb
def persist(filename, host_name, port, db_name, collection_name, collection_name_dbstat):
	
	# Definition of max lat and lon
	lat_max = None
	lat_min = None
	lon_max = None
	lon_min = None
	# Used like a hinge 
	first_url = None

	# Check if the file is a txt
	if filename.endswith('.txt'):
		with open(filename, 'r') as f:
			text = f.read()
		
			# Open db
			dao = Dao(host_name, port)
			dao.connect(db_name)

			rows = text.split('\n')

			counter = 0
			size = len(rows)
		
			print('# Number of rows in \"'+filename+'\": ' + str(size)+'\n')

			# Get the maximum coordinates from the db
			stat = list(dao.query(collection_name_dbstat, ''))
			l_db = None
			if len(stat) > 0:		
				stat_dict = dict(stat[0])
				lat_max = stat_dict['lat_max']
				lat_min = stat_dict['lat_min']
				lon_max = stat_dict['lon_max']
				lon_min = stat_dict['lon_min']
				l_db = Db_stat(lat_max, lon_max, lat_min, lon_min)		

			for row in rows: 
				url = parse_row(row)
				if url != None:
				
					loc = url.getCoordinates()
					if l_db == None:
						l_db = Db_stat(loc[0], loc[1], loc[0], loc[1])	
						l_db.setModified()
					else:	
						l_db.updateLat(loc[0])
						l_db.updateLon(loc[1])	
					
					res = dao.addOne(collection_name, url.__dict__)
				
				counter = counter + 1					
				if counter % (size // 20) == 0:
					print(str(100 // (size / counter)) + ' % Done of \"'+ filename+'\"')

			# add lat_max, lon_max, lat_min and lon_min to db if are better
			stat = list(dao.query(collection_name_dbstat, ''))
			if len(stat) > 0:			
				stat_dict = dict(stat[0])
				if l_db.isModify() == True:

					doc_id = stat_dict["_id"] 

					if l_db.lat_max > float(stat_dict['lat_max']):
						dao.updateOne(collection_name_dbstat, {'_id': doc_id},{'$set':{"lat_max":l_db.lat_max}})
					if l_db.lat_min < float(stat_dict['lat_min']):
						dao.updateOne(collection_name_dbstat, {'_id': doc_id},{'$set':{"lat_min":l_db.lat_min}})
					if l_db.lon_max > float(stat_dict['lon_max']):
						dao.updateOne(collection_name_dbstat, {'_id': doc_id},{'$set':{"lon_max":l_db.lon_max}})
					if l_db.lon_min < float(stat_dict['lon_min']):			
						dao.updateOne(collection_name_dbstat, {'_id': doc_id},{'$set':{"lon_min":l_db.lon_min}})
			else :
				dao.addOne(collection_name_dbstat, l_db.__dict__)

			dao.close()
	print('100 % Done of \"'+ filename+'\"')


# Definition of a class used for thread and parallelize the extraction of rows from the files
class GeoIndexingThread(threading.Thread):
	def __init__(self, file_name, host_name, port, db_name, collection_name, collection_name_dbstat):
		threading.Thread.__init__(self)
		self.file_name = file_name 
		self.host_name = host_name
		self.port = port
		self.db_name = db_name
		self.collection_name = collection_name
		self.collection_dbstat = collection_name_dbstat
	def run(self):
		persist(self.file_name, self.host_name, self.port, self.db_name, self.collection_name, self.collection_dbstat)
			
def main(args):
	db_name = 'db_geo_index'
	collection_name = 'clicks'
	collection_name_dbstat = 'globals'
	
	# args[1] = directory, args[2] = db_host_name args[3] = db_port

	# get files names
	file_list = getFilesList(args[1])
	file_list.sort()

	# How many threads works in the same moment	
	n_threads = 5
	if len(file_list) < n_threads:
		n_threads = len(file_list)

	for file_name in file_list:
		if os.path.isfile(file_name):

			t = GeoIndexingThread(file_name, args[2], int(args[3]),
					  db_name, collection_name, collection_name_dbstat)
			t.start()
			
			if threading.active_count() > n_threads:
				while threading.active_count() > n_threads:
					time.sleep(0.1) 
					
	while threading.active_count() > 1:
		time.sleep(0.1) 


	# if there are more than row in 'globals' merge them
	dao = Dao(args[2], int(args[3]))
	dao.connect(db_name)
	
	generals_list = list(dao.query(collection_name_dbstat, ''))
	print(generals_list)
	db_stat = None
	if len(generals_list) > 1:
		for e in generals_list:
			if db_stat == None:	
				db_stat = Db_stat(e['lat_max'],e['lon_max'],e['lat_min'],e['lon_min'])
			else:
				db_stat.merge(e)
		dao.removeAll(collection_name_dbstat)
		dao.addOne(collection_name_dbstat, db_stat.__dict__)
	dao.close()
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
