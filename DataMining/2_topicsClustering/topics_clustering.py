#!/usr/bin/env python3.5
import sys

# My imports
sys.path.append('..')
import db_utils.dao
from db_utils.dao import Dao
import models.url
from models.url import Url
sys.path.remove('..')

# Topic clustering must: 
# 1. Find the dimension of the grid, watching
#    the urls that are in the db
# 2. Make a logical grid
# 3. Using the above grid for extract rows from
#    the db
# 4. For each url:
# 	a. Check the integrity
#	b. Make LDA on it (???)
# 5. Store the results into another db


# This function return a tupla contains the top right coordinate
# and the bottom left coordinate of all the results
# NOTE : mongodb uses coordinates between 180 and -180
# NOTE2 : for large db this function does not work for memory exceed
def getGridDimension(host, port, db_name):
	dao = Dao(host, port)	
	dao.connect(db_name)
	
	# find the four coordinates query
	query = [
	    { "$unwind": "$loc" },
	    { "$group": { 
		"_id": "$_id",
		"lat": { "$first": "$loc" },
		"lon": { "$last": "$loc" }
	    }},
	    { "$group": {
		"_id": None,
		"min_lat": { "$min": "$lat" },
		"min_lon": { "$min": "$lon" },
		"max_lat": { "$max": "$lat" },
		"max_lon": { "$max": "$lon" }
	    }}
	]
	
	result_list = list(dao.aggregate('clicks',query))
	result = dict(result_list[0])
	bottom_left = (result['min_lat'],result['min_lon'])
	top_right = (result['max_lat'],result['max_lon'])	
	res = [bottom_left, top_right]

	dao.close()

	return res



def main(args):
	import pprint
	print(getGridDimension('localhost', 27017, 'db_geo_index'))



	from mpl_toolkits.basemap import Basemap
	import matplotlib.pyplot as plt
	import numpy as np

	map = Basemap(projection='merc', lat_0 = 57, lon_0 = -135,
	    resolution = 'h', area_thresh = 0.1,
	    llcrnrlon=-136.25, llcrnrlat=56.0,
	    urcrnrlon=-134.25, urcrnrlat=57.75)
	 
	map.drawcoastlines()
	map.drawcountries()
	map.fillcontinents(color = 'coral')
	map.drawmapboundary()
	 
	lon = -135.3318
	lat = 57.0799
	x,y = map(lon, lat)
	map.plot(x, y, 'bo', markersize=24)
	 
	plt.show()


	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))


