#!/usr/bin/python3
from flask import Flask, render_template, request
from .db import query
import json
import operator

app = Flask(__name__)
PORT = 8080
SITES = ['pbinfo', 'infoarena', 'all']


@app.route('/')
@app.route('/index')
def index():
    data = query("Tedyst", "pbinfo")
    return render_template('index.html', problems=data)


@app.route('/api')
def api():
    user = request.args.get('user')
    site = request.args.get('site')
    if site not in SITES:
        return render_template('404.html')
    data = query(user, site)
    if site == "all":
        data = sorted(data, key=operator.itemgetter("data"))
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
