# Main Flask and Flask configs
from flask import Flask
from config import Config
# Flask Extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter

# App & App config setup
app = Flask(__name__)
app.config.from_object(Config)
# App extension setup
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
limiter = Limiter(app, default_limits=["10 per minute"])

from app import models
from app import routes, simple_routes, hidden, dashboard
from app import ftbhot, custom, spotify, panzer, sound