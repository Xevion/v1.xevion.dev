# Main Flask and Flask configs
from flask import Flask
from config import Config
# Flask Extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# App & App config setup
app = Flask(__name__)
app.config.from_object(Config)
# App extension setup
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models
from app import routes, simple_routes, hidden, dashboard, custom
app.jinja_env.globals.update(get_hidden=routes.get_hidden)