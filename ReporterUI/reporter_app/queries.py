coll_params = {
    "phabricator": "id",
    "git": "repo"
}


def get_projection(collection, lang=""):
    if collection == "mediawiki":
        return {
            "$project": {
                "end_date":1,
                "id": 1,
                "_id": 0,
                "total_new_pages": "$mediawiki.{}.total_new_pages".format(lang),
                "total_edits": "$mediawiki.{}.total_edits".format(lang),
                "total_additions": "$mediawiki.{}.total_additions".format(lang),
                "total_new_users": "$mediawiki.{}.total_new_users".format(lang),
                "total_deletions": "$mediawiki.{}.total_deletions".format(lang)
                }
            }
    elif collection == "phabricator":
        return {
            "$project":{
                "end_date":1,
                "id": 1,
                "_id": 0,
                "opened": "$phabricator.opened",
                "changed": "$phabricator.changed",
                "total_close": "$phabricator.total_close",
                "total_open": "$phabricator.total_open",
                "resolved": "$phabricator.resolved",
                "comments": "$phabricator.comments",
                "not_resolved": "$phabricator.not_resolved",
                "closed": "$phabricator.closed"
                }
            }
    elif collection == "git":
        return {
            "$project":{
                "end_date":1,
                "id": 1,
                "_id": 0,
                "additions": "$git.additions",
                "deletions": "$git.deletions",
                "n_commits": "$git.n_commits"
                }
            }
    elif collection == "users_mediawiki":
        return {
            "$project": {
            "end_date":1,
            "id": 1,
            "_id": 0,
            "new_pages": "$totals_mediawiki.users_stats.new_pages",
            "edits":     "$totals_mediawiki.users_stats.edits",
            "additions": "$totals_mediawiki.users_stats.additions",
            "new_users": "$totals_mediawiki.users_stats.new_users",
            "deletions": "$totals_mediawiki.users_stats.deletions",
            "score":     "$totals_mediawiki.users_stats.score"
            }
        }
    elif collection == "users_phab":
        return {
            "$project": {
            "end_date":1,
            "id": 1,
            "_id": 0,
            "opened":  "$totals_phab.users_stats.opened",
            "changed": "$totals_phab.users_stats.changed",
            "resolved": "$totals_phab.users_stats.resolved",
            "comments": "$totals_phab.users_stats.comments",
            "not_resolved": "$totals_phab.users_stats.not_resolved",
            "closed": "$totals_phab.users_stats.closed"
            }
        }
    elif collection == "users_git":
        return {
            "$project": {
            "end_date":1,
            "id": 1,
            "_id": 0,
            "contributions": "$totals_git.users_stats.total_contributions",
            "additions": "$totals_git.users_stats.total_additions",
            "deletions": "$totals_git.users_stats.total_deletions",
            "n_commits": "$totals_git.users_stat.total_commits"
            }
        }
    elif collection == "totals_mediawiki":
        return {
            "$project": {
            "end_date":1,
            "id": 1,
            "_id": 0,
            "new_pages": "$totals_mediawiki.total_new_pages",
            "edits":     "$totals_mediawiki.total_edits",
            "additions": "$totals_mediawiki.total_additions",
            "new_users": "$totals_mediawiki.total_new_users",
            "deletions": "$totals_mediawiki.total_deletions",
            "editors":   "$totals_mediawiki.total_users"
            }
        }
    elif collection == "totals_phabricator":
        return {
            "$project":{
                "end_date":1,
                "id": 1,
                "_id": 0,
                "opened": "$totals_phab.opened",
                "changed": "$totals_phab.changed",
                "total_close": "$totals_phab.total_close",
                "total_open": "$totals_phab.total_open",
                "resolved": "$totals_phab.resolved",
                "comments": "$totals_phab.comments",
                "not_resolved": "$totals_phab.not_resolved",
                "closed": "$totals_phab.closed"
                }
            }
    elif collection == "totals_git":
        return {
            "$project":{
                "end_date":1,
                "id": 1,
                "_id": 0,
                "additions": "$totals_git.total_additions",
                "deletions": "$totals_git.total_deletions",
                "n_commits": "$totals_git.total_commits"
                }
            }



def get_collection_query(collection, params):
    if collection == "mediawiki":
        return [
            {"$match": {"mediawiki.{}".format(params["lang"]):{"$exists":"true"}}},
            get_projection("mediawiki", params["lang"]),
            {"$sort": {"end_date":1}}
        ]
    else:
        return [
            {"$project": {collection : 1, "end_date":1, "_id":0, "id":1}},
            {"$unwind":"${}".format(collection)},
            {"$match": {"{}.{}".format(collection, coll_params[collection]): params[coll_params[collection]]}},
            get_projection(collection),
            {"$sort": {"end_date":1}}
        ]

def get_collection_user_query(collection, params):
    if collection != "phabricator":
        coll_name = "totals_"+ collection
    else:
        coll_name = "totals_phab"
    return [
        {"$project": {coll_name : 1, "end_date":1, "_id":0, "id":1}},
        {"$unwind": "${}.users_stats".format(coll_name)},
        {"$match": {"{}.users_stats.username".format(coll_name): params["username"]}},
        get_projection("users_"+collection),
        {"$sort": {"end_date":1}}
    ]

def get_collection_totals_query(collection):
    return [
        get_projection("totals_"+collection),
        {"$sort": {"end_date":1}}
        ]
