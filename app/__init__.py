import json
import os
import shutil

from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
import functools
from boto3 import client
from botocore.client import Config

from app.db import db_init
from app.models import *
from credentials import ACCESS_KEY, SECRET_KEY, BUCKET

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/ProgramStoreDataBase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

login_manager = LoginManager()
login_manager.init_app(app)


def get_client():
    return client(
        's3',
        config=Config(signature_version='s3v4'),
        region_name="eu-north-1",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY)


def generate_public_url(file_name, timeout=300):
    s3_client = get_client()
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET,
            'Key': file_name
        },
        ExpiresIn=timeout
    )
    return url


def replace_special_characters(input_text):
    special_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    for char in special_characters:
        input_text = input_text.replace(char, '')

    return input_text


from app import routes
