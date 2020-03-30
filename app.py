#!/usr/bin/python3
import json
from threading import Thread
from flask import render_template, Response, request, redirect, url_for
from datetime import datetime, timedelta

from Tracker import app, db, User, SITES, SITES_ALL
import Tracker.dbutils as dbutils
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', SITES=SITES_ALL)
    else:
        return render_template('login.html')


@app.route('/api/users/<user>')
def api_getuser(user):
    # In cazul in care userul cerut nu exista
    if not dbutils.userExists(user):
        error = {
            "message": None
        }
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    # Pentru a creea un raspuns folosind JSON
    # @sites = usernameurile de pe siteuri
    # @id = id-ul din baza de date
    # @fullname = numele specificat de user
    user = dbutils.getUser(user)
    response = {
        "sites": {},
        "id": user.id,
        "fullname": user.fullname
    }
    # Pentru a adauga la fiecare site
    # username si data ultimei actualizari
    for site in SITES:
        if user[site] is None:
            response["sites"][site] = {
                "username": "",
                "last_check": -1
            }
        else:
            response["sites"][site] = {
                "username": user[site],
                "last_check": user["last_" + site]
            }

    # Pentru a specifica browserului ca este un raspuns JSON
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


@app.route('/prob/<nickname>')
def prob_user(nickname):
    user = User.query.filter(User.nickname == nickname).first()

    # In cazul in care userul cerut nu exista
    if user is None:
        return app.response_class(
            response=render_template('404.html'),
            status=404
        )

    # Get user's problems
    data = dbutils.getSurse(user, "all")
    result = []
    for i in data:
        result.append(i.to_dict())
    result = json.dumps(result)
    db.session.commit()

    if dbutils.needsUpdate(user, "all"):
        # If it is locked, it means that the user is updating already
        if user.lock.locked():
            return render_template('prob.html',
                                   data=result,
                                   updating=True,
                                   user=user)
        # Start updating user
        user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[user, "all"])
        thread.start()

        # Return old data to the user before we finish updating
        return render_template('prob.html',
                               data=result,
                               updating=True,
                               user=user)

    return render_template('prob.html',
                           data=result,
                           updating=False,
                           user=user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    site_names = {}
    if request.method == 'GET':
        if current_user.is_authenticated:
            # Ia numele user-ului de pe site-uri
            user = dbutils.getUser(current_user.nickname)
            for site in SITES:
                if user[site] is None:
                    site_names[site] = "None set"
                else:
                    site_names[site] = user[site]

            # site_names = json.dumps(site_names)
            return render_template('settings.html', data=site_names, edit=False)
        return redirect(url_for('index'))

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
        return render_template('settings.html', updated=True)

        # Start updating user
        current_user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[current_user,
                                                              "all"], data=site_names)
        thread.start()

    user = dbutils.getUser(current_user.nickname)
    for site in SITES:
        if user[site] is None:
            site_names[site] = "None set"
        else:
            site_names[site] = user[site]

    return render_template('settings.html', updated=True, data=site_names)


@app.route('/settings', methods=['GET', 'POST'])
def prob():
    if current_user.is_authenticated:
        return redirect(url_for('prob_user', nickname=current_user.nickname))
    return redirect(url_for('index'))


@app.route('/api/users/<nickname>/<site>')
def api_users(nickname, site):
    # In cazul in care site-ul cerut nu exista
    if site not in SITES_ALL:
        error = {
            "message": None
        }
        error["message"] = "Site dosen't exist or is not tracked"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )

    user = User.query.filter(User.nickname == nickname).first()
    # In cazul in care userul cerut nu exista
    if user is None:
        error = {
            "message": None
        }
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )

    # Pentru a creea un raspuns folosind JSON
    # @updating = daca va fi actualizat in viitorul apropiat
    # @result = problemele userului de pe site-ul cerut
    response = {
        "updating": dbutils.needsUpdate(user, site),
        "result": {}
    }

    data = dbutils.getSurse(user, site)
    result = []
    for i in data:
        result.append(i.to_dict())
    response["result"] = result
    db.session.commit()

    if response["updating"]:
        if user.lock.locked():
            return Response(json.dumps(response),
                            status=303,
                            mimetype='application/json')
        user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[user, site])
        thread.start()

        return Response(json.dumps(response),
                        status=303,
                        mimetype='application/json')

    # Pentru a specifica browserului ca este un raspuns JSON
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


@app.route('/api/calendar/<nickname>')
def api_users_calendar(nickname):
    user = User.query.filter(User.nickname == nickname).first()
    # In cazul in care userul cerut nu exista
    if user is None:
        error = {
            "message": None
        }
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )

    # Pentru a creea un raspuns folosind JSON
    # @updating = daca va fi actualizat in viitorul apropiat
    # @result = problemele userului de pe site-ul cerut

    data = dbutils.getSurse(user, "all")
    result = {}
    for i in data:
        timp = int(datetime.fromtimestamp(i.data).replace(hour=0, minute=0, second=0).timestamp())
        try:
            result[timp] += 1
        except Exception:
            result[timp] = 1

    db.session.commit()

    if dbutils.needsUpdate(user, "all"):
        if user.lock.locked():
            return Response(json.dumps(result),
                            status=303,
                            mimetype='application/json')
        user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[user, "all"])
        thread.start()

        return Response(json.dumps(result),
                        status=303,
                        mimetype='application/json')

    # Pentru a specifica browserului ca este un raspuns JSON
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', failedlogin=False)
    elif request.method == 'POST':
        data = request.form
        try:
            if not data['email'] or not data['password']:
                return render_template('login.html', failedlogin=True)
        except KeyError:
            return render_template('login.html')
        remember = False
        try:
            if data['remember'] == 'on':
                remember = True
        except KeyError:
            pass
        user = User.query.filter(User.email == data['email']).first()
        if user is None:
            user = User.query.filter(User.nickname == data['email']).first()
            if user is None:
                return render_template('login.html', failedlogin=True)
        if user.check_password(data['password']):
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        return render_template('login.html', failedlogin=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = request.form
        try:
            if not data['email'] or not data['password'] or not data['name']:
                return render_template('register.html')
        except KeyError:
            return render_template('register.html')
        user = User.query.filter(User.email == data['email']).first()
        if user is None:
            user = User.query.filter(User.nickname == data['email']).first()
        if user is None:
            user = dbutils.createUser(data['name'], data['password'], data['email'])
            login_user(user)
            return render_template('index.html', first_time=True)
        return render_template('register.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(threaded=True, debug=True)
