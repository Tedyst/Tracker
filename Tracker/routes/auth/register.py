from Tracker import app, User, dbutils
from flask_login import login_user
from flask import render_template, request
from Tracker.routes.auth import auth_blueprint
import json


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('notlogged/register.html')
    elif request.method == 'POST':
        data = request.form
        try:
            if not data['email'] or not data['password'] or not data['name']:
                return render_template('notlogged/register.html')
        except KeyError:
            return render_template('notlogged/register.html')
        user = User.query.filter(User.email == data['email']).first()
        if user is None:
            user = User.query.filter(User.nickname == data['email']).first()
        if user is None:
            user = dbutils.createUser(
                data['name'], data['password'], data['email'])
            login_user(user)
            surse = json.dumps([i.__json__()
                                for i in dbutils.getSurse(user, "all")])
            return render_template('profile.html',
                                   first_time=True,
                                   data=surse,
                                   user=user)
        return render_template('notlogged/register.html')
