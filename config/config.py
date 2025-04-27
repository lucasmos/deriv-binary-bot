import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30
    }
    
    # Deriv API
    DERIV_APP_ID = os.environ.get('DERIV_APP_ID')
    DERIV_API_KEY = os.environ.get('DERIV_API_KEY')
    DERIV_DEMO_API_KEY = os.environ.get('DERIV_DEMO_API_KEY')
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # MPESA
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
    MPESA_INITIATOR = os.environ.get('MPESA_INITIATOR')
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL')
    
    # Airtel
    AIRTEL_CLIENT_ID = os.environ.get('AIRTEL_CLIENT_ID')
    AIRTEL_CLIENT_SECRET = os.environ.get('AIRTEL_CLIENT_SECRET')
    AIRTEL_MERCHANT_ID = os.environ.get('AIRTEL_MERCHANT_ID')
    AIRTEL_CALLBACK_URL = os.environ.get('AIRTEL_CALLBACK_URL')
    
    # Replace Stripe config with:
    # Replace Stripe config with:
    PAYSTACK_CONFIG = {
    'SECRET_KEY': os.getenv('PAYSTACK_SECRET_KEY'),
    'PUBLIC_KEY': os.getenv('PAYSTACK_PUBLIC_KEY'),
    'CALLBACK_URL': os.getenv('PAYSTACK_CALLBACK_URL'),
    'CHARGES_ENDPOINT': 'https://api.paystack.co/transaction/initialize'
                    }
    # OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    # AI
    AI_MODEL_PATH = os.environ.get('AI_MODEL_PATH', 'ai/models')
    AI_TRAINING_INTERVAL = int(os.environ.get('AI_TRAINING_INTERVAL', 24))
    
    # Sentry
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    @staticmethod
    def init_app(app):
        """Initialize configuration with the application"""
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL') or 'sqlite://'

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}