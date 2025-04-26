import requests
import base64
from datetime import datetime
from ..base_provider import BasePaymentProvider
from flask import current_app
import hashlib

class SafaricomPaymentProvider(BasePaymentProvider):
    def __init__(self):
        self.base_url = current_app.config['SAFARICOM_API_URL']
        self.consumer_key = current_app.config['SAFARICOM_CONSUMER_KEY']
        self.consumer_secret = current_app.config['SAFARICOM_CONSUMER_SECRET']
        self.passkey = current_app.config['SAFARICOM_PASSKEY']
        self.business_shortcode = current_app.config['SAFARICOM_BUSINESS_SHORTCODE']
        self.callback_url = current_app.config['SAFARICOM_CALLBACK_URL']
    
    def _generate_token(self):
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}"
        }
        
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers
        )
        response.raise_for_status()
        return response.json()['access_token']
    
    def _generate_mpesa_password(self, timestamp):
        data = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()
    
    def initiate_deposit(self, user_id, amount, currency, method_id=None):
        token = self._generate_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self._generate_mpesa_password(timestamp)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": method_id,  # Customer phone number
            "PartyB": self.business_shortcode,
            "PhoneNumber": method_id,
            "CallBackURL": self.callback_url,
            "AccountReference": f"DEPOSIT_{user_id}",
            "TransactionDesc": "Trading account deposit"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'transaction_id': data['CheckoutRequestID'],
                'metadata': {
                    'merchant_request_id': data['MerchantRequestID'],
                    'response_code': data['ResponseCode']
                }
            }
        except Exception as e:
            current_app.logger.error(f"Safaricom deposit error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to initiate Safaricom deposit'
            }
    
    def handle_webhook(self, request):
        data = request.json
        
        # Safaricom sends the result in a nested structure
        callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')
        
        status = 'failed'
        if result_code == '0':
            status = 'completed'
        
        return {
            'transaction_id': checkout_request_id,
            'status': status,
            'metadata': data
        }