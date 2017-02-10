#!/usr/bin/env python3.5
import sys
import os
import time
from scipy import stats

import requests
from bs4 import BeautifulSoup
from math import sqrt

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

MINSIZE_WORD = 4
MAXSIZE_WORD = 15
MINSIZE_CHARSDOC = 100
MINSIZE_WORDSDOC = 50

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
			if len(response.text) > MINSIZE_CHARSDOC: # if the page has only 20 chars cut it		
				return True
			else:
				return False
		else :
			return False
	except:
		return False	

# return an url of an upper layer of a given url. 
# Example1 : https://www.google.it/search?q=hello+world -> https://www.google.it/search
# Example2 : https://www.google.it/search -> https://www.google.it
# It returns None if the remaining url is something like "https://" or something meaningless (len < 8)
def get_url_upperlevel(url, maximize_links):
	if maximize_links == True:
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
	else:
		return None

	
# Return only the text of an html page, all the text in lowercase, and without punctuation.
# Remove all the tags
def html2text(html):

	cleaner = Cleaner()
	cleaner.javascript = True # This is True because we want to activate the javascript filter
	cleaner.style = True 
	cleaner.scripts = True	
	cleaner.comments = True
	cleaner.links = True
	cleaner.meta = True
	cleaner.page_structure = True
	cleaner.processing_instructions = True
	cleaner.forms = True	
	cleaner.add_nofollow = True

	#html = unicodedata.normalize('NFKD', html).encode('ascii','ignore')

	try:
		document = lxml.html.document_fromstring(html)
		c = cleaner.clean_html(document)
		html = lxml.html.tostring(c)

		soup = BeautifulSoup(html, 'lxml')
		parsed_text = soup.get_text()		

		if(len(parsed_text) > MINSIZE_CHARSDOC):
			return parsed_text.lower()	
		else:
			return None
	except: 
		return None


#TODO change documentation
# This function is used for get the html corpus of a given url. If the url is inconsistent it do other tries with upper 
# levels of the url, if all the url is inconsistent, it parse the url and return it as the corpus.
# It returns an array with the html page of a given url and a code that says how many error inconsistence that were  
# found during the process (usefull for compute weights) : [CORPUS, CODE].  If all the url is inconsistent it 
# return -1 as number of errors and it means that the returning corpus is the parsed url.
def get_url_html_corpus(url, max_waiting_time, maximize_links, l_fails):

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
				cutted_url = get_url_upperlevel(cutted_url, maximize_links)
				if cutted_url != None:
					try:
						response = None
						response = requests.get(cutted_url, timeout=t)
					except: 
						#print('\n \t -> Problem with this url : '+cutted_url)
						a = 1# TMP
				
					if check_url_status(response) == True:
						corpus = response.text
						#ret.append(corpus)
						guard = True
					elif cutted_url.count('/') == 2:
						# Add a bad link to fails list
						l_fails.append(cutted_url.split('/')[2])
				else:
					return [None,l_fails]

		
	#except requests.exceptions.RequestException as e:
	except: 
		l_fails.append(url.split('/')[2])	
		return [None,l_fails]

	return [corpus, l_fails]


#TODO change doc
# This function parse html page that comes from 'get_url_html_corpus' and return it only with the text
def get_url_text_corpus(url, max_waiting_time, maximize_links, l_fails):

	ret = get_url_html_corpus(url, max_waiting_time, maximize_links,  l_fails)
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
			#p_stemmer = PorterStemmer()
			
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
			#stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens5]
	
			# remove all the word that are meaning less
			ret = []
			for word in stopped_tokens5:
				if not any(char.isdigit() for char in word):
					if len(word) > 1:
						#check if the word has the alphabet character
						if isAlphabet(word):				
							ret.append(word)

			return [ret,l_fails]
		else:
			return [None,l_fails]
	else:
		return [None,l_fails]


def isAlphabet(word):

	alphabet = ['a','b','c','d','e','f','g','h','j','k','i','l','m','n','o','p','q','r','s','t','u','v','x','y','w','z','à','è','é','ì','í','ò','ó','ù','ú']
	guard = True
	for t in word:
		if t not in alphabet:
			guard = False
	return guard
	



# TODO change documentation
# Given a file name it download all the 'good' corpus (exclude that are not in text/html 
# format and http status 404 403 ecc) and returns a list of corpus : 
# [['word1','word2'],[...]]
def get_corpuses_by_file(filename, max_waiting_time, maximize_links, l_fails):

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
					out = get_url_text_corpus(url, max_waiting_time, maximize_links, l_fails)
					ret = out[0]
					l_fails = out[1]
						
					if ret != None:		
						corpuses.append(ret)
	return [corpuses, l_fails]



