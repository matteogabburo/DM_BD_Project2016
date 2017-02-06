#!/usr/bin/env python3.5
import sys
from random import shuffle

import numpy as np
import matplotlib.pyplot as plt

# My imports
sys.path.append('..')
import utils.http_requests as http
import utils.topic_processing as lda
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
			#print(coherence)
		new_topic_list = []
		new_topic_list.append(topic[0])
		new_topic_list.append(coherence)# / len_d_corpuses)
		my_coherences.append(coherence)# / len_d_corpuses) # for logs
		new_topics_list.append(new_topic_list)

	return new_topics_list


def f_approximation(number):
	i_number = int(number)
	if (number - i_number) > 0.5:
		return i_number + 1
	else:
		return i_number
def main(args):
	
	urls = ['https://www.karamasoft.com/UltimateSpell/Samples/LongText/LongText.aspx',
	'http://catdir.loc.gov/catdir/enhancements/fy0711/2006051179-s.html',	
	'http://www.w3schools.com/html/html_examples.asp',
	'http://www.suzukicycles.com/',
	'https://github.com/att',
	'http://www.tirumala.org/',
	'http://dev.mysql.com/downloads/workbench/',
	'http://lynx.isc.org/',
	'http://www.khilafah.com/',
	'http://www.carleton.edu/',
	'http://www.sankeyrodeo.com/',
	'http://www.ponyclubvic.org/',
	'http://www.kompaktkiste.de/',
	'http://www.irvinechamber.com/',
	'http://www.bobbysherman.com/',
	'http://www.nrcan-rncan.gc.ca/',
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



	shuffle(urls)

	coherences = []

	corpuses = []
	for url in urls:
		print(url)
		ret = http.get_url_text_corpus(url,10,[])[0]
		if ret != None:
			corpuses.append(http.get_url_text_corpus(url,10,[])[0])
	
	k = f_approximation(len(corpuses) / int(args[1]))

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

	for c in l_ksets:

		set1 = c[int(len(c)/2):]
		set2 = c[:int(len(c)/2)]

		lda_ntopics = 1
		lda_npasses = 20
		lda_nwords4topic = 20

		# lda(set 1)
		corpus,document_lda = lda.getTopicsFromDocs(set1, lda_ntopics, lda_npasses)
		topics_set1 = lda.getTopicsRanking(document_lda,corpus, lda_ntopics, lda_nwords4topic)
		#topics_set1 = setCoherences(set1, topics_set1)


		d_set1 = {}
		d_set1['loc'] = [0,0]
		d_set1['topics'] = topics_set1
		d_set1['s'] = 10
		d_set1['ncorpuses'] = len(set1)
	

		# lda(set 2)
		corpus,document_lda = lda.getTopicsFromDocs(set2, lda_ntopics, lda_npasses)
		topics_set2 = lda.getTopicsRanking(document_lda,corpus, lda_ntopics, lda_nwords4topic)
		#topics_set2 = setCoherences(set2, topics_set2)
	
		d_set2 = {}
		d_set2['loc'] = [0,0]
		d_set2['topics'] = topics_set2
		d_set2['s'] = 10
		d_set2['ncorpuses'] = len(set2)


		# lda(set 1 + set2)
		sets12 = set1+set2
		corpus,document_lda = lda.getTopicsFromDocs(sets12, lda_ntopics, lda_npasses)
		topics_sets12 = lda.getTopicsRanking(document_lda,corpus, lda_ntopics, lda_nwords4topic)

		d_sets12 = {}
		d_sets12['loc'] = [0,0]
		d_sets12['topics'] = topics_sets12
		d_sets12['s'] = 10
		d_sets12['ncorpuses'] = len(corpuses)

		# merge 
		d_merge = t.merge([dict(d_set1),dict(d_set2)],lda_ntopics,10)
		topics_merge = d_merge['topics']

		d_merge_clusters = t.mergeClusters([dict(d_set1),dict(d_set2)], lda_ntopics, lda_nwords4topic, 10)
		topics_merge_clusters = d_merge_clusters['topics']


		coherences.append([topics_set1[0][1], topics_set2[0][1], topics_sets12[0][1], topics_merge[0][1], topics_merge_clusters[0][1]])	
	
		print(topics_set1[0][1])
		print(topics_set2[0][1])	
		print(topics_merge[0][1])
		print(topics_sets12[0][1])
		print(topics_merge_clusters[0][1])


	l_x = [i for i in range(0,len(l_ksets))]
	l_0 = [c[0] for c in coherences]
	l_1 = [c[1] for c in coherences]
	l_2 = [c[2] for c in coherences]
	l_3 = [c[3] for c in coherences]
	l_4 = [c[4] for c in coherences]

	print(l_x)
	print(coherences)

	plt.plot(l_x, l_0,'r--') #lda(a)
	plt.plot(l_x, l_1,'b--') # lda(b)
	plt.plot(l_x, l_2,'m') # lda(a,b)
	plt.plot(l_x, l_3,'k') # merge
	plt.plot(l_x, l_4,'g') # cluster merge

	#plt.plot(my_avg_coherence_x, res,'g')
	
	plt.show()

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
