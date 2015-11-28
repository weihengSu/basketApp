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
		cur.execute("SELECT user_id FROM basket_user WHERE user_id = %(id)s", {'id': username })		
		result = cur.fetchall()
		if(username not in result[0]):		
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
				return render_template('error.html',error = 'Wrong Email address or Password.')
		else:
			return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
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
		return render_template('userHome.html')
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
			return render_template('view_user.html')
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
			return user_data
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))	
	finally:
		cur.close()
		conn.close()	
	
	
	
	
if __name__ =="__main__":
   app.run(debug=True)