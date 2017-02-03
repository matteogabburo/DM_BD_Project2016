#!/usr/bin/env python3.5
import sys
import os
import time

import requests
from bs4 import BeautifulSoup

import lxml
from lxml.html.clean import Cleaner

from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer

# My import 
# My imports
sys.path.append('..')
import utils.print_tools as pt
sys.path.remove('..')


# Open a file passed for parameter and return the text. If the file does not exist it return 'None'
def open_file(filename):
	
	if os.path.isfile(filename):	
		in_file = open(filename ,"r")
		text = in_file.read()
		in_file.close()
		return text
	else : 
		return None



#TODO documentation
def write_on_file(out_filename, str):
	out_file = open(out_filename ,"w")
	out_file.write(corpuses)
	out_file.close()


# Parse the row retourning the representation of the row to an array with this format : 
# [GPS coordinates[Latitude, longitude], [url 1, url 2, ..., url n]].
# It returns None if the row is empty
# NOTE : if you want you can change this method in order to manage different formats of rows in the dataset	 
def parse_row(row):
	if len(row) > 0:
		# The actual format of each row in the text dataset is "gps_latitude, gps_longitude, {URL1|URL2|...|URLN}"
		arguments = row.split(',')

		coordinates = []
		coordinates.append(arguments[0])
		coordinates.append(arguments[1])	

		arguments[2] = arguments[2][1:-1]
		urls = arguments[2].split('|')

		res = []
		res.append(coordinates)
		res.append(urls)

		return res
	
	else :
		return None


# Ceck if the url is meaningfull and if it has contents. Return true if it hasm and false in the other cases
def check_url_status(response):
	try:
		if response.status_code == 200 and 'text/html' in response.headers['content-type']:	
			return True
		else :
			return False
	except:
		return False	

# return an url of an upper layer of a given url. 
# Example1 : https://www.google.it/search?q=hello+world -> https://www.google.it/search
# Example2 : https://www.google.it/search -> https://www.google.it
# It returns None if the remaining url is something like "https://" or something meaningless (len < 8)
def get_url_upperlevel(url):
	s_url = url.split('/')[2]
	
	if '?' in url:
		array = url.rpartition('?')
	elif len(url) > 8 and '/' in url:
		array = url.rpartition('/')
		if len(array[0]) <= 8:
			return None
	else :
		return None
	return array[0]

	
# Return only the text of an html page, all the text in lowercase, and without punctuation.
# Remove all the tags
def html2text(html):

	cleaner = Cleaner()
	cleaner.javascript = True # This is True because we want to activate the javascript filter
	cleaner.style = True 

	#html = unicodedata.normalize('NFKD', html).encode('ascii','ignore')

	try:
		document = lxml.html.document_fromstring(html)
		c = cleaner.clean_html(document)
		html = lxml.html.tostring(c)


		soup = BeautifulSoup(html, 'lxml')
		parsed_text = soup.get_text()		

		ret = ''
		for char in parsed_text:
			if char.isalnum():
				ret = ret + char
			elif char == ' ':
				ret = ret + char
		return ret.lower()	
	except: 
		return None


#TODO change documentation
# This function is used for get the html corpus of a given url. If the url is inconsistent it do other tries with upper 
# levels of the url, if all the url is inconsistent, it parse the url and return it as the corpus.
# It returns an array with the html page of a given url and a code that says how many error inconsistence that were  
# found during the process (usefull for compute weights) : [CORPUS, CODE].  If all the url is inconsistent it 
# return -1 as number of errors and it means that the returning corpus is the parsed url.
def get_url_html_corpus(url, max_waiting_time, l_fails):

	# maximum waiting time
	t = float(max_waiting_time)
	
	try:
		s_url = url.split('/')[2]
	except:
		return [None,l_fails]
	if s_url in l_fails:
		return [None,l_fails]

	ret = []
	try:
		response = requests.get(url, timeout=t)

		if check_url_status(response) == True:
			corpus = response.text
			#ret.append(corpus)
		else :
			guard = False
			cutted_url = url
			while guard == False:
				cutted_url = get_url_upperlevel(cutted_url)
				if cutted_url != None:
					response = requests.get(cutted_url, timeout=t)
					if check_url_status(response) == True:
						corpus = response.text
						#ret.append(corpus)
						guard = True
					elif cutted_url.count('/') == 2:
						# Add a bad link to fails list
						l_fails.append(cutted_url.split('/')[2])
				else:
					return [None,l_fails]

		
	except requests.exceptions.RequestException as e:
		return [None,l_fails]

	return [corpus, l_fails]


#TODO change doc
# This function parse html page that comes from 'get_url_html_corpus' and return it only with the text
def get_url_text_corpus(url, max_waiting_time, l_fails):

	ret = get_url_html_corpus(url, max_waiting_time,  l_fails)
	l_fails = ret[1]	
	document = ret[0]

	if ret[0] != None:
		document = ret[0]		
		document = html2text(document)

		# Remove \n and separators
		tmp = ''
		oldc = ''

		if document != None:
			document = document.replace('\t',' ').replace('\n',' ')
			for c in document:
				if c != '\n' and c != '\t':
					if c == ' ':
						if oldc != ' ':
							tmp = tmp + c									
					else :
						tmp = tmp + c
		
				oldc = c
			document = tmp

			tokenizer = RegexpTokenizer(r'\w+')

			# create English stop words list
			en_stop = get_stop_words('en')
			it_stop = get_stop_words('it')
			sp_stop = get_stop_words('es')
			ge_stop = get_stop_words('de')
			fr_stop = get_stop_words('fr')

			# Create p_stemmer of class PorterStemmer
			p_stemmer = PorterStemmer()
			
			# clean and tokenize document string
			raw = document.lower()
			tokens = tokenizer.tokenize(raw)
	
			# remove stop words from tokens
			stopped_tokens1 = [i for i in tokens if not i in en_stop]
			stopped_tokens2 = [i for i in stopped_tokens1 if not i in it_stop]
			stopped_tokens3 = [i for i in stopped_tokens2 if not i in sp_stop]
			stopped_tokens4 = [i for i in stopped_tokens3 if not i in ge_stop]
			stopped_tokens5 = [i for i in stopped_tokens4 if not i in fr_stop]
		
			# stem tokens
			stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens5]
	
			# remove all the word that are meaning less
			ret = []
			for word in stemmed_tokens:
				if not any(char.isdigit() for char in word):
					ret.append(word)

			
	
			return [ret,l_fails]
		else:
			return [None,l_fails]
	else:
		return [None,l_fails]



