import Tracker.db as db
from Tracker import Problema, User


def test_pbinfo():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst", "pbinfo")
    surse = db.getSurse("Tedyst", "pbinfo")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_codeforces():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst", "codeforces")
    surse = db.getSurse("Tedyst", "codeforces")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_infoarena():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst", "infoarena")
    surse = db.getSurse("Tedyst", "infoarena")
    for problema in surse:
        if type(problema) != Problema:
            assert False
    assert True


def test_notfound_pbinfo():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst123", "pbinfo")
    user = db.getUser("Tedyst")
    assert user["pbinfo"] is None


def test_notfound_infoarena():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst123", "infoarena")
    user = db.getUser("Tedyst")
    assert user["pbinfo"] is None


def test_notfound_codeforces():
    db.createUser("Tedyst", "parola")
    db.updateUsername("Tedyst", "Tedyst123", "codeforces")
    user = db.getUser("Tedyst")
    assert user["pbinfo"] is None


def test_return_surse_db():
    db.createUser("Tedyst", "parola")
    sess = db.Session()
    # Force set the username to skip updates
    user = sess.query(User).filter(User.nickname == "Tedyst").first()
    user["pbinfo"] = "Tedyst"

    problema = Problema(user.id, "pbinfo", "test", "1", "100", 1, "Tedyst")
    db.addSurse(sess, [problema])
    sess.commit()

    surse = db._getSurse(user, sess, "pbinfo")
    assert problema == surse[0]
