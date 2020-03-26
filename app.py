#!/usr/bin/python3
import json
from threading import Thread
from flask import render_template, Response

from Tracker import app, db, User, SITES, SITES_ALL
import Tracker.dbutils as dbutils


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', SITES=SITES_ALL)


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
            return render_template('prob.html', data=result, updating=True, user=user)
        # Start updating user
        user.lock.acquire()
        thread = Thread(target=dbutils.updateAndCommit, args=[user, "all"])
        thread.start()

        # Return old data to the user before we finish updating
        return render_template('prob.html', data=result, updating=True, user=user)

    return render_template('prob.html', data=result, updating=False, user=user)


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
