#!/usr/bin/env python3.5

# Class used for manage db_stat document 
# This document contains 
# 	- The max and min lat of the dataset
#	- The max and min lon of the dataset
# NOTE : modify is used for the persistance
class Db_stat:

	def __init__(self, lat_max, lon_max, lat_min, lon_min):
		self.lat_max = float(lat_max)
		self.lon_max = float(lon_max)
		self.lat_min = float(lat_min)
		self.lon_min = float(lon_min)
		self.modify = False
	
	def isModify(self):
		return self.modify

	def setModified(self):
		self.modify = True

	def updateLat(self, lat):	
		lat = float(lat)
		if lat > self.lat_max :	
			self.lat_max = lat
			self.modify = True
		elif lat < self.lat_min :	
			self.lat_min = lat
			self.modify = True

	def updateLon(self, lon):
		lon = float(lon)	
		if lon > self.lon_max :	
			self.lon_max = lon
			self.modify = True
		elif lon < self.lon_min :	
			self.lon_min = lon
			self.modify = True

	def merge(self, db_stat):
		self.updateLat(db_stat['lat_max'])
		self.updateLon(db_stat['lon_max'])
		self.updateLat(db_stat['lat_min'])
		self.updateLon(db_stat['lon_min'])			

	def getCoordinates(self):
		return [self.lat_max, self.lon_max, self.lat_min, self.lon_min]

	def toString(self):
		print(self.lat_max)
		print(self.lon_max)
		print(self.lat_min)
		print(self.lon_min)

