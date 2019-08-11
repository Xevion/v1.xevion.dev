from flask import abort
from flask_login import UserMixin
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

# Just a note, my role system is really quite terrible, but I've implemented as good as a system as I can for a simple RBAC without Hierarchy.
# Once could create a complex system, but it would be better to properly work with SQLAlchemy to create proper permissions, hierarchy, parent/child etc. rather than to work with simple strings.
# One should look into perhaps Pickled Pytthon objects if they were interested in simplfiying interactions while opening a lot more data storage.
@login.user_loader
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    register_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(64))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    search_history = db.relationship('Search', backref='user', lazy='dynamic')
    uroles = db.Column(db.String(80), default='')
    about_me = db.Column(db.String(320))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    show_email = db.Column
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            raise "{} has no password_hash set!".format(self.__repr__())
        return check_password_hash(self.password_hash, password)
    
    # Retains order while making sure that there are no duplicate role values and they are capitalized 
    def post_role_processing(self):
        user_roles = self.get_roles()
        user_roles = list(dict.fromkeys(user_roles))
        self.uroles = ' '.join([role.title() for role in user_roles])
        self.uroles = self.uroles.strip()

    def delete_role(self, role):
        return self.delete_roles([role])

    # Will return True if successful, else False if a role didn't exist
    def delete_roles(self, roles, ignore=True):
        user_roles = self.get_roles()
        success = True
        for role in roles:
            try:
                user_roles.remove(role)
            except ValueError as e:
                if not ignore:
                    raise e
                success = False
        return success
                
    def get_roles(self):
        return self.uroles.split(' ')

    def add_role(self, role):
        self.add_roles([role])

    def add_roles(self, roles, postprocess=True):
        user_roles = self.get_roles()
        # Ensure whitespace is replaced with a underscore
        roles = ['_'.join(role.split()) for role in roles]
        if type(roles) == str:
            user_roles.append(roles)
        elif type(roles) == list:
            user_roles.extend(roles)
        user_roles = ' '.join(user_roles)
        self.uroles = user_roles
        if postprocess:
            self.post_role_processing()
        
    def has_role(self, role):
        return self.has_roles([role])

    # Input: ['Insane', ['Fortunate', 'Blessed']]
    # Meaning: Must have 'Insane' role, as well as 'Fortunate' or 'Blessed' roles.
    def has_roles(self, roles):
        user_roles = self.get_roles()
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