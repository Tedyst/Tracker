from Tracker.utils import roundTime


def streak(probleme):
    result = {
        "highest": {
            "days": 0,
            "date": 0,
            "count": 0
        },
        "current": {
            "days": 0,
            "date": 0,
            "count": 0
        }
    }

    for i in probleme:
        if result["current"]["date"] == roundTime(i.data):
            result["current"]["count"] += 1
        elif result["current"]["date"] == roundTime(i.data) - 86400 * result["current"]["days"]:
            result["current"]["days"] += 1
            result["current"]["count"] += 1
            result["current"]["date"] += 1
        else:
            if result["highest"]["days"] < result["current"]["days"]:
                result["highest"] = result["current"]
            elif result["highest"]["days"] == result["current"]["days"] and \
                    result["highest"]["count"] < result["current"]["count"]:
                result["highest"] = result["current"]
            result["current"] = {
                "days": 1,
                "date": roundTime(i.data),
                "count": 1
            }
    return result
