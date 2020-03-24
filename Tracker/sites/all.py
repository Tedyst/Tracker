import importlib
SITES = ['pbinfo', 'codeforces', 'infoarena']


def getUser(user):
    result = []
    for site in SITES:
        mod = importlib.import_module("sites." + site)
        if mod.testUser(user):
            result += mod.getUser(user)
    return result


def testUser(user):
    for site in SITES:
        mod = importlib.import_module("sites." + site)
        if mod.testUser(user):
            return True
    return False
