import requests
from bs4 import BeautifulSoup
import datetime
import time
from Tracker import Problema

URL = "https://codeforces.com/submissions/"


def _getUser(user, page) -> [Problema]:
    r = requests.get(url=URL + user + '/page/' + str(page))
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', class_='status-frame-datatable')
    result = []

    for sumb in table.find_all('tr'):
        if sumb.contents[1].string != "#":
            idprob = ""
            nume_problema = ""
            scor = ""
            data = ""

            # extrage numele si id-ul problemelor
            link = sumb.contents[7].find_all('a')
            for x in link:
                idprob = x['href']
                nume_problema = x.get_text()
                nume_problema = nume_problema.replace('/contest/', '')
                nume_problema = nume_problema.replace('/gym/', '')
                nume_problema = nume_problema.replace('/problem/', '')

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

            url = "https://codeforces.com" + idprob

            problema = Problema("codeforces",
                                nume_problema.strip(),
                                idprob,
                                scor,
                                data,
                                user,
                                url)
            result.append(problema)

    return result


def _getNumberOfPages(user):
    r = requests.get(url=URL + user)
    if r.url == "https://codeforces.com/":
        return None
    else:
        result = 0
        soup = BeautifulSoup(r.content, 'html.parser')
        result = len(soup.find_all('span', class_="page-index"))

        return result


def getUser(user) -> [Problema]:
    nrpagini = _getNumberOfPages(user)
    result = []
    for i in range(1, nrpagini+1):
        result += _getUser(user, i)

    return result


def testUser(user):
    if _getNumberOfPages(user) == None:
        return False
    return True
