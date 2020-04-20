from Tracker import app, User
from flask_login import login_user
from flask import render_template, redirect, url_for, request
from Tracker.routes.auth import auth_blueprint


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('notlogged/login.html', failedlogin=False)
    elif request.method == 'POST':
        data = request.form
        try:
            if not data['email'] or not data['password']:
                return render_template('notlogged/login.html',
                                       failedlogin=True)
        except KeyError:
            return render_template('notlogged/login.html')
        remember = False
        try:
            if data['remember'] == 'on':
                remember = True
        except KeyError:
            pass
        user = User.query.filter(User.email == data['email']).first()
        if user is None:
            user = User.query.filter(User.nickname == data['email']).first()
            if user is None:
                return render_template('notlogged/login.html',
                                       failedlogin=True)
        if user.check_password(data['password']):
            login_user(user, remember=remember)
            return redirect(url_for('pages.index'))
        return render_template('notlogged/login.html', failedlogin=True)
