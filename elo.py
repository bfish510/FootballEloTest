csvFile = open('data.csv', 'r')
results = open('results.txt', 'w')
teamRatingsFile = open('ratings.txt', 'w')

ratings = open('ratingsGraph.csv', 'w')

ratingsGraph = {}

games = []

#bounds
earliestYear = 2012
latestYear = 2013
postSeasonGames = True
preSeasonGames = False
regularSeasonGames = True

useTeamFilter = False
teamFilter = ['Jets', 'Giants', 'Patriots', 'Bills']

numberOfWeeksInSeason = 0

if(regularSeasonGames):
	numberOfWeeksInSeason += 17
if(postSeasonGames):
	numberOfWeeksInSeason += 4
if(preSeasonGames):
	numberOfWeeksInSeason += 4


def computeEstimatedResult(team1, team2):
	exponent = (team2 - team1)/400
	value = 1/(1 + (10 ** exponent))
	return value

def computeNewRatings(team1, predictedScore, actualScore, isPreseason):
	#teams tend to use new players as a test during the preseason so we have a larger skill margin
	skillFactor = 0
	if(isPreseason):
		skillFactor = 32
	else:
		if(postseason):
			skillFactor = 8
		else:
			skillFactor = 16
	value = team1 + (skillFactor * (actualScore - predictedScore))
	return value

def loadCSV():
	header = csvFile.readline()
	for line in csvFile:
		(homeTeam,homeFirstQuater,homeSecondQuater,homeThirdQuater,
			homeFourthQuater,homeOTQuater,homeTotalScore,awayTeam,
			awayFirstQuater,awaySecondQuater,awayThirdQuater,
			awayFourthQuater,awayOTQuater,awayTotalScore,date, preseason, postseason) = line.split(',')
		awayBoxScore = []
		homeBoxScore = []

		awayBoxScore.append(int(awayFirstQuater))
		awayBoxScore.append(int(awaySecondQuater))
		awayBoxScore.append(int(awayThirdQuater))
		awayBoxScore.append(int(awayFourthQuater))
		awayBoxScore.append(int(awayOTQuater))

		homeBoxScore.append(int(homeFirstQuater))
		homeBoxScore.append(int(homeSecondQuater))
		homeBoxScore.append(int(homeThirdQuater))
		homeBoxScore.append(int(homeFourthQuater))
		homeBoxScore.append(int(homeOTQuater))

		games.append(Game(awayTeam, homeTeam, awayBoxScore, homeBoxScore, int(awayTotalScore), int(homeTotalScore), preseason, postseason, date))
	csvFile.close()

def inDataRange(game):
	if(game.year < earliestYear):
		return False
	if(game.year > latestYear):
		return False
	if(game.preseason == 'True'):
		if(not preSeasonGames):
			return False
		else:
			return True
	if(game.postseason == 'True'):
		if(not postSeasonGames):
			return False
		else:
			return True
	if(game.preseason == 'False'):
		if(game.postseason == 'False'):
			if(not regularSeasonGames):
				return False
	return True

