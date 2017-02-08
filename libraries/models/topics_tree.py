#!/usr/bin/env python3.5
import sys
from operator import itemgetter
from math import sqrt


from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models.coherencemodel import CoherenceModel
from sklearn.cluster import KMeans
import operator


sys.path.append('..')
from models.topic_clustering_matrix import Matrix
from db_utils.dao import GeoDao
sys.path.remove('..')

# ======================================================================
def preprocessingTopicsClusters(clusters):
	clusters.sort(key=lambda x: x[0])
	last = clusters[0][0]
	j = 0
	new_clusters = []
	for i in range(0,len(clusters),1):
		if clusters[i][0] != last:
			array = []
			for clustroid_id, num_docs, topic_id, topic in clusters[j:i]:
				array.append((num_docs,topic))
			array = mergeTopicsSameClusters(array)
			new_clusters.append(array)
			j = i
			last = clusters[i][0]
	
	array=[]
	for clustroid_id, num_docs, topic_id, topic in clusters[j:len(clusters)]:
		array.append((num_docs,topic))
	array = mergeTopicsSameClusters(array)
	new_clusters.append(array)
	
	return new_clusters

def mergeTopicsSameClusters(topics):
	new_coherence = .0
	words = {}
	tot_num_instances = 0
	
	for num_docs, topic in topics:
		tot_num_instances = tot_num_instances + 1
		#print("**")
		#print(topic)
		word_set = topic[0] 
		coherence = topic[1]
		new_coherence = float(new_coherence) + coherence
		for weight, word in word_set:
			if word not in words:
				words[word] = .0
			words[word] = float(words[word]) + float(weight)
		
	words = [(weight/float(tot_num_instances), str(word)) for (word, weight) in sorted(words.items(), key=operator.itemgetter(1), reverse=True)]#sorted(words.items(), reverse=True)]
	
	topic = (words,new_coherence/float(tot_num_instances))
	
	return (num_docs,topic)

def mergeTopicsClusters(topics_list, number_of_words=10, number_of_documents=None):
	#topics_list[x] = (number_of_documents, topic)
	tot_num_docs = 0
	new_coherence = .0
	words = {}
	
	topics_list = preprocessingTopicsClusters(topics_list)
	
	for num_docs, topic in topics_list:
		if len(topics_list) > 1:
			tot_num_docs = tot_num_docs + num_docs
		else:
			tot_num_docs = 1
			num_docs = 1
		coherence = topic[1] 
		word_set = topic[0]
		#print(coherence)
		new_coherence = float(new_coherence) + coherence #* float(num_docs)
		for weight, word in word_set:
			if word not in words:
				words[word] = .0
			words[word] = float(words[word]) + float(weight) * float(num_docs)
	
	#if we have to consider the whole number of documents, but this clustering don't has clusters of other documents
	if number_of_documents != None:
		tot_num_docs = number_of_documents
	
	words = [(weight/float(tot_num_docs), str(word)) for (word, weight) in sorted(words.items(), key=operator.itemgetter(1), reverse=True)[0:number_of_words]]
	'''
	sum_weight = 0.
	for (weight,_) in words:
		sum_weight = sum_weight + weight
	
	words = [(weight/sum_weight, str(word)) for (weight,word) in words]
	'''
	topic = (words,new_coherence)#/float(tot_num_docs))
	
	return (tot_num_docs, topic)

