from reporter_app import app
from flask import render_template, jsonify, request
import datetime
import reporter_app.data_aggregator as dg


@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/report/<date>', methods=['GET'])
def report(date):
    start_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    end_date = datetime.date.today()

    return render_template('report.template', ph_projects = dg.data["phabricator"])

report_ready = False

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
            ph_projs[p].append(dg.pp.lookup_project_phabid_byid(id))

    dg.fetch_data(start_date, end_date,repos, ph_projs, [])
    return jsonify(dg.data)
