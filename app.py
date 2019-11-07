#!/bin/python
from flask import Flask
from flask import request
import os
from flask import jsonify
from helper import *
from model import *
import json
from ast import literal_eval

app = Flask(__name__)
app.debug = True


@app.errorhandler(400)
def bad_request(error=None):
    message = {
        'status': 400,
        'message': 'Bad Request',
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Data Not found',
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@app.route('/getRecentItem/', methods=['GET'])
def recentItem():
    dateGiven = request.args.get('date')
    if not dateGiven:
        return bad_request()
    resultfromDb = get_recent_item(dateGiven)

    if not resultfromDb:
        return not_found()

    return resultfromDb, 200

@app.route('/getBrandsCount/', methods=['GET'])
def brandsCount():
    dateGiven = request.args.get('date')
    if not dateGiven:
        return bad_request()
    resultfromDb = get_brands_count(dateGiven)

    if not resultfromDb:
        return not_found()

    sortedInput = sortByCount(json.loads(resultfromDb))
    return sortedInput, 200

@app.route('/getItemsbyColor/', methods=['GET'])
def recentTenColors():
    colorGiven = request.args.get('color')
    if not colorGiven:
        return bad_request()
    resultfromDb = get_recent_ten_colors(colorGiven)

    if len(resultfromDb) == 0:
        return not_found()
    data = []
    for result in resultfromDb:
      values = literal_eval(result.decode('utf8'))
      del values["colors"]
      values["color"] = colorGiven
      data.append(values)
    return json.dumps(data, indent=4), 200

if __name__ == "__main__":
    app.config['JSON_SORT_KEYS'] = False
    app.run(debug=True, host='0.0.0.0')