#get a cluster of the topics getted from the docs clustering
#clustroids[index] = (n_docs, n_topics, clustroid_topic0, clustroid_topic1, ...) or (n_docs,n_topics,topics)
def mergeClusters(clustroids, max_topics, words_per_topic, s):
	#data description
	"""
	clustroids[x] = (number_of_documents, topics)
	topics[x] = (coherence_coefficient, topic)
	topic[x] = ((coefficient, word), ...)
	"""
	
	tmp = []
	locs = []
	for clustroid in clustroids:
		tmp.append((clustroid['ncorpuses'],clustroid['topics']))
		locs.append(clustroid['loc'])

	clustroids = tmp
	
	dictionary = {}
	topics_only = []
	topics_list = []
	clustroid_id = 0
	total_documents = 0
	
	for (number_of_documents, topics) in clustroids:
		total_documents = total_documents + number_of_documents
		topic_id = 0
		#print("LUNGO?")
		#print(len(topics))
		for topic in topics:
			topics_list.append((clustroid_id,number_of_documents,topic_id,topic))
			#print(topic)
			topic_id = topic_id + 1
			words = []
			#print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
			#print(topic)
			for (coefficient, word) in topic[0]:
				dictionary[word] = 1
				words.append(word)
			topics_only.append(" ".join(words))
		clustroid_id = clustroid_id + 1
	max_topics = min(max_topics,len(topics_only))
	"""
	topics_list = (clustroid_id, topic_id, topic)
	"""
	
	"""
	#preprocessing data:
	*dictionary extraction
	*topics convertion
	"""
	cv = CountVectorizer()#(vocabulary=dictionary)
	X = cv.fit_transform(topics_only)
	dictionary = cv.get_feature_names()
	
	#print(dictionary)
	
	X = X.toarray()
	dictionary = np.array(dictionary)
	
	n, _ = X.shape
	dist = np.zeros((n,n))
	for i in range(n):
		for j in range(n):
			x,y = X[i,:], X[j,:]
			dist[i,j] = np.sqrt(np.sum((x-y)**2))
	dist = 1 - cosine_similarity(X)
	
	#clustering process
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#K-MEANS
	km = KMeans(n_clusters=max_topics)
	km.fit(dist)
	clusters = km.labels_.tolist()
	#print(clusters)
	#print(km)
	
	cluster_map = {}
	for i in range(len(clusters)):
		key = int(clusters[i]) + 1
		if key not in cluster_map:
			cluster_map[key] = []
		cluster_map[key].append(topics_list[i])
	
	result = []
	for label, topics in cluster_map.items():
		res = mergeTopicsClusters(topics,words_per_topic,total_documents)
		result.append(res[1])
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
	#formatting result
	"""
	create a list "result" composed by:
	result = (number_of_documents, topics)
	topics[x] = (coherence_coefficient, topic)
	"""

	d_mergedTopic = {}
	d_mergedTopic['s'] = s
	d_mergedTopic['topics'] = result
	d_mergedTopic['ncorpuses'] = total_documents
	d_mergedTopic['loc'] = [mergeavg([row[0] for row in locs]), mergeavg([row[1] for row in locs])]	

	return (d_mergedTopic)

# ======================================================================


