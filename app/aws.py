from boto3 import client
from botocore.client import Config
from credentials import ACCESS_KEY, SECRET_KEY, BUCKET


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
