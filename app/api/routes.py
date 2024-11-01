from flask import current_app, request, url_for, jsonify, redirect
from flask_login import current_user
from app.aws import delete_folder
from app import db, cache
from app.models import User, Category, Game, Comment, UserGameRating
from app.api import bp
from sqlalchemy import func, select
import json


@bp.route("/categories")
@cache.cached(600, key_prefix="get_categories")
def get_categories():
    try:
        categories = db.session.query(Category).all()
    except:
        return {"success": False, "message": "Something went wrong"}, 500
    return {"success": True, "categories": [category.to_dict() for category in categories]}


@bp.route("/games")
@cache.cached(600, key_prefix="get_games", query_string=True)
def get_games():
    db.session.execute(select(func.set_limit("0.05")))
    try:
        page = request.args.get('page', 1, type=int)
        category = request.args.get("category", type=str)
        order = request.args.get("order", "popularity", type=str)
        desc = request.args.get("desc", 1, type=int)
        title = request.args.get("title", type=str)
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    if order not in ["id", "title", "category_id", "is_paid", "apk_size",
                     "cache_size", "rating", "popularity", "last_changed"]:
        return jsonify({"success": False, "message": "Cannot order by specified field"}), 400

    categories = db.session.query(Category).all()
    if category not in [ctg.name for ctg in categories] and category is not None:
        return jsonify({"success": False, "message": f"No such category as '{category}'"}), 400

    games = db.session.query(Game).join(Category)

    if category:
        games = games.filter_by(name=category)

    if title:
        games = games.with_entities(Game, func.similarity(Game.title, title).label('similarity')). \
            filter(Game.title.bool_op("%")(title))
        if order == "rating":
            games = games.order_by(
                func.similarity(Game.title, title).desc()
            )
        else:
            games = games.order_by(
                func.similarity(Game.title, title).desc(),
                getattr(Game, order).desc() if desc else getattr(Game, order)
            )

    else:
        if order != "rating":
            games = games.order_by(getattr(Game, order).desc() if desc else getattr(Game, order))

    games = games.paginate(
        page=page,
        per_page=current_app.config[
            "ITEMS_PER_PAGE"],
        error_out=False
    )

    games_list = [game.to_dict() if not title else game[0].to_dict() for game in games]

    next_page = games.next_num if games.has_next else None
    prev_page = games.prev_num if games.has_prev else None

    total_pages = games.pages
    if total_pages < page:
        return redirect(
            url_for("api.get_games",
                    page=total_pages,
                    category=category,
                    order=order,
                    desc=desc,
                    title=title
                    ))
    return jsonify({
        "success": True,
        "current_page": page,
        "next_page": next_page,
        "prev_page": prev_page,
        "total_games": games.total,
        "total_pages": total_pages,
        "per_page": current_app.config["ITEMS_PER_PAGE"],
        "games": games_list if order != "rating" else sorted(games_list, key=lambda x: x["rating"],
                                                             reverse=True if desc else False)
    }), 200


@bp.route("/game")
@cache.cached(600, key_prefix="get_game", query_string=True)
def get_game():
    try:
        id = request.args.get("id", None, type=int)
        game = db.session.query(Game).filter_by(id=id).first()
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    if game:
        return jsonify({"success": True, "game": game.to_dict()})
    else:
        return jsonify({"success": False, "message": "Game with such id does not exist"})


