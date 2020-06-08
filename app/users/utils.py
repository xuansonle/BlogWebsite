import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def save_picture(upload_picture):
    #randomize the name of the image, make sure that we use the same extension
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(upload_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, "static/profile_pics", picture_filename)
    #resize then save the picture in our server
    output_size = (256, 256)
    im = Image.open(upload_picture)
    im.thumbnail(output_size, Image.ANTIALIAS)
    im.save(picture_path)

    return picture_filename


def remove_picture(current_picture):
    try:
        picture_path = os.path.join(
            current_app.root_path, "static/profile_pics", current_picture)
        os.remove(picture_path)
    except OSError:
        pass


def send_reset_email(user):
    token = user.get_reset_token()

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