# TODO documentation
def merge(l_topics, topicForCell, s):

	# define the number of topic that any cell has after the merge
	#topicForCell = 20

	mergedTopic = {}
	locs = []	

	# for having the weight of each word
	d_wordsweight = {}
	
	for current_topic in l_topics:
	
		d_topic = dict(current_topic)	

		locs.append(d_topic['loc'])
		l_topic = d_topic['topics']
		n_urls = int(d_topic['ncorpuses'])

		# turn to positive all the coherences
		#l_topic = [[w[0],abs(w[1])] for w in l_topic]

		if not mergedTopic:
			mergedTopic['topics'] = l_topic
			mergedTopic['ncorpuses'] = n_urls
			# add the weight of the word to the dictionary
			for t in l_topic:
				for row in t[0]:
					if row[1] in d_wordsweight :
						d_wordsweight[row[1]].append(row[0] * n_urls)
					else:
						d_wordsweight[row[1]] = [row[0] * n_urls]						
		else:
			# found the most similiar topics between the two topics list
			merged_topic = mergedTopic['topics']				

			# order l1 and l2 for maximize the coerence during the similiarity calculus
			merged_topic = sorted(merged_topic, key=itemgetter(1), reverse = True)
			l_topic = sorted(l_topic, key=itemgetter(1), reverse = True)

			l_merged = [topic[0] for topic in merged_topic]
			l_merged_coerences = [topic[1] for topic in merged_topic]
			l_current = [topic[0] for topic in l_topic]
			l_current_coerences = [topic[1] for topic in l_topic]

			# similiarity
			couples = similiarity(l_merged, l_current)
	
			finaltopics = []
			for couple in couples:

				#add words to de dictionary
				for word in l_merged[couple[0]]:
					if word[1] not in d_wordsweight:
						d_wordsweight[word[1]] = [word[0]]
					else:
						d_wordsweight[word[1]].append(word[0])
				for word in l_current[couple[1]]:
					if word[1] not in d_wordsweight:
						d_wordsweight[word[1]] = [word[0] * n_urls]
					else:
						d_wordsweight[word[1]].append(word[0] * n_urls)

				l_mt = [w[1] for w in l_merged[couple[0]]]
				l_ct = [w[1] for w in l_current[couple[1]]]

				#take the equal word into the two list
				l_equalwords = []
				l_equalwords = set(l_mt) & set(l_ct)
			
				# take the not equals word
				l_allwords = set(l_mt+l_ct)
				l_differentwords = [w for w in l_allwords if w not in l_equalwords]

				# make the new topic list
				l_topicupdated = []
			
				# add equals word
				for word in l_equalwords:
					l_topicupdated.append([mergeavg(d_wordsweight[word]),word])

				# add the different words with the probability multiplied for the number of urls
				tmp_words = [[mergeavg(d_wordsweight[word]),word] 
						for word in l_differentwords]				
				tmp_words = sorted(tmp_words, key=itemgetter(1))				

				# restore the probabilities
				tmp_words = [[mergeavg(d_wordsweight[word]),word] 
						for word in l_differentwords]				

				l_topicupdated_container = []
				l_topicupdated += tmp_words[:(topicForCell*2 - len(l_equalwords))]


				# compute the weight of merge for the coerence, composing by the number of words that are 
				# inserted in the 'finaltopic', that comes from the two topics in percentual
				# ex final list is made using 12 words from the first topic and 8 from the 
				# second, the merge is weighted with these two weigth
				weight1 = 0
				weight2 = 0
				for element in l_topicupdated:
					if element[1] in l_mt:
						weight1 += 1
					if element[1] in l_ct:
						weight2 += 1

				if len(l_topicupdated) > len(l_equalwords):
					# 0.5 is adding for normalization during the average process
					weight1 = 0.5 + (weight1 - (len(l_equalwords))) / (len(l_topicupdated) - len(l_equalwords))	 
					weight2 = 0.5 + (weight2 - (len(l_equalwords))) / (len(l_topicupdated) - len(l_equalwords))		
				else:	
					weight1 = 1
					weight2 = 1	

				w1 = weight1 * abs(l_merged_coerences[couple[0]])
				w2 = weight2 * abs(l_current_coerences[couple[1]])

				l_topicupdated_container.append(l_topicupdated)	
			
				# insert the avg coerence between the two topics
				l_topicupdated_container.append(mergeavg([w1, w2]))	
				
				finaltopics.append(l_topicupdated_container)

			# SAVE THE PROGRESSES
			mergedTopic['topics'] = finaltopics

			#add the number of url
			mergedTopic['ncorpuses'] += n_urls

	
	# take only the first 'topicForCell' number of topics and normalize the weights
	tmptopics = mergedTopic['topics']

	finaltopics = []
	n_tot_urls = mergedTopic['ncorpuses']

	for t in tmptopics:
		t[0] = sorted(t[0], key=itemgetter(0), reverse = True)
		t[0] = [(w[0]/n_tot_urls,w[1]) for w in t[0]]
		t[0] = t[0][:(topicForCell)]

	# compute the centroid
	mergedTopic['loc'] = [mergeavg([row[0] for row in locs]),mergeavg([row[1] for row in locs])]
	mergedTopic['s'] = s
	mergedTopic['topics'] = tmptopics

	return mergedTopic

