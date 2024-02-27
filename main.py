import json
import os
from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
import functools

from db import db_init
from models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/ProgramStoreDataBase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

login_manager = LoginManager()
login_manager.init_app(app)


def replace_special_characters(input_text):
    special_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    for char in special_characters:
        input_text = input_text.replace(char, '')

    return input_text


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    categories = db.session.query(Category).all()
    return render_template("index.html", games=db.session.query(Game).all(), heading="Найпопулярніші ігри",
                           categories=categories)


@app.route("/category/<string:category_name>")
def category(category_name: str):
    categories = db.session.query(Category).all()
    return render_template("index.html", games=db.session.query(Category).filter_by(name=category_name).first().games,
                           heading=category_name.title(), categories=categories)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
