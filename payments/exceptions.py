class PaymentException(Exception):
    """Base exception for payment-related errors"""
    pass

class PaymentProviderError(PaymentException):
    """Exception for provider-specific errors"""
    def __init__(self, provider, message):
        self.provider = provider
        self.message = message
        super().__init__(f"{provider} error: {message}")

class InvalidPaymentMethod(PaymentException):
    """Raised when an invalid payment method is provided"""
    pass

class InsufficientFunds(PaymentException):
    """Raised when account has insufficient funds for transaction"""
    pass

class TransactionNotFound(PaymentException):
    """Raised when a transaction cannot be found"""
    pass

class WebhookVerificationError(PaymentException):
    """Raised when webhook signature verification fails"""
    pass

class CurrencyNotSupported(PaymentException):
    """Raised when currency is not supported by provider"""
    def __init__(self, currency, provider):
        super().__init__(f"Currency {currency} not supported by {provider}")

class PaymentProcessingError(PaymentException):
    """Raised when payment processing fails"""
    def __init__(self, transaction_id, status):
        self.transaction_id = transaction_id
        self.status = status
        super().__init__(f"Payment failed for transaction {transaction_id}. Status: {status}")