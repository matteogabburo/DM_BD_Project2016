#!/usr/bin/env python3.5
import sys
import json
import math	

import numpy as np
import matplotlib.pyplot as plt

def getJson(filename):
	with open(filename) as data_file:    
		data = json.load(data_file)
	return data

def avgList(l):
	ret = 0
	for e in l:
		ret += e
	return ret/len(l)

def mulList(l, k):
	for i in range(0,len(l)):
		l[i] = l[i] * k
	return l

def div2List(l1, l2):
	return [a/b for a,b in zip(l1,l2)]


def makeM2stats(g_nurl,g_nloss,g_download_time, partials, original_coherences, my_coherences, lda_performance):

	print('')
	print('MAKING STATS OF M2')

	print(g_nurl)
	print(g_nloss)
	print(g_download_time) 
	print(partials)
	print(original_coherences) 
	print(my_coherences)
	print(lda_performance)

	
	#avg MY coherences 	
	original_avg_coherence = [0 for i in range(0,len(original_coherences[0]))]
	for c in original_coherences:
		#c.sort()
		ic = 0
		for e in c:
			original_avg_coherence[ic] += e
			ic += 1

	for i in range(0,len(original_avg_coherence)):
		original_avg_coherence[i] = original_avg_coherence[i] / len(original_coherences)
	
	
	#avg MY coherences 
	my_avg_coherence = [0 for i in range(0,len(my_coherences[0]))]
	for c in my_coherences:
		#c.sort()
		ic = 0
		for e in c:
			my_avg_coherence[ic] += e
			ic += 1
	
	for i in range(0,len(my_avg_coherence)):
		my_avg_coherence[i] = my_avg_coherence[i] / len(my_coherences)

	#my_avg_coherence = [math.log10(n) for n in my_avg_coherence]

	print(my_avg_coherence)
	k = 1/1000
	my_avg_coherence = mulList(my_avg_coherence, k)

	
	original_avg_coherence_x = [i for i in range(0,len(original_avg_coherence))]
	my_avg_coherence_x = [i for i in range(0,len(my_avg_coherence))]

	#print(original_avg_coherence)

	print('============')
	print(my_avg_coherence)
	print(original_avg_coherence)

	res = mulList(div2List(original_avg_coherence, my_avg_coherence), 1000)

	print(res)

	print(original_coherences[0])

	for i in range(0,20):
		#original_coherences[i] = mulList(original_coherences[i], k)
		#original_coherences[i] = [math.log1p(n) for n in original_coherences[i]]
		plt.plot(original_avg_coherence_x, original_coherences[i],'r--')#original_avg_coherence,'r--')

		#my_coherences[i] = mulList(my_coherences[i], k)
		#my_coherences[i] = [math.log1p(n) for n in my_coherences[i]]
		plt.plot(my_avg_coherence_x,my_coherences[i],'k') #my_avg_coherence,'k')

	#plt.plot(my_avg_coherence_x, res,'g')
	
	plt.show()



	print('')

def main(args):

	filename = args[1]
	logs = getJson(filename)

	conf = logs['params']	
	


	'''if 'm1' in logs:
		logM1 = logs['m1']
		print(logM1['time'])'''

	if 'm2' in logs:	
		logM2 = logs['m2']		
		print(logM2['time'])
	
		threads = logM2['threads']
		g_nurl = 0
		g_nloss = 0
		g_download_time = 0
		partials = []
		original_coherences = []
		my_coherences = []	
		lda_performance = []
		for thread in threads:
			# LINKS 

			http = thread['http']
			nurl = 0
			nloss = 0
			download_time = 0	
			for cell in http:
				nurl += cell['nurls']
				nloss += cell['nloss']
				download_time += cell['time']
				# TODO textprocessing
			g_nurl += nurl
			g_nloss += nloss
			g_download_time += download_time
			partials.append([nurl,nloss,download_time])

			# LDA
			lda = thread['lda']
			if len(list(lda)) > 0:
				original_coherences.append(lda['original_coherence'])
				my_coherences.append(lda['my_coherence'])
			
				lda_time = lda['lda_time']
				nwords = 0#TODO REMOVE COMMENT lda['lda_nwords']
				npasses = lda['lda_npasses']
				lda_performance.append([lda_time, nwords, npasses])		

		makeM2stats(g_nurl,g_nloss,g_download_time, partials, original_coherences, my_coherences, lda_performance)

	if 'm3' in logs:
		logM3 = logs['m3']		
		print(logM3['time'])

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