@bp.route("/add_popularity", methods=["POST"])
def add_popularity():
    try:
        game_id = request.args.get("game_id", type=int)
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return jsonify({"success": False, "message": "No game with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400
    game.popularity += 1
    db.session.commit()
    cache.clear()
    return {"success": True}, 200


@bp.route("/comments")
@cache.cached(600, key_prefix="get_comments", query_string=True)
def get_comments():
    try:
        page = request.args.get("page", 1, type=int)
        game_id = request.args.get("game_id", type=int)
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return jsonify({"success": False, "message": "No game with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    comments = db.session.query(Comment).filter_by(game_id=game_id).paginate(
        page=page,
        per_page=current_app.config[
            "ITEMS_PER_PAGE"],
        error_out=False
    )

    next_page = comments.next_num if comments.has_next else None
    prev_page = comments.prev_num if comments.has_prev else None

    total_pages = comments.pages
    if total_pages < page:
        return redirect(
            url_for("api.get_comments",
                    page=total_pages,
                    game_id=game_id
                    ))
    return jsonify({
        "success": True,
        "current_page": page,
        "comments": [comment.to_dict() for comment in comments],
        "next_page": next_page,
        "prev_page": prev_page,
        "total_comments": comments.total,
        "total_pages": total_pages,
        "per_page": current_app.config["ITEMS_PER_PAGE"],
    }), 200


@bp.route("/rate_game", methods=["POST"])
def rate_game():
    try:
        game_id = request.args.get("game_id", type=int)
        rating = request.args.get("rating", type=int)
        if current_user.is_authenticated and rating:
            user = current_user
        else:
            raise ValueError
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return jsonify({"success": False, "message": "No game with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    if game not in [g.game for g in user.games_rated]:
        db.session.add(UserGameRating(user=user, game=game, rating=rating))
        db.session.commit()
        cache.clear()
        return jsonify({"success": True, "message": "Rating successfully added"}), 200
    else:
        return jsonify({"success": False, "message": "User already rated this game"}), 403


@bp.route("/add_download_count", methods=["POST"])
def add_download_count():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    user = current_user
    user.download_count += 1
    db.session.commit()
    return jsonify({"success": True, "message": "Download count increased"})


@bp.route("/get_user_status")
def get_user_status():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    user = current_user
    return jsonify({"success": True, "user_status": "Admin" if user.is_admin else "User"})


def delete_game_helper(game):
    try:
        for comment in game.comments:
            db.session.delete(comment)

        for image in game.images:
            db.session.delete(image)

        for rates in db.session.query(UserGameRating).filter_by(game=game).all():
            db.session.delete(rates)

        delete_folder(f"data/{game.folder_name}")

        db.session.delete(game)
        db.session.commit()
        return True
    except Exception as e:
        print("Error deleting game", e)
        db.session.rollback()
        return False


@bp.route("/delete_game", methods=["DELETE"])
def delete_game():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    else:
        if not current_user.is_admin:
            return jsonify({"success": False, "message": "User must be admin"}), 403
    try:
        game_id = request.args.get("game_id", type=int)
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return jsonify({"success": False, "message": "No game with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400
    if delete_game_helper(game):
        cache.clear()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Some unexpected error occured"}), 500


@bp.route("/delete_comment", methods=["DELETE"])
def delete_comment():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    else:
        if not current_user.is_admin:
            return jsonify({"success": False, "message": "User must be admin"}), 403
    try:
        game_id = request.args.get("game_id", type=int)
        comment_id = request.args.get("comment_id", type=int)
        comment = db.session.query(Comment).filter_by(id=comment_id).first()
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game and not comment:
            return jsonify({"success": False, "message": "No game or comment with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    db.session.delete(comment)
    db.session.commit()
    cache.clear()
    return jsonify({"success": True})


@bp.route("/delete_category", methods=["DELETE"])
def delete_category():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    else:
        if not current_user.is_admin:
            return jsonify({"success": False, "message": "User must be admin"}), 403
    try:
        category_name = request.args.get("name", type=str)
        category = db.session.query(Category).filter_by(name=category_name).first()
        if not category:
            return jsonify({"success": False, "message": "No category with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    if category.games:
        return jsonify({"success": False, "message": "Can't delete category that has games. "
                                                     "Change category for those games and retry"}), 409
    db.session.delete(category)
    db.session.commit()
    cache.clear()
    return jsonify({"success": True})


@bp.route("/rename_category", methods=["POST"])
def rename_category():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    else:
        if not current_user.is_admin:
            return jsonify({"success": False, "message": "User must be admin"}), 403
    try:
        new_category_name = request.args.get("name", type=str)
        category_id = request.args.get("id", type=int)
        category = db.session.query(Category).filter_by(id=category_id).first()
        if not category:
            return jsonify({"success": False, "message": "No category with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    existing_category = db.session.query(Category). \
        filter(Category.name == new_category_name, Category.id != category_id).first()
    if existing_category:
        return jsonify({"success": False, "message": "Category with the same name exists"}), 409

    category.name = new_category_name
    db.session.commit()
    cache.clear()
    return jsonify({"success": True})
