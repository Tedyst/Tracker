#!/usr/bin/python3
from flask import render_template, request, Response
from Tracker import app
import Tracker.db as dbutils
from Tracker.db import db
from Tracker.db import sortProbleme_date, User, SITES, SITES_ALL
import json
from threading import Thread
from sqlalchemy.orm import scoped_session
import sys

app.config['SECRET_KEY'] = "asd"
if "pytest" in sys.modules:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db.init_app(app)
db.create_all()

PORT = 8080
ERROR_JSON = {
    "message": None
}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', SITES=SITES_ALL)


@app.route('/api/direct/<user>/<site>')
def api_direct(user, site):
    # In cazul in care site-ul cerut nu exista
    if site not in SITES_ALL:
        error = ERROR_JSON
        error["message"] = "Site dosen't exist or is not tracked"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    # In cazul in care userul cerut nu exista
    if not dbutils.isTracked(user, site):
        error = ERROR_JSON
        error["message"] = "This user is not tracked or is not registered in the database"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    data = dbutils.getSurse(user, site)

    # Pentru a creea un raspuns folosind JSON
    # @updating = daca va fi actualizat in viitorul apropiat
    # @result = problemele userului de pe site-ul cerut
    response = {
        "updating": False,
        "result": {}
    }
    result = []
    for i in data:
        result.append(i.to_dict())
    response["result"] = result

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
        error = ERROR_JSON
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
    # Pentru a adauga fiecare username la fiecare site + data ultimei actualizari
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
            status=404,
            mimetype='application/json'
        )

    # Get user's problems
    data = dbutils.getSurse(user, "all")
    result = []
    for i in data:
        result.append(i.to_dict())
    result = json.dumps(result)
    db.session.commit()

    if dbutils.needsUpdate(nickname, "all"):
        # If it is locked, it means that the user is updating already
        if user.lock.locked():
            return render_template('prob.html', data=result, updating=True, user=user)
        # Start updating user
        user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[nickname, "all"])
        thread.start()

        # Return old data to the user before we finish updating
        return render_template('prob.html', data=result, updating=True, user=user)

    return render_template('prob.html', data=result, updating=False, user=user)


@app.route('/api/users/<nickname>/<site>')
def api_users(nickname, site):
    # In cazul in care site-ul cerut nu exista
    if site not in SITES_ALL:
        error = ERROR_JSON
        error["message"] = "Site dosen't exist or is not tracked"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    # In cazul in care userul cerut nu exista
    if User.query.filter(User.nickname == nickname).first() is None:
        error = ERROR_JSON
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
        "updating": dbutils.needsUpdate(nickname, site),
        "result": {}
    }

    user = User.query.filter(User.nickname == nickname).first()

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
        thread = Thread(target=db.updateAndCommit, args=[nickname, site])
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


@app.route('/search')
def search():
    user = request.args.get('user')
    site = request.args.get('site')
    if site not in SITES_ALL:
        return render_template('404.html')
    data = dbutils.getSurse(user, site)
    if data is None:
        return render_template('404.html')
    data = sorted(data, key=sortProbleme_date)
    return render_template('search.html', problems=data)


def init():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = User.query.filter(User.nickname == "Tedyst").first()
    user["pbinfo"] = "Tedyst"
    user["infoarena"] = "Tedyst"
    user["codeforces"] = "Tedyst"
    db.session.commit()


init()

if __name__ == "__main__":
    app.run(threaded=True)
