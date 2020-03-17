import pandas as pd
import importlib
import os

os.chdir("sites")


def user_convert(user, site):
    mod = importlib.import_module("sites." + site)
    if mod.testUser(user) is False:
        return -1  # user not found
    else:
        problem_set = mod.getUser(user)
        df = pd.DataFrame(problem_set)
        os.chdir("../db")
        df.to_csv(user+'_'+site+'.csv')


if __name__ == "__main__":
    user_convert("RedPipper", "infoarena")
