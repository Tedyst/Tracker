#!/usr/bin/python3
from Tracker import app
from flask import render_template
import Tracker.routes as routes  # noqa: F401

app.register_blueprint(routes.pages.pages_blueprint, url_prefix="")
app.register_blueprint(routes.auth.auth_blueprint, url_prefix="")
app.register_blueprint(routes.api.api_blueprint, url_prefix="/api")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
