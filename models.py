from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    description = db.Column(db.Text, nullable=False)

    # Poster image always named "poster.jpg"
    # poster = db.Column(db.String(200), nullable=False)

    is_paid = db.Column(db.Boolean, nullable=False)
    version = db.Column(db.String(50))
    apk_name = db.Column(db.String(200), unique=True, nullable=False)
    apk_size = db.Column(db.Float, nullable=False)
    cache_name = db.Column(db.String(200), unique=True)
    cache_size = db.Column(db.Float, default=0)
    folder_name = db.Column(db.String(200), nullable=False, unique=True)
    images = relationship('Image', backref='game', lazy=True)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    games = db.relationship("Game", backref="category")
