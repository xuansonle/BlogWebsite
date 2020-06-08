#################################################################################### 
# SETTINGS
####################################################################################
# APP
from flask import Flask
app = Flask(__name__)

# SECRET_KEY
import secrets
secrets.token_hex(16)

# DATABASE
from flask_sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myDB.db"
db = SQLAlchemy(app)
# Initialize database from shell
from app import db
db.create_all()

# BCRYPT
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# LOGIN MANAGER
from flask_login import LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login' #function name of the login route
login_manager.login_message_category = 'bootstrap_class' #Please login to access this page


#################################################################################### 
# FORM
####################################################################################
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class NewForm(Flaskform):
    field = StringField(label="field-label", validators=[DataRequired, Length, Email, EqualTo])
    
    picture_field = FileField(label="picture_field_label", validators=[FileAllowed(["jpg","png"])])
    
    def validate_field(self, field):
        
        if "some_condition" == True:
            raise ValidationError("Validation Message")
        
# Form -> routes.py -> template.html: GET
# template.html -> routes.py: POST
    
# routes.py: 
# form = NewForm()    
# form.validate_on_submit()
# form.field.data -> access form data

# template.html:
# form -> enctype 
# {{form.hidden_tag()}} ##add csrf token
# form.field.label(class="bootstrap-class") / form.field(class="bootstrap-class") -> access label and data of form
# form.field.errors -> access errors of form



#################################################################################### 
# DATABASE
####################################################################################
class User(db.Model, UserMixin):
    column = db.Column(db.String, unique=True, nullable=False, primary_key=True, default="default")
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("uft-8") 
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
            return User.query.get(user_id)
        except:
            return None

user = User.query.filter_by()

class Table1(db.Model):
    column = db.Column(db.String, unique=True, nullable=False, primary_key=True, default="default")
    relationship = db.relationship("Table2", backref="ref_name", lazy=True) #ref_name can be access from Table2

class Table2(db.Model):
    foreignKeyColumn = db.Column(db.String, db.ForeignKey("table1.primaryKey"), nullable=False)
    
Table1.query.filter_by().all()  
Table1.query.get_or_404("postID")  
db.session.add()
db.commit()



#################################################################################### 
# USER AUTHENTICATION - LOGIN MANAGER
####################################################################################
password_hashed = bcrypt.generate_password_hash("password").decode("utf-8")
bcrypt.check_password_hash("password_hashed","password")

from flask_login import UserMixin, login_user, logout_user, current_user, login_required
@login_manager.user_loader()
def load_user(user_id):
    return User.query.get(int(user_id))

# routes.py
# @login_required -> need to login to access this route

# template.html 
# {% if current_user.is_authenticated %} -> check if current user is logged in
# {{ current_user.field }} -> get data from current user
#################################################################################### 
# LOGIN LOGOUT
####################################################################################
login_user(user)
logout_user(user)
from flask import request
next_page = request.args.get("next")
    
    
    
#################################################################################### 
# RESET PASSWORD
####################################################################################
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
s = Serializer("secret", 30)
token = s.dumps()


#################################################################################### 
# FLASH_MESSAGES
####################################################################################
from flask import flash
# routes.py
# flash("Flash Message", "bootstrap-class")

# template.html (base.html)
# {% with msgs = get_flashed_messages(with_categories=True)%} -> {{if msgs}} -> {{for category, msg in msgs}}



#################################################################################### 
# PAGINATION
####################################################################################
# routes.py
page = request.args.get("page",1,type=int)
Table1.query.order_by().paginate(page=page, per_page="amount_per_page")
    
# template.html
# {% for post in posts.items %} -> pagination object
# {% for page_num in posts.iter_pages(left_edge, right_edge, left_current, right_current) %} 
# -> if page_num then create the button, else ...



#################################################################################### 
# SEND EMAIL
####################################################################################
import smtplib, os
from email.message import EmailMessage
from flask import url_for

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

msg = EmailMessage()
msg["Subject"] = "Password reset request"
msg["From"] = EMAIL_ADDRESS
msg["To"] = user.email
msg.set_content(
    f"To reset your password, visiting the following link:\n\n"
    f"{url_for('users.reset_password',token=token, _external=True)}\n\n"
    f"If you did not make this request then simply ignore this email and no changes will be made")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

#################################################################################### 
# OTHERS
####################################################################################
# Resize Images
from PIL import Image

i = Image.open("my_image") #open the image
i.thumbnail((125,125), Image.ANTIALIAS) #resize it, keep ratio
i.save("my_path") #save the picture to file system

# Bootstrap Modal for Delete action