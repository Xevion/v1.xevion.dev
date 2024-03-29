import os, json

basedir = os.path.abspath(os.path.dirname(__file__))
keys = json.load(open(os.path.join(basedir, 'keys.json'), 'r'))

class Config(object):
    SPOTIFY_CACHE_TIME = 3600 # Number of seconds before the spotify-explicit program can be regenerated
    REDDIT_SECRET = keys['REDDIT_SECRET']
    DISCORD_TOKEN = keys['DISCORD_TOKEN']
    SECRET_KEY = keys['SECRET_KEY']
    HIDDEN_NUMBER = keys['HIDDEN_NUMBER']
    TEMPLATES_AUTO_RELOAD=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-User settings
    USER_APP_NAME = "Xevion.dev"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True