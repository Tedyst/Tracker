from Tracker.db import createUser, updateUsername, getSurse, getUser
import Tracker


def test_pbinfo():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst", "pbinfo")
    surse = getSurse("Tedyst", "pbinfo")
    for problema in surse:
        if type(problema) != Tracker.Problema:
            assert False
    assert True


def test_codeforces():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst", "codeforces")
    surse = getSurse("Tedyst", "codeforces")
    for problema in surse:
        if type(problema) != Tracker.Problema:
            assert False
    assert True


def test_infoarena():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst", "infoarena")
    surse = getSurse("Tedyst", "infoarena")
    for problema in surse:
        if type(problema) != Tracker.Problema:
            assert False
    assert True


def test_notfound_pbinfo():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst123", "pbinfo")
    user = getUser("Tedyst")
    assert user.pbinfo is None


def test_notfound_infoarena():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst123", "infoarena")
    user = getUser("Tedyst")
    assert user.infoarena is None


def test_notfound_codeforces():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst123", "codeforces")
    user = getUser("Tedyst")
    assert user.codeforces is None
