from flask import current_app, request, jsonify
from .client import StripePaymentProvider

stripe_provider = StripePaymentProvider()

def handle_stripe_webhook():
    """Specific webhook handler for Stripe"""
    result = stripe_provider.handle_webhook(request)
    if result.get('status') == 'completed':
        # Process successful payment
        pass
    return jsonify({'status': 'received'})