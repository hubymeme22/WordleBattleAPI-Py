'''
WordleBattle API

By:
	Hubert F. Espinola I
	Angelika T. Amatus
'''
from flask import Flask, send_from_directory, request
import json
import sys

sys.path.append('./modules')
from SinglePlayerSession import SingleSessionHandler
from EncryptedSession import EncSession, UserDB


# database for user information
UserDatabase = UserDB()

# Session handlers
SingleSession = SingleSessionHandler('sample.txt', 4)
EncryptedSession = EncSession('sample.txt', 4)
EncryptedSession.connectLocalDB(UserDatabase)


# "factored out" process that are needed (to shorten code):
# 
def checkUserPassTokenValidity(username : str, password : str, token : str):
	return (username != None) and (password != None) and EncryptedSession.isEncTokenRegistered(token)

app = Flask(__name__)

####################
#   GET Requests   #
####################
@app.route('/')
def index():
	return 'Hello world!'

@app.route('/<path:path>')
def staticFileHandler(path):
	return send_from_directory('static_files', path)

############################
#   special GET requests   #
############################
''' Requests for session on single player '''
@app.route('/request/stoken/')
def sessionSingle():
	token = SingleSession.generateKey()
	SingleSession.register(token)

	return token

''' User guesses the answer '''
@app.route('/single/guess/<string:token>/<string:answer>')
def guessAnsSingle(token, answer):
	output = SingleSession.guess(token, answer)
	return str(output)

''' User requests for trying to solve the word again '''
@app.route('/single/try_again/<string:token>')
def tryAgain(token):
	return SingleSession.tryAgain(token)

''' User requests to scramble the set of words to solve '''
@app.route('/single/reset/<string:token>')
def resetWord(token):
	return SingleSession.reset(token)

''' User checks if the token is registered '''
@app.route('/single/isregistered/<string:token>')
def isRegistered(token):
	registered = SingleSession.isRegistered(token)
	if (registered):
		return 'yes'
	return 'no'

##############################
#   Encrypted GET Requests   #
##############################
''' Gets token for encrypted communications '''
@app.route('/encrypted/request/token')
def getEncryptedToken():
	token, P = EncryptedSession.getToken()
	return token + ':' + str(P)

#####################
#   POST Requests   #
#####################
''' Posts data for diffie hellman key exchange '''
@app.route('/encrypted/handshake/<string:token>', methods=['POST'])
def diffieHandshake(token):
	userMixedVal = request.form.get('PAQ')
	QValue = request.form.get('Q')

	if ((userMixedVal != None) and (QValue != None)):
		userMixedVal = int(userMixedVal)
		QValue = int(QValue)
		BMixed = EncryptedSession.handshake(token, userMixedVal, QValue)
		return str(BMixed)

	return 'UnknownParamError'

''' User logs in the given credentials and maps it on the token provided '''
@app.route('/encrypted/login/<string:token>', methods=['POST'])
def login(token):
	username = json.loads(request.form.get('uno'))
	password = json.loads(request.form.get('anji'))

	# convert to character and rejoin
	username = [chr(i) for i in username]
	password = [chr(i) for i in password]
	username = ''.join(username)
	password = ''.join(password)

	# checks if the field are okay and the token is registered
	if (checkUserPassTokenValidity(username, password, token)):
		key = EncryptedSession.getKey(token)

		# decrypts the credentials
		username = EncSession.decrypt(token, key, username)
		password = EncSession.decrypt(token, key, password)

		# checks if the username exists
		if (EncryptedSession.localUserDB.checkUser(username)):
			isRegistered = EncryptedSession.login(username, password, token)
			if (isRegistered): return 'successful'

	return 'unsucessful'

''' Registers the specified username and password '''
@app.route('/encrypted/register/<string:token>', methods=['POST'])
def registerUser(token):
	username = json.loads(request.form.get('uno'))
	password = json.loads(request.form.get('anji'))

	username = [chr(i) for i in username]
	password = [chr(i) for i in password]
	username = ''.join(username)
	password = ''.join(password)

	# checks if the parameters are valid and user does not exist
	if (checkUserPassTokenValidity(username, password, token)):
		# decrypts the credentials
		key = EncryptedSession.getKey(token)
		username = EncSession.decrypt(token, key, username)
		password = EncSession.decrypt(token, key, password)

		if (UserDatabase.checkUser(username)):
			return 'usererror'
		else:
			UserDatabase.register(username, password)
			return 'successful'

	return 'unsucessful'

''' An account user guesses the answer '''
@app.route('/encrypted/guess', methods=['POST'])
def encryptedGuess(token):
	userToken = request.form.get('token')

	if (EncryptedSession.isEncTokenRegistered(userToken)):
		key = EncryptedSession.getKey(userToken)
		encryptedAnswer = json.loads(request.form.get('answer'))
		encryptedAnswer = ''.join([chr(i) for i in encryptedAnswer])

		answer = EncSession.decrypt(userToken, key, encryptedAnswer)
		result = EncryptedSession.guess(userToken, answer)
		return str(result)

	return str([])

#####################
#     Main part     #
#####################
if __name__ == '__main__':
	app.debug = True
	app.run('localhost', 5050)