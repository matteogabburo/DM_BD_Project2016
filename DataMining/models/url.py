#!/usr/bin/env python3.5

# Class used for manage urls from the txt
# EXAMPLE : for convert it into json the right way is : 
# url = Url(1,2,['url1','url2'])
# import json 
# json.dumps(url, default=lambda o: o.__dict__)
# >> '{"loc": [1, 2], "urls": ["url1", "url2"]}'
class Url:

	def __init__(self, latitude, longitude, urls):
		self.loc = [latitude,longitude]
		self.urls = []
		self.urls = urls
	
	def addUrl(self, url):
		self.urls.append(url)

	def setCoordinates(self, latitude, longitude):
		self.loc = (latitude, longitude)

	def getCoordinates(self):
		return self.loc

	def toString(self):
		print(self.loc)
		print(self.urls)

