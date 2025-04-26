import requests
from ..base_provider import BasePaymentProvider
from flask import current_app
import hmac
import hashlib
import json

class AirtelPaymentProvider(BasePaymentProvider):
    def __init__(self):
        self.base_url = current_app.config['AIRTEL_API_URL']
        self.client_id = current_app.config['AIRTEL_CLIENT_ID']
        self.client_secret = current_app.config['AIRTEL_CLIENT_SECRET']
        self.callback_url = current_app.config['AIRTEL_CALLBACK_URL']
    
    def _get_auth_token(self):
        url = f"{self.base_url}/auth/oauth2/token"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['access_token']
    
    def initiate_deposit(self, user_id, amount, currency, method_id=None):
        token = self._get_auth_token()
        url = f"{self.base_url}/merchant/v1/payments/"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "reference": f"deposit_{user_id}_{int(time.time())}",
            "subscriber": {
                "country": "KE",
                "currency": currency,
                "msisdn": method_id  # Phone number for Airtel Money
            },
            "transaction": {
                "amount": amount,
                "country": "KE",
                "currency": currency,
                "id": f"deposit_{user_id}_{int(time.time())}"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'transaction_id': data['data']['transaction']['id'],
                'metadata': {
                    'airtel_reference': data['data']['transaction']['airtel_money_id']
                }
            }
        except Exception as e:
            current_app.logger.error(f"Airtel deposit error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to initiate Airtel deposit'
            }
    
    def initiate_withdrawal(self, user_id, amount, currency, account_details):
        # Similar to deposit but for withdrawals
        pass
    
    def handle_webhook(self, request):
        signature = request.headers.get('X-Callback-Signature')
        payload = request.get_data()
        
        # Verify signature
        secret = current_app.config['AIRTEL_CLIENT_SECRET']
        computed_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, computed_signature):
            return {'status': 'invalid signature'}
        
        data = request.json
        transaction_id = data.get('transaction', {}).get('id')
        status = data.get('transaction', {}).get('status', 'failed').lower()
        
        return {
            'transaction_id': transaction_id,
            'status': status,
            'metadata': data
        }