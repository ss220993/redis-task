#!/bin/python
from flask import Flask
from flask import request
import os
from flask import jsonify
from helper import *
from model import *
import json

app = Flask(__name__)
app.debug = True

url = os.getenv('REDIS_URL')
if url:
    db = redis.Redis.from_url(url)
else:
    db = redis.Redis('localhost')


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


if __name__ == "__main__":
    app.config['JSON_SORT_KEYS'] = False
    app.run(debug=True, use_reloader=False)

