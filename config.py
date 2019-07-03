import os
basedir = os.path.abspath(os.path.dirname(__file__))

with open('hidden', 'r') as hidden:
    hidden = hidden.read()

with open('key', 'r') as key:
    key = key.read()

class Config(object):
    HIDDEN_URL = hidden
    SECRET_KEY = os.environ.get('SECRET_KEY') or key
    TEMPLATES_AUTO_RELOAD=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-User settings
    USER_APP_NAME = "Flask-User QuickStart App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True