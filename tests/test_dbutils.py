import Tracker.dbutils as dbutils
from Tracker import Problema, User
from threading import Thread


def test_pbinfo():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    user.pbinfo = "Tedyst"
    thread = Thread(target=dbutils._threadedupd, args=[user.usernames(), user.lock])
    thread.start()
    thread.join()
    surse = dbutils.getSurse(user, "pbinfo")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_codeforces():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    user.codeforces = "Tedyst"
    thread = Thread(target=dbutils._threadedupd, args=[user.usernames(), user.lock])
    thread.start()
    thread.join()
    surse = dbutils.getSurse(user, "codeforces")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_infoarena():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    user.infoarena = "Tedyst"
    thread = Thread(target=dbutils._threadedupd, args=[user.usernames(), user.lock])
    thread.start()
    thread.join()
    surse = dbutils.getSurse(user, "infoarena")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_notfound_pbinfo():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    dbutils.updateUsername(user, "Tedyst123", "pbinfo")
    user = dbutils.getUser("Tedyst")
    assert user["pbinfo"] is None


def test_notfound_infoarena():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    dbutils.updateUsername(user, "Tedyst123", "infoarena")
    user = dbutils.getUser("Tedyst")
    assert user["infoarena"] is None


def test_notfound_codeforces():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    user = dbutils.getUser("Tedyst")
    dbutils.updateUsername(user, "Tedyst123", "codeforces")
    user = dbutils.getUser("Tedyst")
    assert user["codeforces"] is None


def test_return_surse_dbutils():
    dbutils.createUser("Tedyst", "parola", "stoicatedy@gmail.com")
    # Force set the username to skip updates
    user = dbutils.getUser("Tedyst")
    user["pbinfo"] = "Tedyst"

    problema = Problema("pbinfo", "test", "1", "100", 1, "Tedyst", "")
    dbutils.addSurse([problema])

    surse = dbutils.getSurse(user, "pbinfo")
    assert problema == surse[0]
