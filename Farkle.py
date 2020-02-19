# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 22:45:39 2018

@author: Blake Eakin

TODO:
	-Change it so that players get passed a ScoreTracker instance to get a more 
	complete picture of the game state.
"""

import random

class mainInter :
	"""The main interface between the user and the game itself
		"""
	def __init__ (self) :
		self.farkle = FarkleGame(self.playerQuery(), self.getRounds())
		self.showResults()

	def playerQuery(self) :
		players = ()
		i = input("What players do you want to play against each other? \nOptions:\nRSKY - AI with Risky Strategy\nCONS - AI with Conservative Strategy\nBASE - For you to play\nD - Done choosing\n")
		while( i is not "D" ) :
			players = players + (PlayerGenerator().getPlayerInstance(i),)
			i = input(" ")
			
		return players
	
	def getRounds(self) :
		return int(input("How many iterations do you want to perform? : "))
	
	def showResults(self) :
		self.farkle.playGames()
		game_results = self.farkle.getAllWins()
		for i in game_results :
			print (str(i) + " won " + str(game_results[i]) + " games.")

class FarkleGame :
	
	def __init__(self, player_profiles, number_of_rounds) :
		self.players = player_profiles
		self.rounds_played = 0
		self.iterations = number_of_rounds
		self.player_wins = {}
		#in the future implement some sort of game result object to hold the wins instead of a dict
		for i in range(self.getNumberOfPlayers()):
			self.player_wins[self.getPlayer(i).getID()]=0
		
	def getNumberOfPlayers(self) :
		return len(self.players)
	
	def getAllPlayers(self) :
		return self.players
	
	def getPlayer(self, player_number) :
		return self.players[player_number-1]
	
	def getNumberOfIterations(self) :
		return self.iterations
	
	def updatePlayerWins(self,player_id) :
		self.player_wins[player_id] = self.player_wins[player_id] + 1
		
	def getPlayerWins(self, player_id) :
		return self.player_wins[player_id]
	
	def getAllWins(self) :
		return self.player_wins
	
	def playGames(self) :
		for i in range(self.getNumberOfIterations()) :
			self.updatePlayerWins(self.gameResult(self.getAllPlayers()))
	
	def gameResult(self, set_of_players) :
		return FarkleRound(set_of_players).play()

		
class FarkleRound :
	
	def __init__(self, players):
		self.roller = FarkleRoller()
		self.all_players = players
		self.curr_scorecard = ScoreTracker(self.getNumberOfPlayers())
		self.winning_score = 4000
	
	def getNumberOfPlayers(self) :
		return len(self.all_players)
	
	def play(self) :
		"""Cycles through each player, on each player's turn it cycles through a series
		of rolls for that player, skips and returns current score to 0 if that
		player busts, updates the player's score if the player doesn't bust.
		Checks if the player's score is 2000 or above at end of round and 
		returns that player's ID as the winner if that is the case"""
		winner = ""
		while (winner == "") :
			for i in range(self.getNumberOfPlayers()):
				die_to_roll = 6
				curr_player = self.getAPlayer(i-1)
				current_player_score = self.curr_scorecard.getScore(i)
				player_response = curr_player.rollResponse(self.getARoll(die_to_roll), current_player_score)
				current_round_score = self.getScore(player_response.getHolding())
				while(not player_response.willPass()) :
					die_to_roll = die_to_roll - player_response.getAmtHolding()
					if die_to_roll == 0 :
						die_to_roll = 6
						player_response = curr_player.rollResponse(self.getARoll(die_to_roll), current_player_score+current_round_score)
					else :
						player_response = curr_player.rollResponse(self.getARoll(die_to_roll), current_player_score+current_round_score)
					if player_response.wasABust():
						current_round_score = 0
						break
					current_round_score = current_round_score + self.getScore(player_response.getHolding())
				self.curr_scorecard.updateScore(i, current_round_score)
				if self.curr_scorecard.getScore(i) >= self.winning_score:
					winner = curr_player.getID()
		return winner
	
	def getAPlayer(self, play_num) :
		return self.all_players[play_num]
	
	def getARoll(self, num_of_die) :
		return self.roller.roll(num_of_die)
	
	def getScore(self, subset) :
		"""returns an interpreted score based
		on the rules of Farkle. Takes a tuple of ints, returns an int.
		-In the future extend to allow simple change to different scoring variations"""
		numbers_present = ()
		running_score = 0 
		for i in subset:
			if i not in numbers_present :
				numbers_present = numbers_present + (i,)
		for i in numbers_present :
			count = subset.count(i)
			if i == 1 :
				if count == 3 :
					running_score = running_score + 1000
				else :
					running_score = running_score + 100 * count
			elif i == 5 :
				if count == 3 :
					running_score = running_score + 500
				else :
					running_score = running_score + 50 * count
			else :
				if count == 3 :
					running_score = running_score + i * 100
		
		return running_score
			
			

