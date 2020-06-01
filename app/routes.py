from app import app, db, bcrypt
from app.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                       PostForm, RequestResetForm, ResetPasswordForm)
from app.models import User, Post
from flask import render_template, url_for, flash, redirect, request, abort
import secrets
import os
from flask_login import login_user, current_user, logout_user, login_required ## User Authentication
from PIL import Image
from flask_mail import Message
import smtplib
from email.message import EmailMessage

EMAIL_ADRESS = os.environ.get("EMAIL_ADRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:  # check if user already logged in -> back to homepage
        return redirect(url_for("home"))
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
        return redirect(url_for("home"))
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
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(upload_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, "static/profile_pics", picture_filename)
    #resize then save the picture in our server
    output_size = (256, 256)
    im = Image.open(upload_picture)
    im.thumbnail(output_size, Image.ANTIALIAS)
    im.save(picture_path)

    return picture_filename


def remove_picture(current_picture):
    try:
        picture_path = os.path.join(
            app.root_path, "static/profile_pics", current_picture)
        os.remove(picture_path)
    except OSError:
        pass


@app.route("/account", methods=["GET", "POST"])
# force user to login before they can see this page -> need to define where the login route is located (see init.py)
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            remove_picture(current_user.image_file)
            current_user.image_file = picture_filename
            db.session.commit()
        if (current_user.username != form.username.data) or (current_user.email != form.email.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
        flash("Your account has been updated!", "success")
        # ->force browser to send a get request
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        "static", filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", title="New Post", form=form, legend="New Post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title="Update Post", form=form, legend="Update Post")


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "info")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()

    msg = EmailMessage()    
    msg["Subject"] = "Password reset request"
    msg["From"] = EMAIL_ADRESS
    msg["To"] = user.email
    msg.set_content(
        f"To reset your password, visiting the following link:\n\n"\
        f"{url_for('reset_password',token=token, _external=True)}\n\n"\
        f"If you did not make this request then simply ignore this email and no changes will be made")

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
        smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:  # check if user already logged in -> back to homepage
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email with instructions to reset your password has been sent.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:  # check if user already logged in -> back to homepage
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
            user.password = hashed_password
            db.session.commit()
            flash(
                "Your password has been updated! You are now able to log in.", "success")
            return redirect(url_for("login"))
        return render_template("reset_password.html", title="Reset Password", form=form)
