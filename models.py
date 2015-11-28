from flask.ext.login import UserMixin
import psycopg2





# Take care of User model
class UserNotFoundException(Exception):
	pass


class User(UserMixin):


	CONN = psycopg2.connect("dbname='basketball' user='postgres' "
									 "host='localhost' password='password'")	
	CUR = CONN.cursor()
	CUR.execute('SELECT user_id, user_password FROM basket_user')
	USER = dict(CUR.fetchall()) 
	CUR.execute('SELECT user_id, user_email FROM basket_user')
	EMAIL = dict(CUR.fetchall()) 
	CUR.execute('SELECT user_id, user_admin FROM basket_user')
	USER_ADMIN = dict(CUR.fetchall()) 
	
	CUR.close()
	CONN.close()

	def __init__(self, user_id):
		if user_id not in self.USER or user_id not in self.EMAIL or user_id not in self.USER_ADMIN:
			raise UserNotFoundException
		self.user_id = user_id
		self.password = self.USER[user_id]
		self.name = self.EMAIL[user_id]
		self.user_admin = self.USER_ADMIN[user_id]

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.user_id
	
	def get_role(self):
		return self.user_admin

	def get_name(self):
		return self.name

	@classmethod
	def get(cls, user_id):
		try:
			return cls.USER[user_id]
		except KeyError:
			return None