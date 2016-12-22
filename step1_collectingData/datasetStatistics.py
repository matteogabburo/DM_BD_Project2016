#!/usr/bin/env python3.5

# Make and print statistics of the dataset

import sys
import os
import json

def count_folder_elements(folder_name):
	# Get all the file in a directory
	file_list = os.listdir(folder_name)
	file_list.sort()

	counter = 0
	for file in file_list:
		counter = counter + count_file_elements(folder_name+'/'+file)

	return counter
		
def count_file_elements(filename):
	if os.path.isfile(filename):
		in_file = open(filename ,"r")
		text = in_file.read()
		in_file.close()
		
		tweets = text.split('\n')
		return len(tweets)
	return 0


def main(args):
	# Folder with big json
	folder_dataset_coordinates = './dataset_coordinates'
	folder_dataset_places = './dataset_places'

	# Folder with small json
	out_folder_dataset_coordinates = folder_dataset_coordinates+'/reduced_json'
	out_folder_dataset_places = folder_dataset_places+'/reduced_json'


	# Check if dataset folders exist
	if os.path.isdir(folder_dataset_coordinates) and os.path.isdir(folder_dataset_places):
		# Make stat for coordinates folder
		counter_coordinates = count_folder_elements(folder_dataset_coordinates)
		if os.path.isdir(out_folder_dataset_coordinates):
			counter_parsed_coordinates = count_folder_elements(out_folder_dataset_coordinates)	

		# Make stat for places folder
		counter_places = count_folder_elements(folder_dataset_places)
		if os.path.isdir(out_folder_dataset_places):
			counter_parsed_places = count_folder_elements(out_folder_dataset_places)	

		print(' + Coordinates folder contains : '+str(counter_coordinates)+' elements')
		print('\t- '+str(counter_parsed_coordinates)+' on '+str(counter_coordinates)+' are already compressed')

		print(' + Places folder contains : '+str(counter_places)+' elements')
		print('\t- '+str(counter_parsed_places)+' on '+str(counter_places)+' are already compressed')
		

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))




