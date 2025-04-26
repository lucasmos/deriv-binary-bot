from flask import request, jsonify, current_app
from payments.providers.airtel.utils import (
    verify_airtel_webhook,
    parse_airtel_webhook
)
from payments.providers.airtel.schemas import AirtelWebhookPayload
from payments.models import Transaction
from payments.exceptions import WebhookVerificationError
from app import db

def handle_airtel_webhook():
    """Process Airtel Money payment webhook"""
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Callback-Signature')
        if not verify_airtel_webhook(signature, request.data):
            current_app.logger.warning("Invalid Airtel webhook signature")
            raise WebhookVerificationError("Invalid signature")
        
        # Parse and validate webhook payload
        payload = parse_airtel_webhook(request.json)
        transaction_id = payload.transaction.get('id')
        status = payload.transaction.get('status', '').lower()
        
        if not transaction_id:
            return jsonify({'status': 'error', 'message': 'Missing transaction ID'}), 400
        
        # Update transaction status
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            current_app.logger.error(f"Airtel transaction not found: {transaction_id}")
            return jsonify({'status': 'error', 'message': 'Transaction not found'}), 404
        
        # Process based on status
        if status == 'success':
            transaction.status = 'completed'
            transaction.metadata = {
                **(transaction.metadata or {}),
                'airtel_reference': payload.transaction.get('airtel_money_id'),
                'webhook_data': request.json
            }
            db.session.commit()
            
            # TODO: Add business logic for completed payment
            current_app.logger.info(
                f"Airtel payment completed. Transaction: {transaction_id}, "
                f"Amount: {transaction.amount} {transaction.currency}"
            )
            
        elif status == 'failed':
            transaction.status = 'failed'
            db.session.commit()
            current_app.logger.warning(
                f"Airtel payment failed. Transaction: {transaction_id}"
            )
        
        return jsonify({'status': 'success'}), 200
    
    except WebhookVerificationError as e:
        current_app.logger.error(f"Airtel webhook verification failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 403
    
    except Exception as e:
        current_app.logger.error(f"Error processing Airtel webhook: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500