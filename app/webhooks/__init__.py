from flask import Blueprint

webhooks = Blueprint('webhooks', __name__, prefix='/webhooks')

from . import views