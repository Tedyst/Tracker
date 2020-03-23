import Tracker.db as db
from Tracker import Problema


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
