from Tracker import dbutils, User, app
from Tracker.routes.pages import pages_blueprint
from flask import render_template, redirect, url_for
from flask_login import current_user


@pages_blueprint.route('/prob', methods=['GET', 'POST'])
def probleme():
    if current_user.is_authenticated:
        return redirect(url_for('pages.probleme_user', nickname=current_user.nickname))
    return redirect(url_for('pages.index'))


@pages_blueprint.route('/prob/<nickname>')
def probleme_user(nickname):
    user = User.query.filter(User.nickname == nickname).first()

    # In cazul in care userul cerut nu exista
    if user is None:
        app.logger.debug("Nu am gasit user cu nickname", nickname)
        return app.response_class(
            response=render_template('404.html'),
            status=404
        )

    app.logger.debug("Gasit username cu nickname %s", nickname)

    if dbutils.needsUpdate(user, "all"):
        app.logger.debug("%s are nevoie de update de surse", user.nickname)
        dbutils.updateThreaded(user)

        # Return old data to the user before we finish updating
        return render_template('pages/probleme.html',
                               updating=True,
                               user=user)

    return render_template('pages/probleme.html', user=user)
