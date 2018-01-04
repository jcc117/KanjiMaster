#script file for creating data insertion file

f = open('kanji-insert.py', 'w+')

f.write('#Write all data to the database\n')
f.write('from models import db, User, Report, Kanji\n')
f.write('\n')
f.write('#insert all of the data\n')
f.write('def add_data():\n')

for i in range(1, 501):
	f.write('\tdb.session.add(Kanji(u\'\',\'\', ))\n')

f.write('db.session.commit()\n')