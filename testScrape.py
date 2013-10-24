import urllib.request
import time

urlPrefix = 'http://www.nfl.com/scores/'
scoreBoxString = '<div class="new-score-box">'
quatersString = '<p class="quarters-score">'
go = True
dataFile = open('data.csv', 'w')

def getURL(year, week, preseason, postseason):
	url = urlPrefix + str(year) + '/'
	if(preseason):
		url += 'PRE' + str(week)
	else:
		if(postseason):
			url += 'POST' + str(week)
		else:
			url += 'REG' + str(week)
	return url

def getPage(url):
	return urllib.request.urlopen(url).read().decode('utf-8')

def trimPage(source):
	start = source.index(scoreBoxString)
	source = source[start:]
	return source

#only does one game per page so far
def getNextGameIndex(source):
	games = []
	while source.find(scoreBoxString) != -1:
		start = source.index(scoreBoxString)
		end = source[start + len(scoreBoxString):]
		if(end.find(scoreBoxString) != -1):
			end = end.index(scoreBoxString)
			game = source[start:end]
			games.append(game)
			source = source[end:]
		else:
			game = source[start:]
			games.append(game)
			source = ''
	return games
	

def parseGame(gameSource):
	#init
	awayTeam = gameSource
	awayTotalScore = 0
	awayBoxScore = []

	#parse away team name
	awayTeam = gameSource[gameSource.index("team-name"):]
	awayTeam = awayTeam[:awayTeam.index("</a></p>")]
	awayTeam = awayTeam[awayTeam.rindex(">") + 1:]
	
	#parse away total score
	awayTotalScore = gameSource[gameSource.index('total-score">') + 13:]
	awayTotalScore = awayTotalScore[:awayTotalScore.index('</p>')]
	
	#parse box score
	gameSource = gameSource[gameSource.index(quatersString):]
	awayBoxScoreSource = gameSource[:gameSource.index('</p>')]
	first = awayBoxScoreSource[awayBoxScoreSource.index('<span class="first-qt">'):awayBoxScoreSource.index('</span>')]
	first = first[first.index('>') + 1 :]
	awayBoxScoreSource = awayBoxScoreSource[awayBoxScoreSource.index('<span class="second-qt">'):]
	second = awayBoxScoreSource[awayBoxScoreSource.index('<span class="second-qt">'):awayBoxScoreSource.index('</span>')]
	second = second[second.index('>') + 1 :]
	awayBoxScoreSource = awayBoxScoreSource[awayBoxScoreSource.index('<span class="third-qt">'):]
	third = awayBoxScoreSource[awayBoxScoreSource.index('<span class="third-qt">'):awayBoxScoreSource.index('</span>')]
	third = third[third.index('>') + 1 :]
	awayBoxScoreSource = awayBoxScoreSource[awayBoxScoreSource.index('<span class="fourth-qt">'):]
	fourth = awayBoxScoreSource[awayBoxScoreSource.index('<span class="fourth-qt">'):awayBoxScoreSource.index('</span>')]
	fourth = fourth[fourth.index('>') + 1 :]
	awayBoxScoreSource = awayBoxScoreSource[awayBoxScoreSource.index('<span class="ot-qt">'):]
	ot = awayBoxScoreSource[awayBoxScoreSource.index('<span class="ot-qt">'):awayBoxScoreSource.index('</span>')]
	ot = ot[ot.index('>') + 1 :]
	awayBoxScore.append(first)
	awayBoxScore.append(second)
	awayBoxScore.append(third)
	awayBoxScore.append(fourth)
	if(len(ot) != 0):
		awayBoxScore.append(ot)
	else:
		awayBoxScore.append('0')
	
	#will do this the ugly way for now and just copy code

	gameSource = gameSource[gameSource.index("team-name"):]

	#init
	homeTotalScore = 0
	homeBoxScore = []

	#parse home team name
	homeTeam = gameSource[gameSource.index("team-name"):]
	homeTeam = homeTeam[:homeTeam.index("</a></p>")]
	homeTeam = homeTeam[homeTeam.rindex(">") + 1:]
	
	#parse home total score
	homeTotalScore = gameSource[gameSource.index('total-score">') + 13:]
	homeTotalScore = homeTotalScore[:homeTotalScore.index('</p>')]
	
	#parse box score
	gameSource = gameSource[gameSource.index(quatersString):]
	gameSource = gameSource[:gameSource.index('</p>')]
	first = gameSource[gameSource.index('<span class="first-qt">'):gameSource.index('</span>')]
	first = first[first.index('>') + 1 :]
	gameSource = gameSource[gameSource.index('<span class="second-qt">'):]
	second = gameSource[gameSource.index('<span class="second-qt">'):gameSource.index('</span>')]
	second = second[second.index('>') + 1 :]
	gameSource = gameSource[gameSource.index('<span class="third-qt">'):]
	third = gameSource[gameSource.index('<span class="third-qt">'):gameSource.index('</span>')]
	third = third[third.index('>') + 1 :]
	gameSource = gameSource[gameSource.index('<span class="fourth-qt">'):]
	fourth = gameSource[gameSource.index('<span class="fourth-qt">'):gameSource.index('</span>')]
	fourth = fourth[fourth.index('>') + 1 :]
	gameSource = gameSource[gameSource.index('<span class="ot-qt">'):]
	ot = gameSource[gameSource.index('<span class="ot-qt">'):gameSource.index('</span>')]
	ot = ot[ot.index('>') + 1 :]
	homeBoxScore.append(first)
	homeBoxScore.append(second)
	homeBoxScore.append(third)
	homeBoxScore.append(fourth)
	if(len(ot) != 0):
		homeBoxScore.append(ot)
	else:
		homeBoxScore.append('0')

	return (homeTeam,homeBoxScore,homeTotalScore,awayTeam,awayBoxScore,awayTotalScore)

