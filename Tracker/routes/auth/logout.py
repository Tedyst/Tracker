from flask_login import logout_user, login_required
from Tracker.routes.auth import auth_blueprint
from flask import redirect, url_for


@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.index'))
