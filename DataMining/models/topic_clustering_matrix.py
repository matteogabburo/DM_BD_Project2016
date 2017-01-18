#!/usr/bin/env python3.5
import geopy
from geopy.distance import VincentyDistance
from math import radians, sin, asin, cos, sqrt

# function taken and modified from http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(loc1, loc2):

	lat1 = loc1[0]
	lon1 = loc1[1]
	lat2 = loc2[0]
	lon2 = loc2[1]

	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	return km

def xyHaversine(loc1, loc2):

	lat1 = loc1[0]
	lon1 = loc1[1]
	lat2 = loc2[0]
	lon2 = loc2[1]

	#return lat
	rlat = haversine((lat1,lon1),(lat2,lon1))

	#return lon
	rlon = haversine((lat1,lon1),(lat1,lon2))

	return (rlat,rlon)

# Class used for manage the matrix on step 2
# this matrix isn't charged in RAM and it is only logically
# represented estimating the coordinates for each cell
# NOTE : the first cell (bottom left) is the 0,0 cell
# this coice is motivate becouse it improve the performance 
# of getCell
# EXAMPLE :
# tr = (46.733551, 12.327675)	
# bl = (46.037432, 11.428148)
# matr = Matrix(bl, tr, 1)
# matr.toString()		
# while matr.hasNext():
# 	matr.next()


class Matrix:
	# bottomLeftLoc is the coordinate (lat,lon) of the bottom
	# left margin of the map, topRightLoc is the coordinate 
	# (lat, lon) of the top right margin of the map, and s (km)
	# is the length of the x and y edge of each cell
	def __init__(self, bottomLeftLoc, topRightLoc, s):

		lenX,lenY = xyHaversine(bottomLeftLoc, topRightLoc)

		# converts the sizes fo the map into int
		lenX += 1
		lenY += 1
		lenX = int(lenX)
		lenY = int(lenY)

		# if the map length is not divisible from
		# s, it enlarge the size of the map finding
		# the first length divisible for s
		lenX = lenX + lenX % s
		lenY = lenY + lenY % s
	
		self.blLoc = bottomLeftLoc
		self.trLoc = topRightLoc
		self.brLoc = (self.trLoc[0], self.blLoc[1])
		self.tlLoc = (self.blLoc[0], self.trLoc[1])

		self.lenX = lenX
		self.lenY = lenY
		self.s = s

		# size of the matrix for X and Y
		# TODO probably theres a problem of overflow 
		self.nX = int(self.lenX / s) 
		self.nY = int(self.lenY / s) 

		# current is used by the iterator
		self.current = [0,0]
	
	
	# given the x and y matrix coordinates it return
	# the map coordinates of the bottom left and the 
	# top right of the cell as (latbl,lonbl,lattr,lontr)
	def getCellBT(self, x, y):

		xb,yb = self.getCellB(x,y)
		xt,yt = self.getCellB(x+1,y+1)
	
		return xb,yb,xt,yt
	
	# given the x and y matrix coordinates it return
	# the map coordinates of the bottom left of the 
	# selected cell
	def getCellB(self, x, y):

		ang90 = 90
		ang0 = 0

		# calculus of the X coordinate
		# dx = distance on x edge
		if x > 0:
			dx = self.s * x
			origin = geopy.Point(self.blLoc)
			destination = VincentyDistance(kilometers=dx).destination(origin, ang0)
			lata = destination.latitude
		elif x == 0:
			lata = self.blLoc[0]

		# calculus of the Y coordinate
		# dy = distance on y edge
		if y > 0:
			dy = self.s * y
			origin = geopy.Point(self.blLoc)
			destination = VincentyDistance(kilometers=dy).destination(origin, ang90)
			lona = destination.longitude
		elif y == 0:
			lona = self.blLoc[1]
		
		
		return (lata, lona)


	def __iter__(self):
		return self.getCellBT(self.current[0], self.current[1])

	def hasNext(self):
		if self.current[0] >= self.nX and self.current[1] >= self.nY:
			return False
		else:
			return True 

	def next(self): # Python 3: def __next__(self)
		if self.current[0] > self.nX:
			self.current[0] = 0
			self.current[1] = self.current[1] + 1
			if self.current[1] > self.nY:
				raise StopIteration
		else:
			self.current[0] = self.current[0] + 1	

		return self.getCellBT(self.current[0], self.current[1])


	def toString(self):
		print('main top-right coordinate : \t'+str(self.trLoc))
		print('main bottom-left coordinate : \t'+str(self.blLoc))
		print('s (km) : \t\t\t'+str(self.s))
		print('len of X edge (km) : \t\t'+str(self.lenX))
		print('len of Y edge (km) : \t\t'+str(self.lenY))
		print('len of X edge (#cells) : \t'+str(self.nX))
		print('len of Y edge (#cells) : \t'+str(self.nY))
		print('Number of cells : \t\t'+str(self.nY * self.nX))
		print('Current pos of iterator : \t'+str(self.current))
		

