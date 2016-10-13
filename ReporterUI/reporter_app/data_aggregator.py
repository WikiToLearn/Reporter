import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from . import config

#init the db client
client = MongoClient(config.DB_HOST, config.DB_PORT)
db = client['reports_db']

def get_report(id):
    return {
        "data" : db["reports_data"].find_one({"id":id}),
        "metadata" : db["reports_metadata"].find_one({"id":id})
    }

def get_report_data(id):
    return db["reports_data"].find_one({"id":id})

def get_report_metadata(id):
    return  db["reports_metadata"].find_one({"id":id})

def get_reports_list(status):
    docs = [doc for doc in db["reports_metadata"].find({"status":status}).sort(
                                            [('end_date', pymongo.DESCENDING)])]
    return docs

def get_previous_reports(id):
    previous = []
    pid = db["reports_metadata"].find_one({"id":id})["previous_report"]
    while True:
        if pid != None:
            rp = db["reports_metadata"].find_one({"id":pid})
            previous.append((rp["id"], rp["title"]))
            pid = rp["previous_report"]
        else:
            break
    return previous
