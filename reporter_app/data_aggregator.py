from reporter_app.providers import git_provider as gp
from reporter_app.providers import phabricator_provider as pp
from reporter_app.providers import mediawiki_provider as mp
import json


datas = json.load(open("data_store.json","r"))


def fetch_data(id, start_date, end_date, repos, phab_groups, mediawiki_langs ):
    if id  not in datas:
        data = {}
        datas[id] = data
        data["git"] = {}
        data["phabricator"] = {}
        data["mediawiki"] = {}
    else:
        data = datas[id]
    #getting data from git
    print("Fetching git data...")
    for repo in repos:
        if repo in data["git"]:
            print("Repo {} already fetched...".format(repo))
            continue
        data["git"][repo] = gp.get_complete_stats(repo, start_date, end_date)
    #calculating totals for git
    print("Calculating git totals...")
    datas[id]["totals_git"] = calculate_totals_git(id)
    #getting data from phab

    print("Fetching phabricator data...")
    for ph_gr in phab_groups:
        if ph_gr in data["phabricator"]:
            if data["phabricator"][ph_gr]["phids"] == phab_groups[ph_gr]:
                print("Phabricator group {} already fetched...".format(ph_gr))
                continue
        ph_data = pp.calculate_generic_stats(phab_groups[ph_gr], start_date, end_date)
        data["phabricator"][ph_gr] = ph_data
    #calculate totals for phabricator
    print("Calculating phabricator totals...")
    datas[id]["totals_phab"] = calculate_totals_phabricator(id)
    #mediawiki data

    print("Fetching mediawiki data...")
    for mlang in mediawiki_langs:
        if mlang in data["mediawiki"]:
            print("Lang {} already fetched...".format(mlang))
            continue
        print("Lang: {}".format(mlang))
        mdata =  mp.get_mediawiki_stats(mlang, start_date, end_date)
        data["mediawiki"][mlang] = mdata
    #calculating totals for mediawiki
    print("Calculating mediawiki totals...")
    datas[id]["totals_mediawiki"] = calculate_totals_mediawiki(id)
    #saving all
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
                    "comments":0,
                    "avatar": usd["avatar"],
                    "profile_url": usd["profile_url"]}
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
                    "profile_url" :usd["profile_url"],
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

def calculate_totals_mediawiki(id):
    mdata = datas[id]["mediawiki"]
    result =  {
        "total_additions": 0,
        "total_deletions": 0,
        "total_edits": 0,
        "total_new_pages":0,
        "users_stats" : {}
    }
    for mp in mdata.values():
        result["total_additions"] += mp["total_additions"]
        result["total_deletions"] += mp["total_deletions"]
        result["total_new_pages"] += mp["total_new_pages"]
        result["total_edits"] += mp["total_edits"]
        #calculating totals for users
        usstats = result["users_stats"]
        for user, usd in mp["users_stats"].items():
            if user not in result["users_stats"]:
                usstats[user] =  {
                    "edits": 0,
                    "new_pages": 0,
                    "additions":0,
                    "deletions":0,
                    "score": 0}
            #adding
            usstats[user]["edits"] += usd["edits"]
            usstats[user]["new_pages"] += usd["new_pages"]
            usstats[user]["additions"] += usd["additions"]
            usstats[user]["deletions"] += usd["deletions"]
            usstats[user]["score"] = usd["new_pages"] *10 + usd["edits"]
    result["total_users"] = len(result["users_stats"])
    return result
