# -*- coding: UTF-8 -*-

#Main server file

import os
import json
from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource
import jaconv

from models import db, User, Report, Kanji

from datetime import datetime

#import win_unicode_console
#win_unicode_console.enable()

app = Flask(__name__)
api = Api(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'server.db')

app.config.from_object(__name__)
app.config.from_envvar('SERVER_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

parser = reqparse.RequestParser()
parser.add_argument('score', type=int)
parser.add_argument('dif', type=int)
parser.add_argument('total', type=int)
parser.add_argument('kanji', type=str)
parser.add_argument('romaji', type=str)
parser.add_argument('fname', type=str)
parser.add_argument('lname', type=str)
parser.add_argument('email', type=str)
parser.add_argument('userID', type=str)
parser.add_argument('pass', type=str)
parser.add_argument('pass2', type=str)
parser.add_argument('old_pass', type=str)

def get_user_id(username):
	rv = User.query.filter_by(userID=username).first()
	return rv.userID if rv else None

@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	add_data()
	#db.session.commit()
	print("Initialized the database")

@app.before_request
def before_request():
	#Check if a user is in session
	g.user = None
	if 'userID' in session:
		g.user = User.query.filter_by(userID=session['userID']).first()

@app.route("/", methods = ['GET', 'POST'])
def rootpage():
	#Check if the user is already in session
	if g.user:
		return redirect(url_for('home', userID = g.user.userID))
	error = None
	if request.method == 'POST':
		#Check if a username was entered- extra precautions
		if request.form['name'] is None:
			error = "Please enter a username"
		else:
			#Check for valid username
			name = User.query.filter_by(userID = request.form['name']).first()
			if name is None:
				error = "Invalid credentials"
			#Check for a password
			elif not request.form['pass']:
				error = "Please enter a password"
			#Check for correct password
			elif name.validate_password(request.form['pass']):
				session['userID'] = name.userID
				flash("You have been logged in")
				return redirect(url_for('home', userID = name.userID))
			else:
				error = "Invalid credentials"
	
	return render_template("login.html")

@app.route("/<userID>/", methods=['GET', 'POST'])
def home(userID):
	if g.user:
		#Make sure this is the correct user
		if userID == g.user.userID:
			error = None
			if request.method == "POST":
				print("Nope")
			return render_template('home.html')
		else:
			abort(401)
	#If no one is in session, redirect to the root page
	else:
		return redirect(url_for('rootpage'))


#Route to the signup page, redirect to profile page if in session	
@app.route("/sign_up/", methods = ['GET'])
def sign_up():
	if g.user:
		return redirect(url_for('home', userID=g.user.userID))
	error = None
	return render_template("signup.html", error = error)

#Logout
@app.route("/log_out/")
def logout():
	if g.user:
		session.pop('userID', None)
		return redirect(url_for('rootpage'))
	#If no one is in session, redirect to the root page
	else:
		return redirect(url_for('rootpage'))

#Change the user's password
@app.route("/change_pass/", methods = ['GET', 'POST'])
def change_pass():
	if g.user:
		if request.method == 'POST':
			data = parser.parse_args()
			if data['pass'] is None:
				return json.dumps("No password given"), 400
			elif data['pass2'] is None:
				return json.dumps("Restate password"), 400
			elif data['old_pass'] is None:
				return json.dumps("Type in your old password"), 400
			elif not g.user.validate_password(data['old_pass']):
				return json.dumps("Old password incorrect"), 400
			elif data['pass'] == data['pass2']:
				g.user.reset_password(data['pass'])
				db.session.commit()
				return json.dumps("Success"), 200
			else:
				return json.dumps("New passwords do not match"), 400

		else:
			return render_template("change_pass.html")
	return redirect(url_for('rootpage'))

#Change a user's email
@app.route("/change_email/", methods = ['POST'])
def change_email():
	if g.user:
		data = parser.parse_args()
		if data['email']:
			g.user.new_email(data['email'])
			db.session.commit()
			return json.dumps("Success"), 200
		else:
			return json.dumps("No new email given"), 400
	else:
		return json.dumps("Unauthorized action"), 401

#Get the kanji for a specific category
'''
@app.route("/kanji/", methods = ['POST'])
def get_kanji():
	if g.user:
		#Get the grade level at which the user wants to get kanji from
		grade = request.json
		print(str(grade))
		results = Kanji.query.filter_by(difficulty = grade).all()

		#Format the results for sending to the user
		rv = []
		for i in range(0, len(results)):
			string = "{}:{}".format(results[i].kanji, results[i].romaji)
			rv.append(string)

		print(str(rv))
		return json.dumps(rv)

	else:
		abort(401)
'''

#Lets make this restful
#Restful Kanji Resource
class R_Kanji(Resource):
	#Return all kanji to the user
	def get(self):
		if g.user:
			results = Kanji.query.all()

			#Format for sending back to user
			rv = []
			for i in range(0, len(results)):
				rv.append({"kanji":results[i].kanji, "romaji":results[i].romaji, "dif":results[i].difficulty})
			#print(rv)
			return json.dumps(rv), 200

		return json.dumps('Unauthorized'), 401

	#Post new a new kanji combination to the database
	def post(self):
		if g.user:
			data = parser.parse_args()

			#Check for argument errors
			if not data['dif'] or not data['kanji'] or not data['romaji']:
				return json.dumps("Not enough arguments"), 400

			kanji = data['kanji']
			romaji = data['romaji']
			difficulty = data['dif']

			#Catch any possible input errors
			try:
				db.session.add(Kanji(kanji, romaji, difficulty))
				db.session.commit()
			except:
				return json.dumps("Bad request"), 400

		return json.dumps("Unauthorized"), 401

#Restful Report Resource
class R_Report(Resource):
	#Get all reports for a user
	def get(self):
		if g.user:
			results = Report.query.filter_by(userID = g.user.userID).all()
			rv = []
			for i in range(0, len(results)):
				rv.append({"date":str(results[i].date), "dif":results[i].difficulty, "total":results[i].num_total, "score":results[i].num_correct})
			return json.dumps(rv), 200
		return json.dumps("Unauthorized"), 401

	#Post a new report	
	def post(self):
		if g.user:
			#Parse the request
			#print("Got data")
			data = parser.parse_args()

			#Check for argument errors
			if not data['dif'] or not data['score'] or not data['total']:
				return json.dumps("Not enough arguments"), 400
			#print("Data is good")
			difficulty = data['dif']
			num_correct = data['score']
			num_total = data['total']

			#Add the report to the user
			try:
				db.session.add(Report(g.user.userID, difficulty, num_correct, num_total, datetime.now()))
				db.session.commit()
			except:
				return json.dumps("Bad request"), 400

			return json.dumps("Resource created"), 201
		return json.dumps("Unauthorized"), 401

class R_User(Resource):
	#Get all of the information about the current user
	def get(self):
		if g.user:
			rv = []
			rv.append({"userID":g.user.userID, "fname":g.user.fname, "lname":g.user.lname, "email":g.user.email})
			return json.dumps(rv), 200
		else:
			return json.dumps("Unauthorized"), 401

	#Sign up a new user
	def post(self):
		if not g.user:
			error = None
			data = parser.parse_args()
			#Check for username
			if not data['userID']:
				error = "Please enter a username"
			#Check for a password
			elif not data['pass']:
				error = "Please enter a password"
			#Check for a reentered password
			elif not data['pass2']:
				error = "Please reenter your password"
			#Check the passwords match
			elif data['pass'] != data['pass2']:
				error = "Passwords do not match"
			#Check for a first name
			elif not data['fname']:
				error = "No first name given"
			#Check for a last name
			elif not data['lname']:
				error = "No last name given"
			#Check for an email
			elif not data['email']:
				error = "No email given"
			#Check for taken username
			elif get_user_id(data['userID']) is None:
				#Catch any possible errors
				try:
					db.session.add(User(data['userID'], data['pass'], data['fname'], data['lname'], data['email']))
					db.session.commit()
				except:
					return json.dumps("Bad request"), 400

				return json.dumps("success"), 201
			else:
				error = "That username is already taken"

			return json.dumps(error), 400
		else:
			return json.dumps("Unauthorized action"), 401

		

api.add_resource(R_Kanji, "/kanji/")
api.add_resource(R_Report, "/report/")
api.add_resource(R_User, "/user/")

def add_data():
	db.session.add(Kanji(u'海岸','kaigan', 1))
	db.session.add(Kanji(u'学期','gakki', 1))
	db.session.add(Kanji(u'時期','jiki', 1))
	db.session.add(Kanji(u'期間','kikan', 1))
	db.session.add(Kanji(u'期待','kitai', 1))
	db.session.add(Kanji(u'期末','kimatsu', 1))
	db.session.add(Kanji(u'上級','joukyuu', 1))
	db.session.add(Kanji(u'中級','chukyuu', 1))
	db.session.add(Kanji(u'初級','shokyuu', 1))
	db.session.add(Kanji(u'野球','yakyuu', 1))
	db.session.add(Kanji(u'結局','kekkyoku', 1))
	db.session.add(Kanji(u'苦手','nigate', 1))
	db.session.add(Kanji(u'ー県','ken', 1))
	db.session.add(Kanji(u'金庫','kinko', 1))
	db.session.add(Kanji(u'不幸','fukou', 1))
	db.session.add(Kanji(u'大根','daikon', 1))
	db.session.add(Kanji(u'屋根','yane', 1))
	db.session.add(Kanji(u'球','tama', 1))
	db.session.add(Kanji(u'苦しい','kurushii', 1))
	db.session.add(Kanji(u'苦しむ','kurushimu', 1))
	db.session.add(Kanji(u'苦い','nigai', 1))
	db.session.add(Kanji(u'苦る','nigaru', 1))
	db.session.add(Kanji(u'血','ketsu', 1))
	db.session.add(Kanji(u'湖','mizuumi', 1))
	db.session.add(Kanji(u'幸い','saiwai', 1))
	db.session.add(Kanji(u'幸せ','shiawase', 1))
	db.session.add(Kanji(u'祭る','matsuru', 1))
	db.session.add(Kanji(u'祭り','matsuri', 1))
	db.session.add(Kanji(u'皿','sara', 1))
	#Commented out for now. Will fill in with more later
	'''
	db.session.add(Kanji(u'','shinu', ))
	db.session.add(Kanji(u'','hisshi', ))
	db.session.add(Kanji(u'','yubi', ))
	db.session.add(Kanji(u'','sasu', ))
	db.session.add(Kanji(u'','utsusu', ))
	db.session.add(Kanji(u'','utsuru', ))
	db.session.add(Kanji(u'','owaru', ))
	db.session.add(Kanji(u'','oeru', ))
	db.session.add(Kanji(u'','mezasu', ))
	db.session.add(Kanji(u'','shuuten', ))
	db.session.add(Kanji(u'','akinau', ))
	db.session.add(Kanji(u'','shouten', ))
	db.session.add(Kanji(u'','shouhin', ))
	db.session.add(Kanji(u'','binshou', ))
	'''
	#Hiragana
	db.session.add(Kanji(u'あ','a', 0))
	db.session.add(Kanji(u'い','i', 0))
	db.session.add(Kanji(u'う','u', 0))
	db.session.add(Kanji(u'え','e', 0))
	db.session.add(Kanji(u'お','o', 0))
	db.session.add(Kanji(u'か','ka', 0))
	db.session.add(Kanji(u'き','ki', 0))
	db.session.add(Kanji(u'く','ku', 0))
	db.session.add(Kanji(u'け','ke',0 ))
	db.session.add(Kanji(u'こ','ko', 0))
	db.session.add(Kanji(u'が','ga', 0))
	db.session.add(Kanji(u'ぎ','gi', 0))
	db.session.add(Kanji(u'ぐ','gu', 0))
	db.session.add(Kanji(u'げ','ge', 0))
	db.session.add(Kanji(u'ご','go', 0))
	db.session.add(Kanji(u'さ','sa', 0))
	db.session.add(Kanji(u'し','shi', 0))
	db.session.add(Kanji(u'す','su', 0))
	db.session.add(Kanji(u'せ','se', 0))
	db.session.add(Kanji(u'そ','so', 0))
	db.session.add(Kanji(u'ざ','za', 0))
	db.session.add(Kanji(u'じ','ji', 0))
	db.session.add(Kanji(u'じゅ','ju', 0))
	db.session.add(Kanji(u'ぜ','ze', 0))
	db.session.add(Kanji(u'ぞ','zo', 0))
	db.session.add(Kanji(u'た','ta', 0))
	db.session.add(Kanji(u'ち','chi', 0))
	db.session.add(Kanji(u'つ','tsu', 0))
	db.session.add(Kanji(u'て','te', 0))
	db.session.add(Kanji(u'と','to', 0))
	db.session.add(Kanji(u'だ','da', 0))
	db.session.add(Kanji(u'で','de', 0))
	db.session.add(Kanji(u'ど','do', 0))
	db.session.add(Kanji(u'な','na', 0))
	db.session.add(Kanji(u'に','ni', 0))
	db.session.add(Kanji(u'ね','ne', 0))
	db.session.add(Kanji(u'の','no', 0))
	db.session.add(Kanji(u'は','ha', 0))
	db.session.add(Kanji(u'ひ','hi', 0))
	db.session.add(Kanji(u'ふ','fu', 0))
	db.session.add(Kanji(u'へ','he', 0))
	db.session.add(Kanji(u'ほ','ho', 0))
	db.session.add(Kanji(u'ば','ba', 0))
	db.session.add(Kanji(u'び','bi', 0))
	db.session.add(Kanji(u'ぶ','bu', 0))
	db.session.add(Kanji(u'べ','be', 0))
	db.session.add(Kanji(u'ぼ','bo', 0))
	db.session.add(Kanji(u'ぱ','pa', 0))
	db.session.add(Kanji(u'ぴ','pi', 0))
	db.session.add(Kanji(u'ぷ','pu', 0))
	db.session.add(Kanji(u'ぺ','pe', 0))
	db.session.add(Kanji(u'ぽ','po', 0))
	db.session.add(Kanji(u'ま','ma', 0))
	db.session.add(Kanji(u'み','mi', 0))
	db.session.add(Kanji(u'む','mu', 0))
	db.session.add(Kanji(u'め','me', 0))
	db.session.add(Kanji(u'も','mo', 0))
	db.session.add(Kanji(u'や','ya', 0))
	db.session.add(Kanji(u'ゆ','yu', 0))
	db.session.add(Kanji(u'よ','yo', 0))
	db.session.add(Kanji(u'ら','ra', 0))
	db.session.add(Kanji(u'り','ri', 0))
	db.session.add(Kanji(u'る','ru', 0))
	db.session.add(Kanji(u'れ','re', 0))
	db.session.add(Kanji(u'ろ','ro', 0))
	db.session.add(Kanji(u'わ','wa', 0))
	db.session.add(Kanji(u'を','wo', 0))
	db.session.add(Kanji(u'ん','n', 0))
	db.session.add(Kanji(u'じゃ','ja', 0))
	db.session.add(Kanji(u'じょ','jo', 0))
	#Katakana
	db.session.add(Kanji(u'ア','a', -1))
	db.session.add(Kanji(u'イ','i', -1))
	db.session.add(Kanji(u'ウ','u', -1))
	db.session.add(Kanji(u'エ','e', -1))
	db.session.add(Kanji(u'オ','o', -1))
	db.session.add(Kanji(u'カ','ka', -1))
	db.session.add(Kanji(u'キ','ki', -1))
	db.session.add(Kanji(u'ク','ku', -1))
	db.session.add(Kanji(u'ケ','ke', -1))
	db.session.add(Kanji(u'コ','ko', -1))
	db.session.add(Kanji(u'ガ','ga', -1))
	db.session.add(Kanji(u'ギ','gi', -1))
	db.session.add(Kanji(u'グ','gu', -1))
	db.session.add(Kanji(u'ゲ','ge', -1))
	db.session.add(Kanji(u'ゴ','go', -1))
	db.session.add(Kanji(u'サ','sa', -1))
	db.session.add(Kanji(u'シ','shi', -1))
	db.session.add(Kanji(u'ス','su', -1))
	db.session.add(Kanji(u'セ','se', -1))
	db.session.add(Kanji(u'ソ','so', -1))
	db.session.add(Kanji(u'ザ','za', -1))
	db.session.add(Kanji(u'ジ','ji', -1))
	db.session.add(Kanji(u'ジュ','ju', -1))
	db.session.add(Kanji(u'ゼ','ze', -1))
	db.session.add(Kanji(u'ぞ','zo', -1))
	db.session.add(Kanji(u'タ','ta', -1))
	db.session.add(Kanji(u'チ','chi', -1))
	db.session.add(Kanji(u'ツ','tsu', -1))
	db.session.add(Kanji(u'テ','te', -1))
	db.session.add(Kanji(u'ト','to', -1))
	db.session.add(Kanji(u'ダ','da', -1))
	db.session.add(Kanji(u'デ','de', -1))
	db.session.add(Kanji(u'ド','do', -1))
	db.session.add(Kanji(u'ナ','na', -1))
	db.session.add(Kanji(u'ニ','ni', -1))
	db.session.add(Kanji(u'ネ','ne', -1))
	db.session.add(Kanji(u'ノ','no', -1))
	db.session.add(Kanji(u'ハ','ha', -1))
	db.session.add(Kanji(u'ﾋ','hi', -1))
	db.session.add(Kanji(u'フ','fu', -1))
	db.session.add(Kanji(u'ヘ','he', -1))
	db.session.add(Kanji(u'ホ','ho', -1))
	db.session.add(Kanji(u'バ','ba', -1))
	db.session.add(Kanji(u'ビ','bi', -1))
	db.session.add(Kanji(u'ブ','bu', -1))
	db.session.add(Kanji(u'ベ','be', -1))
	db.session.add(Kanji(u'ボ','bo', -1))
	db.session.add(Kanji(u'パ','pa', -1))
	db.session.add(Kanji(u'ピ','pi', -1))
	db.session.add(Kanji(u'プ','pu', -1))
	db.session.add(Kanji(u'ペ','pe', -1))
	db.session.add(Kanji(u'ポ','po', -1))
	db.session.add(Kanji(u'マ','ma', -1))
	db.session.add(Kanji(u'ミ','mi', -1))
	db.session.add(Kanji(u'ム','mu', -1))
	db.session.add(Kanji(u'メ','me', -1))
	db.session.add(Kanji(u'モ','mo', -1))
	db.session.add(Kanji(u'ヤ','ya', -1))
	db.session.add(Kanji(u'ユ','yu', -1))
	db.session.add(Kanji(u'ヨ','yo', -1))
	db.session.add(Kanji(u'ラ','ra', -1))
	db.session.add(Kanji(u'リ','ri', -1))
	db.session.add(Kanji(u'ル','ru', -1))
	db.session.add(Kanji(u'レ','re', -1))
	db.session.add(Kanji(u'ロ','ro', -1))
	db.session.add(Kanji(u'ワ','wa', -1))
	db.session.add(Kanji(u'ヲ','wo', -1))
	db.session.add(Kanji(u'ン','n', -1))
	db.session.add(Kanji(u'ジャ','ja', -1))
	db.session.add(Kanji(u'ジョ','jo', -1))
	'''
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	db.session.add(Kanji(u'','', ))
	'''
	db.session.commit()

app.secret_key = "Terrible key"