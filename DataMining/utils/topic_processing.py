from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
from itertools import chain
import gensim
from pymining import itemmining

########################################################################
##Global Variables
tokenizer = RegexpTokenizer(r'\w+')

# create English stop words list
en_stop = get_stop_words('en')

# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()
########################################################################

#remove all stop-words and punctuation from document
def textProcessing(document):
	# clean and tokenize document string
	print("____________________________________________________________")
	print("Tokenizing:")
	raw = document.lower()
	#print(raw)
	tokens = tokenizer.tokenize(raw)
	#print(tokens)
	
	# remove stop words from tokens
	stopped_tokens = [i for i in tokens if not i in en_stop]
	print(stopped_tokens)
	# stem tokens
	stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
	print(stemmed_tokens)
	print("____________________________________________________________")
	return stemmed_tokens

#get a number of topics (ratio) in percentual of the number of docs
#ratio = [0,1]
#return (n_docs,n_topics,topics)
def getTopicsFromDocs(texts,n_topics,n_passes):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=n_topics, id2word = dictionary, passes=n_passes)
	return corpus, ldamodel

# TODO doumentation
def getTopicsRanking(lda_model,corpus,number_topics=100,number_words=10):
	ranking = lda_model.top_topics(corpus,max(1,number_words))
	ranking.sort(key=lambda x: abs(x[1]))
	return ranking[0:min(len(ranking),max(number_topics,0))]

# TODO finish, change name and documenting
def testJoinTopicsSets(topics_sets):
	relim_input = itemmining.get_relim_input(topics_sets)
	itemsets = itemmining.relim(relim_input, min_support=2)
	return itemsets
