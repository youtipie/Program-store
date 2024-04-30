from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user
from urllib.parse import urlsplit
from app import app, db, login_manager
from app.aws import generate_public_url
from app.models import User, Category, Game
from app.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    categories = db.session.query(Category).all()
    page = request.args.get('page', 1, type=int)
    games = db.session.query(Game).paginate(page=page, per_page=5, error_out=False)
    next_url = url_for('index', page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('index', page=games.prev_num) \
        if games.has_prev else None
    return render_template("index.html", games=games, heading="Найпопулярніші ігри",
                           categories=categories, generate_public_url=generate_public_url,
                           next_url=next_url, prev_url=prev_url)


@app.route("/category/<string:category_name>")
def category(category_name: str):
    categories = db.session.query(Category).all()
    page = request.args.get('page', 1, type=int)
    games = db.session.query(Game).join(Category).filter_by(name=category_name).paginate(page=page, per_page=5,
                                                                                         error_out=False)
    next_url = url_for('category', category_name=category_name, page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('category', category_name=category_name, page=games.prev_num) \
        if games.has_prev else None
    return render_template("index.html", games=games,
                           heading=category_name.title(), categories=categories,
                           generate_public_url=generate_public_url,
                           next_url=next_url, prev_url=prev_url)


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


@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            print("sex")
        flash("Перевірте пошту!")
        return redirect(url_for("login"))
    return render_template("reset_password_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Пароль змінено.")
        return redirect(url_for('login'))
    return render_template("reset_password.html", form=form)
