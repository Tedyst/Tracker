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
        data = sumb.find('span', class_="format-time")
        print(data)
        
    
    """result.append({
            "problema": nume,
            "scor": scor,
            "sursa": "infoarena",
            "data": data
        })"""


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
    for i in range(0,nrpagini):
        result+=_getUser(user, i)

    return result


def testUser(user):
    if _getNumberOfPages(user)==-1:
        return False
    return True



if __name__ == "__main__":
    _getUser("RedPipper",1)