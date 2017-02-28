#!/usr/bin/env python3
import json
import requests
import datetime
import yaml
pconfig = yaml.load(open('/etc/reporter-providers.conf','r'))

api_token = pconfig['sources']['phabricator_api_token']

def lookup_project_phabid_byname(name):
    return_phab_project_id = None
    data_query = {}
    data_query['api.token'] = api_token
    data_query['names[]'] = name
    url_query = 'https://phabricator.kde.org/api/project.query'
    response_query = requests.get(url_query, data=data_query)
    data_query_in = json.loads(response_query.content.decode('UTF-8'))
    if data_query_in['result'] != None:
        for phab_project_id in data_query_in['result']['data']:
            return_phab_project_id = phab_project_id
    return return_phab_project_id

def lookup_project_phabid_byid(id):
    return_phab_project_id = None
    data_query = {}
    data_query['api.token'] = api_token
    data_query['ids[]'] = id
    url_query = 'https://phabricator.kde.org/api/project.query'
    response_query = requests.get(url_query, data=data_query)
    data_query_in = json.loads(response_query.content.decode('UTF-8'))
    if data_query_in['result'] != None:
        for phab_project_id in data_query_in['result']['data']:
            return_phab_project_id = phab_project_id
    return return_phab_project_id

def make_phab_query(entrypoint, data):
        data['api.token'] = api_token
        url = 'https://phabricator.kde.org/api/{}'.format(entrypoint)
        response = requests.get(url, data=data)
        return response.json()['result']

def get_all_tasks(project_phids):
    print("Getting all tasks {}...".format(project_phids))
    result = {"open_tasks":{}, "closed_tasks":{}}
    for project_phid in project_phids:
        data = {}
        data['projectPHIDs[]'] = project_phid
        data['order'] = "order-modified"
        #getting the different status
        data['status'] = "status-open"
        open_tasks = make_phab_query("maniphest.query", data)
        result['open_tasks'].update(open_tasks)
        data['status'] = "status-closed"
        closed_tasks = make_phab_query("maniphest.query", data)
        result['closed_tasks'].update(closed_tasks)
    return result

def filter_task_by_date(tasks, start_date, end_date):
    print("Filtering tasks...")
    result = {}
    for phid, task in tasks.items():
        d = datetime.datetime.fromtimestamp(int(task['dateModified']))
        if d >= start_date and d<=end_date:
            result[phid] = task
    return result

#cache for transactions of the tasks
transactions_cache = {}
users_cache = {}
users_name_cache = {}

def get_user_metadata(phid):
    data = {"phids[0]": phid}
    result = make_phab_query("user.query", data)[0]
    user_data = {
        "username" : result['userName'],
        "realname" : result['realName'],
        "avatar": result['image'],
        "profile_url": result['uri']
    }
    users_cache[phid] = user_data
    users_name_cache[user_data["username"]] = user_data


def count_status_transition(tasks, oldstatus, newstatus_list, start_date, end_date):
    counter = 0
    users_counter = {}
    users_task_list = {}
    print(oldstatus, " ---> ", newstatus_list)
    for phid, task in tasks.items():
        print("Checking task status: T{}".format(task['id']))
        data = {"ids[0]": task['id']}
        if task['id'] not in transactions_cache:
            transactions_cache.update(make_phab_query('maniphest.gettasktransactions', data))
        #getting transcation for the taskid
        trans = transactions_cache[task['id']]
        for t in trans:
            d = datetime.datetime.fromtimestamp(int(t['dateCreated']))
            if d >= start_date and d<=end_date and t['transactionType']=="status" and \
                t['oldValue'] == oldstatus and t['newValue'] in newstatus_list:
                    counter+=1
                    user_phid = t['authorPHID']
                    if user_phid  not in users_cache:
                        get_user_metadata(user_phid)
                    user_data = users_cache[user_phid]
                    if user_data['username'] in users_counter:
                        users_counter[user_data['username']] += 1
                    else:
                        users_counter[user_data['username']] = 1
                        users_task_list[user_data['username']] = []
                    users_task_list[user_data['username']].append(task["id"])
    return (counter, users_counter, users_task_list)


def count_task_commented(tasks, start_date, end_date):
    counter = 0
    users_counter = {}
    users_task_list = {}
    for phid, task in tasks.items():
        print("Checking comments to task: T{}".format(task['id']))
        data = {"ids[0]": task['id']}
        if task['id'] not in transactions_cache:
            transactions_cache.update(make_phab_query('maniphest.gettasktransactions', data))
        #getting transcation for the taskid
        trans = transactions_cache[task['id']]
        for t in trans:
            d = datetime.datetime.fromtimestamp(int(t['dateCreated']))
            if d >= start_date and d<=end_date and t['transactionType'] == "core:comment":
                    counter+=1
                    #getting user details
                    user_phid = t['authorPHID']
                    if user_phid  not in users_cache:
                        get_user_metadata(user_phid)
                    user_data = users_cache[user_phid]
                    if user_data['username'] in users_counter:
                        users_counter[user_data['username']] += 1
                    else:
                        users_counter[user_data['username']] = 1
                        users_task_list[user_data['username']] = []
                    users_task_list[user_data['username']].append(task["id"])
    return  (counter, users_counter, users_task_list)


