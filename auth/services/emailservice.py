from flask import current_app, url_for
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer
from .models import User

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification',
            max_age=expiration
        )
    except:
        return None
    return email

def send_verification_email(user):
    token = generate_token(user.email)
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    msg = Message('Verify Your Email',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To verify your email, visit the following link:
{verification_url}

If you did not make this request, please ignore this email.
'''
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message('Reset Your Password',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not request a password reset, please ignore this email.
'''
    mail.send(msg)