from Tracker import app, dbutils, User, db
import json
from flask import Response
from Tracker.routes.api import api_blueprint


@api_blueprint.route('/api/grafic1/<nickname>')
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

    data = dbutils.getSurse(user, "all")
    result = []
    for subm in data:
        prob = None
        for i, sub in enumerate(result):
            if sub["name"] == subm.problema:
                if result[i]["solved"] is False:
                    result[i]["attempts"] += 1
                    if subm.scor == "100" or subm.scor == "Accepted":
                        result[i]["solved"] = True
                        result[i]["data"] = subm.data
                    else:
                        result[i]["solved"] = False
                elif result[i]["data"] >= subm.data and not (subm.scor == "100" or subm.scor == "Accepted"):
                    result[i]["attempts"] += 1

                prob = sub
                break

        if prob is None:
            temp = {}
            temp["name"] = subm.problema
            temp["data"] = subm.data
            temp["attempts"] = 1
            if subm.scor == "100" or subm.scor == "Accepted":
                temp["solved"] = True
            else:
                temp["solved"] = False
            result.append(temp)

    result = sorted(result, key=lambda k: k['data'])
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
