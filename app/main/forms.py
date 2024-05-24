from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email


class EmailForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField("New Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Change")

    def validate_password(self, password):
        user = current_user
        if not user.check_password(password.data):
            raise ValidationError("Wrong password!")


class PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("New Password", validators=[DataRequired()])
    submit = SubmitField("Change")

    def validate_password(self, password):
        user = current_user
        if not user.check_password(password.data):
            raise ValidationError("Wrong password!")


class AvatarForm(FlaskForm):
    avatar = FileField("Avatar",
                       validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField("Change")


class CommentForm(FlaskForm):
    comment = TextAreaField("Enter your comment", validators=[DataRequired()])
    submit = SubmitField("Submit")
