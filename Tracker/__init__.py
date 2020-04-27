from flask import Flask
import sys
from flask_sqlalchemy import SQLAlchemy
import threading
import hashlib
from sqlalchemy.orm.attributes import set_attribute, flag_modified
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
import ptvsd
import subprocess


SITES = ['pbinfo', 'infoarena', 'codeforces']
SITES_ALL = ['pbinfo', 'infoarena', 'codeforces', 'all']
git_hash = os.getenv("HASH") or subprocess.check_output(
    ['git', 'rev-parse', '--short', 'HEAD']).strip()


app = Flask(__name__,
            template_folder='../templates',
            static_folder="../static")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or "key"
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.logger.setLevel(logging.INFO)

if os.getenv("APP_ENV") == "docker":
    app.logger.info("Enabled vscode debugger")
    ptvsd.enable_attach()

# Debug mode
if app.debug:
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    toolbar = DebugToolbarExtension(app)
    app.logger.setLevel(logging.DEBUG)

if "pytest" in sys.modules:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    if os.getenv("APP_ENV") == "docker":
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/data.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    password = db.Column(db.String(200))
    email = db.Column(db.String(50))
    lock = threading.Lock()

    for i in SITES:
        vars()[i] = db.Column(db.String)
        vars()["last_" + i] = db.Column(db.Integer)
    del i

    def __init__(self, nickname, password, email):
        self.nickname = nickname
        self.set_password(password)
        self.email = email

    # Te rog nu intreba
    # Am facut asta ca sa putem accesa usernameurile
    # ca user["pbinfo"] si user.pbinfo
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except Exception as e:
            print(e)
            return None

    def __setitem__(self, key, value):
        set_attribute(self, key, value)
        flag_modified(self, key)
        db.session.add(self)
        db.session.commit()

    def avatar(self):
        email = str(self.email).lower().encode('utf-8')
        userhex = str(hashlib.md5(email).hexdigest())
        return "https://www.gravatar.com/avatar/" + userhex

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def usernames(self):
        result = {}
        for i in SITES:
            result[i] = self.__getitem__(i)
        return result


class Problema(db.Model):
    __tablename__ = 'probleme'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    sursa = db.Column(db.String)
    problema = db.Column(db.String)
    idprob = db.Column(db.String)
    scor = db.Column(db.String)
    data = db.Column(db.Integer)
    url = db.Column(db.String)

    def __init__(self,
                 sursa,
                 problema,
                 idprob,
                 scor,
                 data,
                 username,
                 url):
        self.sursa = sursa
        self.problema = problema
        self.idprob = idprob
        self.scor = scor
        self.data = data
        self.username = username
        self.url = url

    def __json__(self):
        data = {
            "sursa": self.sursa,
            "problema": self.problema,
            "idprob": self.idprob,
            "url": self.url,
            "scor": self.scor,
            "data": self.data,
            "username": self.username
        }
        return data


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


def sortProbleme_date(self):
    return self.data


db.create_all()
