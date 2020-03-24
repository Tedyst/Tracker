from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import json
SITES = ['pbinfo', 'infoarena', 'codeforces']
SITES_ALL = ['pbinfo', 'infoarena', 'codeforces', 'all']
sqlBase = declarative_base()


class User(sqlBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(50))
    nickname = Column(String(50))
    password = Column(String(50))

    for i in SITES:
        vars()[i] = Column(String)
        vars()["last_" + i] = Column(Integer)
    del i

    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password

    # Te rog nu intreba
    # Am facut asta ca sa putem accesa usernameurile ca user["pbinfo"] si user.pbinfo
    def __getitem__(self, key):
        try:
            return vars(self)[key]
        except Exception as e:
            print(e)
            return None

    def __setitem__(self, key, value):
        exec("self." + str(key) + " = '" + str(value) + "'")


class Problema(sqlBase):
    __tablename__ = 'probleme'
    id = Column(Integer, primary_key=True)
    iduser = Column(Integer)
    username = Column(String)
    sursa = Column(String)
    problema = Column(String)
    idprob = Column(String)
    scor = Column(String)
    data = Column(Integer)

    def __init__(self, iduser, sursa, problema, idprob, scor, data, username):
        self.iduser = iduser
        self.sursa = sursa
        self.problema = problema
        self.idprob = idprob
        self.scor = scor
        self.data = data
        self.username = username

    def to_json(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return json.dumps(data)

    def to_dict(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return data


def sortProbleme_date(self):
    return self.data