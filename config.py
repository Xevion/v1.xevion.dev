import os
basedir = os.path.abspath(os.path.dirname(__file__))

with open('key', 'r') as key:
	key = key.read()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or key
    TEMPLATES_AUTO_RELOAD=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False