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
    USERS = dict(CUR.fetchall()) 
    CUR.execute('SELECT user_id, user_email FROM basket_user')
    EMAILS = dict(CUR.fetchall()) 
    
    CUR.close()
    CONN.close()

    def __init__(self, id):
        if id not in self.USERS or id not in self.EMAILS:
            raise UserNotFoundException
        self.id = id
        self.password = self.USERS[id]
        self.name = self.EMAILS[id]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_name(self):
        return self.name

    @classmethod
    def get(cls, id):
        try:
            return cls.USERS[id]
        except KeyError:
            return None