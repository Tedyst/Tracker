#!/usr/bin/python3
from flask import Flask, render_template
from .db import query


app = Flask(__name__)
PORT = 8080


@app.route('/')
@app.route('/index')
def index():
    data = query("Tedyst", "pbinfo")
    return render_template('index.html', problems=data)