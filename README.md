# KanjiMaster

A web application to help with Japanese kanji memorization

All credit for music files and png files goes to Team Salvato, Developer of
Doki Doki Literature Club. Their art heavily influenced the design of this site.

Installation instructions
	pip install passlib
	pip install bcrypt
	pip install flask

	See Requirements.txt for all other needed libraries

	Set the environment variable:
		export FLASK_APP=server.py
	If running on windows:
		set FLASK_APP=server.py

	Initialize the database:
		flask initdb

	To start the server:
		flask run

	Open the port specified. It should be port 5000 on most computers

This is known to work on windows. Results on other operating systems are unknown.

TODO:
	Site Tutorial
	Progress Reports
	User Settings
	Kanji Sheets
	Add more content on the site in general
	Fix issues
	Add audio settings
	Add kanji to the list: might wait til encoding is figured out

