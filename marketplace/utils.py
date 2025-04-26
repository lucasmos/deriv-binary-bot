from datetime import timedelta
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

def generate_license_key(user_id, strategy_id):
    """Generate a unique license key for a strategy purchase"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(f"{user_id}:{strategy_id}", salt='license-keys')

def verify_license_key(key, max_age=365*24*3600):
    """Verify a license key and return user_id and strategy_id"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(key, salt='license-keys', max_age=max_age)
        user_id, strategy_id = data.split(':')
        return int(user_id), int(strategy_id)
    except:
        return None, None

def format_price(price):
    """Format price for display"""
    return f"${price:.2f}"

def allowed_strategy_file(filename):
    """Check if uploaded file has allowed extension"""
    allowed_extensions = {'json', 'py', 'zip'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions