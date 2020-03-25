import importlib
from typing import Iterable
import time
from Tracker.utils import validUsername
from flask_sqlalchemy import SQLAlchemy
import json
import threading
import hashlib
from Tracker import app
SITES = ['pbinfo', 'infoarena', 'codeforces']
SITES_ALL = ['pbinfo', 'infoarena', 'codeforces', 'all']
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    password = db.Column(db.String(200))
    email = db.Column(db.String(50))
    lock = threading.Lock()

    for i in SITES:
        vars()[i] = db.Column(db.String)
        vars()["last_" + i] = db.Column(db.Integer)
    del i

    def __init__(self, nickname, password, email):
        self.nickname = nickname
        self.password = password
        self.email = email

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

    def avatar(self):
        email = str(self.email).lower().encode('utf-8')
        return "https://www.gravatar.com/avatar/" + str(hashlib.md5(email).hexdigest())

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password, method='sha256')

    # def check_password(self, password):
    #     """Check hashed password."""
    #     return check_password_hash(self.password, password)


class Problema(db.Model):
    __tablename__ = 'probleme'
    id = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.Integer)
    username = db.Column(db.String)
    sursa = db.Column(db.String)
    problema = db.Column(db.String)
    idprob = db.Column(db.String)
    scor = db.Column(db.String)
    data = db.Column(db.Integer)
    url = db.Column(db.String)

    def __init__(self, iduser, sursa, problema, idprob, scor, data, username, url):
        self.iduser = iduser
        self.sursa = sursa
        self.problema = problema
        self.idprob = idprob
        self.scor = scor
        self.data = data
        self.username = username
        self.url = url

    def to_json(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["url"] = self.url
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return json.dumps(data)

    def to_dict(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["url"] = self.url
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return data


def sortProbleme_date(self):
    return self.data


def getSurse(nickname, site) -> Iterable[Problema]:
    """
    Returneaza sursele unui username de pe un site

    !!! site poate fi doar ['pbinfo' , 'codeforces', 'infoarena', 'all']

    Args:
        @nickname -> numele din baza de date
        @site -> site-ul de pe care sunt cerute sursele

    Returns:
        Iterable[Problema] -> un array cu probleme

    Usage:
        for problema in getSurse():
            print(problema.idprob)
    """
    user = User.query.filter(User.nickname == nickname).first()
    if user is None:
        return
    if site == "all":
        for site in SITES:
            if user[site] is not None:
                if user["last_" + site] is None:
                    updateSurse(user, site)
                elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
                    updateSurse(user, site)
        db.session.commit()
        return getSurse(user, "all")
    if user[site] is not None:
        if user["last_" + site] is None:
            updateSurse(user, site)
        elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
            updateSurse(user, site)
        return getSurse(user, site)
    return None


def getSurse(user: User, site) -> Iterable[Problema]:
    if site == "all":
        q = Problema.query.filter(Problema.iduser == user.id).all()
    else:
        q = Problema.query.filter(Problema.iduser == user.id)\
                                .filter(Problema.sursa == site).all()
    return q


def addSurse(probleme):
    for i in probleme:
        if type(i) != Problema:
            continue
        sursa = Problema.query.filter(Problema.data == i.data).first()
        if sursa is None:
            db.session.add(i)
    db.session.commit()


def updateSurse(user: User, sursa):
    if sursa not in SITES_ALL:
        return
    if sursa == "all":
        for i in SITES:
            updateSurse(user, i)
        return
    if user[sursa] is not None:
        mod = importlib.import_module("Tracker.sites." + sursa)
        print("Updating surse for ", user.nickname, " from site ", sursa)
        if mod.testUser(user[sursa]):
            addSurse(mod.getUser(user.id, user[sursa]))
        user["last_" + sursa] = int(time.time())
    db.session.commit()


def updateAndCommit(nickname, sursa):
    try:
        user = User.query.filter(User.nickname == nickname).first()
        updateSurse(user, sursa)
        db.session.commit()
        print("Committed to databsase")
        user.lock.release()
    except Exception as e:
        user.lock.release()
        raise e


def userExists(nickname):
    user = User.query.filter(User.nickname == nickname).first()
    if user is None:
        return False
    return True


def createUser(nickname, password, email):
    if userExists(nickname):
        return
    user = User(nickname, password, email)
    db.session.add(user)
    db.session.commit()


def getUser(nickname):
    user = User.query.filter(User.nickname == nickname).first()
    return user


def updateUsername(nickname, username, site):
    if site not in SITES:
        return
    if not validUsername(username, site):
        return
    user = User.query.filter(User.nickname == nickname).first()
    user[site] = username
    updateSurse(user, site)


def isTracked(username, site):
    if site not in SITES:
        return False
    problema = Problema.query.filter(Problema.username == username).first()
    if problema is None:
        return False
    return True


def needsUpdate(username, site):
    user = getUser(username)
    if site == "all":
        for site in SITES:
            if user[site] is not None:
                if user["last_" + site] is None:
                    return True
                elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
                    return True
    if user[site] is not None:
        if user["last_" + site] is None:
            return True
        elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
            return True
    return False