class FarkleRoller :
	"""Controls the rolls for the game."""
	def __init__(self) :
		self.roll_set = ()

	def roll(self, num_of_die) :
		self.roll_set = ()
		for i in range(num_of_die) :
			self.roll_set = self.roll_set + (random.randint(1,6),)
		return FarkleRoll(self.roll_set)
	
class FarkleRoll :
	"""Holds values for a roll and has methods to interpret information about that roll"""
	def __init__(self, die_rolls):
		self.roll = die_rolls
		self.triples = self._triplesSearch()
		
	def __iter__(self) :
		return iter(self.roll)
	
	def __str__(self) :
		strang = ""
		for i in iter(self.roll) :
			strang = strang + str(i)
		return strang
		
	def isABust(self) :
		#Cycles through every number in the roll, if it isn't a 1 or 5 or a triple, returns False
		for i in self.roll :
			if i == 1 or i == 5 :
				return False
			elif not len(self.triples) == 0:
				return False
		return True
	
	def oneCount(self) :
		count = 0 
		for i in self.roll :
			if i == 1 :
				count = count + 1
		return count
	
	def fiveCount(self) :
		count = 0 
		for i in self.roll :
			if i == 5 :
				count = count + 1
		return count
		
	def rollSize(self) :
		return len(self.roll)
	
	def getTriples(self) :
		return self.triples
	
	def _triplesSearch(self) :
		trips = ()
		
		if self.rollSize() < 3 :
			return ()
		else:
			for i in self.roll :
				if self.roll.count(i) == 3 :
					trips = trips + (i,)
			return trips

class ScoreTracker :
	"""Keeps a running scorecard for the current game iteration"""
	def __init__(self, num_players) :
		self.number_of_players = num_players
		self.scorecard = {}
		for i in range(self.number_of_players) :
			self.scorecard[i] = 0
			
	def updateScore(self, player_num, points) :
		self.scorecard[player_num] = self.scorecard[player_num] + points
		
	def getScore(self, player_num) :
		return self.scorecard[player_num]
	
class Decision :
	
	def __init__ (self, to_hold = (), will_pass=False, busted = False) :
		self.holding = to_hold
		self.passing = will_pass
		self.bust = busted
	
	def getHolding(self) :
		"""Returns the tuple of die deciding to be held"""
		return self.holding
	
	def getAmtHolding(self) :
		return len(self.holding)
	
	def onesHolding(self) :
		return self.holding.count(1)
	
	def fivesHolding(self) :
		return self.holding.count(5)
	
	def addToHolding(self, addition, times=1) :
		for i in range(times) :
			self.holding = self.holding + (addition,)
		
	def setPassing(self, pass_or) :
		self.passing = pass_or
		
	def setBust(self, bust_or) :
		self.bust = bust_or
	
	def willPass(self) :
		return self.passing
	
	def wasABust(self) :
		return self.bust
	
	
