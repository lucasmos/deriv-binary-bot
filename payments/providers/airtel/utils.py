import hashlib
import hmac
from flask import current_app
from .schemas import AirtelWebhookPayload
from ..exceptions import WebhookVerificationError

def generate_airtel_reference(user_id: str, transaction_type: str) -> str:
    """Generate unique reference for Airtel transactions"""
    timestamp = int(time.time())
    return f"{transaction_type}_{user_id}_{timestamp}"

def verify_airtel_webhook(signature: str, payload: bytes) -> bool:
    """
    Verify Airtel webhook signature
    """
    secret = current_app.config.get('AIRTEL_WEBHOOK_SECRET')
    if not secret:
        raise ValueError("Airtel webhook secret not configured")
    
    computed_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, computed_signature)

def parse_airtel_webhook(payload: dict) -> AirtelWebhookPayload:
    """Parse and validate Airtel webhook payload"""
    try:
        return AirtelWebhookPayload(**payload)
    except Exception as e:
        current_app.logger.error(f"Airtel webhook validation failed: {str(e)}")
        raise WebhookVerificationError("Invalid Airtel webhook payload") from e

def format_airtel_amount(amount: float) -> int:
    """Convert float amount to Airtel's required integer format"""
    return int(amount * 100)