def parseSteps(year, week, preseason, postseason):
	url = getURL(year, week, preseason, postseason)
	f = getPage(url)
	trimedPage = trimPage(f)
	games = getNextGameIndex(trimedPage)
	for game in games:
		(homeTeam,homeBoxScore,homeTotalScore,awayTeam,awayBoxScore,awayTotalScore) = parseGame(game)
		print(homeTeam + ": " + homeTotalScore + "\n" + awayTeam + ": " + awayTotalScore)
		homeBoxScoreString = ''
		awayBoxScoreString = ''
		for i in homeBoxScore:
			homeBoxScoreString += ',' + i
		for i in awayBoxScore:
			awayBoxScoreString += ',' + i

		dataFile.write(homeTeam +homeBoxScoreString+ ',' +homeTotalScore+ ',' +awayTeam+ awayBoxScoreString+ ',' +awayTotalScore + ',' + str(week) + ':' + str(year) +':' + str(preseason) + ':' + str(postseason) + ',' + str(preseason) + ',' + str(postseason) +'\n')
	print(str(year) + ' ' + str(week) + ' ' + str(preseason) + ' ' + str(postseason))
	#sleep so we can keep doing this without nfl thinking we're assholes / hackers
	time.sleep(2)

dataFile.write('homeTeam,homeFirstQuater,homeSecondQuater,homeThirdQuater,homeFourthQuater,homeOTQuater,homeTotalScore,awayTeam,awayFirstQuater,awaySecondQuater,awayThirdQuater,awayFourthQuater,awayOTQuater,awayTotalScore,date,preseason,postseason\n')

if(go):
	for year in range(2001, 2013):
		for week in range(1,5):
			parseSteps(year, week, True, False)
		for week in range(1,18):
			parseSteps(year, week, False, False)
		parseSteps(year, 18, False, True)
		parseSteps(year, 19, False, True)
		parseSteps(year, 20, False, True)
		if(year <= 2008):
			parseSteps(year, 21, False, True)
		else:
			parseSteps(year, 22, False, True)
	for week in range(1,4):
		parseSteps(2013, week, True, False)
	for week in range(1,8):
		parseSteps(2013, week, False, False)
else:
	parseSteps(2013, 1, False, False)
	parseSteps(2013, 2, False, False)







