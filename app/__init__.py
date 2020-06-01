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
login_manager.login_view = "users.login" #set the login route
login_manager.login_message_category = "info" #set the (bootstrap) class for the login message

from app.main.routes import main
from app.posts.routes import posts
from app.users.routes import users

app.register_blueprint(main)
app.register_blueprint(posts)
app.register_blueprint(users)