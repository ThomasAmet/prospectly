from flask import Blueprint

leads = Blueprint('leads', __name__, template_folder='templates', url_prefix='/app/leads')

from .import views