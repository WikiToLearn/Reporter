import requests
import datetime
import time
import config


def get_contributes_per_user(repo, weeks):
    start_date = datetime.date.today()  -datetime.timedelta(weeks=weeks)
    while True:
        r = requests.get("https://api.github.com/repos/"+repo+ "/stats/contributors",
                         auth=(config.github_user, config.github_pass))
        print(r.status_code)
        if r.status_code == 202:
            time.sleep(2)
        elif r.status_code == 200:
            break
        elif r.status_code not in [202, 200]:
            print("Error "+ r.status_code)
            return
    data = r.json()
    result = {"users_data": []}
    for item in data:
        aut  = {
            "username": item['author']['login'],
            "avatar": item['author']['avatar_url'],
            "total_contributions": item['total'],
            "additions": 0,
            "deletions": 0,
            "commits": 0
        }
        for week in item['weeks']:
            w = datetime.date.fromtimestamp(week['w'])
            if w >= start_date:
                aut['additions']+= week['a']
                aut['deletions']+= week['d']
                aut['commits']+= week['c']
        result['users_data'].append(aut)
    return result


def get_total_contributions(repo, weeks):
    start_date = datetime.date.today()  -datetime.timedelta(weeks=weeks)
    while True:
        r = requests.get("https://api.github.com/repos/"+repo+ "/stats/commit_activity",
                         auth=('valsdav', 'Cespedosio1999'))
        print(r.status_code)
        if r.status_code == 202:
            time.sleep(2)
        elif r.status_code == 200:
            break
        elif r.status_code not in [202, 200]:
            print("Error "+ r.status_code)
            return
    data = r.json()
    result = {
        "repo"; repo,
        "n_commit": 0,
        "total_additions" : 0,
        "total_deletions" : 0
    }
    for item in data:
        w = datetime.date.fromtimestamp(item['week'])
        if w>= start_date:
            result['n_commit']+= item['total']

    #additions and deletions
    while True:
        r2 = requests.get("https://api.github.com/repos/"+repo+ "/stats/code_frequency",
                         auth=('valsdav', 'Cespedosio1999'))
        print(r2.status_code)
        if r2.status_code == 202:
            time.sleep(2)
        elif r2.status_code == 200:
            break
        elif r2.status_code not in [202, 200]:
            print("Error "+ r2.status_code)
            return
    data2 = r2.json()
    for item in data2:
        w = datetime.date.fromtimestamp(item[0])
        if w>= start_date:
            result['total_additions']+= item[1]
            result['total_deletions']+= item[2]

    return result



if __name__ == '__main__':
    j = get_contributes_per_user("WikiToLearn/WikiToLearn", 2)
    j2 = get_total_contributions("WikiToLearn/WikiToLearn", 2)
    j.update(j2)
    print(j)
