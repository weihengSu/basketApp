import psycopg2

def create_user(username, email, password):
	conn = psycopg2.connect("dbname='basketball' user='postgres' "
									 "host='localhost' password='password'")							 
	cur = conn.cursor()
	cur.execute("SELECT user_id FROM basket_users \n"
				"WHERE id = '" + username + "';")
	results = cur.fetchall() 
	if(username not in results):			
		cur.execute("INSERT INTO basket_user(user_id, user_email, user_password) VALUES ('" + username + "', '"+ email + "', '" + password+ "');")
		conn.commit()
		return render_template('/')
	else:
		return render_template('/showSignUp')
	cur.close()
	conn.close()
	
def check_login(username, email, password):
	conn = psycopg2.connect("dbname='basketball' user='postgres' "
									 "host='localhost' password='password'")
	cur = conn.cursor()

	cur.execute("SELECT user_id FROM basket_users \n"
				"WHERE id = '" + username + "';")
	results = cur.fetchall() 
	if (len(results) > 0):
		cur.execute("SELECT user_email, user_password FROM basket_users \n"
					  "WHERE id = '" + username + "';")
		result2 = cur.fetchall()
		if (email == result2[0] and password == result2[1]):
			return render_template()
	cur.close()
	conn.close()

	# Check entered credentials against database entry
	if len(results) == 0:
		print("Found no results.")