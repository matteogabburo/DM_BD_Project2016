#!/usr/bin/env python3.5

# Script for collecting tweets and create dataset with geotagged contents

import tweepy
import time
import os
import json
import sys

def main(args):
	# Access data
	consumer_key = 'GnNshPqO6gq2hil2VKJcXmo84'
	consumer_secret = 'PT6t5zwPtJFLXExqTHgWiJzN7PgBmiFoESCs6gxauwAu8k6Htz'
	access_token = '632206582-knvnozwt1wQybGtYdP5x2MtBwlJvjEf0PAdEQUYb'
	access_token_secret = 'z2dJ5emH1JJ5tF109xXp4oKIF21g80RhH0phyJx4uTAcO'

	# Authentication for twitter api
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	# Create alias for twitter api
	api = tweepy.API(auth, wait_on_rate_limit = True, retry_delay = 10, retry_errors=True, timeout=600)

	# Parameters
	nrpp = 100
	npage = 1500

	# Queries
	par_lang = 'en' 
	par_rpp = str(nrpp) # number of tweets for queryes Max 100
	par_geocode = '40.812138,-73.935354,1000km' # Coordinates of New York
	par_since_id = '0'
	par_page = str(npage)

	i = 1 # Index for coordinates
	global_i = i
	k = 1 # Index for places
	global_k = k
	j = 0 # Index for count tweets

	# Output file definition
	folder_coordinate = 'dataset_coordinates'
	name_coordinate = 'tweets_'
	folder_place = 'dataset_places'
	name_place = 'tweets_place_'
	filelen = 50

	# Check if the dataset folders exist, if not create them
	folder_coordinate = './'+folder_coordinate 
	if not os.path.isdir(folder_coordinate):	
	    os.makedirs(folder_coordinate)

	folder_place = './'+folder_place
	if not os.path.isdir(folder_place):	
	    os.makedirs(folder_place)
	
	tweets = ''
	tweetsplace = ''

	# BackUp of dataset parameters
	t1 = time.time()
	backup_time = 600 # 10 minutes

	print('\033[34m\033[1mTweet Finder\033[21m\033[39m\n')

	while True:
		#for result in tweepy.Cursor(api.search, lang=par_lang, rpp=par_rpp, count=par_page, geocode=par_geocode, since_id=par_since_id).items():
		for page in tweepy.Cursor(api.search, lang=par_lang, rpp=par_rpp, count=par_page, geocode=par_geocode, since_id=par_since_id).pages():
			for result in page:
				j = j+1

				# Check only tweets with coordinates
				if result.coordinates != None:
					print('\n\033[92m[ Coordinates found ...')
					print('ID : \t\t'+str(result.id))	
					print('COORDINATES : \t'+str(result.coordinates))	
					print('TEXT : \t\t'+str(result.text))
					print(' ]\033[39m\n')
			
					res_json = json.dumps(result._json)
					tweets = tweets + str(res_json) + '\n'

					if i%filelen == 0:
						day = str(time.strftime("%Y%m%d"))	
						hour = str(time.strftime(":%H%M%S"))

						filename = name_coordinate+day+hour

						print('\033[35mMaking file named : \033[1m'+filename+'\033[21m\033[39m\n')		
				
						# Print on file
						out_file = open(folder_coordinate+'/'+filename,"w")
						out_file.write(tweets)
						out_file.close()
				
						tweets = ''

					i = i+1
					global_i = global_i + 1

				# Check only tweet with place and/or coordinates
				if result.place != None:
					print('\n\033[93m[ Places found ...')
					print('ID : \t\t'+str(result.id))	
					print('PLACE : \t'+str(result.place))	
					print('TEXT : \t\t'+str(result.text))
					print(' ]\033[39m\n')

					res_json = json.dumps(result._json)
					tweetsplace = tweetsplace + str(res_json) + '\n'

					if k%filelen == 0:
						day = str(time.strftime("%Y%m%d"))	
						hour = str(time.strftime(":%H%M%S"))

						filename = name_place+day+hour

						print('\033[35mMaking file named : \033[1m'+filename+'\033[21m\033[39m\n')		
				
						# Print on file
						out_file = open(folder_place+'/'+filename,"w")
						out_file.write(tweetsplace)
						out_file.close()
				
						tweetsplace = ''

					k = k+1
					global_k = global_k + 1
			
		
				# Save all with time boundary
				t2 = time.time()
				if t2 - t1 >= backup_time:
					day = str(time.strftime("%Y%m%d"))	
					hour = str(time.strftime(":%H%M%S"))

					filename = name_place+day+hour

					print('\033[35mMaking file named : \033[1m'+filename+'\033[21m\033[39m\n')		
		
					# Print on file
					out_file = open(folder_place+'/'+filename,"w")
					out_file.write(tweetsplace)
					out_file.close()
		
					tweetsplace = ''

					filename = name_coordinate+day+hour

					print('\033[35mMaking file named : \033[1m'+filename+'\033[21m\033[39m\n')		
			
					# Print on file
					out_file = open(folder_coordinate+'/'+filename,"w")
					out_file.write(tweets)
					out_file.close()
			
					tweets = ''

					# Reset k and i			
					k = 1 
					i = 1 

				t1 = t2

				par_since_id=result.id
		
				if j%nrpp == 0:		
					print(':: '+ str(global_i-1) +' on '+ str(j) + ' found with coordinates')
					print(':: '+ str(global_k-1) +' on '+ str(j) + ' found with places')
				#time.sleep(1)
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
