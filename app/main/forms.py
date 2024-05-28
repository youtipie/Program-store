from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email
from app import db
from app.models import Game


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


class AddGameForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add game")

    def validate_title(self, title):
        game = db.session.query(Game).filter_by(title=title.data).first()
        if game:
            raise ValidationError("Game with such title exists!")


class ChangeGameForm(FlaskForm):
    game_id = HiddenField("Game ID")
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Change game")

    def validate_title(self, title):
        if self.game_id.data:
            current_game = db.session.query(Game).filter_by(id=self.game_id.data).first()
            if current_game and current_game.title == title.data:
                return
        game = db.session.query(Game).filter_by(title=title.data).first()
        if game:
            raise ValidationError("Game with such title exists!")
