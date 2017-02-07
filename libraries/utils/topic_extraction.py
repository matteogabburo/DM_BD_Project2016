#!/usr/bin/env python3.5
import sys
import topic_processing

def main(args):

	file_name = args[1]


	f = open(file_name, 'r')
	text = f.read()

	#print(text)

	text = text.replace('[', '').replace(' ', '').replace('\'', '')

	t1 = text.split('],')

	
	#print(t1)	
	
	max_n = 100
	counter = 0
	texts = []

	ntimes = int(len(t1) / max_n)
	
	for i in range(0,ntimes):		
		for counter in range(0,max_n):
			#print(counter)
			texts.append(t1[counter].split(','))

	print('computing...')

	#topic_processing.test(texts)

	corpus,document_lda = topic_processing.getTopicsFromDocs(texts,30,5)
	ranking = topic_processing.getTopicsRanking(document_lda,corpus,30,10)


	print(document_lda)
	print('')
	print(ranking)



	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))

