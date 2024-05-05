from flask_mail import Message
from flask import current_app
from app import mail, create_app

app = create_app()
app.app_context().push()


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
