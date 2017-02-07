#!/usr/bin/env python3.5
import sys
from operator import itemgetter


sys.path.append('..')
import utils.http_requests as http
sys.path.remove('..')



def avg_list(numbers):
	res = 0.0
	numbers = [n for n in numbers if n > -100]
	if len(numbers) > 0:
		for number in numbers:
			res += number
		return res / len(numbers)
	else:
		return 0.0

def main(args):

	urls = ['https://www.karamasoft.com/UltimateSpell/Samples/LongText/LongText.aspx',
	'http://catdir.loc.gov/catdir/enhancements/fy0711/2006051179-s.html',	
	'http://www.w3schools.com/html/html_examples.asp'
	
	]

	corpuses = []
	for url in urls:
		print(url)
		ret = http.get_url_text_corpus(url,10,[])[0]
		if ret != None:
			corpuses += http.get_url_text_corpus(url,10,[])[0]


	dbefore = getdistribution(corpuses)


	print(corpuses)

	print( http.removeJunk_var(corpuses,0.99,0.99))
	dafter = getdistribution(http.removeJunk_var(corpuses,0.70,0.70))
	

	plot(dbefore, dafter)

def getdistribution(corpuses):
	d_words = {}
	for word in corpuses:
		if word in d_words:
			d_words[word] += 1
		else:
			d_words[word] = 1
	
	l_freq = []
	setwords = list(d_words)
	for word in d_words:
		l_freq.append(d_words[word])

	l_freq.sort()
	
	print(l_freq)

	max_f_x = l_freq[len(l_freq) - 1]
	min_f_x = l_freq[0]
		
	d_freq = {}
	for freq in l_freq:
		if freq in d_freq:
			d_freq[freq] += 1
		else:
			d_freq[freq] = 1	
	
	l_plot= []
	for i in range(min_f_x, max_f_x):
		if i in d_freq:
			l_plot.append(d_freq[i])
		else:
			l_plot.append(0)

	print(l_plot)
	
	#find the highest and lowest y
	max_f_y = 0
	
	for f in l_plot:
		if f > max_f_y:
			max_f_y = f	

	return l_plot, max_f_x, min_f_x, max_f_y


def plot(l1y,l2y):

	import numpy as np
	import matplotlib.pyplot as plt

	# red dashes, blue squares and green triangles

	l1x = [i for i in range(0,len(l1y))]
	l2x = [i for i in range(0,len(l2y))]

	plt.plot(l1x,l1y,'r--')
	plt.plot(l2x,l2y,'k')
	
	plt.show()


if __name__ == '__main__':
	sys.exit(main(sys.argv))
