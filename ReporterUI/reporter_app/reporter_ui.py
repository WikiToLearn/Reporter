from reporter_app import app
from flask import render_template, jsonify, request, abort, redirect, url_for
import datetime
import logging
import reporter_app.data_aggregator as dagg

@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/<id>', methods=['GET'])
def report(id):
    #getting data
    data = dagg.get_report_data(id)
    if data is None:
        return abort(404)
    metadata = dagg.get_report_metadata(id)
    #total statistics
    return render_template('report.template',
                           metadata = metadata,
                           ph_projects = data["phabricator"],
                           ph_totals = data["totals_phab"],
                           ph_devs = data["totals_phab"]['users_stats'],
                           git_projs = data["git"],
                           git_totals = data["totals_git"],
                           git_devs = data["totals_git"]["users_stats"],
                           wiki_plats = data["mediawiki"],
                           wiki_totals = data["totals_mediawiki"],
                           wiki_authors = data["totals_mediawiki"]["users_stats"],
                           previous_reports = dagg.get_previous_reports(id)
                           )

@app.route('/latest', methods=['GET'])
def last_report():
    id =  dagg.get_last_report()["id"]
    return redirect(url_for("report", id=id))



@app.route('/', methods=['GET'])
def index():
    return render_template('index.template',
                           reports = dagg.get_reports_list("published"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.template'), 404

@app.route('/history', methods=['POST'])
def get_history():
    options = request.get_json()
    app.logger.info(str(options))
    if options["user_stats"] in ["true","True", "yes", "1", "Y"]:
        query, result = dagg.get_history(options["collection"], True, options)
    else:
        query, result = dagg.get_history(options["collection"], False, options)
    app.logger.info("Quering history: {}".format(query))
    return jsonify(result)
