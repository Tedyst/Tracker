from Tracker import app, dbutils, User, db
from Tracker.routes.api import api_blueprint
import json
from flask import Response
import datetime


@api_blueprint.route('/api/calendar/<nickname>')
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
        timp = int(datetime.fromtimestamp(i.data).replace(
            hour=0, minute=0, second=0).timestamp())
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
