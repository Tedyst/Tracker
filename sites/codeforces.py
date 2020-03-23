import requests
from bs4 import BeautifulSoup
import datetime
import time
from Tracker.classes import Problema

URL = "https://codeforces.com/submissions/"


def _getUser(idparent, user, page) -> [Problema]:
    r = requests.get(url=URL + user + '/page/' + str(page))
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', class_='status-frame-datatable')
    result = []

    for sumb in table.find_all('tr'):
        if sumb.contents[1].string != "#":
            link_problema = ""
            nume_problema = ""
            scor = ""
            data = ""
            # extrage numele si id-ul problemelor
            link = sumb.contents[7].find_all('a')
            for x in link:
                link_problema = x['href']
                nume_problema = x.get_text()

            # Alta incercare de scor
            scor = ""
            try:
                scor = sumb.contents[11].contents[1].contents[0].contents[0]
                try:
                    scor += sumb.contents[11].contents[1].contents[0].contents[1].contents[0]
                except IndexError:
                    pass
            except AttributeError:
                scor = sumb.contents[11].contents[1].contents[0]

            # extrage data
            data = sumb.contents[3].contents[1].contents[0]
            data = datetime.datetime.strptime(data, "%b/%d/%Y %H:%M")
            data = int(time.mktime(data.timetuple()))

            problema = Problema(idparent,
                                "codeforces",
                                nume_problema.strip(),
                                link_problema,
                                scor,
                                data,
                                user)
            result.append(problema)

    return result


def _getNumberOfPages(user):
    r = requests.get(url=URL + user)
    if r.url == "https://codeforces.com":
        return -1
    else:
        result = 0
        soup = BeautifulSoup(r.content, 'html.parser')
        result = len(soup.find_all('span', class_="page-index"))

        return result


def getUser(idparent, user) -> [Problema]:
    nrpagini = _getNumberOfPages(user)
    result = []
    for i in range(1, nrpagini+1):
        result += _getUser(idparent, user, i)

    return result


def testUser(user):
    if _getNumberOfPages(user) == -1:
        return False
    return True
