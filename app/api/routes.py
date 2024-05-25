from flask import current_app, request, url_for, jsonify, redirect
from flask_login import current_user
from app import db
from app.models import User, Category, Game, Comment, UserGameRating
from app.api import bp
from sqlalchemy import func, select
import json


@bp.route("/categories")
def get_categories():
    try:
        categories = db.session.query(Category).all()
    except:
        return {"success": False, "message": "Something went wrong"}, 500
    return {"success": True, "categories": [category.name for category in categories]}


@bp.route("/games")
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
                     "cache_size", "rating", "popularity"]:
        return jsonify({"success": False, "message": "Cannot order by specified field"}), 400

    categories = db.session.query(Category).all()
    if category not in [ctg.name for ctg in categories] and category is not None:
        return jsonify({"success": False, "message": f"No such category as '{category}'"}), 400

    games = db.session.query(Game).join(Category)

    if category:
        games = games.filter_by(name=category)

    if title:
        games = games.with_entities(Game, func.similarity(Game.title, title).label('similarity')). \
            filter(Game.title.bool_op("%")(title)). \
            order_by(
            func.similarity(Game.title, title).desc(),
            getattr(Game, order).desc() if desc else getattr(Game, order)
        )

    games = games.paginate(
        page=page,
        per_page=current_app.config[
            "ITEMS_PER_PAGE"],
        error_out=False
    )

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
        "games": [game.to_dict() if not title else game[0].to_dict() for game in games]
    }), 200


@bp.route("/game")
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
    token = request.args.get("token", "", type=str)
    game = Game.verify_popularity_token(token)
    if not game:
        return jsonify({"success": False, "message": "Bad token"}), 400
    game.popularity += 1
    db.session.commit()
    return {"success": True}, 200


@bp.route("/comments")
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


@bp.route("/rate_game", methods=["GET"])
def rate_game():
    token = request.args.get("token", "", type=str)

    game, user, rating = Game.verify_rating_token(token)
    if rating:
        db.session.add(UserGameRating(user=user, game=game, rating=rating))
        db.session.commit()
        return jsonify({"success": True, "message": "Rating successfully added"}), 200
    else:
        return jsonify({"success": False, "message": "User have already voted or token is invalid"}), 400


@bp.route("/get_rate_game_tokens", methods=["GET"])
def get_rate_game_token():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    try:
        game_id = request.args.get("game_id", type=int)
        user = current_user
        game = db.session.query(Game).filter_by(id=game_id).first()
        if not game:
            return jsonify({"success": False, "message": "No game with such id"}), 404
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400

    return jsonify(
        {"success": True, "tokens": [game.create_rating_token(user.id, rating) for rating in range(1, 6)]})


@bp.route("/get_popularity_tokens", methods=["GET"])
def get_popularity_token():
    try:
        ids = request.args.getlist("ids")
        if not ids:
            raise ValueError("Missing or empty 'ids' parameter")
    except ValueError or TypeError:
        return jsonify({"success": False, "message": "Bad values"}), 400
    return jsonify(
        {"success": True, "tokens": [game.create_popularity_token() for game in
                                     db.session.query(Game).filter(Game.id.in_(ids)).all()]})


@bp.route("/add_download_count", methods=["POST"])
def add_download_count():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "User mush be logged in"}), 403
    user = current_user
    user.download_count += 1
    db.session.commit()
    return jsonify({"success": True, "message": "Download count increased"})
