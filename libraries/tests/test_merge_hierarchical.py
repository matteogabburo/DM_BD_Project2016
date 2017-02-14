#!/usr/bin/env python3.5
import sys
from random import shuffle
import random
import math

import numpy as np
import matplotlib.pyplot as plt
import pylab as P

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

	if len(cp) > 0:

		cp = [x for x in cp if x != []]
	
		dictionary = corpora.Dictionary(cp)
	  	# run model
		parsed_cp = [dictionary.doc2bow(text) for text in cp]
		model = gensim.models.ldamodel.LdaModel(corpus=parsed_cp, id2word=dictionary, num_topics=ntopics, passes=npasses)
	    
		return model, parsed_cp
	return None, None

'''
	definition : perplexity(D) = exp(-(sum(log(p(words))) / sum(number of words of each docs) ))

'''
def perplexity_topic(topic, n, d_f):

	nominator = 0.0
	words = topic[0]
	for word in words:
		if word[1] in d_f:
			if nominator == 0.0:
				nominator = float(d_f[word[1]]) / n
			else:
				nominator *= float(d_f[word[1]]) / n

	if nominator > 0.0:
		nominator = math.log(nominator, 2)

	return nominator
			
	

def perplexity_topics(topics, corpuses):
	perplexity = 0.0
	
	if len(topics) > 0 and len(corpuses) > 0:
		# count words
		nwords = 0
		for corpus in corpuses:
			nwords += len(corpus)
	
		#l_dict = []
		for corpus in corpuses:
			d_f = {}
			n = len(corpus)
			for word in corpus:
				if word in d_f:
					d_f[word] += 1
				else:
					d_f[word] = 1
			#l_dict.append(d_f)
			if n > 0:
				for topic in topics:
					perplexity += perplexity_topic(topic, n, d_f)

		perplexity = -(perplexity / nwords)

		#perplexity = math.pow(2, perplexity)
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
	'http://www.kent.edu/'
	]

	'''
	
	
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

	lda_ntopics = 20
	lda_npasses = 20
	lda_nwords4topic = 20


	# GRID
	'''
		1  2  3  4  5  6  7  8
		9  10 11 12 13 14 15 16
		17 18 19 20 21 22 23 24
		......................
		......................		
		.................... 64


		l1 : 1-2-3-4|5-6-7-8|9-10-11-12|13-14-15-16
		l2 : 1-2-3-4-5-6-7-8-9-10-11-12-13-14-15-16
		l3 : ....
	'''
	perplexities_simpleLda_1 = []
	perplexities_simpleLda_2 = []
	perplexities_simpleLda_3 = []
	perplexities_merge_1 = []
	perplexities_merge_2 = []
	perplexities_merge_3 = []
	perplexities_mergeCluster_1 = []
	perplexities_mergeCluster_2 = []
	perplexities_mergeCluster_3 = []

	for i in range(0,int(args[1])):

		cells = [] # 64
	
		cells0_level = [] # 64
		cells1_level = [] # 16
		cells2_level = [] # 4
		cells3_level = [] # 1

		cells1_level_merge = [] # 16
		cells2_level_merge = [] # 4
		cells3_level_merge = [] # 1
	
		cells1_level_mergeCluster = [] # 16
		cells2_level_mergeCluster = [] # 4
		cells3_level_mergeCluster = [] # 1


		cells0_lda_perplexity = []
		cells1_level_lda_perplexity = []
		cells2_level_lda_perplexity = []
		cells3_level_lda_perplexity = []

		#cells0_merge_perplexity = []
		cells1_level_merge_perplexity = []
		cells2_level_merge_perplexity = []
		cells3_level_merge_perplexity = []

		#cells0_mergeCluster_perplexity = []
		cells1_level_mergeCluster_perplexity = []
		cells2_level_mergeCluster_perplexity = []
		cells3_level_mergeCluster_perplexity = []


		# populate cells
		shuffle(corpuses)	
		cells = [[] for c in range(0,64)]
		for c in corpuses:
			where = random.randint(0,63)
			cells[where].append(c)


		# lda of each cell
		for c in cells:
			d_s, p_s = makeSet(c,lda_ntopics,lda_npasses,lda_nwords4topic)
			cells0_level.append(d_s)
			cells0_lda_perplexity.append(p_s)

		# SIMPLE LDA ==============================================================================================================

		# lda of the first merge
		k = 0
		m = 0	
		for i in range(0,16):
			four = cells[k]+cells[k+1]+cells[k+8]+cells[k+9]
			d_s, p_s = makeSet(four, lda_ntopics, lda_npasses, lda_nwords4topic)
			cells1_level.append(d_s)
			cells1_level_lda_perplexity.append(p_s)
			if m < 4:
				k += 2
				m += 1		
			else:
				k += 8 + 2
				m = 0

		# lda of the second merge
		k = 0
		m = 0	
		for i in range(0,4):
		
			sixteen = cells[k]+cells[k+1]+cells[k+2]+cells[k+3]+\
				cells[k+8]+cells[k+8+1]+cells[k+8+2]+cells[k+8+3]+\
				cells[k+8*2]+cells[k+8*2+1]+cells[k+8*2+2]+cells[k+8*2+3]+\
				cells[k+8*3]+cells[k+8*3+1]+cells[k+8*3+2]+cells[k+8*3+3]#+\
				#cells[k+8*4]+cells[k+8*4+1]+cells[k+8*4+2]+cells[k+8*4+3]
			d_s, p_s = makeSet(sixteen, lda_ntopics, lda_npasses, lda_nwords4topic)
			cells2_level.append(d_s)
			cells2_level_lda_perplexity.append(p_s)
			if m < 2:
				k += 4
				m += 1		
			else:
				k += 24 + 4
				m = 0

		# lda of the third merge
		a = []
		for c in cells:
			a+=c	

		d_s, p_s = makeSet(a, lda_ntopics, lda_npasses, lda_nwords4topic)
		cells3_level.append(d_s)
		cells3_level_lda_perplexity.append(p_s)

		# MERGE ====================================================================================================================

		# merge	first level
		k = 0
		m = 0
		cells_group = []
		for i in range(0,16):
			'''
			print(cells0_level[k])	
			print(cells0_level[k+1])
			print(cells0_level[k+8])			
			print(cells0_level[k+9])
			'''
			descriptor = t.merge([cells0_level[k], cells0_level[k+1], cells0_level[k+8], cells0_level[k+9]],lda_ntopics,10)
			cells_group.append(cells[k]+cells[k+1]+cells[k+8]+cells[k+9])

			perplexity = perplexity_topics(descriptor['topics'], cells[k]+cells[k+1]+cells[k+8]+cells[k+9])
			cells1_level_merge.append(descriptor)
			cells1_level_merge_perplexity.append(perplexity)
			if m < 4:
				k += 2
				m += 1		
			else:
				k += 8 + 2
				m = 0


		# merge	second level	
		k = 0
		m = 0	
		for i in range(0,4):
			descriptor = t.merge([cells1_level_merge[k], cells1_level_merge[k+1], cells1_level_merge[k+4], cells1_level_merge[k+5]],lda_ntopics,10)
			perplexity = perplexity_topics(descriptor['topics'], cells_group[k]+cells_group[k+1]+cells_group[k+4]+cells_group[k+5])
			cells2_level_merge.append(descriptor)
			cells2_level_merge_perplexity.append(perplexity)
			if m < 2:
				k += 2
				m += 1		
			else:
				k += 4 + 2
				m = 0

		# merge third level
		a = []
		for c in cells:
			a+=c	

		descriptor = t.merge([cells2_level_merge[0], cells2_level_merge[1], cells2_level_merge[2], cells2_level_merge[3]], lda_ntopics, 10)
		perplexity = perplexity_topics(descriptor['topics'], a)

		cells3_level_merge.append(descriptor) # 1
		cells3_level_merge_perplexity.append(perplexity)

		# MERGECLUSTER ==============================================================================================================

		# merge	first level
		k = 0
		m = 0
		cells_group = []
		for i in range(0,16):

			descriptor = t.mergeClusters([cells0_level[k], cells0_level[k+1], cells0_level[k+8], cells0_level[k+9]], lda_ntopics, lda_nwords4topic, 10)
			cells_group.append(cells[k]+cells[k+1]+cells[k+8]+cells[k+9])
			perplexity = perplexity_topics(descriptor['topics'], cells[k]+cells[k+1]+cells[k+8]+cells[k+9])
			cells1_level_mergeCluster.append(descriptor)
			cells1_level_mergeCluster_perplexity.append(perplexity)
			if m < 4:
				k += 2
				m += 1		
			else:
				k += 8 + 2
				m = 0


		# merge	second level	
		k = 0
		m = 0	
		for i in range(0,4):
			descriptor = t.mergeClusters([cells1_level_mergeCluster[k], cells1_level_mergeCluster[k+1], cells1_level_mergeCluster[k+4], cells1_level_mergeCluster[k+5]], lda_ntopics, lda_nwords4topic, 10)
			perplexity = perplexity_topics(descriptor['topics'], cells_group[k]+cells_group[k+1]+cells_group[k+4]+cells_group[k+5])
			cells2_level_mergeCluster.append(descriptor)
			cells2_level_mergeCluster_perplexity.append(perplexity)
			if m < 2:
				k += 2
				m += 1		
			else:
				k += 4 + 2
				m = 0

		# merge third level
		a = []
		for c in cells:
			a+=c	

		descriptor = t.mergeClusters([cells2_level_mergeCluster[0], cells2_level_mergeCluster[1], cells2_level_mergeCluster[2], cells2_level_mergeCluster[3]], lda_ntopics, lda_nwords4topic, 10)
		perplexity = perplexity_topics(descriptor['topics'], a)

		cells3_level_mergeCluster.append(descriptor) # 1
		cells3_level_mergeCluster_perplexity.append(perplexity)
	
		# Collecting data ==============================================================
		
		perplexities_simpleLda_1.append(avgList(cells1_level_lda_perplexity))
		perplexities_simpleLda_2.append(avgList(cells2_level_lda_perplexity))
		perplexities_simpleLda_3.append(avgList(cells3_level_lda_perplexity))

		perplexities_merge_1.append(avgList(cells1_level_merge_perplexity))
		perplexities_merge_2.append(avgList(cells2_level_merge_perplexity))
		perplexities_merge_3.append(avgList(cells3_level_merge_perplexity))

		perplexities_mergeCluster_1.append(avgList(cells1_level_mergeCluster_perplexity))
		perplexities_mergeCluster_2.append(avgList(cells2_level_mergeCluster_perplexity))
		perplexities_mergeCluster_3.append(avgList(cells3_level_mergeCluster_perplexity))	

		
		print(perplexities_simpleLda_1)
		print(perplexities_merge_1)				
		print(perplexities_mergeCluster_1)
		print('')
		print(perplexities_simpleLda_2)
		print(perplexities_merge_2)				
		print(perplexities_mergeCluster_2)
		print('')
		print(perplexities_simpleLda_3)
		print(perplexities_merge_3)				
		print(perplexities_mergeCluster_3)
		print('')
		print('')


	# PLOT ======================================================================================================================
	
	
	P.figure()

	# the histogram of the data with histtype='step'
	#n, bins, patches = P.hist(perplexities_simpleLda_1, bins, normed=1, histtype='bar', rwidth=0.8)	
	

	

	simpleLda1 = avgList(perplexities_simpleLda_1)
	merge1 = avgList(perplexities_merge_1)
	mergeCluster1 = avgList(perplexities_mergeCluster_1)

	simpleLda2 = avgList(perplexities_simpleLda_2)
	merge2 = avgList(perplexities_merge_2)
	mergeCluster2 = avgList(perplexities_mergeCluster_2)

	simpleLda3 = avgList(perplexities_simpleLda_3)
	merge3 = avgList(perplexities_merge_3)
	mergeCluster3 = avgList(perplexities_mergeCluster_3)

	alphab = ['LDA1', 'Merge1', 'MergeCluster1', '' ,'LDA2','Merge2', 'MergeCluster2','' ,'LDA3','Merge3','MergeCluster3' ]  
	frecuences = [simpleLda1, merge1, mergeCluster1, 0,simpleLda2, merge2, mergeCluster2,0, simpleLda3, merge3, mergeCluster3]  
	  
	pos = np.arange(len(alphab))  
	width = 1.0     # gives histogram aspect to the bar diagram  
	  
	ax = plt.axes()  
	ax.set_xticks(pos + (width / 2))  
	ax.set_xticklabels(alphab)  
	  
	plt.bar(pos, frecuences, width, color='r')  
	plt.show()  
	

	return 0


def avgList(l):
	res = 0.0

	l = [x for x in l if x != None and x != 0.0]

	for e in l:
		res += float(e)
	
	if len(l) > 0:
		return float(res) / len(l) 
	else:
		return 0


def makeSet(s,lda_ntopics,lda_npasses,lda_nwords4topic):
	
	topics_s = []
	topics_new = []
	model,c = lda(s,lda_ntopics,lda_npasses)
	if model != None or c != None:	
		topics_s = tp_lda.getTopicsRanking(model, c, lda_ntopics, lda_nwords4topic)
		
		for topic in topics_s:
			topics_new.append([topic[0],topic[1]])
		p_s = perplexity_topics(topics_new, s)
	else:
		p_s = None
		topics_s = []

	d_s = {}
	d_s['loc'] = [0,0]
	d_s['topics'] = topics_new
	d_s['s'] = 10
	d_s['ncorpuses'] = len(s)
	
	return d_s, p_s

if __name__ == '__main__':
	sys.exit(main(sys.argv))
