from EloClass import Elo

dontUseList = ['Texans', 'Titans', 'Raiders', 'Falcons', 'Rams', 'Cardinals', 'Buccaneers', 'Cowboys', 'Chargers', 'Jaguars', 'Dolphins', 'Packers', 'Browns', 'Jets', 'Panthers', 'Redskins', 'Vikings', 'Giants', 'Broncos', 'Lions', 'Saints', 'Bengals', 'Bears', 'Eagles', 'Seahawks', 'Patriots', 'Ravens', '49ers', 'Colts', 'Steelers', 'Bills', 'Chiefs']

ratingsGraph = {}
numGames = 0
pointsScoredPerGame = {}

games = []

#bounds
earliestYear = 2010
latestYear = 2013
latestWeek = 8
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

PRE_SEASON = 0
REGULAR_SEASON = 1
POST_SEASON = 3


def computeEstimatedResult(team1, team2):
	exponent = (team2 - team1)/400
	value = 1/(1 + (10 ** exponent))
	return value

def getKFactor(seasonEnum):
	#teams tend to use new players as a test during the preseason so we have a larger skill margin
	skillFactor = 0
	if(seasonEnum == PRE_SEASON):
		skillFactor = 32
	else:
		if(seasonEnum == POST_SEASON):
			skillFactor = 8
		else:
			skillFactor = 16
	return skillFactor

def loadCSV():
	csvFile = open('data.csv', 'r')
	header = csvFile.readline()
	for line in csvFile:
		(homeTeam,homeFirstQuater,homeSecondQuater,homeThirdQuater,
			homeFourthQuater,homeOTQuater,homeTotalScore,awayTeam,
			awayFirstQuater,awaySecondQuater,awayThirdQuater,
			awayFourthQuater,awayOTQuater,awayTotalScore,date, preseason, postseason) = line.split(',')
		awayBoxScore = [int(awayFirstQuater), int(awaySecondQuater), int(awayThirdQuater), int(awayFourthQuater), int(awayOTQuater)]
		homeBoxScore = [int(homeFirstQuater), int(homeSecondQuater), int(homeThirdQuater), int(homeFourthQuater), int(homeOTQuater)]
		games.append(Game(awayTeam, homeTeam, awayBoxScore, homeBoxScore, int(awayTotalScore), int(homeTotalScore), preseason, postseason, date))
	csvFile.close()

def inDataRange(game):
	if(game.year < earliestYear):
		return False
	if(game.year > latestYear):
		return False
	if(game.week > latestWeek):
		if(game.year == latestYear):
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

def processData():
	#compute ratings
	for game in games:
		#add a check that a game is in the key set of the ratings maps
		if(inDataRange(game)):
			seasonType = REGULAR_SEASON
			if(game.isPreseason):
				seasonType = PRE_SEASON
			else:
				if(game.isPostseason):
					seasonType = POST_SEASON
			for i in range(0, 5):
				#if we are checking overtime
				if(i == 4):
					if(game.homeBoxScore[i] != 0 or game.awayBoxScore[i] != 0):
						elo.matchResults(game.homeTeam, game.homeBoxScore[i], game.awayTeam, game.awayBoxScore[i], getKFactor(seasonType))
				else:
					elo.matchResults(game.homeTeam, game.homeBoxScore[i], game.awayTeam, game.awayBoxScore[i], getKFactor(seasonType))
			overallWeek = int(game.week) + ((int(game.year) - earliestYear) * numberOfWeeksInSeason)
			if(overallWeek not in ratingsGraph):
				ratingsGraph[overallWeek] = {}
				ratingsGraph[overallWeek][game.homeTeam] = elo.getRating(game.homeTeam)
				ratingsGraph[overallWeek][game.awayTeam] = elo.getRating(game.awayTeam)
			else:
				ratingsGraph[overallWeek][game.homeTeam] = elo.getRating(game.homeTeam)
				ratingsGraph[overallWeek][game.awayTeam] = elo.getRating(game.awayTeam)
			#effective points per game
			if(game.homeTeam not in pointScoredOnAverage):
				pointScoredOnAverage[game.homeTeam] = (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam))
			else:
				temp = pointScoredOnAverage[game.homeTeam] * (overallWeek - 1)
				pointScoredOnAverage[game.homeTeam] = (temp + (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam)))/overallWeek
			if(game.awayTeam not in pointScoredOnAverage):
				pointScoredOnAverage[game.awayTeam] = (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam))
			else:
				temp = pointScoredOnAverage[game.awayTeam] * (overallWeek - 1)
				pointScoredOnAverage[game.awayTeam] = (temp + (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam)))/overallWeek
			#effective points let up
			if(game.homeTeam not in pointsGivenUpOnAverage):
				pointsGivenUpOnAverage[game.homeTeam] = (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam))
			else:
				temp = pointsGivenUpOnAverage[game.homeTeam] * (overallWeek - 1)
				pointsGivenUpOnAverage[game.homeTeam] = (temp + (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam)))/overallWeek
			if(game.awayTeam not in pointsGivenUpOnAverage):
				pointsGivenUpOnAverage[game.awayTeam] = (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam))
			else:
				temp = pointsGivenUpOnAverage[game.awayTeam] * (overallWeek - 1)
				pointsGivenUpOnAverage[game.awayTeam] = (temp + (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam)))/overallWeek

