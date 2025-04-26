import stripe
from ..base_provider import BasePaymentProvider
from flask import current_app, request
import hmac
import hashlib

class StripePaymentProvider(BasePaymentProvider):
    def __init__(self):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        self.webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
    
    def initiate_deposit(self, user_id, amount, currency, method_id=None):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency.lower(),
                metadata={
                    'user_id': str(user_id),
                    'purpose': 'trading_deposit'
                },
                payment_method=method_id,
                confirm=True,
                return_url=current_app.config['STRIPE_RETURN_URL']
            )
            
            return {
                'success': True,
                'transaction_id': payment_intent.id,
                'metadata': {
                    'client_secret': payment_intent.client_secret,
                    'status': payment_intent.status
                }
            }
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe deposit error: {str(e)}")
            return {
                'success': False,
                'message': str(e.user_message) if e.user_message else 'Payment failed'
            }
    
    def initiate_withdrawal(self, user_id, amount, currency, account_details):
        try:
            payout = stripe.Payout.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                metadata={
                    'user_id': str(user_id),
                    'purpose': 'trading_withdrawal'
                },
                destination=account_details['stripe_account_id']
            )
            
            return {
                'success': True,
                'transaction_id': payout.id,
                'metadata': {
                    'status': payout.status,
                    'arrival_date': payout.arrival_date
                }
            }
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe withdrawal error: {str(e)}")
            return {
                'success': False,
                'message': str(e.user_message) if e.user_message else 'Withdrawal failed'
            }
    
    def handle_webhook(self, request):
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                self.webhook_secret
            )
        except ValueError as e:
            return {'status': 'invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            return {'status': 'invalid signature'}
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            return {
                'transaction_id': payment_intent['id'],
                'status': 'completed',
                'metadata': {
                    'event_type': event['type'],
                    'amount_received': payment_intent['amount_received']
                }
            }
        elif event['type'] == 'payout.paid':
            payout = event['data']['object']
            return {
                'transaction_id': payout['id'],
                'status': 'completed',
                'metadata': {
                    'event_type': event['type'],
                    'amount': payout['amount']
                }
            }
        
        return {'status': 'unhandled_event'}