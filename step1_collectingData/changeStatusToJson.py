# This script should transform old data into a new json format


import os
import tweepy
import re	


def parse_folder(folder):
	# Get all the file in a directory
	file_list = os.listdir(folder)
	file_list.sort()

	for file in file_list:	
		out = parse(folder + '/' +file)
		
		out_file = open(folder + '/' +file,"w")
		out_file.write(out)
		out_file.close()

def parse(filename):
	if os.path.isfile(filename):
		in_file = open(filename ,"r")
		text = in_file.read()
		in_file.close()
		
		text = text.replace('Status','\nStatus')

		text = re.sub('\n\n', '\n', text)		

		lines = text.split('\n')
		out = ''
		i  =0 
		for line in lines:
			line = re.sub('Status.*_json=', '', line)						
			line = re.sub('(}.*$)', '}', line)			
			i = i + 1				
			out = out + line + '\n'
	
		print(i)
		#return text
		return out

		
# Check if dataset folders exist
folder_dataset_coordinates = './try1'
folder_dataset_places = './try2'

if os.path.isdir(folder_dataset_coordinates) and os.path.isdir(folder_dataset_places):

	# Parse all the document in a folder
	parse_folder(folder_dataset_coordinates)
	parse_folder(folder_dataset_places)
else:
	print('Folders don\'t exist.')



