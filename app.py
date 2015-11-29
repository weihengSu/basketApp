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
		playerIncome = request.form['player_income']
		playerPosition = request.form['player_position']		
		cur.execute("SELECT player_id FROM player_info;")		
		result = cur.fetchall()
		player_list = []
		for i in result:
			player_list.append(i[0])
		if(playerId not in player_list):		
			cur.execute("INSERT INTO player_info (player_id, player_name, player_income, player_position) VALUES (%s, %s, %s, %s)",(playerId, playerName, playerIncome, playerPosition))
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
		cur.execute("CREATE VIEW PLAYERS_VIEW AS SELECT player_id, player_name, player_income, player_position FROM	player_info;")
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
		playerTwoPoints = request.form['player_twoPoints']
		playerThreePoints = request.form['player_threePoints']		
		cur.execute("SELECT playerStat_id FROM player_stat;")		
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
			cur.execute("INSERT INTO player_stat (playerStat_id, playerStat_name, player_twoPoints, player_threePoints) VALUES (%s, %s, %s, %s)",(playerId, playerName, playerTwoPoints, playerThreePoints))
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
		cur.execute("CREATE VIEW PLAYERSTAT_VIEW AS SELECT playerStat_id, playerStat_name, player_twoPoints, player_threePoints FROM player_stat;")
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
		conferenceId = request.form['conference_id']	
		cur.execute("SELECT team_id FROM team;")		
		result = cur.fetchall()
		team_list = []
		for i in result:
			team_list.append(i[0])
		if(teamId not in team_list):		
			cur.execute("INSERT INTO team (team_id, team_name, conference_id) VALUES (%s, %s, %s)",(teamId, teamName, conferenceId))
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
		cur.execute("CREATE VIEW TEAM_VIEW AS SELECT team_id, team_name, conference_id FROM team;")
		cur.execute("SELECT * FROM TEAM_VIEW;")
		teams_data = cur.fetchall()
		return render_template('view_teamInfo.html', teams_data = teams_data, user = session.get('user'))
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()			
		
		
		
		
		
		
		
		
		
		
		
		
		
		


	
	
if __name__ =="__main__":
   app.run(debug=True)