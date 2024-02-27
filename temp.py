import json
import os

from models import *


def replace_special_characters(input_text):
    special_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    for char in special_characters:
        input_text = input_text.replace(char, '')

    return input_text


def json_to_db():
    with open("instance/data.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    for item in data:
        try:
            category = db.session.query(Category).filter_by(name=item.get("category")).first()
            if not category:
                category = Category(name=item.get("category"))

            apk_name = item.get("apk_name")
            cache_name = item.get("cache_name")
            game = Game(
                title=item.get("title"),
                category=category,
                description=item.get("description"),
                is_paid=item.get("is_paid"),
                version=item.get("version"),
                apk_name=apk_name,
                apk_size=os.stat(f"instance/game_files/{apk_name}").st_size / (1024 * 1024),
                cache_name=cache_name,
                folder_name=replace_special_characters(item.get("title"))
            )
            if cache_name:
                game.cache_size = os.stat(f"instance/game_files/{cache_name}").st_size / (1024 * 1024)

            for image in item.get("images_save_path"):
                game.images.append(Image(
                    path=image
                ))
            db.session.add(game)
        except FileNotFoundError:
            pass
    db.session.commit()
