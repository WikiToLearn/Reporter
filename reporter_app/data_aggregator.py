from reporter_app.providers import git_provider as gp
from reporter_app.providers import phabricator_provider as pp
from reporter_app.providers import mediawiki_provider as mp
import json


datas = json.load(open("data_json","r"))


def fetch_data(id, start_date, end_date, repos, phab_groups, mediawiki_langs ):
    if id not in datas:
        data = {}
        datas[id] = data
        data["git"] = []
        #getting data from git
        print("Fetching git data...")
        for repo in repos:
            data["git"].append(
                {
                    "repo_name": repo,
                    "stats_per_user" : gp.get_contributes_per_user(repo, start_date, end_date),
                    "stats_total": gp.get_total_contributions(repo, start_date, end_date)
                 })
        #getting data from phab
        data["phabricator"] = {}
        print("Fetching phabricator data...")
        for ph_gr in phab_groups:
            ph_data = pp.calculate_generic_stats(phab_groups[ph_gr], start_date, end_date)
            data["phabricator"][ph_gr] = ph_data
    json.dump(datas,open("data_json","w"), indent=4)
    return datas[id]


def calculate_totals_phabricator(id):
    phdata = datas[id]["phabricator"]
    result = {
                "opened" : 0,
                "closed" : 0,
                "comments" : 0,
                "total_open" : 0}
    for pr in phdata.values():
        result["opened"] += pr["opened"]
        result["closed"] += pr["closed"]
        result["comments"] += pr["comments"]
        result["total_open"] += pr["total_open"]
    return result
