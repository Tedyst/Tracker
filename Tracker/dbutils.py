import importlib
from typing import Iterable
import time
from Tracker import db, Problema, User, SITES, app
from Tracker.utils import validUsername
from threading import Thread
import queue
from sqlalchemy.orm import raiseload
updatequeue = queue.Queue()


def getSurse(user: User, site) -> Iterable[Problema]:
    if site == "all":
        result = []
        for i in SITES:
            if user[i] is not None:
                result += Problema.query.filter(Problema.username == user[i])\
                    .filter(Problema.sursa == i)\
                    .options(raiseload('*'))\
                    .order_by(Problema.data).all()
        return result
    else:
        q = Problema.query.filter(Problema.username == user[site])\
            .options(raiseload('*'))\
            .filter(Problema.sursa == site)\
            .order_by(Problema.data).all()
    return q


def getSurseSince(user: User, site, since) -> Iterable[Problema]:
    if site == "all":
        result = []
        if user is None:
            return Problema.query.filter(Problema.data >= since)\
                .options(raiseload('*'))\
                .order_by(Problema.data).all()

        for i in SITES:
            if user[i] is not None:
                result += Problema.query.filter(Problema.username == user[i])\
                                        .filter(Problema.sursa == i)\
                                        .filter(Problema.data >= since)\
                                        .options(raiseload('*'))\
                                        .order_by(Problema.data).all()
        return result
    else:
        if user is None:
            return Problema.query.filter(Problema.data >= since)\
                .filter(Problema.sursa == site)\
                .options(raiseload('*'))\
                .order_by(Problema.data).all()

        return Problema.query.filter(Problema.username == user[site])\
            .options(raiseload('*'))\
            .filter(Problema.data >= since)\
            .filter(Problema.sursa == site)\
            .order_by(Problema.data).all()


def addSurse(probleme):
    for i in probleme:
        if type(i) != Problema:
            continue
        sursa = Problema.query.filter(Problema.data == i.data).first()
        if sursa is None:
            db.session.add(i)
    db.session.commit()


def updateSurse(sursa, username):
    mod = importlib.import_module("Tracker.sites." + sursa)
    app.logger.debug(
        "Updating surse for user %s from site %s", username, sursa)
    if mod.testUser(username):
        probleme = mod.getUser(username)
        for i in probleme:
            if type(i) != Problema:
                continue
            updatequeue.put(i)


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
    return user


def getUser(nickname):
    return User.query.filter(User.nickname == nickname).first()


def updateUsername(user: User, username, site):
    if site not in SITES:
        app.logger.debug("Site-ul %s nu exista",
                         site)
        return
    if not validUsername(username, site):
        app.logger.debug("Username %s nu exista pe site-ul %s",
                         username, site)
        return
    app.logger.info("Schimbat username pentru site %s, user %s in %s",
                    site, user.nickname, username)
    user[site] = username
    user["last_" + site] = None
    updateThreaded(user)


def needsUpdate(user: User, site):
    if app.debug:
        app.logger.debug("Fortam update pentu ca avem DEBUG mode.")
        return True
    if site == "all":
        for site in SITES:
            if user[site] is not None:
                if user["last_" + site] is None:
                    return True
                # The DB was updated max 10 mins ago
                elif time.time() - user["last_" + site] > 600:
                    return True
    if user[site] is not None:
        if user["last_" + site] is None:
            return True
        # The DB was updated max 10 mins ago
        elif time.time() - user["last_" + site] > 600:
            return True
    return False


def updateThreaded(user: User):
    # Create a new thread that controls all the other threads
    thread = Thread(target=_threadedupd, args=[user.usernames(), user.lock])
    for i in SITES:
        if user[i] is not None:
            user["last_" + i] = int(time.time())
    db.session.commit()
    thread.start()


def _threadedupd(usernames, lock):
    # If it is locked, it means that the user is updating already
    if lock.locked():
        return
    # Start updating user
    lock.acquire()
    threads = []

    for i in SITES:
        if usernames[i] is not None:
            thread = Thread(target=updateSurse, args=[i, usernames[i]])
            threads.append(thread)

    for site in threads:
        site.start()
    for site in threads:
        site.join()

    deleted = {}
    while True:
        try:
            elem = updatequeue.get_nowait()
        except queue.Empty:
            break
        # Nu am sters inca
        if elem.sursa not in deleted:
            Problema.query.filter(Problema.username == usernames[elem.sursa])\
                          .filter(Problema.sursa == elem.sursa).delete()
            deleted[elem.sursa] = True

        db.session.add(elem)
        updatequeue.task_done()
    db.session.commit()
    app.logger.debug("Committed to databsase")
    lock.release()