def createFinalRatingsFile():
	teamRatingsFile = open('ratings.txt', 'w')
	for team in elo.getTeamList():
		teamRatingsFile.write('\nTeam: ' + team + '\n')
		teamRatingsFile.write('\tRating: ' + str(elo.getRating(team)) + '\n')
	teamRatingsFile.close()

def createRatingsGraph():
	ratings = open('ratingsGraph.csv', 'w')
	headerLabel = 'Week'
	for team in elo.getTeamList():
		if(useTeamFilter):
			if(team in teamFilter):
				headerLabel += ',' + team
		else:
			headerLabel += ',' + team
	for week in ratingsGraph:
		headerLabel += '\n'
		headerLabel += str(week)
		for team in elo.getTeamList():
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
					iterateWeek = week -1
					if(week == 1):
						ratingsGraph[week][team] = 1500
					else:
						while(iterateWeek not in ratingsGraph):
							iterateWeek = iterateWeek - 1
						ratingsGraph[week][team] = ratingsGraph[iterateWeek][team]
					headerLabel += ',' + str(ratingsGraph[week][team])
	ratings.write(headerLabel)
	ratings.close()

def pointsPerGameData():
	for game in games:
		overallWeek = int(game.week) + ((int(game.year) - earliestYear) * numberOfWeeksInSeason)
		if(inDataRange(game)):
			#points scored
			if(game.homeTeam not in pointScoredOnAverage):
				pointScoredOnAverage[game.homeTeam] = game.homeScore
			else:
				temp = pointScoredOnAverage[game.homeTeam] * (overallWeek - 1)
				pointScoredOnAverage[game.homeTeam] = (temp + game.homeScore)/overallWeek
			if(game.awayTeam not in pointScoredOnAverage):
				pointScoredOnAverage[game.awayTeam] = game.awayScore
			else:
				temp = pointScoredOnAverage[game.awayTeam] * (overallWeek - 1)
				pointScoredOnAverage[game.awayTeam] = (temp + game.awayScore)/overallWeek
			#points let up
			if(game.homeTeam not in pointsGivenUpOnAverage):
				pointsGivenUpOnAverage[game.homeTeam] = game.awayScore
			else:
				temp = pointsGivenUpOnAverage[game.homeTeam] * (overallWeek - 1)
				pointsGivenUpOnAverage[game.homeTeam] = (temp + game.awayScore)/overallWeek
			if(game.awayTeam not in pointsGivenUpOnAverage):
				pointsGivenUpOnAverage[game.awayTeam] = game.homeScore
			else:
				temp = pointsGivenUpOnAverage[game.awayTeam] * (overallWeek - 1)
				pointsGivenUpOnAverage[game.awayTeam] = (temp + game.homeScore)/overallWeek

def printPointData():
	pointData = open('pointdata.txt', 'w')
	for team in pointScoredOnAverage:
		pointData.write("Team: " + team + "\n")
		pointData.write("\tPoints on average: " + str(pointScoredOnAverage[team])+ "\n")
		pointData.write("\tPoints given up on average: " + str(pointsGivenUpOnAverage[team])+ "\n")
		pointData.write("\n")
	pointData.close()

def predictions():
	predictionsFile = open('predictions.txt', 'w')
	gamePrediction = []
	gamePrediction.append(('Bengals', 'Dolphins'))
	gamePrediction.append(('Falcons', 'Panthers'))
	gamePrediction.append(('Vikings', 'Cowboys'))
	gamePrediction.append(('Saints', 'Jets'))
	gamePrediction.append(('Titans', 'Rams'))
	gamePrediction.append(('Chiefs', 'Bills'))
	gamePrediction.append(('Chargers', 'Redskins'))
	gamePrediction.append(('Eagles', 'Raiders'))
	gamePrediction.append(('Buccaneers', 'Seahawks'))
	gamePrediction.append(('Ravens', 'Browns'))
	gamePrediction.append(('Steelers', 'Patriots'))
	gamePrediction.append(('Colts', 'Texans'))
	gamePrediction.append(('Bears', 'Packers'))
	for game in gamePrediction:
		predictionsFile.write(game[0] + " vs. " + game[1])
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[0] + " Rating: " + str(elo.getRating(game[0])))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[1] + " Rating: " + str(elo.getRating(game[1])))
		predictionsFile.write("\n")
		#basic for now we can match data later
		estimate0 = elo.computeEstimatedResult(game[0], game[1])
		estimate1 = 1 - estimate0
		score0 = ((pointScoredOnAverage[game[0]] * estimate0) + (pointsGivenUpOnAverage[game[1]] * estimate1)) * 2
		score1 = ((pointScoredOnAverage[game[1]] * estimate1) + (pointsGivenUpOnAverage[game[0]] * estimate0)) * 2
		predictionsFile.write("\t" + game[0] + " Final Score " + str(score0))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[1] + " Rating: " + str(score1))
		predictionsFile.write("\n")
	predictionsFile.close()

def initData():
	loadCSV()
	processData()
	createFinalRatingsFile()
	createRatingsGraph()
	#pointsPerGameData()
	printPointData()
	predictions()

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


pointScoredOnAverage = {}
pointsGivenUpOnAverage = {}
elo = Elo()
initData()
