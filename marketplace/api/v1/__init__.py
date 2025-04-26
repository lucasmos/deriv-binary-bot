from flask_restx import Namespace

ns = Namespace('v1', description='Marketplace API v1 operations')

from . import endpoints