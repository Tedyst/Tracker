import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import datetime
import time


URL = "https://codeforces.com/submissions/"

""" r = requests.get(url = URL+user)
    if r.url == "https://codeforces.com":
        return -1
    else:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('div', class_="datatable")
        for sumbission_time in table.find_all('span', class_="format-time"):
            print(sumbission_time.get_text()) """

def _getUser(user, page):
    r = requests.get(url = URL+user+'/page/'+str(page))
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', class_='status-frame-datatable')
    result= [] 

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

            result.append({
                    "problema": nume_problema.strip(),
                    "id": link_problema,
                    "scor": scor,
                    "sursa": "codeforces",
                    "data": data
                })

    return result
        
    


def _getNumberOfPages(user):
    r = requests.get(url = URL + user)
    if r.url == "https://codeforces.com":
        return -1
    else:
        result = 0
        soup = BeautifulSoup(r.content, 'html.parser')
        result = soup.find_all('span', class_="page-index").__len__()

        #for page_indexes in soup.find_all('span', class_="page-index"):
        #    result+=1

        return result
        


def getUser(user):
    nrpagini = _getNumberOfPages(user)
    result = []
    for i in range(1,nrpagini+1):
        result+=_getUser(user, i)

    return result


def testUser(user):
    if _getNumberOfPages(user)==-1:
        return False
    return True

if __name__ == "__main__":
    for a in getUser("Tedyst"):
        print(a)