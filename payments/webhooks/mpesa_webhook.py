from flask import request, jsonify, current_app
from payments.providers.mpesa.schemas import MpesaCallback
from payments.providers.mpesa.utils import verify_mpesa_callback, parse_mpesa_callback
from payments.models import Transaction
from payments.exceptions import WebhookVerificationError
from app import db
import json

def handle_mpesa_webhook():
    """Process M-Pesa STK Push webhook"""
    try:
        # Verify callback (M-Pesa doesn't sign payloads but we validate business code)
        if not verify_mpesa_callback(request):
            current_app.logger.warning("Invalid M-Pesa callback")
            raise WebhookVerificationError("Invalid M-Pesa callback")
        
        # Parse callback data
        callback_data = parse_mpesa_callback(request.json)
        checkout_request_id = callback_data.get('CheckoutRequestID')
        result_code = callback_data.get('ResultCode')
        mpesa_receipt = callback_data.get('MpesaReceiptNumber')
        amount = callback_data.get('Amount')
        phone = callback_data.get('PhoneNumber')
        
        if not checkout_request_id:
            return jsonify({
                "ResultCode": 1,
                "ResultDesc": "Missing CheckoutRequestID"
            }), 400
        
        # Find transaction
        transaction = Transaction.query.filter_by(transaction_id=checkout_request_id).first()
        if not transaction:
            current_app.logger.error(f"M-Pesa transaction not found: {checkout_request_id}")
            return jsonify({
                "ResultCode": 1,
                "ResultDesc": "Transaction not found"
            }), 404
        
        # Process based on result code
        if result_code == '0':  # Success
            transaction.status = 'completed'
            transaction.metadata = {
                **(transaction.metadata or {}),
                'mpesa_receipt': mpesa_receipt,
                'phone_number': phone,
                'callback_data': callback_data
            }
            db.session.commit()
            
            # TODO: Add business logic for completed payment
            current_app.logger.info(
                f"M-Pesa payment received. Amount: {amount}, "
                f"Phone: {phone}, Receipt: {mpesa_receipt}"
            )
            
            return jsonify({
                "ResultCode": 0,
                "ResultDesc": "Success"
            })
        
        else:  # Failed
            transaction.status = 'failed'
            db.session.commit()
            
            current_app.logger.warning(
                f"M-Pesa payment failed. RequestID: {checkout_request_id}, "
                f"Code: {result_code}"
            )
            
            return jsonify({
                "ResultCode": 0,
                "ResultDesc": "Failed payment acknowledged"
            })
    
    except WebhookVerificationError as e:
        current_app.logger.error(f"M-Pesa webhook verification failed: {str(e)}")
        return jsonify({
            "ResultCode": 1,
            "ResultDesc": "Invalid callback"
        }), 403
    
    except Exception as e:
        current_app.logger.error(f"Error processing M-Pesa webhook: {str(e)}")
        db.session.rollback()
        return jsonify({
            "ResultCode": 1,
            "ResultDesc": "Internal server error"
        }), 500