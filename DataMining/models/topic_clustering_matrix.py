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


# return the locs of the box with center 'loc' and diameter dim of the edge equal to s
def getBox(loc, s):
	s = s / 2
	origin = geopy.Point(loc)

	dEst = VincentyDistance(kilometers=s).destination(origin, 0)
	dNorth = VincentyDistance(kilometers=s).destination(origin, 90)	
	dWest = VincentyDistance(kilometers=s).destination(origin, 180)		
	dSouth = VincentyDistance(kilometers=s).destination(origin, 270)
			
	bl = dWest[0], dSouth[1]
	tr = dEst[0], dNorth[1]

	return [bl, tr]


# return True if the lock is into the area between bl and tr, if not return false
def locIsInto(loc, bl, tr):

	if loc[0] < tr[0] and loc[0] > bl[0] and loc[1] < tr[1] and loc[1] > bl[1]:
		return True
	else:
		return False

# return true if the given coordinate with the given s(diameter) is into the cell, else return false
def isIntoTheCell(loc, s, bl, tr):
	s = s / 2 - s / 16 # for avoid approximation error in the following steps
	#print(s)
	origin = geopy.Point(loc)
	# East distance
	dEst = VincentyDistance(kilometers=s).destination(origin, 0)
	if locIsInto(dEst, bl, tr):
		# North distance
		dNorth = VincentyDistance(kilometers=s).destination(origin, 90)
		if locIsInto(dNorth, bl, tr):			
			# West distance
			dWest = VincentyDistance(kilometers=s).destination(origin, 180)		
			if locIsInto(dWest, bl, tr):									
				# South distance
				dSouth = VincentyDistance(kilometers=s).destination(origin, 270)
				if locIsInto(dSouth, bl, tr):
					return True
	return False	

# return true if the new cell is inside the second one, if not return false. new -> (nbl, ntr) old -> (bl, tr)
def cellIsIntoTheCell(nbl, ntr, bl, tr):
	
	nbr = ntr[0],nbl[1]
	ntl = nbl[0],ntr[1]

	guard = False
	
	if locIsInto(nbl, bl, tr):
		return True
	if locIsInto(nbr, bl, tr):
		return True
	if locIsInto(ntr, bl, tr):
		return True
	if locIsInto(ntl, bl, tr):
		return True

	return guard	


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

		self.numberOfCells = (self.nY+1) * (self.nX+1)
	
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
		if self.current[1] > self.nY:
			return False
		else:
			return True 

	def next(self):
		if self.hasNext():
			if self.current[0] >= self.nX:
				self.current[0] = 0
				self.current[1] = self.current[1] + 1
			else:
				self.current[0] = self.current[0] + 1	
		else:
			raise StopIteration

		return self.getCellBT(self.current[0], self.current[1])


	def toString(self):
		print('main top-right coordinate : \t'+str(self.trLoc))
		print('main bottom-left coordinate : \t'+str(self.blLoc))
		print('s (km) : \t\t\t'+str(self.s))
		print('len of X edge (km) : \t\t'+str(self.lenX))
		print('len of Y edge (km) : \t\t'+str(self.lenY))
		print('len of X edge (#cells) : \t'+str(self.nX+1))
		print('len of Y edge (#cells) : \t'+str(self.nY+1))
		print('Number of cells : \t\t'+str(self.numberOfCells))
		print('Current pos of iterator : \t'+str(self.current))
		

