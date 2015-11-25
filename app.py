from flask import Flask, render_template,json, request
from login_check import *;
app = Flask(__name__)

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

		
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid credentials'
		else:
			return redirect(url_for('hello_world'))
	return render_template('login.html', error=error)
	
		
		
if __name__ =="__main__":
   app.run(debug=True)