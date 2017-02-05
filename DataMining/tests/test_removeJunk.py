#!/usr/bin/env python3.5
import sys
from math import sqrt
from random import shuffle
import json

sys.path.append('..')
import utils.http_requests as http
import utils.topic_processing as l
sys.path.remove('..')

#global confidence
confidencesteps = [0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,0.99]

def estimation(original_corpuses, min_par, max_par, junkselector, step):

	d_log = {}

	negatives = []
	positives = []
	avg_final = []
	var_final = []
	bestnegative = bestpositive = 0

	for i in range(0,len(original_corpuses)):

		bestnegative,bestpositive = evaluation(original_corpuses[i] ,min_par, max_par, junkselector, step)
		negatives.append(bestnegative)
		positives.append(bestpositive)

	d_log['best_negatives'] = negatives	
	d_log['best_positives'] = positives

	bestnegative = f_approximation(avg_list(negatives))
	bestpositive = f_approximation(avg_list(positives))
	
	nwordsBeforeCut = 0
	nwordsAfterCut = 0
	for i in range(0,len(original_corpuses)):
		corpuses = []
		nwordsBeforeCut += wordCounter(original_corpuses[i])
		if junkselector == 1:
			res = http.removeJunk(original_corpuses[i], bestnegative, bestpositive)
			if len(res) > 0:
				corpuses = res[0]
				nwordsAfterCut += wordCounter(original_corpuses[i])

		elif junkselector == 2:
			res = http.removeJunk_var(original_corpuses[i], confidencesteps[bestnegative], confidencesteps[bestpositive])
			if len(res) > 0:
				corpuses = res[0]
				nwordsAfterCut += wordCounter(original_corpuses[i])

		g_avg,g_var = get_lda_avg_and_variance(corpuses)
		if g_avg > 0 and g_var >= 0:
			avg_final.append(g_avg)
			var_final.append(g_var)

	d_log['avg_best'] = avg_final	
	d_log['var_best'] = var_final
	
	print('\nRES:')
	print('\tbestnegative :\t' + str(bestnegative))
	print('\tbestpositive :\t' + str(bestpositive))
	print('\tnwords before the cut :'+str(nwordsBeforeCut))
	print('\tnwords after the cut : '+str(nwordsAfterCut))
	print('\tcoherence avg :\t' + str(avg_list(avg_final)))
	print('\tcoherence var :\t' + str(avg_list(var_final)))
	
	return d_log


def f_approximation(number):
	i_number = int(number)
	if (number - i_number) > 0.5:
		return i_number + 1
	else:
		return i_number

def wordCounter(corpuses):
	# count words
	counter = 0
	for corpus in corpuses:
		counter += len(corpus)
	
	return counter


