from reporter_app import app
from flask import render_template, jsonify, request, abort
import datetime
from reporter_app.data_aggregator import DataAggregator

dagg = DataAggregator("data_store.json","reports_settings")



@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/<id>', methods=['GET'])
def report(id):
    #getting data for the dates
    if id not in dagg.data_store:
        return abort(404)
    data = dagg.data_store[id]
    #total statistics
    return render_template('report.template',
                           ph_projects = data["phabricator"],
                           ph_totals = data["totals_phab"],
                           ph_devs = data["totals_phab"]['users_stats'],
                           git_projs = data["git"],
                           git_totals = data["totals_git"],
                           git_devs = data["totals_git"]["users_stats"],
                           wiki_plats = data["mediawiki"],
                           wiki_totals = data["totals_mediawiki"],
                           wiki_authors = data["totals_mediawiki"]["users_stats"]
                           )


@app.route('/', methods=['GET'])
def index():
    return render_template('index.template',
                           links = list(dagg.data_store.keys()))

@app.route('/update' ,methods= ['POST'])
def update():
    query = request.get_json()
    #some type of check
    dagg.update_settings()


# @app.route('/report/generate', methods=['POST'])
# def generate_report():
#     query = request.get_json()
#     start_date = datetime.datetime.strptime(query["start_date"], "%Y-%m-%d").date()
#     end_date = datetime.datetime.strptime(query["end_date"], "%Y-%m-%d").date()
#     repos = query["git_repos"]
#     ph_projs = {}
#     for p in query["ph_projs"]:
#         ph_projs[p] = []
#         for id in query["ph_projs"][p]:
#             ph_projs[p].append(dagg.pp.lookup_project_phabid_byid(id))
#     mediawiki_langs = query["mediawiki_langs"]
#     id = generate_id(start_date, end_date)
#     dagg.fetch_data(id, start_date, end_date,repos, ph_projs, mediawiki_langs )
#     return jsonify(dagg.data_store[id])
#
# def generate_id(start_date, end_date):
#     return start_date.strftime("%Y-%m-%d")+"_"+end_date.strftime("%Y-%m-%d")
