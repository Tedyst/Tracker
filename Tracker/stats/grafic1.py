def grafic1(data):
    result = []
    for subm in data:
        prob = None
        for i, sub in enumerate(result):
            if sub["name"] == subm.problema:
                if result[i]["solved"] is False:
                    result[i]["attempts"] += 1
                    if subm.scor == "100" or subm.scor == "Accepted":
                        result[i]["solved"] = True
                        result[i]["data"] = subm.data
                    else:
                        result[i]["solved"] = False
                elif result[i]["data"] >= subm.data and not (subm.scor == "100" or subm.scor == "Accepted"):
                    result[i]["attempts"] += 1

                prob = sub
                break

        if prob is None:
            temp = {}
            temp["name"] = subm.problema
            temp["data"] = subm.data
            temp["attempts"] = 1
            if subm.scor == "100" or subm.scor == "Accepted":
                temp["solved"] = True
            else:
                temp["solved"] = False
            result.append(temp)

    result = sorted(result, key=lambda k: k['data'])
    return result
