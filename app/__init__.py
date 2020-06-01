from flask import Flask
from flask_sqlalchemy import SQLAlchemy #database
from flask_bcrypt import Bcrypt #encode the password
from flask_login import LoginManager #extension to manage sessions
from flask_mail import Mail
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "d6a4b3ef837f92a6426490304a392326"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login" #set the login route
login_manager.login_message_category = "info" #set the (bootstrap) class for the login message

# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 587
# app.config["MAIL_USER_TLS"] = True
# app.config['MAIL_USE_SSL'] = False
# app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
# app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
# mail = Mail(app)

from app import routes