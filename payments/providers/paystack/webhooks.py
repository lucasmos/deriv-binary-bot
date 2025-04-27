from flask import request, jsonify
from ..services import payment_service

def handle_paystack_webhook():
    event = request.json
    if event['event'] == 'charge.success':
        reference = event['data']['reference']
        payment_service.confirm_payment(reference)
    return jsonify({"status": "success"})