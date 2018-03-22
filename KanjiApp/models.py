#Models/Schemas

from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
import datetime

db = SQLAlchemy()

class User(db.Model):
	userID = db.Column(db.String(300), primary_key = True)
	password = db.Column(db.String(300), nullable = False)
	reports = db.relationship('Report', backref = 'user', lazy = 'dynamic')
	fname = db.Column(db.String(300), nullable = False)
	lname = db.Column(db.String(300), nullable = False)
	email = db.Column(db.String(300), nullable = False)
	reason = db.Column(db.String(210), nullable = False)
	weekly_goal = db.Column(db.String(200))
	weekly_goal_timestamp = db.Column(db.DateTime)
	date = db.Column(db.DateTime)

	def __init__(self, id, passw, fname, lname, email, reason, goal, tp):
		self.userID = id
		self.password = bcrypt.encrypt(passw)
		self.fname = fname
		self.lname = lname
		self.email = email
		self.reason = reason
		self.weekly_goal = goal
		self.weekly_goal_timestamp = tp
		date = datetime.datetime.now()
		self.date = date + datetime.timedelta(days = -1)

	def validate_password(self, passw):
		return bcrypt.verify(passw, self.password)

	def reset_password(self, passw):
		self.password = bcrypt.encrypt(passw)

	def new_email(self, email):
		self.email = email

	def new_reason(self, reason):
		self.reason = reason

	def latest_report(self, date):
		self.date = date

	def new_weekly_goal(self, goal, time):
		self.weekly_goal = goal
		self.weekly_goal_timestamp = time

class Report(db.Model):
	reportID = db.Column(db.Integer, primary_key = True)
	userID = db.Column(db.String(300), db.ForeignKey('user.userID'), nullable = False)
	difficulty = db.Column(db.Integer)
	num_correct = db.Column(db.Integer)
	num_total = db.Column(db.Integer)
	date = db.Column(db.DateTime)

	def __init__(self, user, difficulty, num_correct, num_total, date):
		self.userID = user
		self.difficulty = difficulty
		self.num_correct = num_correct
		self.num_total = num_total
		self.date = date

class Kanji(db.Model):
	kanji_id = db.Column(db.Integer, primary_key = True)
	kanji = db.Column(db.String(20), nullable = False)
	romaji = db.Column(db.String(40), nullable = False)
	difficulty = db.Column(db.Integer, nullable = False)

	def __init__(self, k, r, d):
		self.kanji = k
		self.romaji = r
		self.difficulty = d

	def __repr__(self):
		return self.kanji

