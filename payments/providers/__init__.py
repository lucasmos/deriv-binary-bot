from .base_provider import BasePaymentProvider
from .airtel.client import AirtelPaymentProvider
from .safaricom.client import SafaricomPaymentProvider
from .providers.paystack.client import PaystackPaymentProvider

class PaymentProviderFactory:
    def __init__(self):
        self.providers = {
            'airtel': AirtelPaymentProvider(),
            'safaricom': SafaricomPaymentProvider(),
            'paystack': PaystackPaymentProvider(),
        }
    
    def get_provider(self, provider_name):
        provider = self.providers.get(provider_name.lower())
        if not provider:
            raise ValueError(f"Payment provider {provider_name} not supported")
        return provider