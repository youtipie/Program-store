from flask import current_app, request, url_for, jsonify
from app import db
from app.aws import generate_public_url
from app.models import User, Category, Game
from app.api import bp


@bp.route("/games")
def get_games():
    page = request.args.get('page', 1, type=int)
    category = request.args.get("category", type=str)
    order = request.args.get("order", "popularity", type=str)
    desc = request.args.get("desc", True, type=bool)

    # if order not in ["title", "category_id", ]
    games = db.session.query(Game).join(Category)

    if category:
        games = games.filter_by(name=category)
    games = games.order_by(
        getattr(Game, order).desc() if desc else getattr(Game, order).apk_size). \
        paginate(
        page=page,
        per_page=current_app.config[
            "ITEMS_PER_PAGE"],
        error_out=False
    )

    next_page = games.next_num if games.has_next else None
    prev_page = games.prev_num if games.has_prev else None
    return jsonify({
        "success": True,
        "next_url": next_page,
        "prev_url": prev_page,
        "total_games": games.total,
        "total_pages": games.pages,
        "per_page": current_app.config["ITEMS_PER_PAGE"],
        "games": [game.to_dict() for game in games]
    })
