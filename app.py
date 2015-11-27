from flask import Flask, render_template,json, request, redirect, url_for, request, get_flashed_messages
from login_check import *
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from models import User


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)

@app.route("/")
def main():
   return render_template('index.html')
 
@app.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')

@app.route('/signUp',methods=['GET','POST'])
def signUp():
	if request.method == 'POST':
		conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		cur = conn.cursor()
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		#if len(username)>0:
		#	create_user(username, email, password)
		#conn = psycopg2.connect(database="basketball", user="postgres", password="password")							 
		#cur = conn.cursor()		
		cur.execute("INSERT INTO basket_user (user_id, user_email,user_password) VALUES (%s, %s, %s)",(username, email, password))
		conn.commit()
		cur.close()
		conn.close()
		return redirect(url_for('main'))
	else:
		return render_template("signup.html")


@app.route('/showSignin')
def showSignin():
	return render_template('signin.html')
	

#def login():
#	if request.method == 'POST':
#		username = request.form['username']
#		password = request.form['password']
#		email = request.form['email']
#		if check_login(username, email, password):
#			user = User(username)
#			login_user(user)
		#else:
		#	return redirect(url_for('login'))
#	return render_template('/login')
@app.route('/login', methods=['GET','POST'])
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
def userHome():
	return render_template('userHome.html')		
		
@app.route('/logout')
@login_required
def logout():
    return render_template('index.html')
	
if __name__ =="__main__":
   app.run(debug=True)