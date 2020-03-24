
import requests
import json
import datetime
import time
from classes import Problema

URL = "https://www.pbinfo.ro/ajx-module/profil/json-jurnal.php"


def getUser(idparent, user) -> [Problema]:
    PARAMS = {"user": user, "force_reload": "true"}
    r = requests.get(url=URL, params=PARAMS)
    data = json.loads(r.content)

    result = []
    for i in data['content']:
        data = datetime.datetime.strptime(i['data_upload'], "%Y-%m-%d")
        data = int(time.mktime(data.timetuple()))
        problema = Problema(idparent,
                            "pbinfo",
                            i['denumire'],
                            i['id'],
                            i['scor'],
                            data,
                            user)
        result.append(problema)
    return result


def testUser(user):
    PARAMS = {"user": user, "force_reload": "true"}
    if user is None:
        return False
    try:
        r = requests.get(url=URL, params=PARAMS)
    except Exception as e:
        print(e)
        return False
    data = json.loads(r.content)
    # The user dosen't exist
    if data['content'] is False:
        return False
    return True