class Player :
	"""Player class prototype. Will be inherited to describe different types
	of players with varying strategies."""
	def __init__(self, player_ID = "BASE") :
		self.player_ID = player_ID
		
	def rollResponse(self, roll, curr_score) :
		"""Takes in a FarkleRoll instance and the current score for the round
		   and returns a Decision object that holds a tuple of the die the 
		   player would hold and whether or not the player would pass
		   
		   currently takes input from the console from a user for testing"""
		if roll.isABust() :
			return Decision((),False, True)
		else :
			print ("Your roll: ")
			for i in roll :
				print(str(i))
			print("Your score: {}".format(curr_score))
			to_hold = input("What will you do? : ")
			holding_tuple = ()
			passing = False
			for i in to_hold :
				if i in ("1","2","3","4","5","6") :
					holding_tuple = holding_tuple + (int(i),)
				elif i.upper() == "P" :
					passing = True
			return Decision(holding_tuple,passing)
			   
	 
	def getID(self) :
		return self.player_ID
	
class ConservativePlayer(Player) :
	def __init__(self) :
		super().__init__("CONS")
	
	def rollResponse(self, roll, curr_score) :
		player_decision = Decision()
		if roll.isABust() :
			player_decision.setBust(True)
		else :
			if roll.rollSize() > 4 :
				if len(roll.getTriples()) > 0 :
					for i in roll.getTriples() :
						if i == 1 or i > 3 or ( i <= 3 and roll.oneCount() == 0 and roll.fiveCount() == 0 ):
							player_decision.addToHolding(i)
						elif roll.oneCount() > 0 :
							player_decision.addToHolding(1)
						elif roll.fiveCount() > 0 :
							player_decision.addToHolding(5)
						else :
							player_decision.setPassing(True)
				else :
					if roll.oneCount() > 0 :
						player_decision.addToHolding(1)
					elif roll.fiveCount() > 0 :
						player_decision.addToHolding(5)
			else :
				player_decision.addToHolding((1,)*roll.oneCount()+(5,)*roll.fiveCount())
				player_decision.setPassing(True)
		return player_decision
			
	
class RiskyPlayer(Player) :
	
	def __init__(self) :
		super().__init__("RSKY")
		
	def rollResponse(self, roll, curr_score) :
		player_decision = Decision()
		if roll.isABust() :
			player_decision.setBust(True)
		else :
			if roll.rollSize() > 3 :
				if len(roll.getTriples()) > 0 :
					for i in roll.getTriples() :
						player_decision.addToHolding(i)
				if (roll.oneCount() - player_decision.onesHolding() > 0) or (roll.fiveCount() - player_decision.fivesHolding() > 0) :
					player_decision.addToHolding((1,)*(roll.oneCount() - player_decision.onesHolding()) + (5,)*(roll.fiveCount() - player_decision.fivesHolding()))
			else : 
				if len(roll.getTriples()) > 0 :
					for i in roll.getTriples() :
						player_decision.addToHolding(i)
				elif roll.oneCount() + roll.fiveCount() == 3 :
					player_decision.addToHolding((1,)*roll.oneCount() + (5,)*roll.fiveCount())
				else :
					player_decision.addToHolding((1,)*roll.oneCount() + (5,)*roll.fiveCount())
					player_decision.setPassing(True)
					
		return player_decision
	
class PlayerGenerator :
	"""Generates instances of different Player objects, usually based on codes
		for different player profiles."""
	BASE = "BASE"
	CONS = "CONS"
	RSKY = "RSKY"
		
	def __init__(self):
			pass
		
	def getPlayerInstance(self, code) :
			"""Returns an instance of a particular type of Player object based
			on a player ID"""
			if code == self.BASE :
				return Player()
			elif code == self.CONS :
				return ConservativePlayer()
			elif code == self.RSKY :
				return RiskyPlayer()
