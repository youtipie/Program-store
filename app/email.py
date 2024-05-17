from flask_mail import Message
from app import mail, create_app


def send_email_(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, with_rq):
    if with_rq:
        app = create_app()
        app.app_context().push()
        rq_job = app.task_queue.enqueue(send_email_,
                                        subject,
                                        sender=sender,
                                        recipients=recipients,
                                        text_body=text_body,
                                        html_body=html_body)
    else:
        send_email_(
            subject,
            sender=sender,
            recipients=recipients,
            text_body=text_body,
            html_body=html_body)
