import requests
from flask import current_app
from ..exceptions import PaymentException

class PaystackPaymentProvider:
    def __init__(self):
        self.secret_key = current_app.config['PAYSTACK_SECRET_KEY']
        self.base_url = 'https://api.paystack.co'

    def initiate_payment(self, email, amount, reference):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Paystack uses kobo/cent units
            "reference": reference,
            "callback_url": current_app.config['PAYSTACK_CALLBACK_URL']
        }

        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['data']['authorization_url']
        except Exception as e:
            raise PaymentException(f"Paystack error: {str(e)}")

    def verify_payment(self, reference):
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=headers
            )
            data = response.json()
            return data['status'], data['data']['amount'] / 100
        except Exception as e:
            raise PaymentException(f"Verification failed: {str(e)}")