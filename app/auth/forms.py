from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import db
from app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Log in")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat password", validators=[DataRequired(), EqualTo("password")])
    recaptcha = RecaptchaField()
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.query(User).filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("User with such username exists. Log in or use other username.")

    def validate_email(self, email):
        user = db.session.query(User).filter_by(username=email.data).first()
        if user is not None:
            raise ValidationError("User with such email exists. Log in or use other email.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Recover")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat password', validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Confirm")
