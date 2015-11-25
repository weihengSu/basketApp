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

@app.route('/signUp',methods=['POST'])
def signUp():
	if request.method == 'POST':
		username = request.form['inputName']
		email = request.form['inputEmail']
		password = request.form['inputPassword']
		if len(username) > 0:
			create_user(username, email, password)
	return render_template('/')	


@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')
	
#@app.route('/', methods=['GET','POST'])
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

	
		
		
if __name__ =="__main__":
   app.run(debug=True)