#!/usr/bin/python3
from flask import Flask, render_template, request
from db import getSurseAPI
from classes import sortProbleme_date
import json
import operator
from classes import SITES_ALL as SITES
app = Flask(__name__)
PORT = 8080


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', SITES=SITES)


@app.route('/api')
def api():
    user = request.args.get('user')
    site = request.args.get('site')
    if site not in SITES:
        return render_template('404.html')
    data = getSurseAPI(user, site)
    result = []
    for i in data:
        result.append(i.to_dict())
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )


@app.route('/search')
def search():
    user = request.args.get('user')
    site = request.args.get('site')
    if site not in SITES:
        return render_template('404.html')
    data = getSurseAPI(user, site)
    data = sorted(data, key=sortProbleme_date)
    return render_template('search.html', problems=data)


if __name__ == "__main__":
    app.run()
