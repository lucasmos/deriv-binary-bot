from flask import current_app, request, jsonify
from .schemas import MpesaCallback
from .utils import verify_mpesa_callback
from ..exceptions import WebhookVerificationError

def handle_mpesa_callback():
    """Process M-Pesa callback (STK Push)"""
    try:
        # Verify callback authenticity
        if not verify_mpesa_callback(request):
            raise WebhookVerificationError("Invalid M-Pesa callback signature")
        
        # Parse and validate callback data
        callback_data = MpesaCallback(**request.json)
        
        # Process successful payment
        if callback_data.ResultCode == 0:
            current_app.logger.info(
                f"M-Pesa payment received. Amount: {callback_data.Amount}, "
                f"Phone: {callback_data.PhoneNumber}, "
                f"Transaction ID: {callback_data.MpesaReceiptNumber}"
            )
            # TODO: Update transaction status in database
            return jsonify({"ResultCode": 0, "ResultDesc": "Success"})
        
        # Handle failed payment
        current_app.logger.warning(
            f"M-Pesa payment failed. Code: {callback_data.ResultCode}, "
            f"Description: {callback_data.ResultDesc}"
        )
        return jsonify({"ResultCode": 0, "ResultDesc": "Failed payment acknowledged"})
    
    except Exception as e:
        current_app.logger.error(f"Error processing M-Pesa callback: {str(e)}")
        return jsonify({"ResultCode": 1, "ResultDesc": "Error processing callback"}), 500