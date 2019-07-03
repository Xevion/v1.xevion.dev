from flask_login import UserMixin
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    search_history = db.relationship('Search', backref='user', lazy='dynamic')
    uroles = db.Column(db.String(80), default='')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            raise "{} has no password_hash set!".format(self.__repr__())
        return check_password_hash(self.password_hash, password)
    
    def get_roles(self):
        return self.uroles.split(' ')

    def add_roles(self, roles):
        user_roles = self.uroles.split(' ')
        if type(roles) == str:
            user_roles.append(roles)
        elif type(roles) == list:
            user_roles.extend(roles)
        user_roles = ' '.join(user_roles)
        self.uroles = user_roles

    # Input: ['Insane', ['Fortunate', 'Blessed']]
    # Meaning: Must have 'Insane' role, as well as 'Fortunate' or 'Blessed' roles.
    def has_roles(self, roles):
        user_roles = self.uroles.split(' ')
        for reqrole in roles:
            # If we have this role
            if type(reqrole) == str:
                if reqrole not in user_roles:
                    return False
            # If we have any of  these roles
            elif type(reqrole) == list:
                if not any([subreqrole in user_roles for subreqrole in reqrole]):
                    return False
        return True

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exact_url = db.Column(db.String(160))
    query_args = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Search by {} @ {}>'.format(User.query.filter_by(id=self.user_id).first().username, self.timestamp)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))