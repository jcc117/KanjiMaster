#Models/Schemas

from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt

db = SQLAlchemy()

class User(db.Model):
	userID = db.Column(db.String(300), primary_key = True)
	password = db.Column(db.String(300), nullable = False)
	reports = db.relationship('Report', backref = 'user', lazy = 'dynamic')

	def __init__(self, id, passw):
		self.userID = id
		self.password = bcrypt.encrypt(passw)

	def validate_password(self, passw):
		return bcrypt.verify(passw, self.password)

class Report(db.Model):
	reportID = db.Column(db.Integer, primary_key = True)
	userID = db.Column(db.String(300), db.ForeignKey('user.userID'), nullable = False)
	difficulty = db.Column(db.Integer)

	def __init__(self, id, user):
		self.reportID = id
		self.userID = user

class Kanji(db.Model):
	kanji_id = db.Column(db.Integer, primary_key = True)
	kanji = db.Column(db.String(20), nullable = False)
	romaji = db.Column(db.String(40), nullable = False)
	difficulty = db.Column(db.Integer, nullable = False)

	def __init__(self, k_id, k, r, d):
		self.kanji_id = k_id
		self.kanji = k
		self.romaji = r
		self.difficulty = d

	def __repr__(self):
		return self.kanji

