from boto3 import client
from botocore.client import Config
from flask import current_app


def get_client():
    return client(
        's3',
        config=Config(signature_version='s3v4'),
        region_name="eu-north-1",
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY"],
        aws_secret_access_key=current_app.config["AWS_SECRET_KEY"])


def generate_public_url(file_name, timeout=300):
    s3_client = get_client()
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': current_app.config["AWS_BUCKET"],
            'Key': file_name
        },
        ExpiresIn=timeout
    )
    return url


def upload_file(file, filename):
    s3_client = get_client()
    try:
        s3_client.put_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=filename,
            Body=file
        )
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def upload_avatar(user_id, file, filename):
    s3_client = get_client()
    try:
        key = f'avatars/{user_id}/avatar.{filename.split(".")[-1]}'
        s3_client.put_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=key,
            Body=file
        )
        return key
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def delete_file(file_key):
    s3_client = get_client()
    try:
        response = s3_client.delete_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=file_key
        )

        print(f"Deleted file: {response['Deleted']}")
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def delete_folder(folder_key):
    s3_client = get_client()
    try:
        objects_to_delete = s3_client.list_objects_v2(
            Bucket=current_app.config["AWS_BUCKET"],
            Prefix=folder_key
        )
        if 'Contents' in objects_to_delete:
            delete_keys = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]

            response = s3_client.delete_objects(
                Bucket=current_app.config["AWS_BUCKET"],
                Delete={'Objects': delete_keys}
            )
            print(f"Deleted: {response['Deleted']}")
            return True
        else:
            print("No objects found to delete.")
            return False
    except Exception as e:
        print(f"Error deleting folder: {e}")
        return False


def move_and_rename_file(source_key, destination_key):
    s3_client = get_client()
    try:
        copy_source = {
            'Bucket': current_app.config["AWS_BUCKET"],
            'Key': source_key
        }
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=current_app.config["AWS_BUCKET"],
            Key=destination_key
        )

        s3_client.delete_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=source_key
        )
        return destination_key
    except Exception as e:
        print(f"Error moving and renaming file: {e}")
        return False


def swap_files(key1, key2):
    s3_client = get_client()
    try:
        temp_key1 = key1 + '.tmp'
        temp_key2 = key2 + '.tmp'

        s3_client.copy_object(
            CopySource={'Bucket': current_app.config["AWS_BUCKET"], 'Key': key1},
            Bucket=current_app.config["AWS_BUCKET"],
            Key=temp_key1
        )

        s3_client.copy_object(
            CopySource={'Bucket': current_app.config["AWS_BUCKET"], 'Key': key2},
            Bucket=current_app.config["AWS_BUCKET"],
            Key=temp_key2
        )

        s3_client.copy_object(
            CopySource={'Bucket': current_app.config["AWS_BUCKET"], 'Key': temp_key1},
            Bucket=current_app.config["AWS_BUCKET"],
            Key=key2
        )

        s3_client.copy_object(
            CopySource={'Bucket': current_app.config["AWS_BUCKET"], 'Key': temp_key2},
            Bucket=current_app.config["AWS_BUCKET"],
            Key=key1
        )

        s3_client.delete_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=temp_key1
        )
        s3_client.delete_object(
            Bucket=current_app.config["AWS_BUCKET"],
            Key=temp_key2
        )

        return True
    except Exception as e:
        print(f"Error swapping files: {e}")
        return False


def replace_special_characters(input_text):
    special_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    for char in special_characters:
        input_text = input_text.replace(char, '')

    return input_text
