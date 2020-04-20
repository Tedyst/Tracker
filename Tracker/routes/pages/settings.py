from Tracker import app, SITES, dbutils
from Tracker.routes.pages import pages_blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, request


@pages_blueprint.route('/usersettings', methods=['POST'])
@login_required
def usersettings():
    data = request.form
    if current_user.check_password(data['oldpassword']):
        app.logger.info("Schimat parola/email pentru %s",
                        current_user.nickname)
        current_user.email = data['email']
        current_user.set_password(data['password'])
    else:
        app.logger.info("Parola veche gresita pentru %s",
                        current_user.nickname)
    return redirect(url_for('pages.settings'))


@pages_blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    site_names = {}
    if request.method == 'GET':
        for site in SITES:
            if current_user[site] is None:
                site_names[site] = "None set"
            else:
                site_names[site] = current_user[site]
        return render_template('pages/settings.html',
                               data=site_names,
                               edit=False)

    user = dbutils.getUser(current_user.nickname)
    for site in SITES:
        if user[site] is None:
            site_names[site] = "None set"
        else:
            site_names[site] = user[site]

    data = request.form
    for i in SITES:
        try:
            site_names[i] = data[i]
        except KeyError:
            pass

        try:
            dbutils.updateUsername(current_user, data[i], i)
        except KeyError:
            pass
    if current_user.lock.locked():
        dbutils.updateThreaded(current_user)
        return render_template('pages/settings.html',
                               updated=True,
                               data=site_names)

    user = dbutils.getUser(current_user.nickname)
    for site in SITES:
        if user[site] is None:
            site_names[site] = "None set"
        else:
            site_names[site] = user[site]

    return render_template('pages/settings.html',
                           updated=True,
                           data=site_names)
