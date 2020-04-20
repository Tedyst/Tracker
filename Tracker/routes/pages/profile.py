from Tracker import app, SITES_ALL, dbutils
from Tracker.routes.pages import pages_blueprint
from flask_login import current_user
from flask import render_template, redirect, url_for


@pages_blueprint.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('pages/profile.html',
                               SITES=SITES_ALL,
                               user=current_user)
    else:
        return redirect(url_for('login'))


@pages_blueprint.route('/profile/<nickname>')
def profile_username(nickname):
    user = dbutils.getUser(nickname)
    if user is None:
        return app.response_class(
            response=render_template('404.html'),
            status=404
        )

        return render_template('notlogged/login.html')
    else:
        return render_template('pages/profile.html',
                               SITES=SITES_ALL,
                               user=user)
