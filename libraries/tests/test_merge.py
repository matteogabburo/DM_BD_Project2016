#!/usr/bin/env python3.5
import sys
from random import shuffle
import math

import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim import corpora, models

# My imports
sys.path.append('..')
import utils.http_requests as http
import utils.topic_processing as tp_lda
import models.topics_tree as t
sys.path.remove('..')


def setCoherences(corpuses, l_topics):
	# modify the coherence of each topic
	d_corpuses_words = {}
	len_d_corpuses = 0
	for corpus in corpuses:
		for word in corpus:
			len_d_corpuses += 1
			if word in d_corpuses_words:
				d_corpuses_words[word] += 1
			else:
				d_corpuses_words[word] = 1
	new_topics_list = []	
	original_coherences = []
	my_coherences = []
	for topic in l_topics:
		coherence = 0
		original_coherences.append(topic[1]) # for logs
		for word in topic[0]:
			coherence += d_corpuses_words[word[1]]
		new_topic_list = []
		new_topic_list.append(topic[0])
		new_topic_list.append(coherence)# / len_d_corpuses)
		my_coherences.append(coherence)# / len_d_corpuses) # for logs
		new_topics_list.append(new_topic_list)

	return new_topics_list



def gensim_perplexity(cp,ntopics,npasses):


	model, parsed_cp = lda(cp,ntopics, npasses)
	
        # show elapsed time for model
	#perplex = model.bound(parsed_cp)
	perplex = model.log_perplexity(parsed_cp)

	return perplex


def lda(cp, ntopics, npasses):

	cp = [x for x in cp if x != []]
	
	dictionary = corpora.Dictionary(cp)
  	# run model
	parsed_cp = [dictionary.doc2bow(text) for text in cp]
	model = gensim.models.ldamodel.LdaModel(corpus=parsed_cp, id2word=dictionary, num_topics=ntopics, passes=npasses)
    
	return model, parsed_cp

'''
	definition : perplexity(D) = exp(-(sum(log(p(words))) / sum(number of words of each docs) ))

'''
def perplexity_topic(topic, n, d_f):
	
	nominator = 0.0

	words = topic[0]
	for word in words:
		if word[1] in d_f:
			nominator += float(d_f[word[1]]) / n

	if nominator > 0.0:
		nominator = math.log(nominator, 2)

	return nominator
			
	

def perplexity_topics(topics, corpuses):

	# count words
	nwords = 0
	for corpus in corpuses:
		nwords += len(corpus)
	
	#l_dict = []
	perplexity = 0.0
	for corpus in corpuses:
		d_f = {}
		n = len(corpus)
		for word in corpus:
			if word in d_f:
				d_f[word] += 1
			else:
				d_f[word] = 1
		#l_dict.append(d_f)
		for topic in topics:
			perplexity += perplexity_topic(topic, n, d_f)

	perplexity = -(perplexity / nwords)

	print(perplexity)

	perplexity = math.pow(math.e, perplexity)
	#perplexity = math.sqrt(perplexity)

	return perplexity


def f_approximation(number):
	i_number = int(number)
	if (number - i_number) > 0.5:
		return i_number + 1
	else:
		return i_number


def l_sumOfStrings(lists):
	res = []
	for l in lists:	
		for e in l:
			res.append(e)
	return res


def s_sumOfStrings(lists):
	res = []
	for l in lists:	
		s = ''
		for e in l:
			if s == '':
				s+=e
			else:
				s+=' '+e
		res.append(s)
	return res


def getDict(string):
	
	d = {}
	for s in string:
		if s in d:
			d[s]+=1
		else:
			d[s]=1
	return d