closed_status = [ "resolved",  "wontfix", "invalid",
                  "duplicate","spite"]
notsolved_status =  ["wontfix", "invalid", "duplicate","spite"]

def calculate_generic_stats(id, proj_ids, start_date, end_date):
    #looking up phids
    proj_phids = []
    for prj in proj_ids:
        proj_phids.append(lookup_project_phabid_byid(prj))
    result = {}
    all_tasks = get_all_tasks(proj_phids)
    result = {
        "id" : id,
        "phids": proj_ids,
        "total_open": len(all_tasks['open_tasks']),
        "total_close" : len(all_tasks['closed_tasks']),
        "users_stats" : []
    }
    users_stats =  {}
    #filter by date
    filt_tasks = {
        "open": filter_task_by_date(all_tasks['open_tasks'], start_date, end_date),
        "close": filter_task_by_date(all_tasks['closed_tasks'], start_date, end_date)
    }
    result["changed"] = len(filt_tasks['open'])+len(filt_tasks['close'])
    #now checking the change of status
    open_stat = count_status_transition(filt_tasks['open'],
                                        None,["open"], start_date, end_date)
    result["opened"] = open_stat[0]
    for user in open_stat[1]:
        if not user in users_stats:
            users_stats[user] = {
                "username" : user,
                "opened": 0,
                "closed": 0,
                "comments":0,
                "resolved":0,
                "not_resolved":0,
                "avatar" : users_name_cache[user]["avatar"],
                "profile_url" : users_name_cache[user]["profile_url"],
                "opened_tasks" : [], "closed_tasks": [],"comments_tasks":[],
                "resolved_tasks" : [], "not_resolved_tasks": []
            }
        users_stats[user]["opened"] += open_stat[1][user]
        users_stats[user]["opened_tasks"] += open_stat[2][user]

    closed_stat = count_status_transition(filt_tasks['close'],"open",
                                          closed_status, start_date, end_date)
    result["closed"] = closed_stat[0]
    for user in closed_stat[1]:
        if not user in users_stats:
            users_stats[user] = {
                "username" : user,
                "opened": 0,
                "closed": 0,
                "comments":0,
                "resolved":0,
                "not_resolved":0,
                "avatar" : users_name_cache[user]["avatar"],
                "profile_url" : users_name_cache[user]["profile_url"],
                "opened_tasks" : [], "closed_tasks": [],"comments_tasks":[],
                "resolved_tasks" : [], "not_resolved_tasks": []
            }
        users_stats[user]["closed"] += closed_stat[1][user]
        users_stats[user]["closed_tasks"] += closed_stat[2][user]

    resolved_stat = count_status_transition(filt_tasks['close'],
                                            "open", ["resolved"], start_date, end_date)
    result["resolved"] = resolved_stat[0]
    for user in resolved_stat[1]:
        if not user in users_stats:
            users_stats[user] = {
                "username" : user,
                "opened": 0,
                "closed": 0,
                "comments":0,
                "resolved":0,
                "not_resolved":0,
                "avatar" : users_name_cache[user]["avatar"],
                "profile_url" : users_name_cache[user]["profile_url"],
                "opened_tasks" : [], "closed_tasks": [],"comments_tasks":[],
                "resolved_tasks" : [], "not_resolved_tasks": []
            }
        users_stats[user]["resolved"] += resolved_stat[1][user]
        users_stats[user]["resolved_tasks"] += resolved_stat[2][user]

    not_resolved_stat = count_status_transition(filt_tasks['close'],
                                             "open", notsolved_status, start_date, end_date)
    result["not_resolved"] = not_resolved_stat[0]
    for user in not_resolved_stat[1]:
        if not user in users_stats:
            users_stats[user] = {
                "username" : user,
                "opened": 0,
                "closed": 0,
                "comments":0,
                "resolved":0,
                "not_resolved":0,
                "avatar" : users_name_cache[user]["avatar"],
                "profile_url" : users_name_cache[user]["profile_url"],
                "opened_tasks" : [], "closed_tasks": [],"comments_tasks":[],
                "resolved_tasks" : [], "not_resolved_tasks": []
            }
        users_stats[user]["not_resolved"] += not_resolved_stat[1][user]
        users_stats[user]["not_resolved_tasks"]+= not_resolved_stat[2][user]


    comments_stat = count_task_commented(filt_tasks["open"], start_date, end_date) + \
                         count_task_commented(filt_tasks["close"], start_date, end_date)
    result["comments"] =  comments_stat[0]
    for user in comments_stat[1]:
        if not user in users_stats:
            users_stats[user] = {
                "username" : user,
                "opened": 0,
                "closed": 0,
                "comments":0,
                "resolved":0,
                "not_resolved":0,
                "avatar" : users_name_cache[user]["avatar"],
                "profile_url" : users_name_cache[user]["profile_url"],
                "opened_tasks" : [], "closed_tasks": [],"comments_tasks":[],
                "resolved_tasks" : [], "not_resolved_tasks": []
            }
        users_stats[user]["comments"] += comments_stat[1][user]
        users_stats[user]["comments_tasks"] += comments_stat[2][user]

    for u in users_stats:
        result["users_stats"].append(users_stats[u])

    return result
