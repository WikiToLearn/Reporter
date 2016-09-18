import requests
import datetime
import time
import reporter_app.providers.provider_config as pconfig


def get_contributes_per_user(repo, start_date, end_date):
    while True:
        r = requests.get("https://api.github.com/repos/"+repo+ "/stats/contributors",
                         auth=(pconfig.github_user, pconfig.github_pass))
        print(repo + " - " + str(r.status_code))
        if r.status_code == 202:
            time.sleep(2)
        elif r.status_code == 200:
            break
        elif r.status_code not in [202, 200]:
            print("Error  {}".format(r.status_code))
            return
    data = r.json()
    result = {}
    for item in data:
        aut  = {
            "avatar": item['author']['avatar_url'],
            "profile_url" : item['author']['html_url'],
            "total_contributions": item['total'],
            "additions": 0,
            "deletions": 0,
            "commits": 0
        }
        for week in item['weeks']:
            w = datetime.date.fromtimestamp(week['w'])
            if w >= start_date and w<=end_date:
                aut['additions']+= week['a']
                aut['deletions']+= week['d']
                aut['commits']+= week['c']
        if aut['commits']>0:
            result[item['author']['login']] = aut
    return result


def get_total_contributions(repo, start_date, end_date):
    while True:
        r = requests.get("https://api.github.com/repos/"+repo+ "/stats/commit_activity",
                        auth=(pconfig.github_user, pconfig.github_pass))
        print(repo + " - " + str(r.status_code))
        if r.status_code == 202:
            time.sleep(2)
        elif r.status_code == 200:
            break
        elif r.status_code not in [202, 200]:
            print("Error  {}".format(r.status_code))
            return
    data = r.json()
    result = {
        "n_commits": 0,
        "additions" : 0,
        "deletions" : 0
    }
    for item in data:
        w = datetime.date.fromtimestamp(item['week'])
        if w>= start_date and w<=end_date:
            result['n_commits']+= item['total']

    #additions and deletions
    while True:
        r2 = requests.get("https://api.github.com/repos/"+repo+ "/stats/code_frequency",
                         auth=(pconfig.github_user, pconfig.github_pass))
        print(repo + "- " + str(r2.status_code))
        if r2.status_code == 202:
            time.sleep(2)
        elif r2.status_code == 200:
            break
        elif r2.status_code not in [202, 200]:
            print("Error  {}".format(r.status_code))
            return
    data2 = r2.json()
    for item in data2:
        w = datetime.date.fromtimestamp(item[0])
        if w>= start_date and w<=end_date:
            result['additions']+= item[1]
            result['deletions']+= item[2]
    return result


def get_complete_stats(repo, start_date, end_date):
    result =  {}
    result.update(get_total_contributions(repo, start_date, end_date))
    result["users_stats"] = get_contributes_per_user(repo, start_date, end_date)
    return result
