from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import db
from app.models import User


class LoginForm(FlaskForm):
    email = StringField("Пошта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Увійти")


class RegisterForm(FlaskForm):
    username = StringField("Нікнейм", validators=[DataRequired()])
    email = StringField("Пошта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password2 = PasswordField("Повторіть пароль", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Зареєструватись")

    def validate_username(self, username):
        user = db.session.query(User).filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Користувач з таким нікнеймом уже існує. Увійдіть або використайте інший нікнейм.")

    def validate_email(self, email):
        user = db.session.query(User).filter_by(username=email.data).first()
        if user is not None:
            raise ValidationError("Користувач з такою поштою уже існує. Увійдіть або використайте іншу пошту.")
