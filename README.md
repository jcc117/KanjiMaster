# KanjiMaster

A web application to help with Japanese kanji memorization

All credit for music files and png files goes to Team Salvato, Developer of
Doki Doki Literature Club. Their artwork acts as placeholders for the time being.

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

	Open the port specified. It should be port 5000 on most machines

This is known to work on windows and and the chrome web browser. Results on other operating systems and browsers are unknown.

	TODO:
	Site Tutorial (pending),    
	Add more content on the site in general, 
	Set Load screen for ajax requests (in a clean way),
	Add kanji to the list, 
	Fix other issues

