#!/usr/bin/env python3.5
import sys
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# My imports
sys.path.append('..')
import db_utils.dao
from db_utils.dao import Dao
import models.url
from models.url import Url
sys.path.remove('..')


# For the installation of mpl_toolkits.basemap :
#	1. Install conda (python dep manager)
#	2. launch 'conda install -c anaconda basemap=1.0.7 '

def plotMap(host, port, db_name):

	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)

	c_list = list(dao.query('globals', ''))
	c_dict = dict(c_list[0])
	
	dao.close()

	# Select the map
	m = Basemap(projection='mill',llcrnrlat=int(c_dict['lat_min']),urcrnrlat=int(c_dict['lat_max']+1),llcrnrlon=int(c_dict['lon_min']),urcrnrlon=int(c_dict['lon_max']+1),resolution='i')

	m.drawcoastlines()
	m.drawcountries()
	m.drawstates()
	m.fillcontinents(color='#04BAE3',lake_color='#FFFFFF')
	m.drawmapboundary(fill_color='#FFFFFF')

	
	# Get maps coordinate
	dao = Dao(host, port)
	dao.connect(db_name)

	it = dao.query('clicks', '')
	

	counter = 0
	hasNext = True
	while hasNext and counter < 20000:
		#x,y = m(lon,lat)			#m.plot(x,y, 'ro')
		try: 
			url = next(it, None)
		except StopIteration:
			hasNext = False
		
		if hasNext:	
			loc = url['loc']
			lat,lon = float(loc[0]),float(loc[1])
			x,y = m(lon,lat)
			m.plot(x,y, 'ro')
		counter += 1
		
		if counter % 1000 == 0:
			print(counter)			
	dao.close()

	plt.title("Geo Plotting")
	plt.show()


def main(args):

	host = args[1]
	port = int(args[2])

	db_name = 'db_geo_index'

	plotMap(host, port, db_name)

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
