from flask import Flask, render_template,json, request, redirect, url_for, request, get_flashed_messages
from login_check import *
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from models import *
from flask import session
from nocache import *

#The web app is based on python 3.4+. python2 may not be compatible. 

app = Flask(__name__)
app.secret_key = 'secret'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
	hashed_pwd = User.get(user_id)
	if hashed_pwd is not None:
		return User(user_id)
	return None
#sess = Session()


	

@app.route("/")
@nocache
def main():
   return render_template('index.html')
 
@app.route('/showSignUp')
@nocache
def showSignUp():
	return render_template('signup.html')

@app.route('/signUp',methods=['GET','POST'])
@nocache
def signUp():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']	
		cur.execute("SELECT user_id FROM basket_user;")		
		result = cur.fetchall()
		user_list = []
		for i in result:
			user_list.append(i[0])
		if(username not in user_list):		
			cur.execute("INSERT INTO basket_user (user_id, user_email,user_password) VALUES (%s, %s, %s)",(username, email, password))
			conn.commit()
			return redirect(url_for('main'))
		else: 
			return render_template('error.html',error = 'User already exists. Please try again')
		cur.close()
		conn.close()
			
	else:
		return render_template("signup.html")


@app.route('/showSignin')
@nocache
def showSignin():
	return render_template('signin.html')	

	
@app.route('/login', methods=['GET','POST'])
@nocache
def login():
	try: 
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		conn = psycopg2.connect("dbname='basketball' user='postgres' "
									 "host='localhost' password='password'")
		cur = conn.cursor()
		cur.execute("SELECT user_id FROM basket_user WHERE user_id = %(id)s", {'id': username })		
		result = cur.fetchall()
		if len(result) > 0:
			cur.execute("SELECT user_email FROM basket_user WHERE user_id = %(id)s", {'id': username }) 
			result_email = cur.fetchall()
			cur.execute("SELECT user_password FROM basket_user WHERE user_id = %(id)s", {'id': username }) 
			result_password = cur.fetchall()
			
			if (email == result_email[0][0] and password == result_password[0][0]):
				user = User(username)
				login_user(user)
				session['user'] = result[0][0]
				return redirect(url_for('userHome'))
			else:
				return render_template('error.html',error = 'Wrong Email address or password.')
		else:
			return render_template('error.html',error = 'Wrong Email address or password.')
 
 
	except Exception as e:
		return render_template('error.html',error = str(e))
	finally:
		cur.close()
		conn.close()	
		

@app.route('/userHome')
@nocache
@login_required
def userHome():
	if session.get('user'):
		return render_template('userHome.html', user=session.get('user'))
	else:
		return render_template('error.html',error = 'Unauthorized access.')	






		
@app.route('/logout')
@nocache
@login_required
def logout():
	logout_user()
	session.pop('user',None)
#	return render_template('index.html')
	return redirect(url_for('main'))

	
	
	
@app.route('/showViewUser')
@nocache
def showViewUser():
	if session.get('user'):
		username = session.get('user')
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("SELECT user_admin FROM basket_user WHERE user_id = %(id)s", {'id': username })		
		result = cur.fetchall()
		if (result[0][0] == True):
			#return render_template('view_user.html')
			return redirect(url_for('viewUsers'))
		else:
			return render_template('error.html', error = 'You must be an admin to access the page')
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
					
	
@app.route('/viewUsers')
@nocache
@login_required
def viewUsers():
	if session.get('user'):
		username = session.get('user')
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("SELECT user_admin FROM basket_user WHERE user_id = %(id)s", {'id': username })		
		result = cur.fetchall()
		if (result[0][0] == True):
			cur.execute("CREATE VIEW USERS_VIEW AS SELECT user_id, user_email, user_admin FROM	basket_user;")
			cur.execute("SELECT * FROM USERS_VIEW;")
			user_data = cur.fetchall()
			users_data = []
			sub_data =[]
			for user in user_data:
			#	sub_data.append(user[0])
				users_data.append(user)
			return render_template('view_user.html', users_data = users_data, user = session.get('user'))
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
	
@app.route('/showPlayerInfo')
@nocache
def showPlayerInfo():
	return render_template('player_info.html', user = session.get('user'))


