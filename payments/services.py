from .models import Transaction, PaymentMethod
from .providers import PaymentProviderFactory
from app import db
from datetime import datetime

class PaymentService:
    def __init__(self):
        self.provider_factory = PaymentProviderFactory()
    
    def process_deposit(self, user_id, amount, currency, provider, method_id=None):
        provider_instance = self.provider_factory.get_provider(provider)
        result = provider_instance.initiate_deposit(user_id, amount, currency, method_id)
        
        if result['success']:
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                currency=currency,
                provider=provider,
                transaction_id=result['transaction_id'],
                status='pending',
                metadata=result.get('metadata')
            )
            db.session.add(transaction)
            db.session.commit()
        
        return result
    
    def process_withdrawal(self, user_id, amount, currency, provider, account_details):
        provider_instance = self.provider_factory.get_provider(provider)
        result = provider_instance.initiate_withdrawal(user_id, amount, currency, account_details)
        
        if result['success']:
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                currency=currency,
                provider=provider,
                transaction_id=result['transaction_id'],
                status='pending',
                metadata={
                    'account_details': account_details,
                    **result.get('metadata', {})
                }
            )
            db.session.add(transaction)
            db.session.commit()
        
        return result
    
    def get_transaction(self, transaction_id):
        return Transaction.query.filter_by(transaction_id=transaction_id).first()
    
    def handle_webhook(self, provider, request):
        provider_instance = self.provider_factory.get_provider(provider)
        result = provider_instance.handle_webhook(request)
        
        if result.get('transaction_id'):
            transaction = Transaction.query.filter_by(
                transaction_id=result['transaction_id']
            ).first()
            
            if transaction:
                transaction.status = result['status']
                transaction.metadata = {
                    **(transaction.metadata or {}),
                    **result.get('metadata', {})
                }
                
                if result['status'] == 'completed':
                    transaction.completed_at = datetime.utcnow()
                
                db.session.commit()
        
        return jsonify({'status': 'received'})