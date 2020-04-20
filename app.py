#!/usr/bin/python3
import json
from flask import render_template, Response, request, redirect, url_for
from datetime import datetime

from Tracker import app, db, User, SITES, SITES_ALL
import Tracker.dbutils as dbutils
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html',
                               SITES=SITES_ALL,
                               user=current_user)
    else:
        return render_template('login.html')


@app.route('/profile/<nickname>')
def profile_username(nickname):
    user = dbutils.getUser(nickname)
    if user is None:
        return app.response_class(
            response=render_template('404.html'),
            status=404
        )

        return render_template('login.html')
    else:
        return render_template('profile.html', SITES=SITES_ALL, user=user)


@app.route('/api/users')
def api_getuserlist():
    # Pentru a creea un raspuns folosind JSON
    users = User.query.all()
    response = []
    for user in users:
        response.append(user.nickname)

    # Pentru a specifica browserului ca este un raspuns JSON
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


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
        return render_template('prob.html',
                               updating=True,
                               user=user)

    return render_template('prob.html',
                           updating=False,
                           user=user)


@app.route('/usersettings', methods=['POST'])
@login_required
def usersettings():
    data = request.form
    if current_user.check_password(data['oldpassword']):
        app.logger.info("Schimat parola/email pentru %s", current_user.nickname)
        current_user.email = data['email']
        current_user.set_password(data['password'])
    else:
        app.logger.info("Parola veche gresita pentru %s", current_user.nickname)
    return redirect(url_for('settings'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    site_names = {}
    if request.method == 'GET':
        for site in SITES:
            if current_user[site] is None:
                site_names[site] = "None set"
            else:
                site_names[site] = current_user[site]
        return render_template('settings.html', data=site_names, edit=False)

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
        return render_template('settings.html', updated=True, data=site_names)

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
    # Adaugam debug pentru ca sa vedem cat de mult dureaza cu toolbar
    debug = False
    if site == "debug" and app.debug is True:
        site = "all"
        debug = True
    load_since = request.args.get('load_since')

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

    if load_since is None:
        app.logger.debug("Incaracam toate sursele...")
        data = dbutils.getSurse(user, site)
    else:
        app.logger.debug("Incarcam sursele mai noi decat %s", load_since)
        data = dbutils.getSurseSince(user, site, load_since)
    result = []
    for i in data:
        result.append(i.__json__())
    response["result"] = result
    db.session.commit()

    if response["updating"]:
        dbutils.updateThreaded(user)
        if debug:
            return render_template('debug.html', data=response)

        return Response(json.dumps(response),
                        status=200,
                        mimetype='application/json')

    if debug:
        return render_template('debug.html', data=response)
    # Pentru a specifica browserului ca este un raspuns JSON
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/grafic1/<nickname>')
def api_grafic1(nickname):
    user = User.query.filter(User.nickname == nickname).first()
    
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
    
    data = dbutils.getSurse(user,"all")
    result = []
    for subm in data:
        prob = None
        for i,sub in enumerate(result):
            if sub["name"] == subm.problema:
                if result[i]["solved"] is False:
                    result[i]["attempts"]+=1
                    if subm.scor == "100" or subm.scor == "Accepted":
                        result[i]["solved"]=True
                        result[i]["data"]=subm.data
                    else:
                        result[i]["solved"]=False
                elif result[i]["data"] >= subm.data and not (subm.scor == "100" or subm.scor == "Accepted"):
                    result[i]["attempts"]+=1

                prob = sub
                break

        if prob is None:
            temp={}
            temp["name"] = subm.problema
            temp["data"] = subm.data
            temp["attempts"]=1
            if subm.scor == "100" or subm.scor == "Accepted":
                temp["solved"]=True
            else:
                temp["solved"]=False
            result.append(temp)
            
    result = sorted(result, key = lambda k: k['data'])
    db.session.commit()

    if dbutils.needsUpdate(user, "all"):
        dbutils.updateThreaded(user)

        return Response(json.dumps(result),
                        status=200,
                        mimetype='application/json')
    
    return app.response_class(
        response=json.dumps(result),
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
    mem = []
    result = {}
    for i in data:
        timp = int(datetime.fromtimestamp(i.data).replace(hour=0, minute=0, second=0).timestamp())
        try:
            if i.idprob not in mem:
                result[timp] += 1
                mem.append(i.idprob)
        except Exception:
            result[timp] = 1
    db.session.commit()

    if dbutils.needsUpdate(user, "all"):
        dbutils.updateThreaded(user)

        return Response(json.dumps(result),
                        status=200,
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
            surse = json.dumps([i.__json__() for i in dbutils.getSurse(user, "all")])
            return render_template('profile.html', first_time=True, data=surse, user=user)
        return render_template('register.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(threaded=True, debug=True)
