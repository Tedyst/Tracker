#!/usr/bin/python3
from flask import Flask, render_template, request
import Tracker.db as db
from classes import sortProbleme_date, User
import json
from classes import SITES_ALL, SITES
from flask_executor import Executor
app = Flask(__name__)
executor = Executor(app)
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
    if site not in SITES_ALL:
        error = ERROR_JSON
        error["message"] = "Site dosen't exist or is not tracked"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    if not db.isTracked(user, site):
        error = ERROR_JSON
        error["message"] = "This user is not tracked or is not registered in the database"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    data = db.getSurseAPI(user, site)
    response = {
        "updating": False,
        "result": {}
    }
    result = []
    for i in data:
        result.append(i.to_dict())
    response["result"] = result
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


@app.route('/api/users/<user>')
def api_getuser(user):
    if not db.userExists(user):
        error = ERROR_JSON
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    user = db.getUser(user)
    response = {
        "sites": {},
        "id": user.id,
        "fullname": user.fullname
    }
    for site in SITES:
        response["sites"][site] = {
                "username": user[site],
                "last_check": user["last_" + site]
            }
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


@app.route('/api/users/<nickname>/<site>')
def api_users(nickname, site):
    if site not in SITES_ALL:
        error = ERROR_JSON
        error["message"] = "Site dosen't exist or is not tracked"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )
    if not db.userExists(nickname):
        error = ERROR_JSON
        error["message"] = "This user does not exist"
        return app.response_class(
            response=json.dumps(error),
            status=404,
            mimetype='application/json'
        )

    response = {
        "updating": db.needsUpdate(nickname, site),
        "result": {}
    }

    user = db.getUser(nickname)
    sess = db.Session()
    if response["updating"]:
        sess = db.Session()
        executor.submit(db._updateSurse, sess, user, site)
        sess.commit()

    data = db._getSurse(user, sess, site)
    result = []
    for i in data:
        result.append(i.to_dict())
    response["result"] = result

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


db.createUser("Tedyst", "parola")
s = db.Session()
user = s.query(User).filter(User.nickname == "Tedyst").first()
user["pbinfo"] = "Tedyst"
user["infoarena"] = "Tedyst"
user["codeforces"] = "Tedyst"
s.commit()

if __name__ == "__main__":
    app.run()
