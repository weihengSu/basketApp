import psycopg2

def create_user(username, email, password):
	conn = psycopg2.connect("dbname='basketball' user='postgres' "
									 "host='localhost' password='password'")
	cur = conn.cursor()

	cur.execute("INSERT INTO basket_user(user_id, user_email, user_password) VALUES ('" + username + "', '"
				+ email + "', '" + password+ "');")
	conn.commit()
	cur.close()
	conn.close()