from flask import Blueprint
api_blueprint = Blueprint('api', __name__)
from Tracker.routes.api import calendar
from Tracker.routes.api import grafic1
from Tracker.routes.api import users
