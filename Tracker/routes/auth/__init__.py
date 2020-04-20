from flask import Blueprint
auth_blueprint = Blueprint('auth', __name__)
from Tracker.routes.auth import login
from Tracker.routes.auth import logout
from Tracker.routes.auth import register
