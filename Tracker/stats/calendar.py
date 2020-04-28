from datetime import datetime


def calendar(probleme):
    mem = []
    result = {}
    for i in probleme:
        timp = int(datetime.fromtimestamp(i.data).replace(
            hour=0, minute=0, second=0).timestamp())
        if i.idprob not in mem:
            if timp not in result:
                result[timp] = 0
            result[timp] += 1
            mem.append(i.idprob)
    return result
