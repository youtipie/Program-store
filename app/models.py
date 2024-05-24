import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.aws import generate_public_url
from hashlib import md5
import jwt
from jwt.exceptions import InvalidTokenError
from time import time
from app import db
from flask import current_app


class UserGameRating(db.Model):
    __tablename__ = "user_game_rating"
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
    game_id = db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True)
    rating = db.Column("rating", db.Integer, nullable=True)

    user = db.relationship("User", backref="games_rated")
    game = db.relationship("Game", backref="users_rated")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    download_count = db.Column(db.Integer, nullable=False, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    avatar_path = db.Column(db.String(150), unique=True)
    reg_date = db.Column(db.DateTime, default=lambda: datetime.datetime.utcnow())
    comments = relationship('Comment', back_populates='user')

    @property
    def ratings(self):
        return db.session.query(UserGameRating).filter_by(user_id=self.id).count()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        if self.avatar_path:
            return generate_public_url(self.avatar_path)
        else:
            digest = md5(self.email.lower().encode("utf-8")).hexdigest()
            return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id, "exp": time() + expires_in}, current_app.config['SECRET_KEY'],
                          algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])["reset_password"]
        except InvalidTokenError or KeyError or TypeError:
            return None
        return db.session.query(User).filter_by(id=user_id).first()


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    description = db.Column(db.Text, nullable=False)
    last_changed = db.Column(db.DateTime, default=lambda: datetime.datetime.utcnow())

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
    popularity = db.Column(db.Integer, default=0, index=True)

    comments = relationship('Comment', back_populates='game')

    @property
    def rating(self):
        rating = db.session.query(
            func.round(func.avg(UserGameRating.rating), 0).label('average_rating')
        ).filter(
            UserGameRating.game_id == self.id
        ).scalar()
        if rating:
            return rating
        else:
            return 0

    def create_popularity_token(self, expires_in=600):
        return jwt.encode({"game_id": self.id, "exp": time() + expires_in}, current_app.config['SECRET_KEY'],
                          algorithm="HS256")

    @staticmethod
    def verify_popularity_token(token):
        try:
            game_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])["game_id"]
        except InvalidTokenError or KeyError or TypeError:
            return None
        return db.session.query(Game).filter_by(id=game_id).first()

    def create_rating_token(self, user_id, rating, expires_in=600):
        return jwt.encode({"game_id": self.id, "user_id": user_id, "rating": rating, "exp": time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm="HS256")

    @staticmethod
    def verify_rating_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            game_id = data["game_id"]
            user_id = data["user_id"]
            rating = data["rating"]
        except InvalidTokenError or KeyError or TypeError:
            return None, None, None
        user = db.session.query(User).filter_by(id=user_id).first()
        game = db.session.query(Game).filter_by(id=game_id).first()
        if game not in [g.game for g in user.games_rated]:
            return game, user, rating
        else:
            return None, None, None

    def to_dict(self):
        return {
            "id": self.id,
            "poster": generate_public_url("data/" + self.folder_name + "/poster.jpg"),
            "title": self.title,
            "category_name": self.category.name,
            "category_id": self.category_id,
            "description": self.description,
            "last_changed": self.last_changed,
            "is_paid": self.is_paid,
            "version": self.version,
            "apk_name": self.apk_name,
            "apk_size": self.apk_size,
            "cache_name": self.cache_name,
            "cache_size": self.cache_size,
            "images": [generate_public_url("data/" + image.path) for image in self.images],
            "rating": self.rating,
            "popularity": self.popularity,
            "game_url": f"game?id={self.id}",
            "apk_url": generate_public_url(f"data/{self.folder_name}/{self.apk_name}"),
            "cache_url": generate_public_url(f"data/{self.folder_name}/{self.cache_name}") if self.cache_name else None
        }


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    games = db.relationship("Game", backref="category")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=lambda: datetime.datetime.utcnow(), index=True)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='comments')

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = relationship('Game', back_populates='comments')

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "content": self.content,
            "username": self.user.username,
            "user_pfp": self.user.avatar(25)
        }
