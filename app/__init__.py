from app.users.routes import users
from app.posts.routes import posts
from app.main.routes import main
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # database
from flask_bcrypt import Bcrypt  # encode the password
from flask_login import LoginManager  # extension to manage sessions
from flask_mail import Mail
import os
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "users.login"  # set the login route
# set the (bootstrap) class for the login message
login_manager.login_message_category = "info"


app.register_blueprint(main)
app.register_blueprint(posts)
app.register_blueprint(users)
