import importlib
SITES = ['pbinfo', 'infoarena']


def getUser(user):
    result = []
    for site in SITES:
        mod = importlib.import_module(site, site)
        if mod.testUser(user):
            result += mod.getUser(user)
    return result


def testUser(user):
    for site in SITES:
        mod = importlib.import_module(site, site)
        if mod.testUser(user):
            return True
    return False
