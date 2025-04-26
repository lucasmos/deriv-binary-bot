import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, redirect, url_for, flash
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

def generate_verification_token(email):
    """Generate a verification token for email confirmation."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_token(token, expiration=3600):
    """Verify the verification token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except Exception:
        return None

def generate_password(length=12):
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    """Hash a password for storing."""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(stored_hash, provided_password):
    """Verify a stored password against one provided by user."""
    return check_password_hash(stored_hash, provided_password)

def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_csrf_token():
    """Generate a CSRF token for forms."""
    return secrets.token_hex(16)