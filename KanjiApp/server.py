# -*- coding: UTF-8 -*-

#Main server file

import os
import json
from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource
#import jaconv

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
parser.add_argument('reason', type=str)

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

@app.route("/change_reason/", methods=['POST'])
def change_reason():
	if g.user:
		data = parser.parse_args()
		if data['reason']:
			g.user.new_reason(data['reason'])
			db.session.commit()
			return json.dumps("Success"), 200
		else:
			return json.dumps("No new reason given"), 400
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
			rv.append({"userID":g.user.userID, "fname":g.user.fname, "lname":g.user.lname, "email":g.user.email, "reason":g.user.reason})
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
			elif not data['reason']:
				error = "No reason to study given"
			#Check for taken username
			elif get_user_id(data['userID']) is None:
				#Catch any possible errors
				try:
					db.session.add(User(data['userID'], data['pass'], data['fname'], data['lname'], data['email'], data['reason']))
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
	'''
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
	#Kanji from JWL Lesson 9
	db.session.add(Kanji(u'一つ', u'ひとつ', 1))
	db.session.add(Kanji(u'一ページ', u'いちぺじ', 1))
	db.session.add(Kanji(u'一ドル', u'いちどる', 1))
	db.session.add(Kanji(u'一セント', u'いちせんと', 1))
	db.session.add(Kanji(u'二つ', u'ふたつ', 1))
	db.session.add(Kanji(u'十', u'じゅう', 1))
	db.session.add(Kanji(u'一日', u'いちにち', 1))
	db.session.add(Kanji(u'二日', u'ふつか', 1))
	db.session.add(Kanji(u'十日', u'とおか', 1))
	db.session.add(Kanji(u'二十日', u'にじゅうにち', 1))
	db.session.add(Kanji(u'七つ', u'ななつ', 1))
	db.session.add(Kanji(u'七日', u'なのか', 1))
	db.session.add(Kanji(u'八日', u'ようか', 1))
	db.session.add(Kanji(u'九つ', u'ここのつ', 1))
	db.session.add(Kanji(u'三つ', u'みつ', 1))
	db.session.add(Kanji(u'三日', u'みっか', 1))
	db.session.add(Kanji(u'分かる', u'わかる', 1))
	db.session.add(Kanji(u'一分', u'いぷん', 1))
	db.session.add(Kanji(u'六分', u'ろっぷん', 1))
	db.session.add(Kanji(u'六', u'ろく', 1))
	db.session.add(Kanji(u'五', u'ご', 1))
	db.session.add(Kanji(u'五分', u'ごふん', 1))
	db.session.add(Kanji(u'十五', u'じゅうご', 1))
	db.session.add(Kanji(u'四', u'し', 1))
	db.session.add(Kanji(u'四分', u'よんぷん', 1))
	db.session.add(Kanji(u'本', u'ほん', 1))
	db.session.add(Kanji(u'一本', u'いっぽん', 1))
	db.session.add(Kanji(u'三本', u'さんぼん', 1))
	db.session.add(Kanji(u'日本', u'ひほん', 1))
	db.session.add(Kanji(u'何日', u'なんにち', 1))
	db.session.add(Kanji(u'何', u'なに', 1))
	db.session.add(Kanji(u'何分', u'なんぷん', 1))
	db.session.add(Kanji(u'何本', u'なんぼん', 1))
	db.session.add(Kanji(u'下さい', u'ください', 1))
	db.session.add(Kanji(u'何千', u'なんぜん', 1))
	db.session.add(Kanji(u'八千', u'はっせん', 1))
	db.session.add(Kanji(u'千本', u'せんぼん', 1))
	db.session.add(Kanji(u'千', u'せん', 1))
	db.session.add(Kanji(u'万', u'まん', 1))
	db.session.add(Kanji(u'一万', u'いちまん', 1))
	db.session.add(Kanji(u'円', u'えん', 1))
	db.session.add(Kanji(u'一円', u'いちえん', 1))
	db.session.add(Kanji(u'四円', u'よえん', 1))
	db.session.add(Kanji(u'何円', u'なんえん', 1))
	db.session.add(Kanji(u'百', u'ひゃく', 1))
	db.session.add(Kanji(u'三百', u'さんびゃく', 1))
	db.session.add(Kanji(u'六百', u'ろっぴゃく', 1))
	db.session.add(Kanji(u'八百', u'はっぴゃく', 1))
	db.session.add(Kanji(u'百万', u'ろっぴゃく', 1))
	db.session.add(Kanji(u'作る', u'つくる', 1))
	db.session.add(Kanji(u'今', u'いま', 1))
	db.session.add(Kanji(u'今日', u'きょう', 1))
	db.session.add(Kanji(u'大きい', u'おおきい', 1))
	db.session.add(Kanji(u'小さい', u'ちいさい', 1))
	db.session.add(Kanji(u'古い', u'ふるい', 1))
	db.session.add(Kanji(u'一時', u'いちじ', 1))
	db.session.add(Kanji(u'何時', u'なんじ', 1))

	#Kanji from JWL lesson 10
	db.session.add(Kanji(u'行く',u'いく', 2))
	db.session.add(Kanji(u'人',u'ひと', 2))
	db.session.add(Kanji(u'女',u'おんな', 2))
	db.session.add(Kanji(u'本田',u'ほんだ', 2))
	db.session.add(Kanji(u'古田',u'ふるた', 2))
	db.session.add(Kanji(u'今田',u'いまだ', 2))
	db.session.add(Kanji(u'三田',u'みた', 2))
	db.session.add(Kanji(u'大田',u'おおた', 2))
	db.session.add(Kanji(u'山',u'やま', 2))
	db.session.add(Kanji(u'山田',u'やまだ', 2))
	db.session.add(Kanji(u'大山',u'おおやま', 2))
	db.session.add(Kanji(u'古山',u'ふるやま', 2))
	db.session.add(Kanji(u'山本',u'やまもと', 2))
	db.session.add(Kanji(u'本山',u'もとやま', 2))
	db.session.add(Kanji(u'小山',u'こやま', 2))
	db.session.add(Kanji(u'小田',u'おだ', 2))
	db.session.add(Kanji(u'子',u'こ', 2))
	db.session.add(Kanji(u'女の子',u'おんなのこ', 2))
	db.session.add(Kanji(u'今日子',u'きょうこ', 2))
	db.session.add(Kanji(u'日曜日',u'にちようび', 2))
	db.session.add(Kanji(u'何曜日',u'なんようび', 2))
	db.session.add(Kanji(u'火曜日',u'かようび', 2))
	db.session.add(Kanji(u'土曜日',u'どようび', 2))
	db.session.add(Kanji(u'木曜日',u'もくようび', 2))
	db.session.add(Kanji(u'お休み',u'おやすみ', 2))
	db.session.add(Kanji(u'男',u'おとこ', 2))
	db.session.add(Kanji(u'男の子',u'おとこのこ', 2))
	db.session.add(Kanji(u'大学',u'だいがく', 2))
	db.session.add(Kanji(u'出る',u'でる', 2))
	db.session.add(Kanji(u'口',u'くち', 2))
	db.session.add(Kanji(u'出口',u'でぐち', 2))
	db.session.add(Kanji(u'山口',u'やまぐち', 2))
	db.session.add(Kanji(u'田口',u'たぐち', 2))
	db.session.add(Kanji(u'入り口',u'いりぐち', 2))
	db.session.add(Kanji(u'毎日',u'まいにち', 2))
	db.session.add(Kanji(u'月',u'つき', 2))
	db.session.add(Kanji(u'毎月',u'まいつき', 2))
	db.session.add(Kanji(u'月曜日',u'げつようび', 2))
	db.session.add(Kanji(u'一か月',u'いっかげつ', 2))
	db.session.add(Kanji(u'何か月',u'なんかげつ', 2))
	db.session.add(Kanji(u'一月',u'いちがつ', 2))
	db.session.add(Kanji(u'何月',u'なんがつ', 2))
	db.session.add(Kanji(u'今月',u'こんげつ', 2))
	db.session.add(Kanji(u'来る',u'くる', 2))
	db.session.add(Kanji(u'来月',u'らいげつ', 2))
	db.session.add(Kanji(u'水曜日',u'すいようび', 2))
	db.session.add(Kanji(u'金曜日',u'きんようび', 2))
	db.session.add(Kanji(u'知る',u'しる', 2))
	db.session.add(Kanji(u'学生',u'がくせい', 2))
	db.session.add(Kanji(u'大学生',u'だいがくせい', 2))
	db.session.add(Kanji(u'先生',u'せんせい', 2))
	db.session.add(Kanji(u'先月',u'せんげつ', 2))
	db.session.add(Kanji(u'見る',u'みる', 2))
	db.session.add(Kanji(u'見せる',u'みせる', 2))
	db.session.add(Kanji(u'見える',u'みえる', 2))
	#Kanji from JWL lesson 11
	db.session.add(Kanji(u'一人',u'ひとり', 3))
	db.session.add(Kanji(u'二人',u'ふたり', 3))
	db.session.add(Kanji(u'三人',u'さんにん', 3))
	db.session.add(Kanji(u'四人',u'よにん', 3))
	db.session.add(Kanji(u'アメリカ人',u'あめりかじん', 3))
	db.session.add(Kanji(u'何人',u'なんにん', 3))
	db.session.add(Kanji(u'大人',u'おとな', 3))
	db.session.add(Kanji(u'間',u'あいだ', 3))
	db.session.add(Kanji(u'時間',u'じかん', 3))
	db.session.add(Kanji(u'一時間',u'いちじかん', 3))
	db.session.add(Kanji(u'何時間',u'なんじかん', 3))
	db.session.add(Kanji(u'来週',u'らいしゅう', 3))
	db.session.add(Kanji(u'毎週',u'まいしゅう', 3))
	db.session.add(Kanji(u'今週',u'こんしゅう', 3))
	db.session.add(Kanji(u'先週',u'せんしゅう', 3))
	db.session.add(Kanji(u'一週間',u'いっしゅうかん', 3))
	db.session.add(Kanji(u'何週間',u'なんしゅうかん', 3))
	db.session.add(Kanji(u'待つ',u'まつ', 3))
	db.session.add(Kanji(u'午前',u'ごぜん', 3))
	db.session.add(Kanji(u'前田',u'まえだ', 3))
	db.session.add(Kanji(u'前',u'まえ', 3))
	db.session.add(Kanji(u'後ろ',u'うしろ', 3))
	db.session.add(Kanji(u'午後',u'ごご', 3))
	db.session.add(Kanji(u'年',u'とし', 3))
	db.session.add(Kanji(u'今年',u'ことし', 3))
	db.session.add(Kanji(u'来年',u'らいねん', 3))
	db.session.add(Kanji(u'毎年',u'まいねん', 3))
	db.session.add(Kanji(u'一年',u'いちねん', 3))
	db.session.add(Kanji(u'何年',u'なんねん', 3))
	db.session.add(Kanji(u'何年間',u'なんねんかん', 3))
	db.session.add(Kanji(u'食べる',u'たべる', 3))
	db.session.add(Kanji(u'方',u'かた', 3))
	db.session.add(Kanji(u'前方',u'ぜんぽう', 3))
	db.session.add(Kanji(u'雨',u'あめ', 3))
	db.session.add(Kanji(u'会う',u'あう', 3))
	db.session.add(Kanji(u'会田',u'あいだ', 3))
	db.session.add(Kanji(u'会社',u'かいしゃ', 3))
	db.session.add(Kanji(u'大会社',u'だいかいしゃ', 3))
	db.session.add(Kanji(u'子会社',u'こかいしゃ', 3))
	db.session.add(Kanji(u'ガス会社',u'がすかいしゃ', 3))
	db.session.add(Kanji(u'思う',u'おもう', 3))
	db.session.add(Kanji(u'駅',u'えき', 3))
	db.session.add(Kanji(u'駅前',u'えきまえ', 3))
	db.session.add(Kanji(u'名前',u'なまえ', 3))
	db.session.add(Kanji(u'朝',u'あさ', 3))
	db.session.add(Kanji(u'毎朝',u'まいあさ', 3))
	db.session.add(Kanji(u'今朝',u'けさ', 3))
	db.session.add(Kanji(u'朝子',u'あさこ', 3))
	db.session.add(Kanji(u'安い',u'やすい', 3))
	db.session.add(Kanji(u'安田',u'やすだ', 3))
	db.session.add(Kanji(u'安子',u'やすこ', 3))
	db.session.add(Kanji(u'私',u'わたし', 3))
	db.session.add(Kanji(u'父',u'ちち', 3))
	db.session.add(Kanji(u'お父さん',u'おとうさん', 3))
	db.session.add(Kanji(u'母',u'はは', 3))
	db.session.add(Kanji(u'お母さん',u'おかあさん', 3))
	db.session.add(Kanji(u'他',u'ほか', 3))
	db.session.add(Kanji(u'外人',u'がいじん', 3))
	db.session.add(Kanji(u'困る',u'こまる', 3))
	db.session.add(Kanji(u'今晩',u'こんばん', 3))
	db.session.add(Kanji(u'毎晩',u'まいばん', 3))
	db.session.add(Kanji(u'旅館',u'りょかん', 3))
	db.session.add(Kanji(u'会館',u'かいかん', 3))
	#Kanji from JWL lesson 12
	db.session.add(Kanji(u'東京',u'とうきょう', 4))
	db.session.add(Kanji(u'東京駅',u'とうきょうえき', 4))
	db.session.add(Kanji(u'東京大学',u'とうきょうだいがく', 4))
	db.session.add(Kanji(u'東大',u'とうだい', 4))
	db.session.add(Kanji(u'京大',u'きょうだい', 4))
	db.session.add(Kanji(u'京子',u'きょうこ', 4))
	db.session.add(Kanji(u'学校',u'がっこう', 4))
	db.session.add(Kanji(u'高い',u'たかい', 4))
	db.session.add(Kanji(u'高校',u'こうこう', 4))
	db.session.add(Kanji(u'高校生',u'こうこうせい', 4))
	db.session.add(Kanji(u'高山',u'たかやま', 4))
	db.session.add(Kanji(u'高田',u'たかた', 4))
	db.session.add(Kanji(u'高し',u'たかし', 4))
	db.session.add(Kanji(u'高子',u'たかこ', 4))
	db.session.add(Kanji(u'兄',u'あに', 4))
	db.session.add(Kanji(u'お兄さん',u'おにいさん', 4))
	db.session.add(Kanji(u'姉',u'あね', 4))
	db.session.add(Kanji(u'お姉さん',u'おねえさん', 4))
	db.session.add(Kanji(u'書く',u'かく', 4))
	db.session.add(Kanji(u'言う',u'いう', 4))
	db.session.add(Kanji(u'店',u'みせ', 4))
	db.session.add(Kanji(u'一時半',u'いちじはん', 4))
	db.session.add(Kanji(u'半',u'はん', 4))
	db.session.add(Kanji(u'一日半',u'いちにちはん', 4))
	db.session.add(Kanji(u'半時間',u'はんじかん', 4))
	db.session.add(Kanji(u'半日',u'はんにち', 4))
	db.session.add(Kanji(u'半年',u'はんとし', 4))
	db.session.add(Kanji(u'半田',u'はんだ', 4))
	db.session.add(Kanji(u'手前',u'てまえ', 4))
	db.session.add(Kanji(u'手紙',u'てがみ', 4))
	db.session.add(Kanji(u'白',u'しろ', 4))
	db.session.add(Kanji(u'白い',u'しろい', 4))
	db.session.add(Kanji(u'白田',u'しろた', 4))
	db.session.add(Kanji(u'白山',u'しろやま', 4))
	db.session.add(Kanji(u'話す',u'はなす', 4))
	db.session.add(Kanji(u'話',u'はなし', 4))
	db.session.add(Kanji(u'電話',u'でんわ', 4))
	db.session.add(Kanji(u'車',u'くるま', 4))
	db.session.add(Kanji(u'電車',u'でんしゃ', 4))
	db.session.add(Kanji(u'赤い',u'あかい', 4))
	db.session.add(Kanji(u'赤ちゃん',u'あかちゃん', 4))
	db.session.add(Kanji(u'赤電話',u'あかでんわ', 4))
	db.session.add(Kanji(u'後',u'あと', 4))
	db.session.add(Kanji(u'後ほど',u'のちほど', 4))
	db.session.add(Kanji(u'明日',u'あした', 4))
	db.session.add(Kanji(u'明後日',u'あさって', 4))
	db.session.add(Kanji(u'本屋',u'ほんや', 4))
	db.session.add(Kanji(u'山本屋',u'やまもとや', 4))
	db.session.add(Kanji(u'名古屋',u'なごや', 4))
	db.session.add(Kanji(u'買う',u'かう', 4))
	db.session.add(Kanji(u'友だち',u'ともだち', 4))
	db.session.add(Kanji(u'友田',u'ともだ', 4))
	db.session.add(Kanji(u'大友',u'おおとも', 4))
	db.session.add(Kanji(u'友子',u'ともこ', 4))
	db.session.add(Kanji(u'参る',u'まいる', 4))
	db.session.add(Kanji(u'事',u'こと', 4))
	db.session.add(Kanji(u'用事',u'ようじ', 4))
	db.session.add(Kanji(u'火事',u'かじ', 4))
	db.session.add(Kanji(u'仕事',u'しごと', 4))
	#Kanji from JWL lesson 13
	db.session.add(Kanji(u'電話中',u'でんわちゅう', 5))
	db.session.add(Kanji(u'仕事中',u'しごとちゅう', 5))
	db.session.add(Kanji(u'話し中',u'はなしちゅう', 5))
	db.session.add(Kanji(u'中山',u'なかやま', 5))
	db.session.add(Kanji(u'山中',u'やまなか', 5))
	db.session.add(Kanji(u'田中',u'たなか', 5))
	db.session.add(Kanji(u'中田',u'なかだ', 5))
	db.session.add(Kanji(u'中野',u'なかの', 5))
	db.session.add(Kanji(u'野田',u'のだ', 5))
	db.session.add(Kanji(u'野口',u'のぐち', 5))
	db.session.add(Kanji(u'野中',u'のなか', 5))
	db.session.add(Kanji(u'小野',u'おの', 5))
	db.session.add(Kanji(u'大野',u'おおの', 5))
	db.session.add(Kanji(u'高野',u'たかの', 5))
	db.session.add(Kanji(u'使う',u'つかう', 5))
	db.session.add(Kanji(u'使用中',u'しようちゅ', 5))
	db.session.add(Kanji(u'大使館',u'たいしかん', 5))
	db.session.add(Kanji(u'大使',u'たいし', 5))
	db.session.add(Kanji(u'切る',u'きる', 5))
	db.session.add(Kanji(u'大切',u'たいせつ', 5))
	db.session.add(Kanji(u'切らす',u'きらす', 5))
	db.session.add(Kanji(u'ローマ字',u'ろうまじ', 5))
	db.session.add(Kanji(u'数字',u'すうじ', 5))
	db.session.add(Kanji(u'数学',u'すうがく', 5))
	db.session.add(Kanji(u'弱い',u'よわい', 5))
	db.session.add(Kanji(u'強い',u'つよい', 5))
	db.session.add(Kanji(u'勉強',u'べんきょう', 5))
	db.session.add(Kanji(u'日本語',u'にほんご', 5))
	db.session.add(Kanji(u'何語',u'なにご', 5))
	db.session.add(Kanji(u'語学',u'ごがく', 5))
	db.session.add(Kanji(u'英語',u'えいご', 5))
	db.session.add(Kanji(u'英会話',u'えいかいわ', 5))
	db.session.add(Kanji(u'英子',u'えいこ', 5))
	db.session.add(Kanji(u'英一',u'えいいち', 5))
	db.session.add(Kanji(u'日系',u'にっけい', 5))
	db.session.add(Kanji(u'日系人',u'にっけいじん', 5))
	db.session.add(Kanji(u'覚える',u'おぼえる', 5))
	db.session.add(Kanji(u'時々',u'ときどき', 5))
	db.session.add(Kanji(u'地下',u'ちか', 5))
	db.session.add(Kanji(u'地図',u'ちず', 5))
	db.session.add(Kanji(u'図書館',u'としょかん', 5))
	db.session.add(Kanji(u'何階',u'なんがい', 5))
	db.session.add(Kanji(u'一階',u'いっかい', 5))
	db.session.add(Kanji(u'三階',u'さんがい', 5))
	db.session.add(Kanji(u'地下二階',u'ちかにかい', 5))
	db.session.add(Kanji(u'教える',u'おしえる', 5))
	db.session.add(Kanji(u'教会',u'きょうかい', 5))
	db.session.add(Kanji(u'キリスト教',u'きりすときょう', 5))
	db.session.add(Kanji(u'イスラム教',u'いすらむきょう', 5))
	db.session.add(Kanji(u'ユダヤ教',u'ゆだやきょう', 5))
	db.session.add(Kanji(u'近い',u'ちかい', 5))
	db.session.add(Kanji(u'近く',u'ちかく', 5))
	db.session.add(Kanji(u'読む',u'よむ', 5))
	db.session.add(Kanji(u'読書',u'どくしょ', 5))
	db.session.add(Kanji(u'新しい',u'あたらしい', 5))
	db.session.add(Kanji(u'新館',u'しんかん', 5))
	db.session.add(Kanji(u'聞く',u'きく', 5))
	db.session.add(Kanji(u'聞こえる',u'きこえる', 5))
	db.session.add(Kanji(u'英字新聞',u'えいじしんぶん', 5))
	db.session.add(Kanji(u'朝日新聞',u'あさひしんぶん', 5))
	db.session.add(Kanji(u'毎日新聞',u'まいにちしんぶん', 5))
	db.session.add(Kanji(u'新聞社',u'しんぶんしゃ', 5))
	db.session.add(Kanji(u'飲む',u'のむ', 5))
	db.session.add(Kanji(u'右',u'みぎ', 5))
	db.session.add(Kanji(u'右手',u'みぎて', 5))
	db.session.add(Kanji(u'左',u'ひだり', 5))
	db.session.add(Kanji(u'左手',u'ひだりて', 5))
	db.session.add(Kanji(u'歩く',u'あるく', 5))
	#Kanji from JWL lesson 14
	db.session.add(Kanji(u'水田',u'みずた', 6))
	db.session.add(Kanji(u'水野',u'みずの', 6))
	db.session.add(Kanji(u'便利',u'べんり', 6))
	db.session.add(Kanji(u'利用',u'りよう', 6))
	db.session.add(Kanji(u'不便',u'ふべん', 6))
	db.session.add(Kanji(u'漢字',u'かんじ', 6))
	db.session.add(Kanji(u'室',u'しつ', 6))
	db.session.add(Kanji(u'教室',u'きょうしつ', 6))
	db.session.add(Kanji(u'地下室',u'ちかしつ', 6))
	db.session.add(Kanji(u'君',u'きみ', 6))
	db.session.add(Kanji(u'中野君',u'なかのくん', 6))
	db.session.add(Kanji(u'本当',u'ほんと', 6))
	db.session.add(Kanji(u'頼む',u'たのむ', 6))
	db.session.add(Kanji(u'を昼',u'おひる', 6))
	db.session.add(Kanji(u'ご飯',u'ごはん', 6))
	db.session.add(Kanji(u'朝ご飯',u'あさごはん', 6))
	db.session.add(Kanji(u'昼ご飯',u'ひるごはん', 6))
	db.session.add(Kanji(u'晩ご飯',u'ばんごはん', 6))
	db.session.add(Kanji(u'少し',u'すこし', 6))
	db.session.add(Kanji(u'少々',u'しょうしょう', 6))
	db.session.add(Kanji(u'留守',u'るす', 6))
	db.session.add(Kanji(u'留守中',u'るすちゅう', 6))
	db.session.add(Kanji(u'出前',u'でまえ', 6))
	db.session.add(Kanji(u'半分',u'はんぶん', 6))
	db.session.add(Kanji(u'同じ',u'おなじ', 6))
	db.session.add(Kanji(u'元年',u'がんねん', 6))
	db.session.add(Kanji(u'元気',u'げんき', 6))
	db.session.add(Kanji(u'病気',u'びょうき', 6))
	db.session.add(Kanji(u'病人',u'びょうにん', 6))
	db.session.add(Kanji(u'病後',u'びょうご', 6))
	db.session.add(Kanji(u'病院',u'びょういん', 6))
	db.session.add(Kanji(u'大学院',u'だいがくいん', 6))
	db.session.add(Kanji(u'大学院生',u'だいがくいんせい', 6))
	db.session.add(Kanji(u'去年',u'きょねん', 6))
	db.session.add(Kanji(u'色',u'いろ', 6))
	db.session.add(Kanji(u'何色',u'なんいろ', 6))
	db.session.add(Kanji(u'お茶',u'おちゃ', 6))
	db.session.add(Kanji(u'茶色',u'ちゃいろ', 6))
	db.session.add(Kanji(u'京都',u'きょうと', 6))
	db.session.add(Kanji(u'京都大学',u'きょうとだいがく', 6))
	db.session.add(Kanji(u'一才',u'いっさい', 6))
	db.session.add(Kanji(u'三才',u'さんさい', 6))
	db.session.add(Kanji(u'何才',u'なんさい', 6))
	db.session.add(Kanji(u'寺',u'てら', 6))
	db.session.add(Kanji(u'東大寺',u'とうだいじ', 6))
	db.session.add(Kanji(u'山寺',u'やまでら', 6))
	db.session.add(Kanji(u'天気',u'てんき', 6))
	db.session.add(Kanji(u'天ぷら',u'てんぷら', 6))
	#Kanji from JWL lesson 15
	db.session.add(Kanji(u'一名',u'いちめい', 7))
	db.session.add(Kanji(u'六名',u'ろくめい', 7))
	db.session.add(Kanji(u'何名',u'なんめい', 7))
	db.session.add(Kanji(u'声',u'こえ', 7))
	db.session.add(Kanji(u'大声',u'おおごえ', 7))
	db.session.add(Kanji(u'小声',u'こごえ', 7))
	db.session.add(Kanji(u'雪',u'ゆき', 7))
	db.session.add(Kanji(u'雪子',u'ゆきこ', 7))
	db.session.add(Kanji(u'存じる',u'ぞんじる', 7))
	db.session.add(Kanji(u'ご存知',u'ごぞんじ', 7))
	db.session.add(Kanji(u'知人',u'', 7))
	db.session.add(Kanji(u'申す',u'もうす', 7))
	db.session.add(Kanji(u'国',u'くに', 7))
	db.session.add(Kanji(u'外国',u'がいこく', 7))
	db.session.add(Kanji(u'外国人',u'がいこくじん', 7))
	db.session.add(Kanji(u'外国語',u'がいこくご', 7))
	db.session.add(Kanji(u'四国',u'しこく', 7))
	db.session.add(Kanji(u'英国',u'えいこく', 7))
	db.session.add(Kanji(u'英国人',u'えいこくじん', 7))
	db.session.add(Kanji(u'中国',u'ちゅうこく', 7))
	db.session.add(Kanji(u'国語',u'こくご', 7))
	db.session.add(Kanji(u'中国語',u'ちゅうこくご', 7))
	db.session.add(Kanji(u'国外',u'こくがい', 7))
	db.session.add(Kanji(u'大国',u'たいこく', 7))
	db.session.add(Kanji(u'国々',u'くにぐに', 7))
	db.session.add(Kanji(u'米',u'こめ', 7))
	db.session.add(Kanji(u'米屋',u'こめや', 7))
	db.session.add(Kanji(u'米国',u'べいこく', 7))
	db.session.add(Kanji(u'日米',u'にべい', 7))
	db.session.add(Kanji(u'英米',u'えいべい', 7))
	db.session.add(Kanji(u'冷たい',u'つめたい', 7))
	db.session.add(Kanji(u'願う',u'ねがう', 7))
	db.session.add(Kanji(u'酒',u'さけ', 7))
	db.session.add(Kanji(u'酒屋',u'さけや', 7))
	db.session.add(Kanji(u'酒田',u'さかた', 7))
	db.session.add(Kanji(u'五号室',u'ごごうしつ', 7))
	db.session.add(Kanji(u'何号室',u'なんごうしつ', 7))
	db.session.add(Kanji(u'月号',u'がつごう', 7))
	db.session.add(Kanji(u'過ぎる',u'すぎる', 7))
	db.session.add(Kanji(u'食べ過ぎる',u'たべすぎる', 7))
	db.session.add(Kanji(u'元気過ぎる',u'げんきすぎる', 7))
	db.session.add(Kanji(u'十時過ぎ',u'じゅうじすぎ', 7))
	db.session.add(Kanji(u'高過ぎる',u'たかすぎる', 7))
	db.session.add(Kanji(u'全国',u'ぜんこく', 7))
	db.session.add(Kanji(u'全校',u'ぜんこう', 7))
	db.session.add(Kanji(u'全社',u'ぜんしゃ', 7))
	db.session.add(Kanji(u'全部',u'ぜんぶ', 7))
	db.session.add(Kanji(u'東部',u'とうぶ', 7))
	db.session.add(Kanji(u'部室',u'ぶしつ', 7))
	db.session.add(Kanji(u'部下',u'ぶか', 7))
	db.session.add(Kanji(u'一番',u'いちばん', 7))
	db.session.add(Kanji(u'何番',u'なんばん', 7))
	db.session.add(Kanji(u'番号',u'ばんごう', 7))
	db.session.add(Kanji(u'電話番号',u'でんわばんごう', 7))
	db.session.add(Kanji(u'留守番',u'るすばん', 7))
	db.session.add(Kanji(u'留守番電話',u'るすばんでんわ', 7))
	db.session.add(Kanji(u'何名様',u'なんめいさま', 7))
	db.session.add(Kanji(u'様',u'さま', 7))
	db.session.add(Kanji(u'お父様',u'おとうさま', 7))
	db.session.add(Kanji(u'お母様',u'おかあさま', 7))
	db.session.add(Kanji(u'客',u'きゃく', 7))
	db.session.add(Kanji(u'お客様',u'おきゃくさま', 7))
	db.session.add(Kanji(u'客室',u'きゃくしつ', 7))
	db.session.add(Kanji(u'来客',u'らいきゃく', 7))
	db.session.add(Kanji(u'来客中',u'らいきゃくちゅう', 7))
	db.session.add(Kanji(u'料理',u'りょうり', 7))
	db.session.add(Kanji(u'日本料理',u'にほんりょうり', 7))
	db.session.add(Kanji(u'手料理',u'てりょうり', 7))
	db.session.add(Kanji(u'料理学校',u'りょうりがっこう', 7))
	db.session.add(Kanji(u'長い',u'ながい', 7))
	db.session.add(Kanji(u'長山',u'ながやま', 7))
	db.session.add(Kanji(u'長田',u'ながだ', 7))
	db.session.add(Kanji(u'長野',u'ながの', 7))
	db.session.add(Kanji(u'社長',u'しゃちょ', 7))
	db.session.add(Kanji(u'部長',u'ぶちょ', 7))
	db.session.add(Kanji(u'学長',u'がくちょ', 7))
	db.session.add(Kanji(u'校長',u'こうちょ', 7))
	db.session.add(Kanji(u'院長',u'ぶちょ', 7))
	db.session.add(Kanji(u'料理長',u'りょうりちょ', 7))
	db.session.add(Kanji(u'家',u'いえ', 7))
	db.session.add(Kanji(u'内',u'うち', 7))
	db.session.add(Kanji(u'内田',u'うちだ', 7))
	db.session.add(Kanji(u'内山',u'うちやま', 7))
	db.session.add(Kanji(u'大内',u'おおうち', 7))
	db.session.add(Kanji(u'内野',u'うちの', 7))
	db.session.add(Kanji(u'校内',u'こうない', 7))
	db.session.add(Kanji(u'学内',u'がくない', 7))
	db.session.add(Kanji(u'社内',u'しゃない', 7))
	db.session.add(Kanji(u'部内',u'ぶない', 7))
	db.session.add(Kanji(u'国内',u'こくない', 7))
	db.session.add(Kanji(u'主人',u'しゅじん', 7))
	db.session.add(Kanji(u'好き',u'すき', 7))
	db.session.add(Kanji(u'花',u'はな', 7))
	db.session.add(Kanji(u'花屋',u'はなや', 7))
	db.session.add(Kanji(u'花田',u'はなだ', 7))
	db.session.add(Kanji(u'花子',u'はなこ', 7))
	db.session.add(Kanji(u'花見',u'はなみ', 7))
	db.session.add(Kanji(u'代わる',u'かわる', 7))
	db.session.add(Kanji(u'代える',u'かえる', 7))
	#Kanji from JWL lesson 16
	'''
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	db.session.add(Kanji(u'',u'', ))
	'''
	db.session.commit()

app.secret_key = "Terrible key"