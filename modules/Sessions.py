'''
Session handler for each users in WordleBattle. This supports
both duel battle and singleplayer.

By: Hubert F. Espinola I
'''
from Wordle import Wordle
import random
import string


# Handles user and their specified wordle object
# the 'key' also acts as user 'token' which identifies
# the user and the game he/she's playing.
class UserHandler:
	def __init__(self, fpath : str, numOfWordsToGuess : int) -> None:
		self.fpath = fpath
		self.numOfWordsToGuess = numOfWordsToGuess
		self.userMap = {'key' : Wordle(fpath, numOfWordsToGuess, 5)}

	# generates key available for the session
	def generateKey(self) -> str:
		keyGen = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
		if (keyGen not in self.userMap):
			return keyGen
		return self.generateKey()

	# retrieves the wordle object of the specified user
	def getWordle(self, token : str) -> Wordle:
		if (token in self.userMap):
			return self.userMap[token]
		return None

	# registers the token and maps on empty Wordle object
	def register(self, key : str):
		if (key not in self.userMap):
			print('KEY IS REGISTERED!')
			self.userMap[key] = Wordle(self.fpath, self.numOfWordsToGuess, 5)

		print('KEY REGISTRATION DONE')


# Interface class where you can modify on how you
# will use the guess method
# Handles the user session
class SessionHandler(UserHandler):
	def __init__(self, fpath: str, numOfWordsToGuess : int) -> None:
		super().__init__(fpath, numOfWordsToGuess)

	# checks the answer of the user
	def guess(self, key : str, answer : str) -> list:
		pass