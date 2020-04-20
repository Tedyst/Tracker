from Tracker import app, dbutils, User, SITES, SITES_ALL, db
import json
from Tracker.routes.api import api_blueprint
from flask import render_template, request, Response


@api_blueprint.route('/api/users')
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


@api_blueprint.route('/api/users/<user>')
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


@api_blueprint.route('/api/users/<nickname>/<site>')
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