def evaluation(original_corpuses, init_par1, init_par2, selector, step):

	if(selector == 2):
		init_par1 = 0
		init_par2 = len(confidencesteps)-1

	negative1 = init_par1
	negative2 = init_par2	
	positive1 = init_par1
	positive2 = init_par2

	bestnegative = bestpositive = 0

	nWordsAfter = 0

	for i in range(0,len(original_corpuses)):
		nWordsAfter += wordCounter(original_corpuses[i])

	guard = False
	while guard == False:

		nWordsPost1 = nWordsPost2 = 0

		if selector == 1:
			res =  http.removeJunk(original_corpuses, negative1, 1)
			if len(res) > 0:
				corpuses = res[0]
				avg1,var1 = get_lda_avg_and_variance(corpuses)				
				for i in range(0,len(corpuses)):
					nWordsPost1 += wordCounter(corpuses[i])
			else:
				avg1 = var1 = 0	

			res = http.removeJunk(original_corpuses, negative2, 1)
			if len(res) > 0:
				corpuses = res[0]
				avg2,var2 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost2 += wordCounter(corpuses[i])
			else:
				avg2 = var2 = 0	

		elif selector == 2:
			res =  http.removeJunk_var(original_corpuses, confidencesteps[negative1], 0.99)
			if len(res) > 0:
				corpuses = res[0]
				avg1,var1 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost1 += wordCounter(corpuses[i])
			else:
				avg1 = var1 = 0	

			res = http.removeJunk_var(original_corpuses, confidencesteps[negative2], 0.99)
			if len(res) > 0:
				corpuses = res[0]
				avg2,var2 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost2 += wordCounter(corpuses[i])
			else:
				avg2 = var2 = 0	

		# w1 calculus
		avg1 = avg1 * avg1
		var1 = var1 * var1
		w1 = (nWordsAfter - nWordsPost1) * compute_w(avg1, var1)
		# w2 calculus
		avg2 = avg2 * avg2
		var2 = var2 * var2
		w2 = (nWordsAfter - nWordsPost2) * compute_w(avg2, var2)

		

		if negative1 >= 0 and negative2 >= 0:
			if w1 == w2 == 0:
				negative2 = negative2 - step
				negative1 = negative1 + step
			else:
				if w1 > w2:
					negative2 = negative2 - step
					bestnegative = negative1
				else:
					negative1 = negative1 + step
					bestnegative = negative2
	
		if negative1 >= negative2:
			guard = True
	
	guard = False
	while guard == False:
		
		if selector == 1:
			res =  http.removeJunk(original_corpuses, 1, positive1)
			if len(res) > 0:
				corpuses = res[0]
				avg1,var1 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost1 += wordCounter(corpuses[i])
			else:
				avg1 = var1 = 0	
			res = http.removeJunk(original_corpuses, 1, positive2)
			if len(res) > 0:
				corpuses = res[0]
				avg2,var2 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost2 += wordCounter(corpuses[i])
			else:
				avg2 = var2 = 0	

		elif selector == 2:
			res = http.removeJunk_var(original_corpuses, 0.99, confidencesteps[positive1])
			if len(res) > 0:
				corpuses = res[0]
				avg1,var1 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost1 += wordCounter(corpuses[i])
			else:
				avg1 = var1 = 0	
			
			res = http.removeJunk_var(original_corpuses, 0.99, confidencesteps[positive2])			
			if len(res) > 0:
				corpuses = res[0]
				avg2,var2 = get_lda_avg_and_variance(corpuses)
				for i in range(0,len(corpuses)):
					nWordsPost2 += wordCounter(corpuses[i])
			else:
				avg2 = var2 = 0	


		# w1 calculus
		avg1 = avg1 * avg1
		var1 = var1 * var1
		w1 = (nWordsAfter - nWordsPost1) * compute_w(avg1, var1)
		# w2 calculus
		avg2 = avg2 * avg2
		var2 = var2 * var2
		w2 = (nWordsAfter - nWordsPost2) * compute_w(avg2, var2)
		
		if positive1 <= len(confidencesteps)-1 and positive2 <= len(confidencesteps)-1:
			if w1 == w2 == 0:
				positive2 = positive2 - step
				positive1 = positive1 + step
			else:		
				if w1 > w2:
					positive2 = positive2 - step
					bestpositive = positive1
				else:
					positive1 = positive1 + step
					bestpositive = positive2

		#print('\n\t'+str(bestpositive), end='\n')
	
		if positive1 >= positive2:
			guard = True
	
	return bestnegative,bestpositive


def get_lda_avg_and_variance(corpuses):

	l_topics = lda(corpuses, 20, 2, 20)
	#calc of the avg coherence and the variance
	if len(l_topics) > 0:
		coherence = 0.0
		for topic in l_topics:
			coherence += topic[1]
		avgcoherence = coherence / len(l_topics)
	
		var = 0.0
		for topic in l_topics:
			var += topic[1] * topic[1]

		#print(str(var) + ' / '+str(len(l_topics))+' - ' +str(avgcoherence * avgcoherence)+' '*100)
		var = var / len(l_topics) - avgcoherence * avgcoherence

		# epsilon
		if var < 0.00000001:
			var = 0

		return avgcoherence, sqrt(var)
	else:
		return -1000, -1000


def lda(corpuses, lda_ntopics, lda_npasses, lda_nwords4topic):
	corpuses = [x for x in corpuses if x != []]	

	if len(corpuses) > 0:
		corpus,document_lda = l.getTopicsFromDocs(corpuses, lda_ntopics, lda_npasses)
		l_topics = l.getTopicsRanking(document_lda,corpus, lda_ntopics, lda_nwords4topic)

		return l_topics
	else:
		return []


