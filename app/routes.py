from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User, Post
from flask import render_template, url_for, flash, redirect, request
import secrets, os
# User Authentication
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:  # check if user already logged in -> back to homepage
        redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # check if user already logged in -> back to homepage
        redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.email.data) | (
            User.username == form.email.data)).first()
        # User Authentication for login: check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # do the log in
            # get the next parameter from the url (this is where we were trying to go to before the login_required blocked us)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login failed! Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

def save_picture(upload_picture):
    #randomize the name of the image, make sure that we use the same extension 
    random_hex=secrets.token_hex(8)
    _, f_ext = os.path.splitext(upload_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path,"static/profile_pics",picture_filename)
    #resize then save the picture in our server
    output_size = (125,125)
    im = Image.open(upload_picture)
    im.thumbnail(output_size)
    im.save(picture_path)
    
    return picture_filename

@app.route("/account", methods=["GET", "POST"])
# force user to login before they can see this page -> need to define where the login route is located (see init.py)
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            current_user.image_file=picture_filename
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("Your account has been updated!","success")
        return redirect(url_for("account")) #->force browser to send a get request
    elif request.method=="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        "static", filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account", image_file=image_file, form=form)
