import requests
import datetime
import yaml

pconfig = yaml.load(open('/etc/reporter-providers.conf','r'))

def get_recentchanges_data(lang, start_date, end_date):
    params = {"action":"query",
              "list":"recentchanges",
              "format":"json",
              "rcdir": "newer",
              "rcstart": start_date.strftime("%Y%m%d%H%M%S"),
              "rcend": end_date.strftime("%Y%m%d%H%M%S"),
              "rcprop":"user|sizes",
              "rctype":"edit",
              "rcshow": "!anon",
              "rclimit": 100}
    rclist_edit = []
    while True:
        r = requests.get(pconfig['sources']['mediawiki_api_url'].format(lang),
                         params=params).json()
        rclist_edit += r["query"]["recentchanges"]
        if "continue" in r:
            params["rccontinue"] = r["continue"]["rccontinue"]
            print('#')
        else:
            break
    #now new pages
    params["rctype"] = "new"
    if "rccontinue" in params:
        params.pop("rccontinue")
    print("getting new pages")
    rclist_new = []
    while True:
        r = requests.get(pconfig['sources']['mediawiki_api_url'].format(lang),
                         params=params).json()
        rclist_new += r["query"]["recentchanges"]
        if "continue" in r:
            params["rccontinue"] = r["continue"]["rccontinue"]
            print('%')
        else:
            break
    return {
        "edit": rclist_edit,
        "new": rclist_new}

def get_new_users_number(lang, start_date, end_date ):
    print("Getting new users for lang: {}".format(lang))
    params = {"action":"query",
              "list":"logevents",
              "format":"json",
              "ledir": "newer",
              "lestart": start_date.strftime("%Y%m%d%H%M%S"),
              "leend": end_date.strftime("%Y%m%d%H%M%S"),
              "leaction": "newusers/create",
              "leprop": "user",
              "rclimit": 100}
    new_users = []
    while True:
        r = requests.get(pconfig['sources']['mediawiki_api_url'].format(lang),
                         params=params).json()
        new_users += r["query"]["logevents"]
        if "continue" in r:
            params["lecontinue"] = r["continue"]["lecontinue"]
            print('#')
        else:
            break
    return len(new_users)


def get_mediawiki_stats(lang, start_date, end_date, blacklist):
    data = get_recentchanges_data(lang, start_date, end_date)
    result = {
        "total_new_pages": len(data["new"]),
        "total_edits": len(data["edit"]),
        "total_additions": 0,
        "total_deletions": 0,
        "total_new_users" : get_new_users_number(lang, start_date, end_date),
        "users_stats": []
    }
    used_users = {}
    for nrc in data['new']:
        user = nrc["user"]
        if user in blacklist:
            continue
        result["total_additions"] += nrc["newlen"]
        if user in used_users and "additions" in used_users[user]:
            used_users[user]["additions"] += nrc["newlen"]
            used_users[user]["new_pages"] +=1
        else:
            used_users[user] = { "username": user, "additions": nrc["newlen"],
                                          "deletions": 0, "new_pages":0, "edits":0}
    for erc in data["edit"]:
        ch = erc["newlen"] - erc["oldlen"]
        user = erc["user"]
        if user in blacklist:
            continue
        if ch >= 0:
            result["total_additions"] += ch
            if user in used_users and "additions" in used_users[user]:
                used_users[user]["additions"] += ch
                used_users[user]["edits"] += 1
            else:
                used_users[user] = { "username": user, "additions": ch, "deletions": 0,
                                              "new_pages":0, "edits":1}
        else:
            result["total_deletions"] += ch
            if user in used_users and "deletions" in used_users[user]:
                used_users[user]["deletions"] += ch
                used_users[user]["edits"] += 1
            else:
                used_users[user] = {"username": user,"additions":0, "deletions": ch,
                                              "new_pages": 0, "edits":1}
    for u in used_users:
        result["users_stats"].append(used_users[u])
    return result
