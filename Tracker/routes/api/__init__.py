from flask import Blueprint
api_blueprint = Blueprint('api', __name__)
from Tracker.routes.pages.index import *
