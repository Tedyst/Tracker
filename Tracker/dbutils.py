import importlib
from typing import Iterable
import time
from Tracker import db, Problema, User, SITES, SITES_ALL


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


def updateAndCommit(user: User, sursa):
    try:
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


def updateUsername(user: User, username, site):
    if site not in SITES:
        return
    user[site] = username
    updateSurse(user, site)


def needsUpdate(user: User, site):
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
