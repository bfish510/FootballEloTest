from EloClass import Elo
import time

#this is used for auto complete so that I can type in predictions quicker.
dontUseList = ['Texans', 'Titans', 'Raiders', 'Falcons', 'Rams', 'Cardinals', 'Buccaneers', 'Cowboys', 'Chargers', 'Jaguars', 'Dolphins', 'Packers', 'Browns', 'Jets', 'Panthers', 'Redskins', 'Vikings', 'Giants', 'Broncos', 'Lions', 'Saints', 'Bengals', 'Bears', 'Eagles', 'Seahawks', 'Patriots', 'Ravens', '49ers', 'Colts', 'Steelers', 'Bills', 'Chiefs']
ratingsGraph = {}

#bounds
earliestYear = 2002
latestYear = 2013
latestWeek = 10
postSeasonGames = True
preSeasonGames = False
regularSeasonGames = True

useTeamFilter = False
teamFilter = ['Jets', 'Giants', 'Patriots', 'Bills']



PRE_SEASON = 0
REGULAR_SEASON = 1
POST_SEASON = 3

kFactorTuple = ()

#use this to determine ppg fall off


def computeEstimatedResult(team1, team2):
	exponent = (team2 - team1)/400
	value = 1/(1 + (10 ** exponent))
	return value

#used for back testing
def setKFactor(ktuple):
	kFactorTuple = ktuple

def getKFactor(seasonEnum):
	#teams tend to use new players as a test during the preseason so we have a larger skill margin
	skillFactor = 0
	if(len(kFactorTuple) == 3):
		if(seasonEnum == PRE_SEASON):
			#was 32
			skillFactor = kFactorTuple[0]
		else:
			#was 8
			if(seasonEnum == POST_SEASON):
				skillFactor = kFactorTuple[1]
			else:
				#was 16
				skillFactor = kFactorTuple[2]
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

#add prediction variables

yearBuffer = 1

def setupPredictions(game):
	if(game.year - yearBuffer >= earliestYear):
		#add year before buffer or something to eliminate early outliers
		overallWeek = int(game.week) + ((int(game.year) - earliestYear) * numberOfWeeksInSeason)
		#by rating
		if(elo.getRating(game.homeTeam) > elo.getRating(game.awayTeam)):
			predictedWinner = game.homeTeam
		else:
			predictedWinner = game.awayTeam
		ratingPrediction.addPrediction(game.homeTeam, game.awayTeam, overallWeek, predictedWinner)
		#by ppg
		estimate0 = elo.computeEstimatedResult(game.homeTeam, game.awayTeam)
		estimate1 = 1 - estimate0
		scoreHome = ((pointScoredOnAverage[game.homeTeam] * estimate0) + (pointsGivenUpOnAverage[game.awayTeam] * estimate1)) * 2
		scoreAway = ((pointScoredOnAverage[game.awayTeam] * estimate1) + (pointsGivenUpOnAverage[game.homeTeam] * estimate0)) * 2
		if(scoreHome > scoreAway):
			predictedWinner = game.homeTeam
		else:
			predictedWinner = game.awayTeam
		ppgPrediction.addPrediction(game.homeTeam, game.awayTeam, overallWeek, predictedWinner)
		
def processPredictionResults(game):
	overallWeek = int(game.week) + ((int(game.year) - earliestYear) * numberOfWeeksInSeason)
	if(game.homeScore > game.awayScore):
		ppgPrediction.matchResult(game.homeTeam, game.awayTeam, overallWeek, game.homeTeam)
		ratingPrediction.matchResult(game.homeTeam, game.awayTeam, overallWeek, game.homeTeam)
	else:
		ppgPrediction.matchResult(game.homeTeam, game.awayTeam, overallWeek, game.awayTeam)
		ratingPrediction.matchResult(game.homeTeam, game.awayTeam, overallWeek, game.awayTeam)

def processData():
	#compute ratings
	for game in games:
		#add a check that a game is in the key set of the ratings maps
		if(inDataRange(game)):
			setupPredictions(game)
			processPredictionResults(game)
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
			pointsPerGameData(game)

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