# give a list of list and return a list of index containing the most similar sub element 2 by 2 
def similiarity(l1, l2):
	
	# index 1, index 2, rank(n of equals word)
	ranks = []

	i1 = 0
	i2 = 0

	for sl1 in l1:
		swl1 = [w[1] for w in sl1]
		i2 = 0
		for sl2 in l2:
			swl2 = [w[1] for w in sl2]
			# take the minimum size of the list for make the score
			if len(swl1) < len(swl2):
				m = len(swl1)
			else:
				m = len(swl2)
			# rank is '# common word / size of the smallest list * 100
			ranks.append([i1,i2,(len(set(swl1) & set(swl2))/m)*100])

			i2 += 1
		i1 += 1

	ranks = sorted(ranks, key=itemgetter(2), reverse = True)	

	taken1 = []
	taken2 = []
	finalRanks = []
	# ordering the topics

	for rank in ranks:
		
		if rank[0] not in taken1 and rank[1] not in taken2 :
			finalRanks.append(rank)
		
			taken1.append(rank[0])
			taken2.append(rank[1])

	return finalRanks

#make an avg of a list of numbers
def mergeavg(l):
	res = 0
	for e in l:
		res += e

	return res / len(l)



class TopicsTree:
	# bottomLeftLoc is the coordinate (lat,lon) of the bottom
	# left margin of the map, topRightLoc is the coordinate 
	# (lat, lon) of the top right margin of the map, and s (km)
	# is the length of the x and y edge of each cell
	# numberOfLevels is the number of level that the generated
	# three has at the end of the computation
	# splitNumber is the number of how many we have to cluster 
	# for each level of the tree
	def __init__(self, bottomLeftLoc, topRightLoc, s, numberOfLevels, splitNumber = 4):

		# main bottom left and main top right		
		self.mbl = bottomLeftLoc
		self.mtr = topRightLoc
		self.s = s
		self.nl = numberOfLevels
		self.sn = sqrt(splitNumber)
						
		# every element of this list represent a level of the three
		self.l_matrixes = []
		dim = self.s
		for i in range(0, self.nl):
			dim = dim * self.sn
			self.l_matrixes.append(Matrix(self.mbl, self.mtr, dim))


	def generate_cluster(self,host, port, db_name, collection_in, collection_out, ntopics, nwords):
		dao = GeoDao(host, port)

		firstIteration = True
		for m in self.l_matrixes:

			if firstIteration == True:
				dao.connect(db_name, collection_in)
				firstIteration = False
			
	
			l_topics = []
			l_d_topics = []
			
			while m.hasNext():
				locs = m.next()

				bl = [locs[0],locs[1]]
				tr = [locs[2],locs[3]]
				
				# I expecting sn topics for each call			
				l_topics = list(dao.getUrlsByBox(bl,tr))

				l_topics = [w for w in l_topics if float(w['s']) == (m.s/self.sn)]

				if len(l_topics) > 0:
					l_d_topics.append(mergeClusters(l_topics, ntopics, nwords, m.s))
							
			if len(l_d_topics) > 0:
				dao.connect(db_name, collection_out)
				dao.addMany(collection_out, l_d_topics)
			
		dao.close()		

	# it generate the tree merging the element for each level
	def generate(self, host, port, db_name, collection_in, collection_out, ntopics):

		dao = GeoDao(host, port)

		firstIteration = True
		for m in self.l_matrixes:

			if firstIteration == True:
				dao.connect(db_name, collection_in)
				firstIteration = False
			
	
			l_topics = []
			l_d_topics = []
			while m.hasNext():
				locs = m.next()

				bl = [locs[0],locs[1]]
				tr = [locs[2],locs[3]]
				
				# I expecting sn topics for each call			
				l_topics = list(dao.getUrlsByBox(bl,tr))

				l_topics = [w for w in l_topics if float(w['s']) == (m.s/self.sn)]

				if len(l_topics) > 0:
					l_d_topics.append(merge(l_topics,ntopics, m.s))	
			
			if len(l_d_topics) > 0:
				dao.connect(db_name, collection_out)
				dao.addMany(collection_out, l_d_topics)
		dao.close()


	def toString(self):
		print('TODO')		

