from flask_mail import Message
from app import mail, create_app

app = create_app()
app.app_context().push()


def send_email_(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    send_email_(
        subject,
        sender=sender,
        recipients=recipients,
        text_body=text_body,
        html_body=html_body)