def main(args):
	
	urls = ['https://www.karamasoft.com/UltimateSpell/Samples/LongText/LongText.aspx',
	'http://catdir.loc.gov/catdir/enhancements/fy0711/2006051179-s.html',	
	'http://www.w3schools.com/html/html_examples.asp',
	'http://www.suzukicycles.com/',
	'https://github.com/att',
	'http://dev.mysql.com/downloads/workbench/',
	'http://lynx.isc.org/',
	'http://www.khilafah.com/',
	'http://www.carleton.edu/',
	'http://www.sankeyrodeo.com/',
	'http://www.ponyclubvic.org/',
	'http://www.kompaktkiste.de/',
	'http://www.tirumala.org/',
	'http://www.irvinechamber.com/',
	'http://www.bobbysherman.com/',
	'http://www.nrcan-rncan.gc.ca/',
	'http://www.law.cornell.edu/',
	'http://www.epa.gov/oppts/',
	'http://library.dartmouth.edu/',
	'http://www.fas.org/man/dod-101/sys/ac/p-3.htm',
	'http://www.wslc.org/',
	'http://tpwd.texas.gov/fishboat/fish/',
	'http://hitman-reborn.livejournal.com/',
	'http://tfl.gov.uk/',
	'http://www.pagop.org/',
	'http://www.praguechamber.org/',
	'http://en.wikipedia.org/wiki/Firearm_case_law_in_the_United_States',
	'http://www.stopnato.org.uk/du-watch/',
	'http://www.realtokyo.co.jp/',
	'http://cool.cc/index/Top/Regional/Asia/Japan/Prefectures/Tokyo',
	'http://www.filmsite.org/',
	'http://cool.cc/index/Top/Arts/Movies',
	'http://www.ctan.org/tex-archive/biblio/bibtex/',
	'http://cool.cc/index/Top/Computers/Software/Typesetting/TeX',
	'http://www.dmoz.org/',
	'http://cool.cc/index/Top/Computers/Internet/Searching',
	'http://www.woodcraft.org.uk/',
	'http://cool.cc/index/Top/Regional/Europe/United_Kingdom/',
	'http://www.coventry.ac.uk/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/',
	'http://www.nalc.org/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Society_and_Culture/Labor',
	'http://www.musicweb-international.com/lutyens/',
	'http://cool.cc/index/Top/Arts/Music/Composition/Composers/L',
	'http://www.owlsports.com/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Pennsylvania',
	'http://desantis.house.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Florida/Government/Federal/US_House',
	'http://www.sikhnet.com/',
	'http://cool.cc/index/Top/Society/Religion_and_Spirituality',
	'http://uo.stratics.com/',
	'http://cool.cc/index/Top/Games/Video_Games/Roleplaying/Massive_Multiplayer_Online',
	'http://www.bnrmetal.com/',
	'http://cool.cc/index/Top/Arts/Music/Styles/R/Rock',
	'http://www.tourism.gov.my/',
	'http://cool.cc/index/Top/Regional/Asia/Malaysia',
	'http://www.cnrs.fr/',
	'http://cool.cc/index/Top/Regional/Europe',
	'http://www.bseindia.com/',
	'http://cool.cc/index/Top/Regional/Asia/India/Business_and_Economy',
	'http://www.artsci.ccsu.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Connecticut/',
	'http://www.kent.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Ohio',
	'http://www.specialolympics.org/',
	'http://cool.cc/index/Top/Sports/Disabled',
	'http://www.oprah.com/',
	'http://cool.cc/index/Top/Arts/Television/Programs/Talk_Shows',
	'http://judiciary.senate.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Government/Legislative_Branch/Senate/Committees',
	'http://www.harewood.org/',
	'http://cool.cc/index/Top/Regional/Europe/United_Kingdom/England/West_Yorkshire',
	'http://tours.tsom.org/',
	'http://cool.cc/index/Top/Arts/Music/Bands_and_Artists/S/Si',
	'http://www.kjcgames.com/quest.htm',
	'http://cool.cc/index/Top/Games/Play-By-Mail/Companies/KJC_Games',
	'http://www.thesunconference.com/index.aspx?tab=womenstennis&amp;path=wten',
	'http://cool.cc/index/Top/Sports/Tennis/College_and_University',
	'http://www.disabilities-r-us.com/',
	'http://cool.cc/index/Top/Society',
	'http://www.nvg.ntnu.no/sinclair',
	'http://cool.cc/index/Top/Computers/Systems',
	'http://inouye.senate.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Government/Legislative_Branch/Senate/Ex-Senators',
	'http://www.uwgsports.com/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Georgia',
	'http://pelosi.house.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/California/Government/Federal/US_House_of_Representatives',
	'http://www.halton.ca/',
	'http://cool.cc/index/Top/Regional/North_America/Canada/Ontario/Localities',
	'http://africa.uima.uiowa.edu/',
	'http://cool.cc/index/Top/Arts/Visual_Arts',
	'http://www.wilmccarthy.com/',
	'http://cool.cc/index/Top/Arts/Literature/Genres/Science_Fiction/Authors',
	'http://www.girlguides.org.za/',
	'http://cool.cc/index/Top/Recreation/Scouting/Organizations',
	'http://www.daytonabeach.com/biketoberfest/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Florida/Localities/D/Daytona_Beach',
	'http://www.robins.af.mil/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Government/Military/Air_Force/Installations',
	'http://www.wienerart.net/',
	'http://cool.cc/index/Top/Arts/Music/Bands_and_Artists/D',
	'http://www.menwithouthats.com/',
	'http://cool.cc/index/Top/Arts/Music/Styles/By_Decade/1980s/Bands_and_Artists',
	'http://www.morningstarchapel.org/writings.html',
	'http://cool.cc/index/Top/Society/Religion_and_Spirituality/Christianity/Denominations',
	'http://www.roundhillva.org/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Virginia/Localities/R',
	'http://www.brown.edu/academics/gradschool/apply',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Rhode_Island',
	'http://www.w3.org/TR/xsl/',
	'http://cool.cc/index/Top/Computers/Data_Formats/Markup_Languages/XML',
	'http://www.thealamo.org/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Texas/Society_and_Culture',
	'http://www.modlang.ccsu.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Connecticut/',
	'http://www.dbu.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Texas',
	'http://www.computer.org/',
	'http://cool.cc/index/Top/Computers',
	'http://www.iatse-intl.org/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Society_and_Culture/Labor',
	'http://www.bizjournals.com/seattle/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Washington',
	'http://en.wikipedia.org/wiki/Category:United_States_presidential_elections_in_Oregon',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Oregon/Society_and_Culture/Politics/Candidates_and_Campaigns',
	'http://www.ajli.org/',
	'http://cool.cc/index/Top/Society/People/Women/Organizations',
	'http://www.tug.org/utilities/plain/cseq.html',
	'http://cool.cc/index/Top/Computers/Software/Typesetting/TeX',
	'http://www.usad.org/',
	'http://cool.cc/index/Top/Society/Organizations/Student/Academic',
	'http://www.turnermaine.com/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Maine/Localities',
	'http://arcanum.aodevs.com/',
	'http://cool.cc/index/Top/Games/Video_Games/Roleplaying/Massive_Multiplayer_Online',
	'http://www.russojapanesewar.com/',
	'http://cool.cc/index/Top/Society/History/By_Time_Period/Twentieth_Century/Wars_and_Conflicts',
	'http://www.bcbs.com/',
	'http://cool.cc/index/Top/Business/Financial_Services/Insurance',
	'http://www.nps.gov/nr/',
	'http://cool.cc/index/Top/Regional/North_America/United_States',
	'http://luetkemeyer.house.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Missouri/Government/Federal/US_House_of_Representatives',
	'http://www.themushroomkingdom.net/',
	'http://cool.cc/index/Top/Games/Video_Games/Platform',
	'http://www.brunswickmd.gov/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Maryland/Localities/B',
	'https://armycadets.com/',
	'http://cool.cc/index/Top/Regional/Europe/United_Kingdom/Government/Defence/Cadets',
	'http://en.wikipedia.org/wiki/Category:Nevada_gubernatorial_elections',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Nevada/Society_and_Culture/Politics',
	'http://www.mystmasterpiece.com/',
	'http://cool.cc/index/Top/Games/Video_Games/Adventure/Graphical_Adventures/Myst_Series',
	'http://www.burnley.gov.uk/',
	'http://cool.cc/index/Top/Regional/Europe/United_Kingdom/England/Lancashire',
	'http://chicora.org/',
	'http://cool.cc/index/Top/Reference/Museums',
	'http://www.abacos.com/',
	'http://cool.cc/index/Top/Regional/Caribbean',
	'http://music.msn.com/artist/?artist=144277',
	'http://cool.cc/index/Top/Society/Religion_and_Spirituality/Christianity/Music/Styles',
	'http://www.lakenheath.af.mil/',
	'http://cool.cc/index/Top/Regional/North_America/United_States/Government/Military/Air_Force/Installations',
	'http://xroads.virginia.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Virginia/University_of_Virginia/',
	'http://www.wizards.com/Magic/',
	'http://cool.cc/index/Top/Games/Trading_Card_Games',
	'http://www.wvu.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States',
	'http://www.me.go.kr/',
	'http://cool.cc/index/Top/Regional/Asia/South_Korea/Government/Executive_Branch',
	'http://www.modarchive.org/',
	'http://cool.cc/index/Top/Arts/Music/Sound_Files',
	'http://www.nhc.noaa.gov/',
	'http://cool.cc/index/Top/Science/Earth_Sciences/Atmospheric_Sciences/Meteorology/Weather_Phenomena',
	'http://sourceforge.net/projects/lambdamoo/',
	'http://cool.cc/index/Top/Games/Online/MUDs/Development/Codebases',
	'http://www.tug.org/utilities/plain/cseq.html',
	'http://cool.cc/index/Top/Computers/Software/Typesetting/TeX'
	]

	'''
	
	
	'''

	coherences = []

	corpuses = []
	for url in urls:
		print(url)
		ret = http.get_url_text_corpus(url,10,False,[])[0]
		if ret != None:
			corpuses.append(http.get_url_text_corpus(url,10,False,[])[0])
	
	corpuses = [x for x in corpuses if x != []]

	#=================================================================================


	perplexities_s1 = []
	perplexities_s2 = []
	perplexities_s3 = []
	perplexities_s4 = []
	
	perplexities_s5 = []
	perplexities_s6 = []
	perplexities_s7 = []
	perplexities_s8 = []

	perplexities_s12 = []
	perplexities_s1234 = []
	perplexities_s12345678 = []

	perplexities_merge12 =[]
	perplexities_merge1234 =[]	
	perplexities_merge12345678 =[]

	perplexities_merge_cluster12 = []
	perplexities_merge_cluster1234 = []
	perplexities_merge_cluster12345678 = []


	for i in range(0,int(args[1])):

		shuffle(corpuses)

		k = int(len(corpuses) / 8)#int(args[1]))

		l_ksets = []
		i = 0
		tmp = []
		for corpus in corpuses:
			if i < k:
				tmp.append(corpus)
			else :
				i = 0
				l_ksets.append(tmp)
				tmp = []
			i += 1

		print(len(l_ksets))



		for c in l_ksets:		

			set1 = []
			set2 = []
			set3 = []
			set4 = []
			set5 = []
			set6 = []
			set7 = []
			set8 = []

			a = 0
			for i in range(int(len(c)/8)):
				set1.append(c[a])
				set2.append(c[a+1])
				set3.append(c[a+2])
				set4.append(c[a+3])
				set5.append(c[a+4])
				set6.append(c[a+5])
				set7.append(c[a+6])
				set8.append(c[a+7])
				a += 8

			'''print(len(set1))
			print(len(set2))
			print(len(set3))
			print(len(set4))
			print(len(set5))
			print(len(set6))
			print(len(set7))
			print(len(set8))'''

			lda_ntopics = 20
			lda_npasses = 20
			lda_nwords4topic = 20


			# PERPLEXITY

			# set 1
			d_set1, p_set1 = makeSet(set1,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 2
			d_set2, p_set2 = makeSet(set2,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 3
			d_set3, p_set3 = makeSet(set3,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 4
			d_set4, p_set4 = makeSet(set4,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 5
			d_set5, p_set5 = makeSet(set5,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 6
			d_set6, p_set6 = makeSet(set6,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 7
			d_set7, p_set7 = makeSet(set7,lda_ntopics,lda_npasses,lda_nwords4topic)
			# set 8
			d_set8, p_set8 = makeSet(set8,lda_ntopics,lda_npasses,lda_nwords4topic)


			# set 1 + 2
			set12 = set1+set2
			model,c = lda(set12,lda_ntopics,lda_npasses)
			topics_set12 = tp_lda.getTopicsRanking(model, c, lda_ntopics, lda_nwords4topic)
			p_set12 = perplexity_topics(topics_set12, set12)

			# set 1 + 2 + 3 + 4
			set1234 = set1+set2+set3+set4
			model,c = lda(set1234, lda_ntopics, lda_npasses)
			topics_set1234 = tp_lda.getTopicsRanking(model, c, lda_ntopics, lda_nwords4topic)
			p_set1234 = perplexity_topics(topics_set1234, set1234)

			# set 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8
			set12345678 = set1+set2+set3+set4+set5+set6+set7+set8
			model,c = lda(set12345678, lda_ntopics, lda_npasses)
			topics_set12345678 = tp_lda.getTopicsRanking(model, c, lda_ntopics, lda_nwords4topic)
			p_set12345678 = perplexity_topics(topics_set12345678, set12345678)


			# merge 12
			topics_merge12 = t.merge([dict(d_set1),dict(d_set2)],lda_ntopics,10)['topics']
			p_merge12 = perplexity_topics(topics_merge12, set12)

			# merge 1234
			topics_merge1234 = t.merge([dict(d_set1),dict(d_set2),dict(d_set3),dict(d_set4)],lda_ntopics,10)['topics']
			p_merge1234 = perplexity_topics(topics_merge1234, set1234)

			# merge 12345678
			topics_merge12345678 = t.merge([dict(d_set1),dict(d_set2),dict(d_set3),dict(d_set4),dict(d_set5),dict(d_set6),dict(d_set7),dict(d_set8)],lda_ntopics,10)['topics']
			p_merge12345678 = perplexity_topics(topics_merge12345678, set12345678)
		

			# merge cluster 12
			topics_merge_clusters12 = t.mergeClusters([dict(d_set1),dict(d_set2)], lda_ntopics, lda_nwords4topic, 10)['topics']
			p_merge_clusters12 = perplexity_topics(topics_merge_clusters12, set12)

			# merge cluster 1234
			topics_merge_clusters1234 = t.mergeClusters([dict(d_set1),dict(d_set2),dict(d_set3),dict(d_set4)], lda_ntopics, lda_nwords4topic, 10)['topics']
			p_merge_clusters1234 = perplexity_topics(topics_merge_clusters1234, set1234)

			# merge cluster 12345678
			topics_merge_clusters12345678 = t.mergeClusters([dict(d_set1),dict(d_set2),dict(d_set3),dict(d_set4),dict(d_set5),dict(d_set6),dict(d_set7),dict(d_set8)], lda_ntopics, lda_nwords4topic, 10)['topics']
			p_merge_clusters12345678 = perplexity_topics(topics_merge_clusters12345678, set12345678)


			print('')
			print(p_set1)
			print(p_set2)
			print(p_set12)
			print(p_set1234)
			print(p_set12345678)
			print(p_merge12)		
			print(p_merge1234)		
			print(p_merge12345678)
			print(p_merge_clusters12)
			print(p_merge_clusters1234)
			print(p_merge_clusters12345678)		
			print('')

			#perplexities_s1.append(p_set1)
			#perplexities_s2.append(p_set2)
			perplexities_s12.append(p_set12)
			perplexities_s1234.append(p_set1234)
			perplexities_s12345678.append(p_set12345678)
				
			perplexities_merge12.append(p_merge12)
			perplexities_merge1234.append(p_merge1234)
			perplexities_merge12345678.append(p_merge12345678)

			perplexities_merge_cluster12.append(p_merge_clusters12)
			perplexities_merge_cluster1234.append(p_merge_clusters1234)
			perplexities_merge_cluster12345678.append(p_merge_clusters12345678)


	l_x = [i for i in range(0,len(perplexities_s12))]	
	
	fig1 = plt.figure(figsize = (8,8))
	plt.subplots_adjust(hspace=0.4)

	#plt.plot(l_x, perplexities_s1,'r--')
	#plt.plot(l_x, perplexities_s2,'b--')

	p1 = plt.subplot(3,1,1)
	plt.plot(l_x, perplexities_s12,'m--') 
	plt.plot(l_x, perplexities_merge12,'k')
	plt.plot(l_x, perplexities_merge_cluster12,'g')
	
	p1 = plt.subplot(3,1,2)
	plt.plot(l_x, perplexities_s1234,'m--') 
	plt.plot(l_x, perplexities_merge1234,'k')
	plt.plot(l_x, perplexities_merge_cluster1234,'g')	

	p1 = plt.subplot(3,1,3)
	plt.plot(l_x, perplexities_s12345678,'m--') 
	plt.plot(l_x, perplexities_merge12345678,'k')	
	plt.plot(l_x, perplexities_merge_cluster12345678,'g')


	#plt.plot(my_avg_coherence_x, res,'g')
	
	plt.show()

	return 0


def makeSet(s,lda_ntopics,lda_npasses,lda_nwords4topic):
	
	model,c = lda(s,lda_ntopics,lda_npasses)
	topics_s = tp_lda.getTopicsRanking(model, c, lda_ntopics, lda_nwords4topic)
	p_s = perplexity_topics(topics_s, s)
	d_s = {}
	d_s['loc'] = [0,0]
	d_s['topics'] = topics_s
	d_s['s'] = 10
	d_s['ncorpuses'] = len(s)
	
	return d_s, p_s

if __name__ == '__main__':
	sys.exit(main(sys.argv))
