import unittest
from app import create_app, db
from app.models import User, Category, Game, Image, Comment
from app.aws import generate_public_url
from config import Config
from sqlalchemy import text
import json


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = Config.TEST_DATABASE_URI


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS pg_trgm'))

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class UserTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(UserTestCase, self).setUp()
        self.user = User(username="john", email="john@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

    def test_avatar(self):
        u = User(username="john", email="john@example.com")
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_set_password(self):
        u = User(username="jane", email="jane@example.com")
        u.set_password("password")
        self.assertTrue(u.check_password("password"))
        self.assertFalse(u.check_password("wrongpassword"))

    def test_reset_password_token(self):
        u = User(username='susan', email='susan@example.com')
        u.set_password("password")
        db.session.add(u)
        db.session.commit()
        token = u.get_reset_password_token()
        self.assertIsNotNone(User.verify_reset_password_token(token))

    def test_invalid_reset_password_token(self):
        token = self.user.get_reset_password_token()
        token = token[:-1] + "a"
        u = User.verify_reset_password_token(token)
        self.assertIsNone(u)

    def test_duplicate_email(self):
        u = User(username="jane", email="john@example.com")
        u.set_password("password")
        db.session.add(u)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_duplicate_username(self):
        u = User(username="john", email="jane@example.com")
        u.set_password("password")
        db.session.add(u)
        with self.assertRaises(Exception):
            db.session.commit()


class GameTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(GameTestCase, self).setUp()
        self.category = Category(name="Action")
        db.session.add(self.category)
        db.session.commit()

        self.game = Game(
            title="Fortnite",
            category_id=self.category.id,
            description="A fun game",
            is_paid=True,
            version="1.0",
            apk_name="Fortnite.apk",
            apk_size=50.5,
            folder_name="Fortnite"
        )
        db.session.add(self.game)
        db.session.commit()

    def test_create_popularity_token(self):
        token = self.game.create_popularity_token()
        g = Game.verify_popularity_token(token)
        self.assertEqual(g, self.game)

    def test_invalid_popularity_token(self):
        token = self.game.create_popularity_token()
        token = token[:-1] + "a"
        g = Game.verify_popularity_token(token)
        self.assertIsNone(g)

    def test_to_dict(self):
        image1 = Image(path="img1.jpg", game_id=self.game.id)
        image2 = Image(path="img2.jpg", game_id=self.game.id)
        db.session.add(image1)
        db.session.add(image2)
        db.session.commit()

        expected_dict = {
            "id": self.game.id,
            "poster": generate_public_url("data/" + self.game.folder_name + "/poster.jpg"),
            "title": self.game.title,
            "category_name": self.game.category.name,
            "category_id": self.game.category_id,
            "description": self.game.description,
            "is_paid": self.game.is_paid,
            "version": self.game.version,
            "apk_name": self.game.apk_name,
            "apk_size": self.game.apk_size,
            "cache_name": self.game.cache_name,
            "cache_size": self.game.cache_size,
            "images": [generate_public_url("data/" + image.path) for image in self.game.images],
            "rating": self.game.rating,
            "rating_count": self.game.rating_count,
            "popularity": self.game.popularity
        }
        self.assertDictEqual(self.game.to_dict(), expected_dict)


class CommentTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(CommentTestCase, self).setUp()
        self.user = User(username="john", email="john@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

        self.category = Category(name="Action")
        db.session.add(self.category)
        db.session.commit()

        self.game = Game(
            title="Sample Game",
            category_id=self.category.id,
            description="A fun game",
            is_paid=True,
            version="1.0",
            apk_name="sample_game.apk",
            apk_size=50.5,
            folder_name="sample_game"
        )
        db.session.add(self.game)
        db.session.commit()

        self.comment = Comment(content="Great game!", user_id=self.user.id, game_id=self.game.id)
        db.session.add(self.comment)
        db.session.commit()

    def test_comment_creation(self):
        self.assertIsNotNone(self.comment.user)
        self.assertIsNotNone(self.comment.game)
        self.assertEqual(self.user.comments[0].content, self.comment.content)
        self.assertEqual(self.user.comments[0].user_id, self.comment.user_id)
        self.assertEqual(self.user.comments[0].game_id, self.comment.game_id)

    def test_comment_without_content(self):
        comment = Comment(user_id=self.user.id, game_id=self.game.id)
        db.session.add(comment)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_comment_to_dict(self):
        expected_dict = {
            "id": self.comment.id,
            "date": self.comment.date,
            "content": self.comment.content,
            "username": self.comment.user.username,
            "user_pfp": self.comment.user.avatar(256)
        }
        self.assertDictEqual(self.comment.to_dict(), expected_dict)


class CategoryTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(CategoryTestCase, self).setUp()
        self.category = Category(name="Action")
        db.session.add(self.category)
        db.session.commit()

    def test_duplicate_category_name(self):
        category = Category(name="Action")
        db.session.add(category)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_category_association_with_game(self):
        game = Game(
            title="Sample Game",
            category_id=self.category.id,
            description="A fun game",
            is_paid=True,
            version="1.0",
            apk_name="sample_game.apk",
            apk_size=50.5,
            folder_name="sample_game"
        )
        db.session.add(game)
        db.session.commit()

        self.assertEqual(len(self.category.games), 1)
        self.assertEqual(self.category.games[0], game)


class APITestCase(BaseTestCase):
    def setUp(self) -> None:
        super(APITestCase, self).setUp()
        self.client = self.app.test_client()
        self.category = Category(name="Action")
        db.session.add(self.category)
        db.session.commit()

        self.category2 = Category(name="RPG")
        db.session.add(self.category2)
        db.session.commit()

        for i in range(self.app.config['ITEMS_PER_PAGE'] + self.app.config['ITEMS_PER_PAGE'] // 2):
            self.game = Game(
                title="Sample Game",
                category_id=self.category.id if i != 0 else self.category2.id,
                description="A fun game",
                is_paid=True,
                version="1.0",
                apk_name=f"sample_game.apk{i}",
                apk_size=50.5,
                folder_name=f"sample_game{i}"
            )
            db.session.add(self.game)
        db.session.commit()

        self.user = User(username="john", email="john@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

        for i in range(self.app.config['ITEMS_PER_PAGE'] + self.app.config['ITEMS_PER_PAGE'] // 2):
            self.comment = Comment(content="Great game!", user_id=self.user.id, game_id=self.game.id)
            db.session.add(self.comment)
        db.session.commit()

    def test_get_games(self):
        # Test successful retrieval of games
        response = self.client.get('/api/games')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['games']), self.app.config['ITEMS_PER_PAGE'])
        self.assertEqual(data['total_games'],
                         self.app.config['ITEMS_PER_PAGE'] + self.app.config['ITEMS_PER_PAGE'] // 2)
        self.assertEqual(data['next_page'], 2)
        self.assertIsNone(data['prev_page'])

        # Test pagination
        response = self.client.get('/api/games?page=2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['games']), self.app.config['ITEMS_PER_PAGE'] - self.app.config['ITEMS_PER_PAGE'] // 2)
        self.assertEqual(data['prev_page'], 1)
        self.assertIsNone(data['next_page'])

        # Test pagination redirect
        response = self.client.get('/api/games?page=99')
        self.assertEqual(response.status_code, 302)

        # Test invalid order parameter
        response = self.client.get('/api/games?order=invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Test filtering by category
        response = self.client.get('/api/games?category=RPG')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['games']), 1)
        self.assertEqual(len(data['games']), data['total_games'])

        # Test invalid category
        response = self.client.get('/api/games?category=Invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_add_popularity(self):
        # Test successful addition of popularity
        token = self.game.create_popularity_token()
        response = self.client.get(f'/api/add_popularity?token={token}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(self.game.popularity, 1)

        # Test invalid token
        response = self.client.get('/api/add_popularity?token=invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_get_comments(self):
        # Test successful retrieval of comments
        response = self.client.get(f'/api/comments?game_id={self.game.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['comments']), self.app.config['ITEMS_PER_PAGE'])
        self.assertEqual(data['total_comments'],
                         self.app.config['ITEMS_PER_PAGE'] + self.app.config['ITEMS_PER_PAGE'] // 2)
        self.assertEqual(data['next_page'], 2)
        self.assertIsNone(data['prev_page'])

        # Test invalid game_id
        response = self.client.get('/api/comments?game_id=999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Test pagination
        response = self.client.get(f'/api/comments?game_id={self.game.id}&page=2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['comments']),
                         self.app.config['ITEMS_PER_PAGE'] - self.app.config['ITEMS_PER_PAGE'] // 2)
        self.assertEqual(data['prev_page'], 1)
        self.assertIsNone(data['next_page'])

        # Test pagination redirect
        response = self.client.get(f'/api/comments?game_id={self.game.id}&page=99')
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main(verbosity=2)