@app.route('/addPlayerInfo',methods=['GET','POST'])
@nocache
def addPlayerInfo():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		playerId = request.form['player_id']
		playerName = request.form['player_name']
		playerPosition = request.form['player_position']	
		teamId = request.form['team_id']		
		cur.execute("SELECT player_id FROM player_info;")		
		result = cur.fetchall()
		player_list = []
		for i in result:
			player_list.append(i[0])
		if(playerId not in player_list):		
			cur.execute("INSERT INTO player_info (player_id, player_name, player_position, team_id) VALUES (%s, %s, %s, %s)",(playerId, playerName, playerPosition, teamId))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Player already exists. Try to add another player.')
		cur.close()
		conn.close()
	else:
		return render_template("userHome.html")

@app.route('/showViewPlayer')
@nocache
def showViewPlayer():
	return redirect(url_for('viewPlayers'))

					
	
@app.route('/viewPlayers')
@nocache
@login_required
def viewPlayers():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW PLAYERS_VIEW AS SELECT player_id, player_name, player_position, team_id FROM player_info;")
		cur.execute("SELECT * FROM PLAYERS_VIEW;")
		players_data = cur.fetchall()
		return render_template('view_playerInfo.html', players_data = players_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	




		
		
	




	
@app.route('/showPlayerStat')
@nocache
def showPlayerStat():
	return render_template('player_stat.html', user = session.get('user'))


@app.route('/addPlayerStat',methods=['GET','POST'])
@nocache
def addPlayerStat():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		playerId = request.form['playerS_id']
		playerName = request.form['playerS_name']
		playerPoints = request.form['player_points']
		rebounds = request.form['rebounds']
		assists = request.form['rebounds']
		steals = request.form['steals']
		cur.execute("SELECT player_id FROM player_stat;")		
		result = cur.fetchall()
		player_list = []
		for i in result:
			player_list.append(i[0])
		cur.execute("SELECT player_id FROM player_info;")
		resultI = cur.fetchall()
		playerI_list = []
		for i in resultI:
			playerI_list.append(i[0])
		
		if(playerId not in player_list and playerId in playerI_list):		
			cur.execute("INSERT INTO player_stat (player_id, player_name, player_points, rebounds, assists, steals) VALUES (%s, %s, %s, %s, %s, %s)",(playerId, playerName, playerPoints, rebounds, assists, steals))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Player statistics information already exists or player has not been added. Try to add another player.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewPlayerStat')
@nocache
def showViewPlayerStat():
	return redirect(url_for('viewPlayerStat'))

					
	
@app.route('/viewPlayerStat')
@nocache
@login_required
def viewPlayerStat():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW PLAYERSTAT_VIEW AS SELECT player_id, player_name, player_points, rebounds, assists, steals FROM player_stat;")
		cur.execute("SELECT * FROM PLAYERSTAT_VIEW;")
		players_data = cur.fetchall()
		return render_template('view_playerStat.html', players_data = players_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	




		
		
		
		







	
@app.route('/showTeamInfo')
@nocache
def showTeamInfo():
	return render_template('team_info.html', user = session.get('user'))


@app.route('/addTeamInfo',methods=['GET','POST'])
@nocache
def addTeamInfo():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		teamId = request.form['team_id']
		teamName = request.form['team_name']
		divisionName = request.form['division_name']	
		cur.execute("SELECT team_id FROM team;")		
		result = cur.fetchall()
		team_list = []
		for i in result:
			team_list.append(i[0])
		if(teamId not in team_list):		
			cur.execute("INSERT INTO team (team_id, team_name, division_name) VALUES (%s, %s, %s)",(teamId, teamName, divisionName))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Team already exists. Try to add another team.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewTeam')
@nocache
def showViewTeam():
	return redirect(url_for('viewTeams'))

					
	
@app.route('/viewTeams')
@nocache
@login_required
def viewTeams():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW TEAM_VIEW AS SELECT team_id, team_name, division_name FROM team;")
		cur.execute("SELECT * FROM TEAM_VIEW;")
		teams_data = cur.fetchall()
		return render_template('view_teamInfo.html', teams_data = teams_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()			
		
		
		
		
		
		
		
		
		
		
		







	
@app.route('/showTeamStat')
@nocache
def showTeamStat():
	return render_template('team_stat.html', user = session.get('user'))


@app.route('/addTeamStat',methods=['GET','POST'])
@nocache
def addTeamStat():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		teamId = request.form['team_id']
		teamName = request.form['team_name']
		divisionName = request.form['division_name']
		teamPoints = request.form['team_points']
		rebounds = request.form['rebounds']
		assists = request.form['assists']
		steals = request.form['steals']			
		cur.execute("SELECT team_id FROM team_stat;")		
		result = cur.fetchall()
		team_list = []
		for i in result:
			team_list.append(i[0])
		cur.execute("SELECT team_id FROM team;")
		resultI = cur.fetchall()
		teamI_list = []
		for i in resultI:
			teamI_list.append(i[0])
		
		if(teamId not in team_list and teamId in teamI_list):		
			cur.execute("INSERT INTO team_stat (team_id, team_name, division_name, team_points, rebounds, assists, steals) VALUES (%s, %s, %s, %s, %s, %s, %s)",(teamId, teamName, divisionName, teamPoints, rebounds, assists, steals))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Team statistics information already exists or Team has not been added. Try to add another player.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewTeamStat')
@nocache
def showViewTeamStat():
	return redirect(url_for('viewTeamStat'))

					
	
@app.route('/viewTeamStat')
@nocache
@login_required
def viewTeamStat():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW TEAMSTAT_VIEW AS SELECT team_id, team_name, division_name, team_points, rebounds, assists, steals FROM team_stat;")
		cur.execute("SELECT * FROM TEAMSTAT_VIEW;")
		teams_data = cur.fetchall()
		return render_template('view_teamStat.html', teams_data = teams_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	




		














	
@app.route('/showPlayerInjury')
@nocache
def showPlayerInjury():
	return render_template('player_injury.html', user = session.get('user'))


@app.route('/addPlayerInjury',methods=['GET','POST'])
@nocache
def addPlayerInjury():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		playerId = request.form['player_id']
		playerName = request.form['player_name']
		injuryName = request.form['injury_name']		
		cur.execute("SELECT player_id FROM player_injury;")		
		result = cur.fetchall()
		players_list = []
		for i in result:
			players_list.append(i[0])
		cur.execute("SELECT player_id FROM player_info;")
		resultI = cur.fetchall()
		playerI_list = []
		for i in resultI:
			playerI_list.append(i[0])
		
		if(playerId not in players_list and playerId in playerI_list):		
			cur.execute("INSERT INTO player_injury (player_id, player_name, injury_name) VALUES (%s, %s, %s)",(playerId, playerName, injuryName))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Player Injury information already exists or Team has not been added. Try to add another player.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewPlayerInjury')
@nocache
def showViewPlayerInjury():
	return redirect(url_for('viewPlayerInjury'))

					
	
@app.route('/viewPlayerInjury')
@nocache
@login_required
def viewPlayerInjury():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW PLAYERINJURY_VIEW AS SELECT player_id, player_name, injury_name FROM player_injury;")
		cur.execute("SELECT * FROM PLAYERINJURY_VIEW;")
		players_data = cur.fetchall()
		return render_template('view_playerInjury.html', players_data = players_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	

		



		
		
		
		
		
		
		
		

		
		


	
@app.route('/showCoach')
@nocache
def showCoach():
	return render_template('team_coach.html', user = session.get('user'))


@app.route('/addCoach',methods=['GET','POST'])
@nocache
def addCoach():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		teamId = request.form['team_id']
		teamName = request.form['team_name']
		coachName = request.form['coach_name']		
		cur.execute("SELECT team_id FROM team_coach;")		
		result = cur.fetchall()
		team_list = []
		for i in result:
			team_list.append(i[0])
		cur.execute("SELECT team_id FROM team;")
		resultI = cur.fetchall()
		coach_list = []
		for i in resultI:
			coach_list.append(i[0])
		
		if(teamId not in team_list and teamId in coach_list):		
			cur.execute("INSERT INTO team_coach (team_id, team_name, coach_name) VALUES (%s, %s, %s)",(teamId, teamName, coachName))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Coach information already exists or Team has not been added. Try to add a team or a coach of an existing team.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewCoach')
@nocache
def showViewCoach():
	return redirect(url_for('viewCoach'))

					
	
@app.route('/viewCoach')
@nocache
@login_required
def viewCoach():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW COACH_VIEW AS SELECT team_id, team_name, coach_name FROM team_coach;")
		cur.execute("SELECT * FROM COACH_VIEW;")
		coaches_data = cur.fetchall()
		return render_template('view_coach.html', coaches_data = coaches_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
		
		
		
		





		
		
		
		
		
		
		



	
@app.route('/showDivision')
@nocache
def showDivision():
	return render_template('division.html', user = session.get('user'))


@app.route('/addDivision',methods=['GET','POST'])
@nocache
def addDivision():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		divisionId = request.form['division_id']
		divisionName = request.form['division_name']
		cur.execute("SELECT division_id FROM division;")		
		result = cur.fetchall()
		division_list = []
		for i in result:
			division_list.append(i[0])
		if(divisionId not in division_list):		
			cur.execute("INSERT INTO division (division_id, division_name) VALUES (%s, %s)",(divisionId, divisionName))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Division already exists. Try to add another division.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewDivision')
@nocache
def showViewDivision():
	return redirect(url_for('viewDivision'))

					
	
@app.route('/viewDivision')
@nocache
@login_required
def viewDivision():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW DIVISION_VIEW AS SELECT division_id, division_name FROM division;")
		cur.execute("SELECT * FROM DIVISION_VIEW;")
		divisions_data = cur.fetchall()
		return render_template('view_division.html', divisions_data = divisions_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
		
		
		
		
		
		












	
@app.route('/showAttendance')
@nocache
def showAttendance():
	return render_template('attendance.html', user = session.get('user'))


@app.route('/addAttendance',methods=['GET','POST'])
@nocache
def addAttendance():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		divisionId = request.form['division_id']
		divisionName = request.form['division_name']
		numOfAttendee = request.form['number_of_attendee']		
		cur.execute("SELECT division_id FROM attendance;")		
		result = cur.fetchall()
		division_list = []
		for i in result:
			division_list.append(i[0])
		cur.execute("SELECT division_id FROM division;")
		resultI = cur.fetchall()
		divisionI_list = []
		for i in resultI:
			divisionI_list.append(i[0])
		
		if(divisionId not in division_list and divisionId in divisionI_list):		
			cur.execute("INSERT INTO attendance (division_id, division_name, number_of_attendee) VALUES (%s, %s, %s)",(divisionId, divisionName, numOfAttendee))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Attendance information already exists or division has not been added. Try to add a division or the attendance information of an existing team.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewAttendance')
@nocache
def showViewAttendance():
	return redirect(url_for('viewAttendance'))

					
	
@app.route('/viewAttendance')
@nocache
@login_required
def viewAttendance():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW Attendance_VIEW AS SELECT division_id, division_name, number_of_attendee FROM attendance;")
		cur.execute("SELECT * FROM Attendance_VIEW;")
		attendance_data = cur.fetchall()
		return render_template('view_attendance.html', attendance_data = attendance_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
		
		










	
@app.route('/showReferee')
@nocache
def showReferee():
	return render_template('referee.html', user = session.get('user'))


@app.route('/addReferee',methods=['GET','POST'])
@nocache
def addReferee():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		divisionId = request.form['division_id']
		divisionName = request.form['division_name']
		refereeId = request.form['referee_id']
		refereeName = request.form['referee_name']		
		cur.execute("SELECT division_id FROM referee;")		
		result = cur.fetchall()
		division_list = []
		for i in result:
			division_list.append(i[0])
		cur.execute("SELECT division_id FROM division;")
		resultI = cur.fetchall()
		divisionI_list = []
		for i in resultI:
			divisionI_list.append(i[0])
		
		if(divisionId not in division_list and divisionId in divisionI_list):		
			cur.execute("INSERT INTO referee (division_id, division_name, referee_id, referee_name) VALUES (%s, %s, %s, %s)",(divisionId, divisionName, refereeId, refereeName))
			conn.commit()
			return redirect(url_for('userHome'))
		else: 
			return render_template('error.html',error = 'Referee information already exists or division has not been added. Try to add a division or the referee information of an existing team.')
		cur.close()
		conn.close()
			
	else:
		return render_template("userHome.html")

@app.route('/showViewReferee')
@nocache
def showViewReferee():
	return redirect(url_for('viewReferee'))

					
	
@app.route('/viewReferee')
@nocache
@login_required
def viewReferee():
	try:
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		cur.execute("CREATE VIEW referee_VIEW AS SELECT division_id, division_name, referee_id, referee_name FROM referee;")
		cur.execute("SELECT * FROM referee_VIEW;")
		referee_data = cur.fetchall()
		return render_template('view_referee.html', referee_data = referee_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
		
		




		
		
		


	
	
if __name__ =="__main__":
   app.run(debug=True)