def compute_w(avg, var):
	
	if var > 0:
		return avg / (2 * var)
	else:
		return avg
	

def avg_list(numbers):
	res = 0.0
	numbers = [n for n in numbers if n > -100]
	if len(numbers) > 0:
		for number in numbers:
			res += number
		return res / len(numbers)
	else:
		return 0.0

def test(nurls_set, testtype):

	urlsTest = ['https://www.karamasoft.com/UltimateSpell/Samples/LongText/LongText.aspx',
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
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States/Connecticut/)</p',
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
	'http uploads solicited (MODs screened for quality.) Polls for favorite MODs (<a href=',
	'http://cool.cc/index/Top/Arts/Music/Sound_Files',
	'http://www.nhc.noaa.gov/',
	'http://cool.cc/index/Top/Science/Earth_Sciences/Atmospheric_Sciences/Meteorology/Weather_Phenomena',
	'http://sourceforge.net/projects/lambdamoo/',
	'http://cool.cc/index/Top/Games/Online/MUDs/Development/Codebases',
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
	'http://www.wvu.edu/',
	'http://cool.cc/index/Top/Reference/Education/Colleges_and_Universities/North_America/United_States',
	'http://www.me.go.kr/',
	'http://cool.cc/index/Top/Regional/Asia/South_Korea/Government/Executive_Branch',
	'http://www.modarchive.org/',
	'http uploads solicited (MODs screened for quality.) Polls for favorite MODs (<a href=',
	'http://cool.cc/index/Top/Arts/Music/Sound_Files',
	'http://www.nhc.noaa.gov/',
	'http://cool.cc/index/Top/Science/Earth_Sciences/Atmospheric_Sciences/Meteorology/Weather_Phenomena',
	'http://sourceforge.net/projects/lambdamoo/',
	'http://cool.cc/index/Top/Games/Online/MUDs/Development/Codebases'
	]

	# set of urls generators
	urls_sets = []
	
	dim_set = int(len(urlsTest) / nurls_set)
	#print(urlsTest[0])
	shuffle(urlsTest)
	#print(urlsTest[0])

	counter = 0
	urls = []
	for url in urlsTest:
		if len(urls_sets) < nurls_set:
			if counter < dim_set-1:
				urls.append(url)
			else:			
				urls.append(url)
				urls_sets.append(urls)
				urls = []
				counter = 0
			counter += 1

	# get corpuses
	print('Downloading the corpuses...')
	
	i = 0
	original_corpuses = []
	for urls in urls_sets:
		#print('\t downloading set : '+str(i))	
		corpuses = http.get_corpuses(urls, 10, [], False, 0, 1, 1)[0]
		original_corpuses.append([x for x in corpuses if x != []])
		i += 1

	print('Links :')
	print('Number of urls : '+str(len(urlsTest)))
	print('Number of sets : '+str(nurls_set))	
	print('Dim of each set :'+str(dim_set))
	print('')

	d_log = {}
	d_log['nurls'] = len(urlsTest)
	d_log['urlsforset'] = nurls_set
	d_log['dim_set'] = dim_set

	# params ==========================
	min_par = 1
	max_par = 5
	step = 1
	# =================================

	print('Estimation phase ...')
	# estimation for the negative

	if(testtype == 1 or testtype == 3):
		print('')
		print('Estimation for the positive and negative static ...')
		d_log['static'] = estimation(original_corpuses, min_par, max_par, 1, step)	
	if(testtype == 2 or testtype == 3):
		print('')
		print('Estimation for the positive and negative dinamic ...')
		d_log['dinamic'] = estimation(original_corpuses, min_par, max_par, 2, step)
	
	return d_log

def main(args):
	
	log = {}

	print('=================================================')
	print('TEST with 2 sets')
	log['a'] = test(2, 2)
	print('=================================================')
	print('TEST with 4 sets')
	log['b'] = test(4, 2)
	print('=================================================')
	print('TEST with 8 sets')
	log['c'] = test(8, 2)
	print('=================================================')
	print('TEST with 16 sets')
	log['d'] = test(16, 2)
	print('=================================================')
	print('TEST with 32 sets')
	log['e'] = test(32, 2)

	
	with open('test_log.json', 'w') as outfile:
		json.dump(log, outfile)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
