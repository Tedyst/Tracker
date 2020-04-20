from flask import Blueprint
pages_blueprint = Blueprint('pages', __name__)
from Tracker.routes.pages.index import *
