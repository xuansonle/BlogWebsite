from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # database
from flask_bcrypt import Bcrypt  # encode the password
from flask_login import LoginManager  # extension to manage sessions
from flask_mail import Mail
import os
from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"  # set the login route
login_manager.login_message_category = "info" # set the (bootstrap) class for the login message


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.users.routes import users
    from app.posts.routes import posts
    from app.main.routes import main
    from app.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app
