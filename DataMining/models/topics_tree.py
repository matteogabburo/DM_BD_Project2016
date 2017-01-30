#!/usr/bin/env python3.5
import sys
from operator import itemgetter
from math import sqrt

sys.path.append('..')
from models.topic_clustering_matrix import Matrix
from db_utils.dao import GeoDao
sys.path.remove('..')

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

	# tmp merging function

	'''
		{ "_id" : ObjectId("588878d99c99ea7b58176e2b"), 
		"s" : 5,
		"topics" : [ 
						[
							 [
								[ 0.01055389360811648, "tim" ],
								[ 0.010543791734159697, "giorno" ], 
								[ 0.010543788901076859, "mb" ], 
								[ 0.010543311900654046, "gb" ], 
								[ 0.010541878577036446, "iva" ], 
								[ 0.010539792094810364, "lofferta" ], 
								[ 0.010537464305717533, "giorni" ], 
								[ 0.010536935142465667, "usufruir" ], 		
								[ 0.010535999214882802, "deve" ], 
								[ 0.01053593645388195, "rinnovo" ], 
								[ 0.01053549291489606, "vengono" ], 
								[ 0.010535432359617188, "dellopzion" ], 
								[ 0.010534929172343825, "persi" ], 
								[ 0.010534200156986072, "pc" ], 
								[ 0.010534103655269795, "poter" ], 
								[ 0.010533290853250048, "traffico" ], 
								[ 0.010532901438550136, "internet" ], 
								[ 0.010532692984097002, "tablet" ], 
								[ 0.010532686805938997, "navigando" ], 
								[ 0.01053228941001652, "automatico" ] 
							], 118.52816787575084 
						],
						[
				 			[
								[ 0.02895684210150628, "tim" ], 
								[ 0.02450245666111411, "gb" ], 
								[ 0.024502355439902708, "mb" ], 
								[ 0.024502354838712305, "giorno" ], 
								[ 0.020047066624956648, "giorni" ], 
								[ 0.020046572659709227, "lofferta" ], 
								[ 0.020046129900649905, "iva" ], 
								[ 0.015592078435817313, "smartphon" ], 
								[ 0.015592022051271954, "maggior" ], 
								[ 0.015591958025325621, "costo" ], 
								[ 0.015591866943976523, "inclusa" ], 
								[ 0.015591854101156395, "preved" ], 
								[ 0.015591736876884416, "card" ], 
								[ 0.015591652246337797, "ã" ], 
								[ 0.015591592215290866, "nazional" ], 
								[ 0.0155915728934583, "credito" ], 
								[ 0.015591533839593363, "automatico" ], 
								[ 0.015591449510744254, "navigando" ], 
								[ 0.015591448199716824, "tablet" ], 
								[ 0.015591403964929472, "internet" ] 
							], 118.52816787575084 ]
			 ], 
		"loc" : [ 46.072639544097356, 10.945089662773075 ] }

	'''

	def merge(self, l_topics, s):

		# define the number of topic that any cell has after the merge
		topicForCell = 20

		mergedTopic = {}
		locs = []	
		coerences = []	

		# for having the weight of each word
		d_wordsweight = {}
		
		for current_topic in l_topics:
			
			d_topic = dict(current_topic)	
		
			locs.append(d_topic['loc'])
			l_topic = d_topic['topics']
			n_urls = int(d_topic['ncorpuses'])

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

				l_merged = [topic[0] for topic in merged_topic]
				l_merged_coerences = [topic[1] for topic in merged_topic]
				l_current = [topic[0] for topic in l_topic]
				l_current_coerences = [topic[1] for topic in l_topic]

				# similiarity
				couples = self.similiarity(l_merged, l_current)
		
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
						l_topicupdated.append([self.mergeavg(d_wordsweight[word]),word])

					# add the different words with the probability multiplied for the number of urls
					tmp_words = [[self.mergeavg(d_wordsweight[word]),word] 
							for word in l_differentwords]				
					tmp_words = sorted(tmp_words, key=itemgetter(1))				

					# restore the probabilities
					tmp_words = [[self.mergeavg(d_wordsweight[word]),word] 
							for word in l_differentwords]				

					l_topicupdated_container = []
					l_topicupdated += tmp_words[:(topicForCell*2 - len(l_equalwords))]

					l_topicupdated_container.append(l_topicupdated)
					
					# insert the avg coerence between the two topics
					l_topicupdated_container.append(self.mergeavg([abs(l_merged_coerences[couple[0]]),
									abs(l_current_coerences[couple[1]])]))				
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
		mergedTopic['loc'] = [self.mergeavg([row[0] for row in locs]),self.mergeavg([row[1] for row in locs])]
		mergedTopic['s'] = s
		mergedTopic['topics'] = tmptopics

		return mergedTopic
	
	# give a list of list and return a list of index containing the most similar sub element 2 by 2 
	def similiarity(self, l1, l2):
		
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
	def mergeavg(self, l):
		res = 0
		for e in l:
			res += e

		return res / len(l)


	# it generate the tree merging the element for each level
	def generate(self, host, port, db_name, collection_in, collection_out):

		dao = GeoDao(host, port)

		firstIteration = True
		for m in self.l_matrixes:

			print(m.s)
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
					l_d_topics.append(self.merge(l_topics, m.s))	
		
			if len(l_d_topics) > 0:
				print(' -> 'len(l_d_topics))
				dao.connect(db_name, collection_out)
				dao.addMany(collection_out, l_d_topics)
		
		dao.close()


	def toString(self):
		print('TODO')		

