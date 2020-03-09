from flask import Blueprint

crm = Blueprint('crm', __name__, url_prefix='/app', template_folder='templates')

from . import views