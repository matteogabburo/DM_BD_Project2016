#!/usr/bin/env python3.5

# Parse tweets, and compress them in a smaller json

import os
import json
import sys

def parse_folder(folder, last_file_parsed, out_folder):
	# Get all the file in a directory
	file_list = os.listdir(folder)
	file_list.sort()

	if last_file_parsed == '0':
		for file in file_list:	
			if not os.path.isdir(folder + '/' +file):
				tw_json_list = parse(folder + '/' +file)
				out = ''
				for tweet in tw_json_list:
					out = out+tweet+'\n'

				# Save compressed json list
				if not os.path.isdir(out_folder):	
				    os.makedirs(out_folder)				

				out_file = open(out_folder + '/' +file,"w")
				out_file.write(out)
				out_file.close()
	else :
		checked = True
		for file in file_list:
			if not os.path.isdir(folder + '/' +file):
				if checked == True:
					if file == last_file_parsed:
						checked = False
				else:
					tw_json_list = parse(folder + '/' +file)
					out = ''
					for tweet in tw_json_list:
						out = out+tweet+'\n'

					# Save compressed json list
					if not os.path.isdir(out_folder):	
					    os.makedirs(out_folder)				
	
					out_file = open(out_folder + '/' +file,"w")
					out_file.write(out)
					out_file.close()
			
	return file
				

def parse(filename):
	if os.path.isfile(filename):
		in_file = open(filename ,"r")
		text = in_file.read()
		in_file.close()
		
		tweets = text.split('\n')

		# Extract fields
		tw_json_list = []		
		for tweet in tweets:
			if len(tweet) > 0:
				tw_json = json.loads(tweet)
					
				tw_json_compressed = {}
				tw_json_compressed['id'] = tw_json['id']
				tw_json_compressed['text'] = tw_json['text']
				tw_json_compressed['coordinates'] = tw_json['coordinates']
				tw_json_compressed['place'] = tw_json['place']

				json_data = json.dumps(tw_json_compressed)

				tw_json_list.append(json_data)
		return tw_json_list		

def main(args):
	# read conf file
	config_file_name = 'parseTweets.conf'
	
	if os.path.isfile(config_file_name):
		in_file = open(config_file_name ,"r")
		conf_test = in_file.read()
		options = conf_test.split('\n')
		in_file.close()
	else :
		out_file = open(config_file_name,"w")
		out_file.write('0\n0\n')
		conf_test = '0'
		out_file.close()
		options = ['0','0']

	conf_test_coordinates = options[0]
	conf_test_places = options[1]

	# Folder with big json
	folder_dataset_coordinates = './dataset_coordinates'
	folder_dataset_places = './dataset_places'

	# Folder with small json
	out_folder_dataset_coordinates = folder_dataset_coordinates+'/reduced_json'
	out_folder_dataset_places = folder_dataset_places+'/reduced_json'

	# Check if dataset folders exist
	if os.path.isdir(folder_dataset_coordinates) and os.path.isdir(folder_dataset_places):

		# Parse all the document in a folder
		options[0] = parse_folder(folder_dataset_coordinates, conf_test_coordinates, out_folder_dataset_coordinates)
		options[1] = parse_folder(folder_dataset_places, conf_test_places, out_folder_dataset_places)

		out_file = open(config_file_name,"w")
		out_file.write(options[0]+'\n'+options[1]+'\n')
		out_file.close()

	else:
		print('Folders don\'t exist.')

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))


	





