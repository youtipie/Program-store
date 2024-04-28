from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user
from urllib.parse import urlsplit
from app import app, db, login_manager
from app.aws import generate_public_url
from app.models import User, Category, Game
from app.forms import LoginForm, RegisterForm


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
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password")
            return redirect(url_for("login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Вітаємо, Ви зареєструвались. Тепер можете увійти!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
