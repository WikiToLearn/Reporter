from reporter_app import app
from flask import render_template
import datetime
import reporter_app.data_aggregator as dg

@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/report/<date>', methods=['GET'])
def report(date):
    start_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    end_date = datetime.date.today()
    dg.fetch_data(start_date, end_date,["WikiToLearn/WikiToLearn", "WikiToLearn/CourseEditor"],
               {"WikiToLearn (1.0)":["PHID-PROJ-rzv3cv7obh4chahwejq3"]}, [])
    return render_template('report.template', ph_projects = dg.data["phabricator"])
