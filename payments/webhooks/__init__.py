from flask import Blueprint
from .airtel_webhook import handle_airtel_webhook
from .mpesa_webhook import handle_mpesa_webhook

webhooks_bp = Blueprint('payment_webhooks', __name__)

# Register webhook handlers
webhooks_bp.add_url_rule(
    '/airtel', 
    view_func=handle_airtel_webhook, 
    methods=['POST']
)
webhooks_bp.add_url_rule(
    '/mpesa', 
    view_func=handle_mpesa_webhook, 
    methods=['POST']
)

__all__ = ['webhooks_bp']