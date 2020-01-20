from flask import Blueprint

crm = Blueprint('crm', __name__)

from . import views, errors