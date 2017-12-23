#Models/Schemas

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	userID = db.Column(db.String(20), primary_key = True)
	password = db.Column(db.String(20), nullable = False)
	reports = db.relationship('Report', backref = 'user', lazy = 'dynamic')

	def __init__(self, id, passw):
		self.userID = id
		self.password = passw

class Report(db.Model):
	reportID = db.Column(db.Integer, primary_key = True)
	userID = db.Column(db.String(20), db.ForeignKey('user.userID'), nullable = False)
	difficulty = db.Column(db.Integer)

	def __init__(self, id, user):
		self.reportID = id
		self.userID = user

class Kanji(db.Model):
	kanji_id = db.Column(db.Integer, primary_key = True)
	kanji = db.Column(db.String(20), nullable = False)
	romaji = db.Column(db.String(40), nullable = False)

	def __init__(self, k_id, k, r):
		self.kanji_id = k_id
		self.kanji = k
		self.romaji = r

	def __repr__(self):
		return self.kanji

