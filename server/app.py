#!/usr/bin/python3

import pymongo
from bson.json_util import dumps

from flask import Flask
from flask import render_template
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    # MongoDB setup and connection
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.wifidata
    collection = db.accesspoints

    # Query MongoDB for all available data points
    dbResult = collection.find({}, projection={'_id': False})

    # Convert result to a json formated string
    dbResult_json = dumps(dbResult)

    return dbResult_json

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
