from reporter_app import app
from flask import render_template, jsonify, request
import datetime
import reporter_app.data_aggregator as dagg


@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/report/<id>', methods=['GET'])
def report(id):
    #getting data for the dates
    data = dagg.datas[id]
    totals_git = dagg.calculate_totals_git(id)
    return render_template('report.template',
                           ph_projects = data["phabricator"],
                           ph_totals = dagg.calculate_totals_phabricator(id),
                           git_projs = data["git"],
                           git_totals = totals_git,
                           git_devs = totals_git["users_stats"]
                           )



@app.route('/report/generate', methods=['POST'])
def generate_report():
    query = request.get_json()
    start_date = datetime.datetime.strptime(query["start_date"], "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(query["end_date"], "%Y-%m-%d").date()
    repos = query["git_repos"]
    ph_projs = {}
    for p in query["ph_projs"]:
        ph_projs[p] = []
        for id in query["ph_projs"][p]:
            ph_projs[p].append(dagg.pp.lookup_project_phabid_byid(id))
    id = generate_id(start_date, end_date)
    dagg.fetch_data(id, start_date, end_date,repos, ph_projs, [])
    return jsonify(dagg.datas[id])

def generate_id(start_date, end_date):
    return start_date.strftime("%Y-%m-%d")+"_"+end_date.strftime("%Y-%m-%d")
