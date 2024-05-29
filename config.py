import os
import uuid
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or str(uuid.uuid4())
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    TEST_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = int(os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False)
    ITEMS_PER_PAGE = int(os.environ.get("ITEMS_PER_PAGE") or 20)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["youtipie@gmail.com"]
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
    REDIS_URL = os.environ.get("REDIS_URL")
    USE_RQ_TO_SEND_EMAILS = int(os.environ.get("USE_RQ_TO_SEND_EMAILS") or False)
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
    AWS_BUCKET = os.environ.get("AWS_BUCKET")
    SESSION_TYPE = "sqlalchemy"
