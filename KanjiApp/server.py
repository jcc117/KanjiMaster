#Main server file

import os
import json
from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource

from models import db, User, Report, Kanji

from datetime import datetime

app = Flask(__name__)
api = Api(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'server.db')

app.config.from_object(__name__)
app.config.from_envvar('SERVER_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

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
@app.route("/sign_up/", methods = ['GET', 'POST'])
def sign_up():
	if g.user:
		return redirect(url_for('home', userID=g.user.userID))
	error = None
	if request.method == 'POST':
		#Check for username
		if not request.form['name']:
			error = "Please enter a username"
		#Check for a password
		elif not request.form['pass']:
			error = "Please enter a password"
		#Check for a reentered password
		elif not request.form['pass2']:
			error = "Please reenter your password"
		#Check the passwords match
		elif request.form['pass'] != request.form['pass2']:
			error = "Passwords do not match"
		#Check for taken username
		elif get_user_id(request.form['name']) is None:
			db.session.add(User(request.form['name'], request.form['pass']))
			db.session.commit()
			return redirect(url_for('rootpage'))
		else:
			error = "That username is already taken"
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

#Get the kanji for a specific category
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

#Lets make this restful
#Restful Kanji Resource
class R_Kanji(Resource):
	def get(self):
		return None

	def post(self):
		if g.user:
			data = request.json
			kanji = ''
			romaji = ''
			difficulty = 0

			db.session.add(Kanji(kanji, romaji, difficulty))
		return None

#Restful Report Resource
class Report(Resource):
	#Get all reports for a user
	def get(self):
		if g.user:
			results = Report.query.filter_by(userID = g.user.userID)
			rv = []
			for i in range(0, len(results)):
				string = "{}:{}:{}:{}".format(results[i].date, results[i].difficulty, results[i].num_total, results[i].num_correct)
				rv.append(string)
			return json.dumps(rv), 200
		return json.dumps("Unauthorized"), 401

	#Post a new report	
	def post(self):
		if g.user:
			#Parse the request
			data = request.json
			difficulty = 0
			num_correct = 0
			num_total = 0

			#Add the report to the user
			db.session.add(Report(g.user.userID, difficulty, num_correct, num_total, datetime.now()))
			return json.dumps("Resource created"), 201
		return json.dumps("Unauthorized"), 401

		

#api.add_resource(Kanji, "/kanji/")
api.add_resource(Report, "/report/")

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
	db.session.add(Kanji('ー県','ken', 1))
	db.session.add(Kanji('金庫','kinko', 1))
	db.session.add(Kanji('不幸','fukou', 1))
	db.session.add(Kanji('大根','daikon', 1))
	db.session.add(Kanji('屋根','yane', 1))
	db.session.add(Kanji('球','tama', 1))
	db.session.add(Kanji('苦しい','kurushii', 1))
	db.session.add(Kanji('苦しむ','kurushimu', 1))
	db.session.add(Kanji('苦い','nigai', 1))
	db.session.add(Kanji('苦る','nigaru', 1))
	db.session.add(Kanji('血','ketsu', 1))
	db.session.add(Kanji('湖','mizuumi', 1))
	db.session.add(Kanji('幸い','saiwai', 1))
	db.session.add(Kanji('幸せ','shiawase', 1))
	db.session.add(Kanji('祭る','matsuru', 1))
	db.session.add(Kanji('祭り','matsuri', 1))
	db.session.add(Kanji('皿','sara', 1))
	#Commented out for now. Will fill in with more later
	'''
	db.session.add(Kanji(30, '','', 0))
	db.session.add(Kanji(31, '','', 0))
	db.session.add(Kanji(32, '','', 0))
	db.session.add(Kanji(33, '','', 0))
	db.session.add(Kanji(34, '','', 0))
	db.session.add(Kanji(35, '','', 0))
	db.session.add(Kanji(36, '','', 0))
	db.session.add(Kanji(37, '','', 0))
	db.session.add(Kanji(38, '','', 0))
	db.session.add(Kanji(39, '','', 0))
	db.session.add(Kanji(40, '','', 0))
	db.session.add(Kanji(41, '','', 0))
	db.session.add(Kanji(42, '','', 0))
	db.session.add(Kanji(43, '','', 0))
	db.session.add(Kanji(44, '','', 0))
	db.session.add(Kanji(45, '','', 0))
	db.session.add(Kanji(46, '','', 0))
	db.session.add(Kanji(47, '','', 0))
	db.session.add(Kanji(48, '','', 0))
	db.session.add(Kanji(49, '','', 0))
	db.session.add(Kanji(50, '','', 0))
	db.session.add(Kanji(51, '','', 0))
	db.session.add(Kanji(52, '','', 0))
	db.session.add(Kanji(53, '','', 0))
	db.session.add(Kanji(54, '','', 0))
	db.session.add(Kanji(55, '','', 0))
	db.session.add(Kanji(56, '','', 0))
	db.session.add(Kanji(57, '','', 0))
	db.session.add(Kanji(58, '','', 0))
	db.session.add(Kanji(59, '','', 0))
	db.session.add(Kanji(60, '','', 0))
	db.session.add(Kanji(61, '','', 0))
	db.session.add(Kanji(62, '','', 0))
	db.session.add(Kanji(63, '','', 0))
	db.session.add(Kanji(64, '','', 0))
	db.session.add(Kanji(65, '','', 0))
	db.session.add(Kanji(66, '','', 0))
	db.session.add(Kanji(67, '','', 0))
	db.session.add(Kanji(68, '','', 0))
	db.session.add(Kanji(69, '','', 0))
	db.session.add(Kanji(70, '','', 0))
	db.session.add(Kanji(71, '','', 0))
	db.session.add(Kanji(72, '','', 0))
	db.session.add(Kanji(73, '','', 0))
	db.session.add(Kanji(74, '','', 0))
	db.session.add(Kanji(75, '','', 0))
	db.session.add(Kanji(76, '','', 0))
	db.session.add(Kanji(77, '','', 0))
	db.session.add(Kanji(78, '','', 0))
	db.session.add(Kanji(79, '','', 0))
	db.session.add(Kanji(80, '','', 0))
	db.session.add(Kanji(81, '','', 0))
	db.session.add(Kanji(82, '','', 0))
	db.session.add(Kanji(83, '','', 0))
	db.session.add(Kanji(84, '','', 0))
	db.session.add(Kanji(85, '','', 0))
	db.session.add(Kanji(86, '','', 0))
	db.session.add(Kanji(87, '','', 0))
	db.session.add(Kanji(88, '','', 0))
	db.session.add(Kanji(89, '','', 0))
	db.session.add(Kanji(90, '','', 0))
	db.session.add(Kanji(91, '','', 0))
	db.session.add(Kanji(92, '','', 0))
	db.session.add(Kanji(93, '','', 0))
	db.session.add(Kanji(94, '','', 0))
	db.session.add(Kanji(95, '','', 0))
	db.session.add(Kanji(96, '','', 0))
	db.session.add(Kanji(97, '','', 0))
	db.session.add(Kanji(98, '','', 0))
	db.session.add(Kanji(99, '','', 0))
	db.session.add(Kanji(100, '','', 0))
	db.session.add(Kanji(101, '','', 0))
	db.session.add(Kanji(102, '','', 0))
	db.session.add(Kanji(103, '','', 0))
	db.session.add(Kanji(104, '','', 0))
	db.session.add(Kanji(105, '','', 0))
	db.session.add(Kanji(106, '','', 0))
	db.session.add(Kanji(107, '','', 0))
	db.session.add(Kanji(108, '','', 0))
	db.session.add(Kanji(109, '','', 0))
	db.session.add(Kanji(110, '','', 0))
	db.session.add(Kanji(111, '','', 0))
	db.session.add(Kanji(112, '','', 0))
	db.session.add(Kanji(113, '','', 0))
	db.session.add(Kanji(114, '','', 0))
	db.session.add(Kanji(115, '','', 0))
	db.session.add(Kanji(116, '','', 0))
	db.session.add(Kanji(117, '','', 0))
	db.session.add(Kanji(118, '','', 0))
	db.session.add(Kanji(119, '','', 0))
	db.session.add(Kanji(120, '','', 0))
	db.session.add(Kanji(121, '','', 0))
	db.session.add(Kanji(122, '','', 0))
	db.session.add(Kanji(123, '','', 0))
	db.session.add(Kanji(124, '','', 0))
	db.session.add(Kanji(125, '','', 0))
	db.session.add(Kanji(126, '','', 0))
	db.session.add(Kanji(127, '','', 0))
	db.session.add(Kanji(128, '','', 0))
	db.session.add(Kanji(129, '','', 0))
	db.session.add(Kanji(130, '','', 0))
	db.session.add(Kanji(131, '','', 0))
	db.session.add(Kanji(132, '','', 0))
	db.session.add(Kanji(133, '','', 0))
	db.session.add(Kanji(134, '','', 0))
	db.session.add(Kanji(135, '','', 0))
	db.session.add(Kanji(136, '','', 0))
	db.session.add(Kanji(137, '','', 0))
	db.session.add(Kanji(138, '','', 0))
	db.session.add(Kanji(139, '','', 0))
	db.session.add(Kanji(140, '','', 0))
	db.session.add(Kanji(141, '','', 0))
	db.session.add(Kanji(142, '','', 0))
	db.session.add(Kanji(143, '','', 0))
	db.session.add(Kanji(144, '','', 0))
	db.session.add(Kanji(145, '','', 0))
	db.session.add(Kanji(146, '','', 0))
	db.session.add(Kanji(147, '','', 0))
	db.session.add(Kanji(148, '','', 0))
	db.session.add(Kanji(149, '','', 0))
	db.session.add(Kanji(150, '','', 0))
	db.session.add(Kanji(151, '','', 0))
	db.session.add(Kanji(152, '','', 0))
	db.session.add(Kanji(153, '','', 0))
	db.session.add(Kanji(154, '','', 0))
	db.session.add(Kanji(155, '','', 0))
	db.session.add(Kanji(156, '','', 0))
	db.session.add(Kanji(157, '','', 0))
	db.session.add(Kanji(158, '','', 0))
	db.session.add(Kanji(159, '','', 0))
	db.session.add(Kanji(160, '','', 0))
	db.session.add(Kanji(161, '','', 0))
	db.session.add(Kanji(162, '','', 0))
	db.session.add(Kanji(163, '','', 0))
	db.session.add(Kanji(164, '','', 0))
	db.session.add(Kanji(165, '','', 0))
	db.session.add(Kanji(166, '','', 0))
	db.session.add(Kanji(167, '','', 0))
	db.session.add(Kanji(168, '','', 0))
	db.session.add(Kanji(169, '','', 0))
	db.session.add(Kanji(170, '','', 0))
	db.session.add(Kanji(171, '','', 0))
	db.session.add(Kanji(172, '','', 0))
	db.session.add(Kanji(173, '','', 0))
	db.session.add(Kanji(174, '','', 0))
	db.session.add(Kanji(175, '','', 0))
	db.session.add(Kanji(176, '','', 0))
	db.session.add(Kanji(177, '','', 0))
	db.session.add(Kanji(178, '','', 0))
	db.session.add(Kanji(179, '','', 0))
	db.session.add(Kanji(180, '','', 0))
	db.session.add(Kanji(181, '','', 0))
	db.session.add(Kanji(182, '','', 0))
	db.session.add(Kanji(183, '','', 0))
	db.session.add(Kanji(184, '','', 0))
	db.session.add(Kanji(185, '','', 0))
	db.session.add(Kanji(186, '','', 0))
	db.session.add(Kanji(187, '','', 0))
	db.session.add(Kanji(188, '','', 0))
	db.session.add(Kanji(189, '','', 0))
	db.session.add(Kanji(190, '','', 0))
	db.session.add(Kanji(191, '','', 0))
	db.session.add(Kanji(192, '','', 0))
	db.session.add(Kanji(193, '','', 0))
	db.session.add(Kanji(194, '','', 0))
	db.session.add(Kanji(195, '','', 0))
	db.session.add(Kanji(196, '','', 0))
	db.session.add(Kanji(197, '','', 0))
	db.session.add(Kanji(198, '','', 0))
	db.session.add(Kanji(199, '','', 0))
	db.session.add(Kanji(200, '','', 0))
	db.session.add(Kanji(201, '','', 0))
	db.session.add(Kanji(202, '','', 0))
	db.session.add(Kanji(203, '','', 0))
	db.session.add(Kanji(204, '','', 0))
	db.session.add(Kanji(205, '','', 0))
	db.session.add(Kanji(206, '','', 0))
	db.session.add(Kanji(207, '','', 0))
	db.session.add(Kanji(208, '','', 0))
	db.session.add(Kanji(209, '','', 0))
	db.session.add(Kanji(210, '','', 0))
	db.session.add(Kanji(211, '','', 0))
	db.session.add(Kanji(212, '','', 0))
	db.session.add(Kanji(213, '','', 0))
	db.session.add(Kanji(214, '','', 0))
	db.session.add(Kanji(215, '','', 0))
	db.session.add(Kanji(216, '','', 0))
	db.session.add(Kanji(217, '','', 0))
	db.session.add(Kanji(218, '','', 0))
	db.session.add(Kanji(219, '','', 0))
	db.session.add(Kanji(220, '','', 0))
	db.session.add(Kanji(221, '','', 0))
	db.session.add(Kanji(222, '','', 0))
	db.session.add(Kanji(223, '','', 0))
	db.session.add(Kanji(224, '','', 0))
	db.session.add(Kanji(225, '','', 0))
	db.session.add(Kanji(226, '','', 0))
	db.session.add(Kanji(227, '','', 0))
	db.session.add(Kanji(228, '','', 0))
	db.session.add(Kanji(229, '','', 0))
	db.session.add(Kanji(230, '','', 0))
	db.session.add(Kanji(231, '','', 0))
	db.session.add(Kanji(232, '','', 0))
	db.session.add(Kanji(233, '','', 0))
	db.session.add(Kanji(234, '','', 0))
	db.session.add(Kanji(235, '','', 0))
	db.session.add(Kanji(236, '','', 0))
	db.session.add(Kanji(237, '','', 0))
	db.session.add(Kanji(238, '','', 0))
	db.session.add(Kanji(239, '','', 0))
	db.session.add(Kanji(240, '','', 0))
	db.session.add(Kanji(241, '','', 0))
	db.session.add(Kanji(242, '','', 0))
	db.session.add(Kanji(243, '','', 0))
	db.session.add(Kanji(244, '','', 0))
	db.session.add(Kanji(245, '','', 0))
	db.session.add(Kanji(246, '','', 0))
	db.session.add(Kanji(247, '','', 0))
	db.session.add(Kanji(248, '','', 0))
	db.session.add(Kanji(249, '','', 0))
	db.session.add(Kanji(250, '','', 0))
	db.session.add(Kanji(251, '','', 0))
	db.session.add(Kanji(252, '','', 0))
	db.session.add(Kanji(253, '','', 0))
	db.session.add(Kanji(254, '','', 0))
	db.session.add(Kanji(255, '','', 0))
	db.session.add(Kanji(256, '','', 0))
	db.session.add(Kanji(257, '','', 0))
	db.session.add(Kanji(258, '','', 0))
	db.session.add(Kanji(259, '','', 0))
	db.session.add(Kanji(260, '','', 0))
	db.session.add(Kanji(261, '','', 0))
	db.session.add(Kanji(262, '','', 0))
	db.session.add(Kanji(263, '','', 0))
	db.session.add(Kanji(264, '','', 0))
	db.session.add(Kanji(265, '','', 0))
	db.session.add(Kanji(266, '','', 0))
	db.session.add(Kanji(267, '','', 0))
	db.session.add(Kanji(268, '','', 0))
	db.session.add(Kanji(269, '','', 0))
	db.session.add(Kanji(270, '','', 0))
	db.session.add(Kanji(271, '','', 0))
	db.session.add(Kanji(272, '','', 0))
	db.session.add(Kanji(273, '','', 0))
	db.session.add(Kanji(274, '','', 0))
	db.session.add(Kanji(275, '','', 0))
	db.session.add(Kanji(276, '','', 0))
	db.session.add(Kanji(277, '','', 0))
	db.session.add(Kanji(278, '','', 0))
	db.session.add(Kanji(279, '','', 0))
	db.session.add(Kanji(280, '','', 0))
	db.session.add(Kanji(281, '','', 0))
	db.session.add(Kanji(282, '','', 0))
	db.session.add(Kanji(283, '','', 0))
	db.session.add(Kanji(284, '','', 0))
	db.session.add(Kanji(285, '','', 0))
	db.session.add(Kanji(286, '','', 0))
	db.session.add(Kanji(287, '','', 0))
	db.session.add(Kanji(288, '','', 0))
	db.session.add(Kanji(289, '','', 0))
	db.session.add(Kanji(290, '','', 0))
	db.session.add(Kanji(291, '','', 0))
	db.session.add(Kanji(292, '','', 0))
	db.session.add(Kanji(293, '','', 0))
	db.session.add(Kanji(294, '','', 0))
	db.session.add(Kanji(295, '','', 0))
	db.session.add(Kanji(296, '','', 0))
	db.session.add(Kanji(297, '','', 0))
	db.session.add(Kanji(298, '','', 0))
	db.session.add(Kanji(299, '','', 0))
	db.session.add(Kanji(300, '','', 0))
	db.session.add(Kanji(301, '','', 0))
	db.session.add(Kanji(302, '','', 0))
	db.session.add(Kanji(303, '','', 0))
	db.session.add(Kanji(304, '','', 0))
	db.session.add(Kanji(305, '','', 0))
	db.session.add(Kanji(306, '','', 0))
	db.session.add(Kanji(307, '','', 0))
	db.session.add(Kanji(308, '','', 0))
	db.session.add(Kanji(309, '','', 0))
	db.session.add(Kanji(310, '','', 0))
	db.session.add(Kanji(311, '','', 0))
	db.session.add(Kanji(312, '','', 0))
	db.session.add(Kanji(313, '','', 0))
	db.session.add(Kanji(314, '','', 0))
	db.session.add(Kanji(315, '','', 0))
	db.session.add(Kanji(316, '','', 0))
	db.session.add(Kanji(317, '','', 0))
	db.session.add(Kanji(318, '','', 0))
	db.session.add(Kanji(319, '','', 0))
	db.session.add(Kanji(320, '','', 0))
	db.session.add(Kanji(321, '','', 0))
	db.session.add(Kanji(322, '','', 0))
	db.session.add(Kanji(323, '','', 0))
	db.session.add(Kanji(324, '','', 0))
	db.session.add(Kanji(325, '','', 0))
	db.session.add(Kanji(326, '','', 0))
	db.session.add(Kanji(327, '','', 0))
	db.session.add(Kanji(328, '','', 0))
	db.session.add(Kanji(329, '','', 0))
	db.session.add(Kanji(330, '','', 0))
	db.session.add(Kanji(331, '','', 0))
	db.session.add(Kanji(332, '','', 0))
	db.session.add(Kanji(333, '','', 0))
	db.session.add(Kanji(334, '','', 0))
	db.session.add(Kanji(335, '','', 0))
	db.session.add(Kanji(336, '','', 0))
	db.session.add(Kanji(337, '','', 0))
	db.session.add(Kanji(338, '','', 0))
	db.session.add(Kanji(339, '','', 0))
	db.session.add(Kanji(340, '','', 0))
	db.session.add(Kanji(341, '','', 0))
	db.session.add(Kanji(342, '','', 0))
	db.session.add(Kanji(343, '','', 0))
	db.session.add(Kanji(344, '','', 0))
	db.session.add(Kanji(345, '','', 0))
	db.session.add(Kanji(346, '','', 0))
	db.session.add(Kanji(347, '','', 0))
	db.session.add(Kanji(348, '','', 0))
	db.session.add(Kanji(349, '','', 0))
	db.session.add(Kanji(350, '','', 0))
	db.session.add(Kanji(351, '','', 0))
	db.session.add(Kanji(352, '','', 0))
	db.session.add(Kanji(353, '','', 0))
	db.session.add(Kanji(354, '','', 0))
	db.session.add(Kanji(355, '','', 0))
	db.session.add(Kanji(356, '','', 0))
	db.session.add(Kanji(357, '','', 0))
	db.session.add(Kanji(358, '','', 0))
	db.session.add(Kanji(359, '','', 0))
	db.session.add(Kanji(360, '','', 0))
	db.session.add(Kanji(361, '','', 0))
	db.session.add(Kanji(362, '','', 0))
	db.session.add(Kanji(363, '','', 0))
	db.session.add(Kanji(364, '','', 0))
	db.session.add(Kanji(365, '','', 0))
	db.session.add(Kanji(366, '','', 0))
	db.session.add(Kanji(367, '','', 0))
	db.session.add(Kanji(368, '','', 0))
	db.session.add(Kanji(369, '','', 0))
	db.session.add(Kanji(370, '','', 0))
	db.session.add(Kanji(371, '','', 0))
	db.session.add(Kanji(372, '','', 0))
	db.session.add(Kanji(373, '','', 0))
	db.session.add(Kanji(374, '','', 0))
	db.session.add(Kanji(375, '','', 0))
	db.session.add(Kanji(376, '','', 0))
	db.session.add(Kanji(377, '','', 0))
	db.session.add(Kanji(378, '','', 0))
	db.session.add(Kanji(379, '','', 0))
	db.session.add(Kanji(380, '','', 0))
	db.session.add(Kanji(381, '','', 0))
	db.session.add(Kanji(382, '','', 0))
	db.session.add(Kanji(383, '','', 0))
	db.session.add(Kanji(384, '','', 0))
	db.session.add(Kanji(385, '','', 0))
	db.session.add(Kanji(386, '','', 0))
	db.session.add(Kanji(387, '','', 0))
	db.session.add(Kanji(388, '','', 0))
	db.session.add(Kanji(389, '','', 0))
	db.session.add(Kanji(390, '','', 0))
	db.session.add(Kanji(391, '','', 0))
	db.session.add(Kanji(392, '','', 0))
	db.session.add(Kanji(393, '','', 0))
	db.session.add(Kanji(394, '','', 0))
	db.session.add(Kanji(395, '','', 0))
	db.session.add(Kanji(396, '','', 0))
	db.session.add(Kanji(397, '','', 0))
	db.session.add(Kanji(398, '','', 0))
	db.session.add(Kanji(399, '','', 0))
	db.session.add(Kanji(400, '','', 0))
	db.session.add(Kanji(401, '','', 0))
	db.session.add(Kanji(402, '','', 0))
	db.session.add(Kanji(403, '','', 0))
	db.session.add(Kanji(404, '','', 0))
	db.session.add(Kanji(405, '','', 0))
	db.session.add(Kanji(406, '','', 0))
	db.session.add(Kanji(407, '','', 0))
	db.session.add(Kanji(408, '','', 0))
	db.session.add(Kanji(409, '','', 0))
	db.session.add(Kanji(410, '','', 0))
	db.session.add(Kanji(411, '','', 0))
	db.session.add(Kanji(412, '','', 0))
	db.session.add(Kanji(413, '','', 0))
	db.session.add(Kanji(414, '','', 0))
	db.session.add(Kanji(415, '','', 0))
	db.session.add(Kanji(416, '','', 0))
	db.session.add(Kanji(417, '','', 0))
	db.session.add(Kanji(418, '','', 0))
	db.session.add(Kanji(419, '','', 0))
	db.session.add(Kanji(420, '','', 0))
	db.session.add(Kanji(421, '','', 0))
	db.session.add(Kanji(422, '','', 0))
	db.session.add(Kanji(423, '','', 0))
	db.session.add(Kanji(424, '','', 0))
	db.session.add(Kanji(425, '','', 0))
	db.session.add(Kanji(426, '','', 0))
	db.session.add(Kanji(427, '','', 0))
	db.session.add(Kanji(428, '','', 0))
	db.session.add(Kanji(429, '','', 0))
	db.session.add(Kanji(430, '','', 0))
	db.session.add(Kanji(431, '','', 0))
	db.session.add(Kanji(432, '','', 0))
	db.session.add(Kanji(433, '','', 0))
	db.session.add(Kanji(434, '','', 0))
	db.session.add(Kanji(435, '','', 0))
	db.session.add(Kanji(436, '','', 0))
	db.session.add(Kanji(437, '','', 0))
	db.session.add(Kanji(438, '','', 0))
	db.session.add(Kanji(439, '','', 0))
	db.session.add(Kanji(440, '','', 0))
	db.session.add(Kanji(441, '','', 0))
	db.session.add(Kanji(442, '','', 0))
	db.session.add(Kanji(443, '','', 0))
	db.session.add(Kanji(444, '','', 0))
	db.session.add(Kanji(445, '','', 0))
	db.session.add(Kanji(446, '','', 0))
	db.session.add(Kanji(447, '','', 0))
	db.session.add(Kanji(448, '','', 0))
	db.session.add(Kanji(449, '','', 0))
	db.session.add(Kanji(450, '','', 0))
	db.session.add(Kanji(451, '','', 0))
	db.session.add(Kanji(452, '','', 0))
	db.session.add(Kanji(453, '','', 0))
	db.session.add(Kanji(454, '','', 0))
	db.session.add(Kanji(455, '','', 0))
	db.session.add(Kanji(456, '','', 0))
	db.session.add(Kanji(457, '','', 0))
	db.session.add(Kanji(458, '','', 0))
	db.session.add(Kanji(459, '','', 0))
	db.session.add(Kanji(460, '','', 0))
	db.session.add(Kanji(461, '','', 0))
	db.session.add(Kanji(462, '','', 0))
	db.session.add(Kanji(463, '','', 0))
	db.session.add(Kanji(464, '','', 0))
	db.session.add(Kanji(465, '','', 0))
	db.session.add(Kanji(466, '','', 0))
	db.session.add(Kanji(467, '','', 0))
	db.session.add(Kanji(468, '','', 0))
	db.session.add(Kanji(469, '','', 0))
	db.session.add(Kanji(470, '','', 0))
	db.session.add(Kanji(471, '','', 0))
	db.session.add(Kanji(472, '','', 0))
	db.session.add(Kanji(473, '','', 0))
	db.session.add(Kanji(474, '','', 0))
	db.session.add(Kanji(475, '','', 0))
	db.session.add(Kanji(476, '','', 0))
	db.session.add(Kanji(477, '','', 0))
	db.session.add(Kanji(478, '','', 0))
	db.session.add(Kanji(479, '','', 0))
	db.session.add(Kanji(480, '','', 0))
	db.session.add(Kanji(481, '','', 0))
	db.session.add(Kanji(482, '','', 0))
	db.session.add(Kanji(483, '','', 0))
	db.session.add(Kanji(484, '','', 0))
	db.session.add(Kanji(485, '','', 0))
	db.session.add(Kanji(486, '','', 0))
	db.session.add(Kanji(487, '','', 0))
	db.session.add(Kanji(488, '','', 0))
	db.session.add(Kanji(489, '','', 0))
	db.session.add(Kanji(490, '','', 0))
	db.session.add(Kanji(491, '','', 0))
	db.session.add(Kanji(492, '','', 0))
	db.session.add(Kanji(493, '','', 0))
	db.session.add(Kanji(494, '','', 0))
	db.session.add(Kanji(495, '','', 0))
	db.session.add(Kanji(496, '','', 0))
	db.session.add(Kanji(497, '','', 0))
	db.session.add(Kanji(498, '','', 0))
	db.session.add(Kanji(499, '','', 0))
	db.session.add(Kanji(500, '','', 0))
	'''
	db.session.commit()

app.secret_key = "Terrible key"