# TODO change documentation
# Given a set of urls, download all the 'good' corpus (exclude that are not in text/html 
# format and http status 404 403 ecc) and returns a list of corpus : 
# [['word1','word2'],[...]]
# remove junk == 1 -> static remove junk == 2 -> dinamic
def get_corpuses(urls_list, max_waiting_time, l_fails, log, maximize_links, selector_removeJunk, negative_removejunk, positive_removejunk):

	start_time = time.time()

	#elements for print
	s_urls = len(urls_list)
	counter = 0
	loss = 0

	corpuses = []
	for url in urls_list:		
		ret = None	
		out = get_url_text_corpus(url, max_waiting_time, maximize_links, l_fails)
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
	if corpuses != None:
		if selector_removeJunk == 1:
			corpuses = removeJunk(corpuses, negative_removejunk, positive_removejunk)	
		elif selector_removeJunk == 2:
			corpuses = removeJunk_var(corpuses, negative_removejunk, positive_removejunk)

	end_time = time.time()
	final_time = end_time - start_time	

	# logs for the stats
	logs = {}
	logs['nurls'] = counter
	logs['nloss'] = loss
	logs['time'] = final_time
	
	logs_junk = {}
	if (selector_removeJunk == 1 or selector_removeJunk == 2):
		if len(corpuses) > 0:
			logs_junk['j_nw'] = corpuses[1]
			logs_junk['j_nr'] = corpuses[2]
			logs_junk['j_avg'] = corpuses[3]
			logs_junk['j_var'] = corpuses[4]
			corpuses = corpuses[0]
		else:
			logs['nloss'] = logs['nurls']

	logs['txt_p'] = logs_junk

	return [corpuses, l_fails, logs]

# function that remove junk from corpuses. It cut all the words with less frequency than nfc
# the words with frequency > than pfc
def removeJunk(corpuses, nfc, pfc):

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
		varFrequence = varFrequence  - avgFrequence * avgFrequence	
		varFrequence = varFrequence / (len(words) * len(words))	
		
		if varFrequence < 0.00001:
			varFrequence = 0.0
		else:
			varFrequence = sqrt(varFrequence)	

		'''
		print('\n')
		print(avgFrequence)	
		print(varFrequence)
		'''


	if len(words) > 0:

		# thresholds with negative and positive frequences cutters
		negativeThreshold = avgFrequence / nfc
		positiveThreshold = highestFrequence - avgFrequence / pfc	

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
				if words[word] > negativeThreshold and words[word] < positiveThreshold and len(word) < MAXSIZE_WORD and len(word) > MINSIZE_WORD:
					ret_corpus.append(word)
				else:
					nremovedwords += 1
			if len(ret_corpus) > MINSIZE_WORDSDOC: 
				ret.append(ret_corpus)

		if len(ret) > 0:
			return [ret, nwords, nremovedwords, avgFrequence, varFrequence] 	
		else:	
			return []
	else:
		return []

def removeJunk_var(corpuses, ntm, ptm):
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
		varFrequence = varFrequence  - avgFrequence * avgFrequence	
		varFrequence = varFrequence / (len(words) * len(words))	

		if varFrequence < 0.00001:
			varFrequence = 0.0
		else:
			varFrequence = sqrt(varFrequence)			

	if len(words) > 0:

		# thresholds ntm is negative treshold multiplier and ptm is positive threshold multiplier for the variance
		'''negativeThreshold = avgFrequence - ntm * varFrequence
		positiveThreshold = avgFrequence + ptm * varFrequence'''
		
		
		negativeThreshold = positiveThreshold = 0
		if len(words) < 30: #use z
		
			z = {}	#dict for z table
			z['0.7'] = 1.04
			z['0.75'] = 1.15
			z['0.8'] = 1.28
			z['0.85'] = 1.44
			z['0.9'] = 1.645
			z['0.92'] = 1.75
			z['0.95'] = 1.96
			z['0.96'] = 2.05
			z['0.98'] = 2.33
			z['0.99'] = 2.58

			negativeThreshold = f_approximation(avgFrequence - z[str(ntm)] * (varFrequence / sqrt(len(words))))
			positiveThreshold = f_approximation(avgFrequence + z[str(ptm)] * (varFrequence / sqrt(len(words))))

		else : # use t-student
			#print(str(ntm) +' , '+str(len(words)))
			#print(str(avgFrequence)+' - '+str(stats.t.ppf(ntm, len(words)))+' * '+str((varFrequence / sqrt(len(words)))))
			negativeThreshold = f_approximation(avgFrequence - stats.t.ppf(ntm, len(words)) * (varFrequence / sqrt(len(words))))
			positiveThreshold = f_approximation(avgFrequence + stats.t.ppf(ptm, len(words)) * (varFrequence / sqrt(len(words))))

		'''if negativeThreshold < 1:
			negativeThreshold = 1'''

		'''print('==============')
		print(negativeThreshold)
		print(positiveThreshold)		
		print('==============')'''

		ret = []
		# remove words from the text
		nremovedwords = 0
		nwords = 0
		for corpus in corpuses:
			ret_corpus = []
			for word in corpus:
				nwords += 1
				if words[word] >= negativeThreshold and words[word] <= positiveThreshold:
					ret_corpus.append(word)
				else:
					nremovedwords += 1
			if len(ret_corpus) > MINSIZE_WORDSDOC: 
				ret.append(ret_corpus)

		if len(ret) > 0:
			return [ret, nwords, nremovedwords, avgFrequence, varFrequence] 	
		else:	
			return []
	else:
		return []


def f_approximation(number):

	i_number = int(number)
	if (number - i_number) > 0.5:
		return i_number + 1
	else:
		return i_number

def main(args):
	
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
