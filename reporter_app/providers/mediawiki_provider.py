import requests
import reporter_app.providers.provider_config as pconfig
import datetime

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
              "rclimit": 20}
    rclist_edit = []
    while True:
        r = requests.get(pconfig.mediawiki_api_url.format(lang),
                         params=params).json()
        rclist_edit += r["query"]["recentchanges"]
        if "continue" in r:
            params["rccontinue"] = r["continue"]["rccontinue"]
            print('#')
        else:
            break
    #now new pages
    params["rctype"] = "new"
    rclist_new = []
    while True:
        r = requests.get(pconfig.mediawiki_api_url.format(lang),
                         params=params).json()
        rclist_new += r["query"]["recentchanges"]
        if "continue" in r:
            params["rccontinue"] = r["continue"]["rccontinue"]
            print('#')
        else:
            break
    return {
        "edit": rclist_edit,
        "new": rclist_new}


def get_mediawiki_stats(lang, start_date, end_date):
    data = get_recentchanges_data(lang, start_date, end_date)
    result = {
        "total_new_pages": len(data["new"]),
        "total_edits": len(data["edit"]),
        "total_addictions": 0,
        "total_deletions": 0,
        "users_data": {}
    }
    for nrc in data['new']:
        user = nrc["user"]
        result["total_addictions"] += nrc["newlen"]
        if user in result["users_data"] and "addictions" in result["users_data"][user] :
            result["users_data"][user]["addictions"] += nrc["newlen"]
            result["users_data"][user]["new_pages"] +=1
        else:
            result["users_data"][user] = { "addictions": nrc["newlen"],
                                          "deletions": 0, "new_pages":0}
    for erc in data["edit"]:
        ch = erc["newlen"] - erc["oldlen"]
        user = erc["user"]
        if ch >= 0:
            result["total_addictions"] += ch
            if user in result["users_data"] and "addictions" in result["users_data"][user]:
                result["users_data"][user]["addictions"] += ch
            else:
                result["users_data"][user] = { "addictions": ch, "deletions": 0}
        else:
            result["total_deletions"] += ch
            if user in result["users_data"] and "deletions" in result["users_data"][user]:
                result["users_data"][user]["deletions"] += ch
            else:
                result["users_data"][user] = {"addictions":0, "deletions": ch}
    return result
