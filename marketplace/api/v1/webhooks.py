from flask import request, jsonify, current_app
from ..services import MarketplaceService
from . import api_bp
import hmac
import hashlib

service = MarketplaceService()

@api_bp.route('/webhooks/payment', methods=['POST'])
def payment_webhook():
    """Handle payment provider webhooks"""
    # Verify signature
    signature = request.headers.get('X-Signature')
    payload = request.get_data()
    
    expected_signature = hmac.new(
        current_app.config['WEBHOOK_SECRET'].encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 403
    
    data = request.json
    user_id = data.get('user_id')
    strategy_id = data.get('strategy_id')
    transaction_id = data.get('transaction_id')
    
    # Process purchase
    success, message = service.purchase_strategy(user_id, strategy_id)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': message,
            'transaction_id': transaction_id
        }), 200
    else:
        return jsonify({
            'status': 'failed',
            'message': message,
            'transaction_id': transaction_id
        }), 400