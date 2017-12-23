#Main server file

import os
import json
from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource

from models import db, User, Report, Kanji
import kanji-insert

app = Flask(__name__)
api = Api(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'server.db')

app.config.from_object(__name__)
app.config.from_envvar('SERVER_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

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
		return redirect(url_for('home', username = g.user.username))
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
			elif name.password == request.form['pass']:
				session['userID'] = name.userID
				flash("You have been logged in")
				return redirect(url_for('home', username = name.userID))
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
				#Add a new chatroom
				chat = ChatRoom.query.filter_by(title = request.form['title']).first()
				if not request.form['title']:
					#Check that a title has been added
					error = "Please enter a title"
				elif chat is not None:
					error = "That title already exists"
				else:
					#Note: chatrooms can have the same titles, does not affect overall implementation
					newChat = ChatRoom(request.form['title'], g.user.user_id)
					db.session.add(newChat)
					g.user.chatrooms.append(newChat)
					db.session.commit()
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
		return redirect(url_for('home', username=g.user.userID))
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
