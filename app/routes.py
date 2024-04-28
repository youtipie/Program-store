from flask import render_template, redirect, url_for, flash
from app import app, login_manager
from app.aws import generate_public_url
from app.models import *
from app.forms import *


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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login successful")
        redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Register successful")
        redirect(url_for("register"))
    return render_template("register.html", form=form)