def pointsPerGameData(game):
	#points scored
	if(game.homeTeam not in pointScoredOnAverage):
		pointScoredOnAverage[game.homeTeam] = (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam))
	else:
		temp = (pointScoredOnAverage[game.homeTeam] * pointExponent) + ((1 - pointExponent) * (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam)))
		pointScoredOnAverage[game.homeTeam] = temp
	if(game.awayTeam not in pointScoredOnAverage):
		pointScoredOnAverage[game.awayTeam] = (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam))
	else:
		temp = (pointScoredOnAverage[game.awayTeam] * pointExponent) + ((1 - pointExponent) * (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam)))
		pointScoredOnAverage[game.awayTeam] = temp
	#points let up
	if(game.homeTeam not in pointsGivenUpOnAverage):
		pointsGivenUpOnAverage[game.homeTeam] = (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam))
	else:
		temp = (pointsGivenUpOnAverage[game.homeTeam] * pointExponent) + ((1 - pointExponent) * (game.awayScore * elo.computeEstimatedResult(game.homeTeam, game.awayTeam)))
		pointsGivenUpOnAverage[game.homeTeam] = temp
	if(game.awayTeam not in pointsGivenUpOnAverage):
		pointsGivenUpOnAverage[game.awayTeam] = (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam))
	else:
		temp = (pointsGivenUpOnAverage[game.awayTeam] * pointExponent) + ((1 - pointExponent) * (game.homeScore * elo.computeEstimatedResult(game.awayTeam, game.homeTeam)))
		pointsGivenUpOnAverage[game.awayTeam] = temp

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
	gamePrediction.append(('Colts', 'Titans'))
	gamePrediction.append(('Jets', 'Bills'))
	gamePrediction.append(('Falcons', 'Buccaneers'))
	gamePrediction.append(('Lions', 'Steelers'))
	gamePrediction.append(('Redskins', 'Eagles'))
	gamePrediction.append(('Jaguars', 'Cardinals'))
	gamePrediction.append(('Raiders', 'Texans'))
	gamePrediction.append(('Ravens', 'Bears'))
	gamePrediction.append(('Browns', 'Bengals'))
	gamePrediction.append(('Dolphins', 'Chargers'))
	gamePrediction.append(('Packers', 'Giants'))
	gamePrediction.append(('Vikings', 'Seahawks'))
	gamePrediction.append(('49ers', 'Saints'))
	gamePrediction.append(('Chiefs', 'Broncos'))
	gamePrediction.append(('Panthers', 'Patriots'))
	for game in gamePrediction:
		predictionsFile.write(game[0] + " vs. " + game[1])
		predictionsFile.write("\n")
		if(elo.getRating(game[0]) > elo.getRating(game[1])):
			print("Expecting " + game[0] + " over " + game[1] + " with confidence: " + str((elo.getRating(game[0]) - elo.getRating(game[1]))))
		else:
			print("Expecting " + game[1] + " over " + game[0] + " with confidence: " + str((elo.getRating(game[0]) - elo.getRating(game[1]))))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[0] + " Rating: " + str(elo.getRating(game[0])))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[1] + " Rating: " + str(elo.getRating(game[1])))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + "Difference Rating: " + str((elo.getRating(game[0]) - elo.getRating(game[1]))))
		predictionsFile.write("\n")
		#basic for now we can match data later
		estimate0 = elo.computeEstimatedResult(game[0], game[1])
		estimate1 = 1 - estimate0
		score0 = ((pointScoredOnAverage[game[0]] * estimate0) + (pointsGivenUpOnAverage[game[1]] * estimate1)) * 2
		score1 = ((pointScoredOnAverage[game[1]] * estimate1) + (pointsGivenUpOnAverage[game[0]] * estimate0)) * 2
		predictionsFile.write("\t" + game[0] + " Final Score " + str(score0))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + game[1] + " Final Score: " + str(score1))
		predictionsFile.write("\n")
		predictionsFile.write("\t" + "Difference Score: " + str((score0 - score1)))
		predictionsFile.write("\n\n")
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

class Prediction:

	def __init__(self):
		self.predictedGames = {}
		self.correct = 0
		self.wrong = 0

	# we add the week as an error check for missing games
	def addPrediction(self, team1, team2, week, winningTeam):
		if(team1 < team2):
			firstTeam = team1
			secondTeam = team2
		else:
			firstTeam = team2
			secondTeam = team1
		self.predictedGames[(firstTeam, secondTeam, week)] = winningTeam

	def matchResult(self, team1, team2, week, winningTeam):
		if(team1 < team2):
			firstTeam = team1
			secondTeam = team2
		else:
			firstTeam = team2
			secondTeam = team1
		matchInfo = (firstTeam, secondTeam, week) 
		if(matchInfo in self.predictedGames):
			if(self.predictedGames[matchInfo] == winningTeam):
				self.correct += 1
			else:
				self.wrong += 1

	def getResult(self):
		return (self.correct / (self.correct + self.wrong))

pointExponentStarting = .5
ppgBest = 0
ratingBest = 0

total = 0
totalItems = 10 * 45 * 45 * 45

startTime = time.time()

games = []
loadCSV()
bestRatingResults = open('backtesting.txt' , 'w')

print("Starting time: " + str(startTime))
for i in range(8, 9):
	for postK in range(5, 6):
		for regularK in range(5, 6):
			total += 1
			setKFactor((0, postK, regularK))
			pointExponent = pointExponentStarting + (.05 * i)
			numberOfWeeksInSeason = 0
			if(regularSeasonGames):
				numberOfWeeksInSeason += 17
			if(postSeasonGames):
				numberOfWeeksInSeason += 4
			if(preSeasonGames):
				numberOfWeeksInSeason += 4
			
			ppgPrediction = Prediction()
			ratingPrediction = Prediction()
			pointScoredOnAverage = {}
			pointsGivenUpOnAverage = {}
			elo = Elo()
			initData()
			if(False):
				if(ppgBest < ppgPrediction.getResult()):
					print('result')
					ppgBest = ppgPrediction.getResult()
					bestRatingResults.write("\nBest ppg:")
					bestRatingResults.write("\tPreK: " + str(0))
					bestRatingResults.write("\tPostK: " + str(postK))
					bestRatingResults.write("\tRegularK: " + str(regularK))
					bestRatingResults.write("\tPoint exponent: " + str(pointExponent))
					bestRatingResults.write("\tppg Result: " + str(ppgPrediction.getResult()))
					bestRatingResults.write("\trating Result: " + str(ratingPrediction.getResult()))
					bestRatingResults.write("\n")
				if(ratingBest < ratingPrediction.getResult()):
					ratingBest = ratingPrediction.getResult()
					print('result')
					bestRatingResults.write("\nBest rating:")
					bestRatingResults.write("\tPreK: " + str(0))
					bestRatingResults.write("\tPostK: " + str(postK))
					bestRatingResults.write("\tRegularK: " + str(regularK))
					bestRatingResults.write("\tPoint exponent: " + str(pointExponent))
					bestRatingResults.write("\tppg Result: " + str(ppgPrediction.getResult()))
					bestRatingResults.write("\trating Result: " + str(ratingPrediction.getResult()))
					bestRatingResults.write("\n")
	bestRatingResults.close()
	bestRatingResults = open('backtesting' + str(i) + '.txt' , 'w')
	print(time.time() - startTime)
	startTime = time.time()
	print(i)
