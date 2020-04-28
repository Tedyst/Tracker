import importlib
from datetime import datetime


def validUsername(username, site):
    mod = importlib.import_module("Tracker.sites." + site)
    if mod.testUser(username):
        return True
    return False


def roundTime(time):
    return int(datetime.fromtimestamp(time).replace(
        hour=0, minute=0, second=0).timestamp())