# TODO change documentation
# Given a file name it download all the 'good' corpus (exclude that are not in text/html 
# format and http status 404 403 ecc) and returns a list of corpus : 
# [['word1','word2'],[...]]
def get_corpuses_by_file(filename, max_waiting_time, l_fails):

	text = open_file(filename)

	corpuses = []

	if text == None:
		return None
	else :
		rows = text.split('\n')
		for row in rows:
			parsed_row = parse_row(row)
			if  parsed_row != None :	
				
				urls = parsed_row[1]			
				for url in urls:
					ret = None	
					out = get_url_text_corpus(url, max_waiting_time, l_fails)
					ret = out[0]
					l_fails = out[1]
						
					if ret != None:		
						corpuses.append(ret)
	return [corpuses, l_fails]



# TODO change documentation
# Given a set of urls, download all the 'good' corpus (exclude that are not in text/html 
# format and http status 404 403 ecc) and returns a list of corpus : 
# [['word1','word2'],[...]]
def get_corpuses(urls_list, max_waiting_time, l_fails, log=True):

	start_time = time.time()

	#elements for print
	s_urls = len(urls_list)
	counter = 0
	loss = 0

	corpuses = []
	for url in urls_list:		
		ret = None	
		out = get_url_text_corpus(url, max_waiting_time, l_fails)
		# Print infos
		counter += 1
		pt.conditionalPrintCB(0,s_urls,counter,'\t'+str(counter)+'/'+str(s_urls), log)

		ret = out[0]
		l_fails = out[1]
		
		if ret != None:		
			corpuses.append(ret)
		else:
			loss += 1
	# Print infos
	pt.conditionalPrintCB(0,s_urls,counter,'\t'+str(counter)+'/'+str(s_urls)+'\t # loss : ' +str(loss), log)
	pt.conditionalPrint('',log)

	# remove junk
	junkres = removeJunk(corpuses)	
	
	end_time = time.time()
	final_time = end_time - start_time	

	# logs for the stats
	logs = {}
	logs['nurls'] = counter
	logs['nloss'] = loss
	logs['time'] = final_time

	corpuses = []
	if len(junkres) > 0:
		corpuses = junkres[0]

		logs['j_nwords'] = junkres[1]
		logs['j_nremovedwords'] = junkres[2]
		logs['j_avgFrequence'] = junkres[3]
		logs['j_varFrequence'] = junkres[4]
	else:
		logs['nloss'] = logs['nurls']

	return [corpuses, l_fails, logs]

# function that remove junk from corpuses. It cut all the words with less frequency than avg/2 and
# the words with frequency > than max frequence - avg/4 
def removeJunk(corpuses):
	words = {}
	
	highestFrequence = 0
	# word frequence
	for corpus in corpuses:
		for word in corpus:
			if word in words:
				words[word] += 1
			else:
				words[word] = 1
			if words[word] > highestFrequence:
				highestFrequence = words[word]
			
	# avg frequence
	avgFrequence = 0.0
	for word in words:
		avgFrequence += words[word]

	if len(words) > 0:
		avgFrequence = avgFrequence / len(words)

	# variance 
	varFrequence = 0.0
	for word in words:
		varFrequence += words[word] * words[word]
	
	if len(words) > 0:	
		varFrequence = varFrequence / len(words) - avgFrequence	* avgFrequence	

	if len(words) > 0:

		# thresholds
		negativeThreshold = avgFrequence / 2
		positiveThreshold = highestFrequence - avgFrequence / 4	

		if negativeThreshold < 1:
			negativeThreshold = 1

		ret = []
		# remove words from the text
		nremovedwords = 0
		nwords = 0
		for corpus in corpuses:
			ret_corpus = []
			for word in corpus:
				nwords += 1
				if words[word] > negativeThreshold and words[word] < positiveThreshold:
					ret_corpus.append(word)
				else:
					nremovedwords += 1
			if len(ret_corpus) > 20: 
				ret.append(ret_corpus)

		if len(ret) > 0:
			return [ret, nwords, nremovedwords, avgFrequence, varFrequence] 	
		else:	
			return []
	else:
		return []


def main(args):

	in_filename = args[1]
	out_filename = args[2]
	max_waiting_time = float(args[3])
	
	l_fails = []

	#ret = get_corpuses_by_file(in_filename, max_waiting_time, l_fails)	
	#corpuses = ret[0]
	#l_fails = ret[1]	

	urls = []
	urls.append('http://www.google.com')
	urls.append('http://www.google.com')
	urls.append('http://www.fidal.it/societa/ASD-A-S-A-DETUR-NAPOLI/NA078')
	urls.append('http://stackoverflow.com/questions/6797984/how-to-convert-string-to-lowercase-in-python')

	ret = get_corpuses(urls, max_waiting_time, l_fails)

	corpuses = ret[0]
	l_fails = ret[1]

	out_file = open(out_filename ,"w")
	text = out_file.write(str(corpuses))
	out_file.close()

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
