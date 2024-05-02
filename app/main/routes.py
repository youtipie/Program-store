from flask import render_template, redirect, url_for, flash, request
from app import db
from app.aws import generate_public_url
from app.models import User, Category, Game
from app.main import bp


@bp.route("/")
def index():
    categories = db.session.query(Category).all()
    page = request.args.get("page", 1, type=int)
    games = db.session.query(Game).paginate(page=page, per_page=5, error_out=False)
    next_url = url_for("main.index", page=games.next_num) \
        if games.has_next else None
    prev_url = url_for("main.index", page=games.prev_num) \
        if games.has_prev else None
    return render_template("index.html", games=games, heading="Найпопулярніші ігри",
                           categories=categories, generate_public_url=generate_public_url,
                           next_url=next_url, prev_url=prev_url)


@bp.route("/category/<string:category_name>")
def category(category_name: str):
    categories = db.session.query(Category).all()
    page = request.args.get('page', 1, type=int)
    games = db.session.query(Game).join(Category).filter_by(name=category_name).paginate(page=page, per_page=5,
                                                                                         error_out=False)
    next_url = url_for("main.category", category_name=category_name, page=games.next_num) \
        if games.has_next else None
    prev_url = url_for("main.category", category_name=category_name, page=games.prev_num) \
        if games.has_prev else None
    return render_template("index.html", games=games,
                           heading=category_name.title(), categories=categories,
                           generate_public_url=generate_public_url,
                           next_url=next_url, prev_url=prev_url)