def initData():
	loadCSV()

	#compute ratings
	for game in games:
		#add a check that a game is in the key set of the ratings maps
		skip = False
		if(game.homeTeam not in teamRating):
			teamRating[game.homeTeam] = 1500
		if(game.awayTeam not in teamRating):
			teamRating[game.awayTeam] = 1500
		if(inDataRange(game)):
			for i in range(0, 5):
				skip = False
				if(i == 4):
					if(game.homeScore == 0):
						if(game.awayScore == 0):
							skip = True
				if(not skip):
					eSHome = computeEstimatedResult(teamRating[game.homeTeam], teamRating[game.awayTeam])
					eSAway = computeEstimatedResult(teamRating[game.awayTeam], teamRating[game.homeTeam])
					scoreHome = 0
					scoreAway = 0
					if((game.awayBoxScore[i] + game.homeBoxScore[i]) != 0):
						scoreHome = (game.homeBoxScore[i]/(game.awayBoxScore[i] + game.homeBoxScore[i]))
						scoreAway = (game.awayBoxScore[i]/(game.awayBoxScore[i] + game.homeBoxScore[i]))
					else:
						scoreHome = 0.5
						scoreAway = 0.5
					teamRating[game.homeTeam] = computeNewRatings(teamRating[game.homeTeam], eSHome, scoreHome, game.isPreseason)
					teamRating[game.awayTeam] = computeNewRatings(teamRating[game.awayTeam], eSAway, scoreAway, game.isPreseason)

					results.write('\n')
					results.write('Home team: ' + game.homeTeam + '\n')
					results.write('Away team: ' + game.awayTeam + '\n')
					results.write('eSHome: ' + str(eSHome) + '\n')
					results.write('eSAway: ' + str(eSAway) + '\n')
					results.write('scoreHome: ' + str(scoreHome) + '\n')
					results.write('scoreAway: ' + str(scoreAway) + '\n')
					results.write('Home Rating: ' + str(teamRating[game.homeTeam]) + '\n')
					results.write('Away Rating: ' + str(teamRating[game.awayTeam]) + '\n')
			
			overallWeek = int(game.week) + ((int(game.year) - earliestYear) * numberOfWeeksInSeason)
			if(overallWeek not in ratingsGraph):
				ratingsGraph[overallWeek] = {}
				ratingsGraph[overallWeek][game.homeTeam] = teamRating[game.homeTeam]
				ratingsGraph[overallWeek][game.awayTeam] = teamRating[game.awayTeam]
			else:
				ratingsGraph[overallWeek][game.homeTeam] = teamRating[game.homeTeam]
				ratingsGraph[overallWeek][game.awayTeam] = teamRating[game.awayTeam]
			#ratingsGraph.write(game.homeTeam + ',' + str(overallWeek) + ',' + str(teamRating[game.homeTeam]) + '\n')
			#ratingsGraph.write(game.awayTeam + ',' + str(overallWeek) + ',' + str(teamRating[game.awayTeam]) + '\n')

	for team in teamRating:
		teamRatingsFile.write('\nTeam: ' + team + '\n')
		teamRatingsFile.write('\tRating: ' + str(teamRating[team]) + '\n')

	headerLabel = 'Week'
	for team in teamRating:
		if(useTeamFilter):
			if(team in teamFilter):
				headerLabel += ',' + team
		else:
			headerLabel += ',' + team
	for week in ratingsGraph:
		headerLabel += '\n'
		headerLabel += str(week)
		for team in teamRating:
			if(useTeamFilter):
				if(team in teamFilter):
					if(team in ratingsGraph[week]):
						headerLabel += ',' + str(ratingsGraph[week][team])
					else:
						ratingsGraph[week][team] = ratingsGraph[week - 1][team]
						headerLabel += ',' + str(ratingsGraph[week][team])
			else:
				if(team in ratingsGraph[week]):
					headerLabel += ',' + str(ratingsGraph[week][team])
				else:
					ratingsGraph[week][team] = ratingsGraph[week - 1][team]
					headerLabel += ',' + str(ratingsGraph[week][team])
	print(headerLabel)
	ratings.write(headerLabel)


class Game:
	def __init__(self, awayTeam, homeTeam, awayBoxScore, homeBoxScore, awayScore, homeScore, preseason, postseason, date):
		self.awayTeam = awayTeam
		self.homeTeam = homeTeam
		self.awayScore = awayScore
		self.homeScore = homeScore
		self.preseason = preseason
		self.postseason = postseason
		self.homeBoxScore = homeBoxScore
		self.awayBoxScore = awayBoxScore
		self.date = date
		(self.week, self.year,x,y) = date.split(':')
		self.week = int(self.week)
		self.year = int(self.year)

	def numQuaters(self):
		return len(self.awayScore)

	def isPreseason(self):
		return self.preseason

	def isPostseason(self):
		return self.postseason


teamRating = {}
initData()
