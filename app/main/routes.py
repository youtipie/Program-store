from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.aws import upload_avatar
from app.models import User, Game, Comment
from app.main.forms import PasswordForm, EmailForm, AvatarForm, CommentForm
from app.main import bp


@bp.route("/")
def index():
    return render_template("home.html")


@bp.route("/game", methods=["GET", "POST"])
def game_page():
    form = CommentForm()
    if request.method == "POST" and current_user.is_authenticated:
        if form.validate_on_submit():
            comment = Comment(content=form.comment.data,
                              user=current_user,
                              game=db.session.query(Game).filter_by(id=request.args.get("id")).first())
            db.session.add(comment)
            db.session.commit()
            return jsonify({"message": "Comment submitted successfully"})

        errors = form.errors
        return jsonify({"errors": errors}), 400
    return render_template("pageofgame.html", form=form)


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = current_user
    password_form = PasswordForm()
    email_form = EmailForm()
    avatar_form = AvatarForm()
    if request.method == "POST":
        if password_form.validate_on_submit():
            user.set_password(password_form.password2.data)
            db.session.commit()
            return jsonify({"message": "Password updated successfully"})

        if email_form.validate_on_submit():
            existing_user = db.session.query(User).filter_by(email=email_form.email.data).first()
            if existing_user is not None:
                return jsonify({"errors": {
                    "email_errors": {"email": ["User with such email exists!"]}
                }}), 400
            user.email = email_form.email.data
            db.session.commit()
            return jsonify({"message": "Email updated successfully"})

        if avatar_form.validate_on_submit():
            file = avatar_form.avatar.data
            filename = secure_filename(file.filename)
            new_avatar_path = upload_avatar(user.id, file, filename)
            if new_avatar_path:
                user.avatar_path = new_avatar_path
                db.session.commit()
                return jsonify({"message": "Avatar updated successfully"})
            else:
                return jsonify({"errors": {
                    "avatar_errors": {"avatar": ["Unexpected error occurred!"]}
                }}), 500

        errors = {
            "password_errors": password_form.errors,
            "email_errors": email_form.errors,
            "avatar_errors": avatar_form.errors
        }
        return jsonify({"errors": errors}), 400
    return render_template("account.html", user=user, password_form=password_form, email_form=email_form,
                           avatar_form=avatar_form)


@bp.route("/add-game", methods=["GET", "POST"])
@login_required
def add_game():
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "This page is for admin only!"}), 403

    return render_template("pageofadmin.html")
