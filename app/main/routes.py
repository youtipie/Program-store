from flask import render_template, redirect, url_for, flash, request
from app import db
from app.aws import generate_public_url
from app.models import User, Category, Game
from app.main import bp


@bp.route("/")
def index():
    categories = db.session.query(Category).all()
    return render_template("home.html", categories=categories)
