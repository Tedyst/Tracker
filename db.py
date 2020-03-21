import sqlalchemy
import importlib
from classes import User, Problema, sqlBase, SITES
from typing import Iterable


engine = sqlalchemy.create_engine('sqlite:///data.db', echo=True)
Session = sqlalchemy.orm.sessionmaker(bind=engine)
sqlBase.metadata.create_all(engine)


def getSurse(iduser, site) -> Iterable[Problema]:
    sess = Session()
    if site == "all":
        q = sess.query(Problema).filter(Problema.iduser == iduser).all()
    else:
        q = sess.query(Problema).filter(Problema.iduser == iduser).filter(Problema.sursa == site).all()
    return q


def getSurseAPI(user, site) -> Iterable[Problema]:
    sess = Session()
    if site == "all":
        q = sess.query(Problema).filter(Problema.username == user).all()
    else:
        q = sess.query(Problema).filter(Problema.sursa == site)\
                                .filter(Problema.username == user).all()
    return q


def addSurse(probleme):
    s = Session()
    for i in probleme:
        if type(i) != Problema:
            continue
        sursa = s.query(Problema).filter(Problema.data == i.data).first()
        if sursa is None:
            s.add(i)
    s.commit()


def updateSurse(nickname, sursa):
    if sursa == "all":
        for i in SURSE:
            updateSurse(nickname, i)
        return
    mod = importlib.import_module("sites." + sursa)
    user = getUser(nickname)
    print("Updating surse for " + user.nickname)
    if mod.testUser(user[sursa]):
        addSurse(mod.getUser(user.id, user[sursa]))


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
    s.commit()


if __name__ == "__main__":
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst", "pbinfo")
    updateSurse("Tedyst", "pbinfo")
    for i in getSurse(1, "pbinfo"):
        print(i.scor)
