
import requests
from bs4 import BeautifulSoup
import datetime
import time
from urllib.parse import urlencode

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
    PARAMS = {"only_table": "1", "first_entry": "0", "display_entries": 100, "user": user}
    r = requests.get(url=URL + urlencode(PARAMS))
    soup = BeautifulSoup(r.content, "lxml")
    asd = soup.contents[0].contents[0].contents[0].contents[0]
    nr = len(asd.contents) - 3
    return int(asd.contents[nr].contents[0])


def _getUser(user, page):
    PARAMS = {"only_table": "1", "first_entry": page*100, "display_entries": 100, "user": user}
    r = requests.get(url=URL + urlencode(PARAMS))
    soup = BeautifulSoup(r.content, "lxml")
    result = []
    for problema in soup.find('table').find('tbody'):
        nume = problema.contents[2].contents[0].contents[0]
        data = _formattedDate(problema.contents[5].contents[0])
        data = int(time.mktime(datetime.datetime.strptime(data, "%d %m %y %H:%M:%S").timetuple()))
        scor = str(problema.contents[6].contents[0].contents[0].contents[0])
        if "Eroare" in scor:
            scor = -1
        else:
            scor = scor.replace("Evaluare completa: ", "")
            scor = int(scor.replace("puncte", ""))
        result.append({
            "problema": nume,
            "scor": scor,
            "sursa": "infoarena",
            "data": data
        })
    return result


def getUser(user):
    nrpagini = _getNumberOfPages(user)
    result = []
    for i in range(0, nrpagini):
        result += _getUser(user, i)
    return result


def testUser(user):
    return True


if __name__ == "__main__":
    dicti = getUser("alexbolfa")
    print(dicti)