from Tracker.db import createUser, updateUsername, getSurse


def test_pbinfo():
    createUser("Tedyst", "parola")
    updateUsername("Tedyst", "Tedyst", "pbinfo")
    surse = getSurse("Tedyst", "pbinfo")
    for i in surse:
        print(i.idprob)

