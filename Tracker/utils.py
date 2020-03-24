import importlib


def validUsername(username, site):
    mod = importlib.import_module("Tracker.sites." + site)
    if mod.testUser(username):
        return True
    return False
