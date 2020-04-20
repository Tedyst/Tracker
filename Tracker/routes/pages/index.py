from flask_login import current_user
from Tracker.routes.pages import pages_blueprint
from flask import render_template, redirect, url_for


@pages_blueprint.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('pages/index.html')
    else:
        return redirect(url_for('login.login'))
