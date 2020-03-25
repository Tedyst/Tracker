import importlib
from typing import Iterable
import time
from Tracker.utils import validUsername
import json
import threading
import hashlib
from Tracker import db, Problema, User, SITES, SITES_ALL


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
