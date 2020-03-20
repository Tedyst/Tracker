import pandas as pd
import importlib

def user_convert(user, site):
    mod = importlib.import_module("sites." + site)
    if mod.testUser(user) is False:
        return -1  # user not found
    else:
        problem_set = mod.getUser(user)
        df = pd.DataFrame(problem_set)
        df.to_csv("db/" + user + '_' + site + '.csv')


# Ne cam trebuie asta btw
def query(user, site):
    mod = importlib.import_module("sites." + site)
    if mod.testUser(user) is False:
        return None
    else:
        return mod.getUser(user)
