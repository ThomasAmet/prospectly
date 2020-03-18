from flask import Blueprint

affiliation = Blueprint('affiliation', __name__, url_prefix='/affiliation', template_folder='templates')

from . import views