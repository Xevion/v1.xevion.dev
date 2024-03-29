from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    RadioField,
    FileField,
)
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email, URL

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    @staticmethod
    def validate_username(username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("That username is not available.")

    @staticmethod
    def validate_email(email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("That email address is not available.")


class ProfileSettingsForm(FlaskForm):
    show_email = RadioField(
        "Show Email",
        default="registered",
        choices=[
            ("public", "Public"),
            ("registered", "Registered Users Only"),
            ("hidden", "Hidden"),
        ],
    )
    submit = SubmitField("Save Profile Settings")


class ProfilePictureForm(FlaskForm):
    profile_picture_file = FileField("Upload Profile Picture")
    profile_picture_url = StringField("Use URL for Profile Picture", validators=[URL()])
    submit = SubmitField("Submit Profile Picture")
