from flask import render_template
from app import app, login_manager, generate_public_url
from app.models import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    categories = db.session.query(Category).all()
    return render_template("index.html", games=db.session.query(Game).all(), heading="Найпопулярніші ігри",
                           categories=categories, generate_public_url=generate_public_url)


@app.route("/category/<string:category_name>")
def category(category_name: str):
    categories = db.session.query(Category).all()
    return render_template("index.html", games=db.session.query(Category).filter_by(name=category_name).first().games,
                           heading=category_name.title(), categories=categories,
                           generate_public_url=generate_public_url)
