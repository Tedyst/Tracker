
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import datetime
import time
from urllib.parse import urlencode
from Tracker.classes import Problema

URL = "https://infoarena.ro/monitor?"


def _formattedDate(data: str):
    data = data.replace("ian", "01")
    data = data.replace("feb", "02")
    data = data.replace("mar", "03")
    data = data.replace("apr", "04")
    data = data.replace("mai", "05")
    data = data.replace("iun", "06")
    data = data.replace("iul", "07")
    data = data.replace("aug", "08")
    data = data.replace("sep", "09")
    data = data.replace("oct", "10")
    data = data.replace("nov", "11")
    data = data.replace("dec", "12")
    return data


def _getNumberOfPages(user):
    PARAMS = {
        "only_table": "1",
        "first_entry": "0",
        "display_entries": 100,
        "user": user
    }
    r = requests.get(url=URL + urlencode(PARAMS))
    soup = BeautifulSoup(r.content, "lxml")
    pages = soup.contents[0].contents[0].contents[0].contents[0]
    if type(pages) == NavigableString:
        return 0
    if len(pages) == 5:
        return 1
    nr = len(pages.contents) - 3
    return int(pages.contents[nr].contents[0])


def _getUser(idparent, user, page) -> [Problema]:
    PARAMS = {
        "only_table": "1",
        "first_entry": page*100,
        "display_entries": 100,
        "user": user
    }
    r = requests.get(url=URL + urlencode(PARAMS))
    soup = BeautifulSoup(r.content, "lxml")
    result = []
    for problema in soup.find('table').find('tbody'):
        nume = problema.contents[2].contents[0].contents[0]

        data = _formattedDate(problema.contents[5].contents[0])
        data = datetime.datetime.strptime(data, "%d %m %y %H:%M:%S")
        data = int(time.mktime(data.timetuple()))

        scor = str(problema.contents[6].contents[0].contents[0].contents[0])
        if "Eroare" in scor:
            scor = -1
        else:
            scor = scor.replace("Evaluare completa: ", "")
            scor = int(scor.replace("puncte", ""))

        idprob = problema.contents[2].contents[0].attrs['href'].replace('/problema/', '')
        url = "https://www.infoarena.ro/problema/" + idprob

        problema = Problema(idparent,
                            "infoarena",
                            nume,
                            idprob,
                            scor,
                            data,
                            user,
                            url)
        result.append(problema)

    return result


def getUser(idparent, user) -> [Problema]:
    nrpagini = _getNumberOfPages(user)
    result = []
    for i in range(0, nrpagini):
        result += _getUser(idparent, user, i)
    return result


def testUser(user):
    if _getNumberOfPages(user) == 0:
        return False
    return True
