class Elo:
	teams = {}
	DEFAULT_RATING = 1500

	def printElo(self):
		for team in self.teams:
			print(str(team) + " " + str(self.teams[team]))
	
	def getRating(self, team):
		return self.teams[team]

	#should be used for testing only
	def setRating(self, team, rating):
		self.teams[team] = rating

	def getTeamList(self):
		return self.teams.keys()

	def addTeams(self, teamList):
		for team in teamList:
			self.addTeam(team)

	def addTeam(self, teamName):		
		self.teams[teamName] = self.DEFAULT_RATING

	def computeNewRatings(self, playerRating, predictedScore, actualScore, kFactor):
		return (playerRating + (kFactor * (actualScore - predictedScore)))

	def computeEstimatedResult(self, team, opponent):
		if(team not in self.teams):
			self.addTeam(team)
		if(opponent not in self.teams):
			self.addTeam(opponent)
		exponent = (self.teams[opponent] - self.teams[team])/400
		value = 1/(1 + (10 ** exponent))
		return value

	def matchResults(self, team1Name, team1ActualScore, team2Name, team2ActualScore, kFactor):
		if(team1Name not in self.teams):
			self.addTeam(team1Name)
		if(team2Name not in self.teams):
			self.addTeam(team2Name)
		#the total of the two scores must add to 1 so we make them a ratio of the total points scored
		denom = team1ActualScore + team2ActualScore
		if(denom == 0):
			team1ActualScorePercent = .5
			team2ActualScorePercent = .5
		else:
			team1ActualScorePercent = team1ActualScore / denom
			team2ActualScorePercent = team2ActualScore / denom

		#get their predicted scores
		team1Predicted = self.computeEstimatedResult(team1Name, team2Name)
		team2Predicted = 1 - team1Predicted

		#update scores
		self.teams[team1Name] = self.computeNewRatings(self.teams[team1Name], team1Predicted, team1ActualScorePercent, kFactor)
		self.teams[team2Name] = self.computeNewRatings(self.teams[team2Name], team2Predicted, team2ActualScorePercent, kFactor)
		
