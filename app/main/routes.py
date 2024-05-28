import json
import uuid

from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.aws import upload_avatar, upload_file, swap_files, delete_file, move_and_rename_file, \
    replace_special_characters
from app.models import User, Game, Comment, Category, Image
from app.main.forms import PasswordForm, EmailForm, AvatarForm, CommentForm, AddGameForm, ChangeGameForm
from app.main import bp
from werkzeug.datastructures.file_storage import FileStorage
import os


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


def get_file_size(temp_file):
    temp_file.seek(0, os.SEEK_END)
    file_size = temp_file.tell()
    temp_file.seek(0)
    return file_size / (1024 * 1024)


@bp.route("/add-game", methods=["GET", "POST"])
@login_required
def add_game():
    if current_user.is_authenticated and not current_user.is_admin:
        return jsonify({"success": False, "message": "This page is for admin only!"}), 403

    form = AddGameForm()
    if request.method == "POST":
        if form.validate_on_submit():
            files = request.files.getlist('files[]')
            types = request.form.getlist('types')
            title = form.title.data
            description = form.description.data

            category_name = request.form.get("category")
            new_category_name = request.form.get("new_category")

            if new_category_name:
                if Category.query.filter(Category.name.ilike(new_category_name)).first():
                    return jsonify({"errors": {"description": ["Category with such name exists!"]}
                                    }), 400
                category = Category(name=new_category_name)
                db.session.add(category)
            else:
                category = db.session.query(Category).filter_by(name=category_name).first()

            version = request.form.get('version')

            game = Game()
            game.title = title
            game.category = category
            game.description = description
            game.version = version
            game.folder_name = replace_special_characters(game.title)
            game.is_paid = request.form.get("subscription") == "on"

            try:
                for file, filetype in zip(files, types):
                    filename = secure_filename(file.filename)
                    if filetype == "image":
                        path = f"{game.folder_name}/images/{filename}"
                        game.images.append(Image(path=path))
                        upload_file(file, f"data/{path}")
                    elif filetype == "poster":
                        upload_file(file, f"data/{game.folder_name}/poster.jpg")
                        pass
                    elif filetype == "apk":
                        game.apk_name = filename
                        game.apk_size = get_file_size(file)
                        upload_file(file, f"data/{game.folder_name}/{filename}")
                    elif filetype == "cache":
                        game.cache_name = filename
                        game.cache_size = get_file_size(file)
                        upload_file(file, f"data/{game.folder_name}/{filename}")
            except Exception as e:
                print(e)
                return jsonify({"errors": {"description": ["Some unexpected error occurred"]}
                                }), 500
            db.session.add(game)
            db.session.commit()
            return jsonify({"message": "Game added successfully"})

        errors = form.errors
        return jsonify({"errors": errors}), 400
    return render_template("pageofadmin.html", form=form)


@bp.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    game = db.session.query(Game).filter_by(id=game_id).first()
    if not game:
        return jsonify({"success": False, "message": "No game with such id"})
    form = ChangeGameForm(obj=game)
    form.game_id.data = game.id
    if form.validate_on_submit():
        original_files = game.to_dict().get("images_names")
        original_files.extend([game.apk_name, "poster.jpg"])
        if game.cache_name:
            original_files.append(game.cache_name)

        new_files = request.files.getlist('files[]')
        existing_files = json.loads(request.form.get('existing_filenames'))
        types = request.form.getlist('types')
        title = form.title.data
        description = form.description.data

        category_name = request.form.get("category")
        new_category_name = request.form.get("new_category")

        if new_category_name:
            if Category.query.filter(Category.name.ilike(new_category_name)).first():
                return jsonify({"errors": {"description": ["Category with such name exists!"]}
                                }), 400
            category = Category(name=new_category_name)
            db.session.add(category)
        else:
            category = db.session.query(Category).filter_by(name=category_name).first()

        version = request.form.get('version')

        game.title = title
        game.category = category
        game.description = description
        game.version = version
        game.is_paid = request.form.get("subscription") == "on"
        game.update_last_change()

        for file in original_files:
            if file not in existing_files:
                if file.endswith(".apk") or file.endswith(".rar") or file.endswith(".zip") or file == "poster.jpg":
                    delete_file(f"data/{game.folder_name}/{file}")
                else:
                    delete_file(f"data/{game.folder_name}/images/{file}")
                    game.delete_image_by_name(file)

        switch_poster_image = True
        for file, filetype in zip(existing_files + new_files, types):
            if isinstance(file, FileStorage):
                filename = secure_filename(file.filename)
                if filetype == "image":
                    path = f"{game.folder_name}/images/{filename}"
                    game.images.append(Image(path=path))
                    upload_file(file, f"data/{path}")
                elif filetype == "poster":
                    upload_file(file, f"data/{game.folder_name}/poster.jpg")
                    switch_poster_image = False
                elif filetype == "apk":
                    game.apk_name = filename
                    game.apk_size = get_file_size(file)
                    upload_file(file, f"data/{game.folder_name}/{filename}")
                elif filetype == "cache":
                    game.cache_name = filename
                    game.cache_size = get_file_size(file)
                    upload_file(file, f"data/{game.folder_name}/{filename}")
            else:
                if filetype == "image":
                    if file == "poster.jpg":
                        if switch_poster_image:
                            print("Poster <-> image")  # Pass for now, we will change it later
                        else:
                            print("Poster -> image")
                            move_and_rename_file(f"data/{game.folder_name}/poster.jpg",
                                                 f"data/{game.folder_name}/images/{str(uuid.uuid4())}.jpg")
                    else:
                        print("Pass")
                elif filetype == "poster":
                    if file == "poster.jpg":
                        print("Pass")
                    else:
                        if switch_poster_image:
                            print("Poster <-> image")
                            swap_files(f"data/{game.folder_name}/poster.jpg", f"data/{game.folder_name}/images/{file}")
                        else:
                            print("Image -> poster")
                            move_and_rename_file(f"data/{game.folder_name}/images/{file}",
                                                 f"data/{game.folder_name}/poster.jpg")
                else:
                    pass  # Other files don't need to change

        db.session.commit()
        return jsonify({"message": "Game added successfully"})

    return render_template("pageofadmin.html", form=form)
