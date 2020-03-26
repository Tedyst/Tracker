from flask import Flask
import sys
from flask_sqlalchemy import SQLAlchemy
import threading
import hashlib
from sqlalchemy.orm.attributes import set_attribute, flag_modified
SITES = ['pbinfo', 'infoarena', 'codeforces']
SITES_ALL = ['pbinfo', 'infoarena', 'codeforces', 'all']


app = Flask(__name__,
            template_folder='../templates',
            static_folder="../static")
app.config['SECRET_KEY'] = "asd"
app.config['SQLALCHEMY_ECHO'] = False
if "pytest" in sys.modules:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'

db = SQLAlchemy(app)


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
        self.password = password
        self.email = email

    # Te rog nu intreba
    # Am facut asta ca sa putem accesa usernameurile ca user["pbinfo"] si user.pbinfo
    def __getitem__(self, key):
        db.session.commit()
        try:
            return getattr(self, key)
        except Exception as e:
            print(e)
            return None

    def __setitem__(self, key, value):
        db.session.commit()
        set_attribute(self, key, value)
        flag_modified(self, key)
        db.session.add(self)
        db.session.commit()

    def avatar(self):
        email = str(self.email).lower().encode('utf-8')
        userhex = str(hashlib.md5(email).hexdigest())
        return "https://www.gravatar.com/avatar/" + userhex

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password, method='sha256')

    # def check_password(self, password):
    #     """Check hashed password."""
    #     return check_password_hash(self.password, password)


class Problema(db.Model):
    __tablename__ = 'probleme'
    id = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.Integer)
    username = db.Column(db.String)
    sursa = db.Column(db.String)
    problema = db.Column(db.String)
    idprob = db.Column(db.String)
    scor = db.Column(db.String)
    data = db.Column(db.Integer)
    url = db.Column(db.String)

    def __init__(self, iduser, sursa, problema, idprob, scor, data, username, url):
        self.iduser = iduser
        self.sursa = sursa
        self.problema = problema
        self.idprob = idprob
        self.scor = scor
        self.data = data
        self.username = username
        self.url = url

    def to_json(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["url"] = self.url
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return json.dumps(data)

    def to_dict(self):
        data = {}
        data["sursa"] = self.sursa
        data["problema"] = self.problema
        data["idprob"] = self.idprob
        data["url"] = self.url
        data["scor"] = self.scor
        data["data"] = self.data
        data["username"] = self.username
        return data


def sortProbleme_date(self):
    return self.data

db.create_all()
