#!/usr/bin/env python3.5
import sys
import numpy
from math import radians, cos, sin, asin, sqrt

# My imports
sys.path.append('..')
import db_utils.dao
from db_utils.dao import Dao
from db_utils.dao import GeoDao
import models.url
from models.url import Url
from models.topic_clustering_matrix import Matrix
sys.path.remove('..')

# Topic clustering must: 
# 1. Find the dimension of the grid, watching
#    the urls that are in the db
# 2. Make a logical grid
#	a. optimization for the memory finding the empty cells
# 3. Using the above grid for extract rows from
#    the db
# 4. For each url:
# 	a. Check the integrity
#	b. Make LDA on it (???)
# 5. Store the results into another db


# TODO readme
# it return the max lat max lon min lat min lon from the db
def getBoundaries(host, port, db_name):
	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)
	c_list = list(dao.query('globals', ''))
	c_dict = dict(c_list[0])
	dao.close()	
	return (float(c_dict['lat_max']),float(c_dict['lon_max'])),(float(c_dict['lat_min']),float(c_dict['lon_min']))

#TODO readme
def mapSpace():
	m = 10
	n = 10
	matr = a = numpy.zeros(shape=(m,n))

	print(matr)


def main(args):
		
	host = args[1]
	port = int(args[2])
	db_name = 'db_geo_index'	
	collection_name = 'clicks'

	max_loc, min_loc = getBoundaries(host, port, db_name)

	s = 100
	matrix = Matrix(min_loc, max_loc, s)
	matrix.toString()

	# connect to geo dao
	dao = GeoDao(host, port)
	dao.connect(db_name, collection_name)

	empty_cell_counter = 0
	n_cells = 0
	while matrix.hasNext():
		locs = matrix.next()

		bl = [locs[0],locs[1]]
		tr = [locs[2],locs[3]]
		
		result = dao.getUrlsByBox(bl,tr)
	
		#do something with result
		l_res = list(result)
		if len(l_res) == 0:
			empty_cell_counter = empty_cell_counter + 1		
		n_cells = n_cells + 1

	dao.close()

	print('')
	print('# cells : '+str(n_cells))	
	print('# empty : '+str(empty_cell_counter))

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))


