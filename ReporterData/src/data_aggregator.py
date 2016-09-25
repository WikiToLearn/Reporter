from providers import git_provider as gp
from providers import phabricator_provider as pp
from providers import mediawiki_provider as mp
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import config
import json
import glob
import yaml

#init the db client
client = MongoClient(config.DB_HOST, config.DB_PORT)
db = client['reports_db']

def update_settings():
    '''
    This method reads the reports configurations from yaml files and
    fetch the data requested. The metadata are then stored in the metadata_store.
    '''
    for repo in glob.glob(config.settings_dir+"/*.yaml"):
        meta = yaml.load(open(repo, "r"))
        db["reports_metadata"].update({"id":meta["id"]},meta, upsert=True)
        print(">>> Reading report: {}".format(meta["id"]))
        fetch_data(meta["id"], meta["start_date"],
                        meta["end_date"], meta["git_repos"],
                        meta["phab_groups"], meta["mediawiki_langs"])
        #updating metadata
        db["reports_metadata"].replace_one({"id":meta["id"]},
                                           meta, upsert=True)


def fetch_data(id, start_date, end_date, repos, phab_groups, mediawiki_langs ):
    #checking if the id is in the db
    data = db["reports_data"].find_one({"id":id})
    if data == None:
        data = {"id": id, "start_date": start_date, "end_date": end_date}
        data["git"] = []
        data["phabricator"] = []
        data["mediawiki"] = {}
        git_metadata = []
        ph_metadata = {}
    else:
        #checking if the datas are changed
        if data["start_date"]!= start_date or data["end_date"]!=end_date:
            #wipe out all the dataset
            data = {"id": id, "start_date": start_date, "end_date": end_date}
            data["git"] = []
            data["phabricator"] = []
            data["mediawiki"] = {}
            git_metadata = []
            ph_metadata = {}
        else:
            #git metadata
            git_metadata = []
            for g in data["git"]:
                git_metadata.append(g["repo"])
            #loading phabrictor metadata
            ph_metadata = {}
            for p in data["phabricator"]:
                ph_metadata[p["id"]] = p["phids"]

    #getting data from git
    print("Fetching git data...")
    new_git_data = []
    #saving old data that is requested again
    for oldrepo in data["git"]:
        if oldrepo["repo"] in repos:
            #saving it
            print("Repo {} already fetched...".format(oldrepo["repo"]))
            new_git_data.append(oldrepo)
        else:
            print("Deleted repo: {}".format(oldrepo["repo"]))
    #adding new requested repos
    for repo in repos:
        if repo not in git_metadata:
            new_git_data.append(gp.get_complete_stats(repo, start_date, end_date))
    #saving new data
    data["git"] = new_git_data
    #calculating totals for git
    print("Calculating git totals...")
    data["totals_git"] = calculate_totals_git(data)

    #getting data from phab
    print("Fetching phabricator data...")
    new_phab_data = []
    #saving old data requested again
    for oph in data["phabricator"]:
        if oph["id"] in phab_groups:
            if oph["phids"] == phab_groups[oph["id"]]:
                #saving it
                print("Phab group {} already fetched...".format(oph["id"]))
                new_phab_data.append(oph)
        else:
            print("Deleted phab group: {}".format(oph["id"]))
    #adding new data and modified groups
    for ph_gr in phab_groups:
        if ph_gr in ph_metadata:
            if  phab_groups[ph_gr] != ph_metadata[ph_gr]:
                new_phab_data.append(pp.calculate_generic_stats(ph_gr,phab_groups[ph_gr],
                                                     start_date, end_date))
        else:
            new_phab_data.append(pp.calculate_generic_stats(ph_gr,phab_groups[ph_gr],
                                                 start_date, end_date))
    #saving new data
    data["phabricator"] = new_phab_data
    #calculate totals for phabricator
    print("Calculating phabricator totals...")
    data["totals_phab"] = calculate_totals_phabricator(data)

    #mediawiki data
    print("Fetching mediawiki data...")
    new_mediawiki_data = {}
    for omd in data["mediawiki"]:
        if omd in mediawiki_langs:
            #saving it
            print("Mediawiki lang {} already fetched...".format(omd))
            new_mediawiki_data[omd] = data["mediawiki"][omd]
        else:
            print("Deleted mediawiki lang {}".format(omd))
    for mlang in mediawiki_langs:
        if mlang not in data["mediawiki"]:
            print("Fetching lang: {}".format(mlang))
            new_mediawiki_data[mlang] = mp.get_mediawiki_stats(mlang, start_date, end_date)
    #saving data
    data["mediawiki"] = new_mediawiki_data
    #calculating totals for mediawiki
    print("Calculating mediawiki totals...")
    data["totals_mediawiki"] = calculate_totals_mediawiki(data)
    #saving all
    print("Updating database...")
    db["reports_data"].replace_one({"id":id}, data, upsert=True)
    print("DONE!")

def calculate_totals_phabricator(data):
    phdata = data["phabricator"]
    result = {
                "opened" : 0,
                "closed" : 0,
                "comments" : 0,
                "total_open" : 0,
                "users_stats": []
            }
    for pr in phdata:
        result["opened"] += pr["opened"]
        result["closed"] += pr["closed"]
        result["comments"] += pr["comments"]
        result["total_open"] += pr["total_open"]
        #calculating totals for users
        usstats = {}
        for usd in pr["users_stats"]:
            user = usd["username"]
            if user not in usstats:
                usstats[user] =  {
                    "username": user,
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
        for u in usstats:
            result["users_stats"].append(usstats[u])
    return result


def calculate_totals_git(data):
    gdata = data["git"]
    result = {
        "total_commits": 0,
        "total_additions":0,
        "total_deletions": 0,
        "users_stats" : []
        }
    for gp in gdata:
        result["total_commits"] += gp["n_commits"]
        result["total_additions"] += gp["additions"]
        result["total_deletions"] += gp["deletions"]
        #calculating totals for users
        usstats = {}
        for usd in gp["users_stats"]:
            user = usd["username"]
            if user not in usstats:
                usstats[user] =  {
                    "username": user,
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
        for u in usstats:
            result["users_stats"].append(usstats[u])
    return result

def calculate_totals_mediawiki(data):
    mdata = data["mediawiki"]
    result =  {
        "total_additions": 0,
        "total_deletions": 0,
        "total_edits": 0,
        "total_new_pages":0,
        "users_stats" : []
    }
    for mp in mdata.values():
        result["total_additions"] += mp["total_additions"]
        result["total_deletions"] += mp["total_deletions"]
        result["total_new_pages"] += mp["total_new_pages"]
        result["total_edits"] += mp["total_edits"]
        #calculating totals for users
        usstats = {}
        for usd in mp["users_stats"]:
            user = usd["username"]
            if user not in usstats:
                usstats[user] =  {
                    "username": user,
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
        for u in usstats:
            result["users_stats"].append(usstats[u])
    result["total_users"] = len(result["users_stats"])
    return result

if __name__ == '__main__':
    update_settings()
