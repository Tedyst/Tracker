from flask import Blueprint
pages_blueprint = Blueprint('pages', __name__)
import Tracker.routes.pages.index
import Tracker.routes.pages.probleme
import Tracker.routes.pages.profile
import Tracker.routes.pages.settings
