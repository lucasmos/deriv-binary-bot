import base64
import hashlib
from datetime import datetime
from flask import current_app
from ..exceptions import WebhookVerificationError

def generate_mpesa_password(business_shortcode: str, passkey: str) -> str:
    """Generate M-Pesa API password using shortcode, passkey and timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = f"{business_shortcode}{passkey}{timestamp}"
    return base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()

def generate_mpesa_timestamp() -> str:
    """Generate timestamp in M-Pesa required format"""
    return datetime.now().strftime("%Y%m%d%H%M%S")

def verify_mpesa_callback(request) -> bool:
    """Verify M-Pesa callback authenticity"""
    # M-Pesa doesn't sign callbacks but we can validate business shortcode
    expected_shortcode = current_app.config.get('SAFARICOM_BUSINESS_SHORTCODE')
    if not expected_shortcode:
        raise ValueError("M-Pesa business shortcode not configured")
    
    # Extract shortcode from callback (implementation depends on callback structure)
    callback_shortcode = request.json.get('BusinessShortCode')
    return callback_shortcode == expected_shortcode

def format_mpesa_amount(amount: float) -> str:
    """Format amount for M-Pesa API (string with 2 decimal places)"""
    return "{0:.2f}".format(amount)

def parse_mpesa_callback(data: dict):
    """Parse M-Pesa callback data into structured format"""
    items = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
    result = {}
    
    for item in items:
        if 'Name' in item and 'Value' in item:
            result[item['Name']] = item['Value']
    
    return result