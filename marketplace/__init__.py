from flask import Blueprint
from flask_login import login_required
from .services import MarketplaceService

marketplace_bp = Blueprint('marketplace', __name__, template_folder='templates')

@marketplace_bp.route('/')
@login_required
def marketplace_home():
    """Marketplace home page showing available strategies"""
    service = MarketplaceService()
    strategies = service.get_available_strategies()
    return render_template('marketplace/marketplace.html', strategies=strategies)

from . import routes