def main():
	teama = 1600
	teamb = 1200
	print("Team A Rating: " + str(teama))
	print("Team B Rating: " + str(teamb))
	eSA = computeEstimatedResult(teama, teamb)
	eSB = computeEstimatedResult(teamb, teama)
	print("Team A Estimated Score: " + str(eSA))
	print("Team B Estimated Score: " + str(eSB))
	aSA = 16
	aSB = 7
	print("Team A Actual Score: " + str(aSA/(aSA + aSB)))
	print("Team B Actual Score: " + str(aSB/(aSA + aSB)))
	teama = computeNewRatings(teama, eSA, (aSA/(aSA + aSB)))
	teamb = computeNewRatings(teamb, eSB, (aSB/(aSA + aSB)))
	print("Team A New Rating: " + str(teama))
	print("Team B New Rating: " + str(teamb))


def computeEstimatedResult(team1, team2):
	exponent = (team2 - team1)/400
	value = 1/(1 + (10 ** exponent))
	return value

def computeNewRatings(team1, predictedScore, actualScore, isPreseason):
	skillFactor = 16
	if(isPreseason):
		skillFactor = 32
	value = team1 + (skillFactor * (actualScore - predictedScore))
	return value

def initData():
	#teams
	teams = ['Bears','Cardinals','Packers','Giants','Lions','Redskins','Steelers','Eagles','Rams','49ers','Browns','Colts','Cowboys','Raiders','Patriots','Titans','Broncos','Chargers','Jets','Chiefs','Bills','Vikings','Dolphins','Falcons','Saints','Bengals','Seahawks','Buccaneers','Jaguars','Panthers','Ravens','Texans']
	
	for team in teams:
		teamRating[team] = 1500

	#2013 preseason week 1

	games = []
	games.append(Game('Ravens', 'Buccaneers', [0, 24, 7, 13], [3,10,3,0], True))

	#compute ratings
	for game in games:
		#add a check that a game is in the key set of the ratings maps
		for i in range(0, game.numQuaters()):
			print("\nRating for the " + game.homeTeam + " is: " + str(teamRating[game.homeTeam]))
			print("Rating for the " + game.awayTeam + " is: " + str(teamRating[game.awayTeam]))
			eSHome = computeEstimatedResult(teamRating[game.homeTeam], teamRating[game.awayTeam])
			eSAway = computeEstimatedResult(teamRating[game.awayTeam], teamRating[game.homeTeam])
			teamRating[game.homeTeam] = computeNewRatings(teamRating[game.homeTeam], eSHome, (game.homeScore[i]/(game.awayScore[i] + game.homeScore[i])), game.isPreseason)
			teamRating[game.awayTeam] = computeNewRatings(teamRating[game.awayTeam], eSAway, (game.awayScore[i]/(game.awayScore[i] + game.homeScore[i])), game.isPreseason)
			print("\nNew Rating for the " + game.homeTeam + " is: " + str(teamRating[game.homeTeam]))
			print("New Rating for the " + game.awayTeam + " is: " + str(teamRating[game.awayTeam]))
			





class Game:
	def __init__(self, awayTeam, homeTeam, awayScore, homeScore, preseason):
		self.awayTeam = awayTeam
		self.homeTeam = homeTeam
		self.awayScore = awayScore
		self.homeScore = homeScore
		self.preseason = preseason

	def numQuaters(self):
		return len(self.awayScore)

	def isPreseason(self):
		return self.preseason


teamRating = {}
initData()
