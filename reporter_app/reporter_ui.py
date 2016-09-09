from reporter_app import app
from flask import render_template

@app.route('/manager', methods=['GET'])
def manager():
    return render_template('create_report.template')

@app.route('/report', methods=['GET'])
def report():
    return render_template('report.template')
