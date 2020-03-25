#!/usr/bin/python3
from flask import Flask, render_template, request, Response
import Tracker.db as db
from Tracker.classes import sortProbleme_date, User, SITES, SITES_ALL
import json
from threading import Thread
from sqlalchemy.orm import scoped_session
import time
app = Flask(__name__)
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
    if not db.isTracked(user, site):
        error = ERROR_JSON
        error["message"] = "This user is not tracked or is not registered in the database"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    data = db.getSurseAPI(user, site)

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
    if not db.userExists(user):
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
    user = db.getUser(user)
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
    sess = scoped_session(db.Session)()
    user = sess.query(User).filter(User.nickname == nickname).first()
    # In cazul in care userul cerut nu exista
    if user is None:
        error = ERROR_JSON
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )

    # Pentru a creea un raspuns folosind JSON
    # @updating = daca va fi actualizat in viitorul apropiat
    # @result = problemele userului de pe toate siteurile
    response = {
        "updating": db.needsUpdate(nickname, "all"),
        "result": {}
    }

    data = db._getSurse(user, sess, "all")

    result = []
    for i in data:
        result.append(i.to_dict())

    sess.commit()
    username = ""
    if user.fullname:
        username = user.fullname
    else:
        username = user.nickname

    if response["updating"]:
        if user.lock.locked():
            return render_template('prob.html', data=result, updating=True, user=username)
        user.lock.acquire()
        thread = Thread(target=db.updateAndCommit, args=[nickname, "all"])
        thread.start()

        return render_template('prob.html', data=result, updating=True, user=username)

    return render_template('prob.html', data=result, updating=False, user=username)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/charts')
def charts():
    return render_template('charts.html')


@app.route('/login')
def login():
    return render_template('login.html')


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
    sess = scoped_session(db.Session)()
    # In cazul in care userul cerut nu exista
    if s.query(User).filter(User.nickname == nickname).first() is None:
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
        "updating": db.needsUpdate(nickname, site),
        "result": {}
    }

    user = sess.query(User).filter(User.nickname == nickname).first()

    data = db._getSurse(user, sess, site)
    result = []
    for i in data:
        result.append(i.to_dict())
    response["result"] = result
    sess.commit()

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
    data = db.getSurse(user, site)
    if data is None:
        return render_template('404.html')
    data = sorted(data, key=sortProbleme_date)
    return render_template('search.html', problems=data)

def init():
    db.createUser("Tedyst", "parola")
    s = db.Session()
    user = s.query(User).filter(User.nickname == "Tedyst").first()
    user["pbinfo"] = "Tedyst"
    user["infoarena"] = "Tedyst"
    user["codeforces"] = "Tedyst"
    s.commit()
    s.close()

init()

if __name__ == "__main__":
    app.run(threaded=True)
