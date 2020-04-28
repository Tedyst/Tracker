from Tracker import User, Problema, dbutils, db, SITES
from datetime import datetime, timedelta
from Tracker.utils import roundTime


def last_days(probleme: [Problema]):
    result = {
        "resolved": 0,
        "failed": 0,
        "count": {}
    }

    for i in probleme:
        time = roundTime(i.data)
        if time not in result["count"]:
            result["count"][time] = {
                "resolved": 0,
                "failed": 0
            }
        if i.scor == "Accepted" or i.scor == "100":
            result["count"][time]["resolved"] += 1
            result["resolved"] += 1
        else:
            result["count"][time]["failed"] += 1
            result["failed"] += 1
    return result
