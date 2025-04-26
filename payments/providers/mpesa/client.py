import requests
from datetime import datetime
import base64
import json
from urllib.parse import urljoin
from payments.models import Transaction
from app import db, current_app
from ..exceptions import PaymentProcessingError

class MpesaClient:
    API_BASE = "https://sandbox.safaricom.co.ke/"
    
    def __init__(self):
        self.consumer_key = current_app.config['MPESA_CONSUMER_KEY']
        self.consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
        self.business_shortcode = current_app.config['MPESA_SHORTCODE']
        self.passkey = current_app.config['MPESA_PASSKEY']
        self.callback_url = current_app.config['MPESA_CALLBACK_URL']
        self.access_token = None
        self.token_expiry = None
        
    def _get_auth_token(self):
        """Get OAuth access token with caching"""
        if self.access_token and self.token_expiry > datetime.utcnow():
            return self.access_token
            
        auth_url = urljoin(self.API_BASE, "/oauth/v1/generate?grant_type=client_credentials")
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {"Authorization": f"Basic {encoded_auth}"}
        response = requests.get(auth_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_expiry = datetime.utcnow() + timedelta(seconds=int(data['expires_in']))
            return self.access_token
        raise PaymentProcessingError("Failed to obtain MPESA access token")
    
    def _generate_password(self):
        """Generate LIPA Na M-PESA password"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode()).decode()
    
    async def initiate_stk_push(self, phone, amount, reference, description="Trading deposit"):
        """Initiate STK push payment request"""
        try:
            access_token = self._get_auth_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password()
            
            url = urljoin(self.API_BASE, "/mpesa/stkpush/v1/processrequest")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": str(amount),
                "PartyA": phone,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone,
                "CallBackURL": self.callback_url,
                "AccountReference": reference,
                "TransactionDesc": description
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200:
                # Create transaction record
                transaction = Transaction(
                    user_id=current_user.id,
                    amount=amount,
                    provider='mpesa',
                    reference=reference,
                    checkout_request_id=response_data['CheckoutRequestID'],
                    merchant_request_id=response_data['MerchantRequestID'],
                    status='pending',
                    metadata=json.dumps(response_data),
                    transaction_type='deposit'
                )
                db.session.add(transaction)
                db.session.commit()
                
                return {
                    "success": True,
                    "checkout_request_id": response_data['CheckoutRequestID'],
                    "merchant_request_id": response_data['MerchantRequestID']
                }
            else:
                error_message = response_data.get('errorMessage', 'Payment request failed')
                raise PaymentProcessingError(error_message)
                
        except Exception as e:
            current_app.logger.error(f"MPESA STK push failed: {str(e)}")
            raise PaymentProcessingError(str(e))
    
    async def process_refund(self, transaction, amount, reason):
        """Process refund for a transaction"""
        try:
            access_token = self._get_auth_token()
            url = urljoin(self.API_BASE, "/mpesa/reversal/v1/request")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "Initiator": current_app.config['MPESA_INITIATOR'],
                "SecurityCredential": self._get_security_credential(),
                "CommandID": "TransactionReversal",
                "TransactionID": transaction.provider_reference,
                "Amount": str(amount),
                "ReceiverParty": transaction.metadata.get('PhoneNumber'),
                "RecieverIdentifierType": "11",
                "ResultURL": urljoin(current_app.config['BASE_URL'], "/api/payments/mpesa/refund_callback"),
                "QueueTimeOutURL": urljoin(current_app.config['BASE_URL'], "/api/payments/mpesa/refund_timeout"),
                "Remarks": reason,
                "Occasion": "Refund"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "conversation_id": response_data['ConversationID'],
                    "originator_conversation_id": response_data['OriginatorConversationID']
                }
            else:
                error_message = response_data.get('errorMessage', 'Refund request failed')
                raise PaymentProcessingError(error_message)
                
        except Exception as e:
            current_app.logger.error(f"MPESA refund failed: {str(e)}")
            raise PaymentProcessingError(str(e))
    
    def _get_security_credential(self):
        """Generate encrypted security credential"""
        # Implementation depends on your MPESA API setup
        pass