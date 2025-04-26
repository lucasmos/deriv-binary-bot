from abc import ABC, abstractmethod

class BasePaymentProvider(ABC):
    @abstractmethod
    def initiate_deposit(self, user_id, amount, currency, method_id=None):
        pass
    
    @abstractmethod
    def initiate_withdrawal(self, user_id, amount, currency, account_details):
        pass
    
    @abstractmethod
    def handle_webhook(self, request):
        pass
    
    def verify_signature(self, request):
        """Verify webhook signature if needed"""
        return True