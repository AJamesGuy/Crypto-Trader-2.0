from flask import Blueprint

trade_bp = Blueprint('trade', __name__)

from . import routes