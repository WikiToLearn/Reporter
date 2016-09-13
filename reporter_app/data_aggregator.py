from reporter_app.providers import git_provider as gp
from reporter_app.providers import phabricator_provider as pp
from reporter_app.providers import mediawiki_provider as mp
import json


datas = json.load(open("data_store.json","r"))


def fetch_data(id, start_date, end_date, repos, phab_groups, mediawiki_langs ):
    if id not in datas:
        data = {}
        datas[id] = data
        data["git"] = {}
        #getting data from git
        print("Fetching git data...")
        for repo in repos:
            data["git"][repo] = gp.get_complete_stats(repo, start_date, end_date)
        #getting data from phab
        data["phabricator"] = {}
        print("Fetching phabricator data...")
        for ph_gr in phab_groups:
            ph_data = pp.calculate_generic_stats(phab_groups[ph_gr], start_date, end_date)
            data["phabricator"][ph_gr] = ph_data
        json.dump(datas,open("data_store.json","w"), indent=4)
    return datas[id]


def calculate_totals_phabricator(id):
    phdata = datas[id]["phabricator"]
    result = {
                "opened" : 0,
                "closed" : 0,
                "comments" : 0,
                "total_open" : 0,
                "users_stats": {}
            }
    for pr in phdata.values():
        result["opened"] += pr["opened"]
        result["closed"] += pr["closed"]
        result["comments"] += pr["comments"]
        result["total_open"] += pr["total_open"]
        #calculating totals for users
        usstats = result["users_stats"]
        for user, usd in pr["users_stats"].items():
            if user not in result["users_stats"]:
                usstats[user] =  {
                    "opened":0,
                    "closed": 0,
                    "resolved":0,
                    "comments":0}
            #adding
            usstats[user]["opened"] += usd["opened"]
            usstats[user]["closed"] += usd["closed"]
            usstats[user]["resolved"] += usd["resolved"]
            usstats[user]["comments"] += usd["comments"]
    return result

def calculate_totals_git(id):
    phdata = datas[id]["git"]
    result = {
        "total_commits": 0,
        "total_additions":0,
        "total_deletions": 0,
        "users_stats" : {}
        }
    for gp in phdata.values():
        result["total_commits"] += gp["n_commits"]
        result["total_additions"] += gp["additions"]
        result["total_deletions"] += gp["deletions"]
        #calculating totals for users
        usstats = result["users_stats"]
        for user, usd in gp["users_stats"].items():
            if user not in result["users_stats"]:
                usstats[user] =  {
                    "avatar" : usd["avatar"],
                    "total_contributions":0,
                    "total_commits": 0,
                    "total_additions":0,
                    "total_deletions":0}
            #adding
            usstats[user]["total_contributions"] += usd["total_contributions"]
            usstats[user]["total_commits"] += usd["commits"]
            usstats[user]["total_additions"] += usd["additions"]
            usstats[user]["total_deletions"] += usd["deletions"]

    return result
