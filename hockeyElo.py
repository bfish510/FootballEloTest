from EloClass import Elo
import time

accuracy = 0

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

for i in range(10, 50):
	dataFile = open('hockeyData.txt', 'r')
	elo = Elo()
	ratingPrediction = Prediction()
	gameNum = 0
	kFactor = i

	for line in dataFile:
		gameNum += 1
		(homeTeam, homeScore, awayTeam, awayScore) = line.split(',')
		homeRating = elo.getRating(homeTeam)
		awayRating = elo.getRating(awayTeam)
		hS = int(homeScore)
		awayS = int(awayScore)
		if(gameNum > 100000):
			if(homeRating > awayRating):
				ratingPrediction.addPrediction(homeTeam, awayTeam, gameNum, homeTeam)
			else:
				ratingPrediction.addPrediction(homeTeam, awayTeam, gameNum, awayTeam)
			if(hS > awayS):
				ratingPrediction.matchResult(homeTeam, awayTeam, gameNum,homeTeam)
			else:
				ratingPrediction.matchResult(homeTeam, awayTeam, gameNum, awayTeam)
		elo.matchResults(homeTeam, int(homeScore), awayTeam, int(awayScore), kFactor)
	dataFile.close()
	#elo.printElo()
	print("" + str(i) + "\n")
	if(ratingPrediction.getResult() > accuracy):
		accuracy = ratingPrediction.getResult()
		print("KFactor: " + str(kFactor) + "\nRating: " + str(ratingPrediction.getResult()))
	print(gameNum)