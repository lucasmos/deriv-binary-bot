from flask import Blueprint
from .v1.endpoints import ns as v1_namespace
from flask_restx import Api

api_bp = Blueprint('marketplace_api', __name__, url_prefix='/api')

api = Api(api_bp, 
          version='1.0', 
          title='Marketplace API',
          description='API for the Deriv Trading Bot Marketplace')

api.add_namespace(v1_namespace)

from . import webhooks