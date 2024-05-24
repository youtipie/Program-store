from flask import render_template, current_app


def send_support_email(topic, content):
    rq_job = current_app.task_queue.enqueue("app.email.send_email",
                                            f"PROBLEM: {topic}",
                                            sender=current_app.config["ADMINS"][0],
                                            recipients=current_app.config["ADMINS"],
                                            text_body=render_template("email/send_problem.txt",
                                                                      topic=topic, content=content),
                                            html_body=render_template("email/send_problem.html",
                                                                      topic=topic, content=content))
