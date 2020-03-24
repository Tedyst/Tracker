import sqlalchemy
import importlib
from classes import User, Problema, sqlBase, SITES, SITES_ALL
from typing import Iterable
import time


engine = sqlalchemy.create_engine('sqlite:///data.db', echo=True)
Session = sqlalchemy.orm.sessionmaker(bind=engine)
sqlBase.metadata.create_all(engine)


def getSurse(nickname, site) -> Iterable[Problema]:
    sess = Session()
    user = sess.query(User).filter(User.nickname == nickname).first()
    if user is None:
        return
    if site == "all":
        for site in SITES:
            if user[site] is not None:
                if user["last_" + site] is None:
                    _updateSurse(sess, user, site)
                elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
                    _updateSurse(sess, user, site)
        sess.commit()
        return _getSurse(user, sess, "all")
    if user[site] is not None:
        if user["last_" + site] is None:
            updateSurse(user, site)
        elif time.time() - user["last_" + site] > 600:  # The DB was updated max 10 mins ago
            updateSurse(user, site)
        return _getSurse(user, sess, site)
    return None


def _getSurse(user: User, sess: Session, site) -> Iterable[Problema]:
    if site == "all":
        q = sess.query(Problema).filter(Problema.iduser == user.id).all()
    else:
        q = sess.query(Problema).filter(Problema.iduser == user.id)\
                                .filter(Problema.sursa == site).all()
    return q


def getSurseAPI(user, site) -> Iterable[Problema]:
    sess = Session()
    if site == "all":
        q = sess.query(Problema).filter(Problema.username == user).all()
    else:
        q = sess.query(Problema).filter(Problema.sursa == site)\
                                .filter(Problema.username == user).all()
    return q


def addSurse(s: Session, probleme):
    for i in probleme:
        if type(i) != Problema:
            continue
        sursa = s.query(Problema).filter(Problema.data == i.data).first()
        if sursa is None:
            s.add(i)


def _updateSurse(s: Session, user: User, sursa):
    if sursa not in SITES_ALL:
        return
    if sursa == "all":
        for i in SITES:
            updateSurse(user, i)
        return
    if user[sursa] is not None:
        mod = importlib.import_module("sites." + sursa)
        print("Updating surse for ", user.nickname, " from site ", sursa)
        if mod.testUser(user[sursa]):
            addSurse(s, mod.getUser(user.id, user[sursa]))
        user["last_" + sursa] = int(time.time())


def updateSurse(user: User, sursa):
    s = Session()
    _updateSurse(s, user, sursa)
    s.commit()


def userExists(nickname):
    s = Session()
    user = s.query(User).filter(nickname == nickname).first()
    if user is None:
        return False
    return True


def createUser(nickname, password):
    s = Session()
    if userExists(nickname):
        return
    user = User(nickname, password)
    s.add(user)
    s.commit()


def getUser(nickname):
    s = Session()
    user = s.query(User).filter(User.nickname == nickname).first()
    return user


def updateUsername(nickname, username, site):
    if site not in SITES:
        return
    s = Session()
    user = s.query(User).filter(User.nickname == nickname).first()
    user[site] = username
    _updateSurse(s, user, site)
    s.commit()
