from flask import render_template, redirect, url_for, flash
from app.support import bp
from app.support.forms import SupportForm
from app.support.email import send_support_email


@bp.route("/support", methods=["GET", "POST"])
def support():
    form = SupportForm()
    if form.validate_on_submit():
        send_support_email(form.topic, form.content)
        flash("Problem sent!")
        return redirect(url_for("support.support"))
    return render_template("support.html", form=form)
