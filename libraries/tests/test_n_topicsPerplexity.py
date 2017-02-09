#!/usr/bin/env python3.5
import sys
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from itertools import chain
import gensim
from pymining import itemmining
from hurry.filesize import size
import collections
import random

def main(args):

	grid = {}

	# Choose a parameter you are wanting to search, for example num_topics or alpha / eta, make sure you substitute "parameter_value"
	# into the model below instead of a static value.
	#
	# num topics
	parameter_list=[10, 20, 30, 45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
	
	# alpha / eta
	# parameter_list=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 1.5]
	
	# we can sample if we like
	cp = random.sample(corpus,200000)

	# shuffle corpus
	# cp = list(corpus)
	# random.shuffle(cp)

	# split into 80% training and 20% test sets
	p = int(len(cp) * .5)
	cp_train = cp[0:p]
	cp_test = cp[p:]

	# for num_topics_value in num_topics_list:
	for parameter_value in parameter_list:

		# print "starting pass for num_topic = %d" % num_topics_value
		print("starting pass for parameter_value = %.3f" % parameter_value)
		start_time = time.time()

		# run model
		model = models.ldamodel.LdaModel(corpus=cp_train, id2word=dictionary, num_topics=parameter_value, chunksize=3125, 
										passes=25, update_every=0, alpha=None, eta=None, decay=0.5,
										distributed=True)
	
		# show elapsed time for model
		elapsed = time.time() - start_time
		print("Elapsed time: %s" % elapsed)
	
		perplex = model.bound(cp_test)
		print("Perplexity: %s" % perplex)
		grid[parameter_value].append(perplex)
	
		per_word_perplex = np.exp2(-perplex / sum(cnt for document in cp_test for _, cnt in document))
		print("Per-word Perplexity: %s" % per_word_perplex)
		grid[parameter_value].append(per_word_perplex)

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
