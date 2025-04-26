from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active_broker = db.Column(db.String(50), default='deriv')
    account_type = db.Column(db.String(10), default='demo')  # demo or real
    broker_accounts = db.Column(JSONB, default={
        'deriv': {'api_key': None, 'account_id': None},
        'quotex': {'email': None, 'password': None},
        'iqoption': {'email': None, 'password': None},
        'pocketoption': {'email': None, 'password': None}
    })
    trading_preferences = db.Column(JSONB, default={
        'risk_level': 'medium',
        'preferred_strategies': ['trend_following', 'range_bound'],
        'default_amount': 10,
        'default_duration': 5
    })
    demo_balance = db.Column(db.Float, default=10000.00)
    last_balance_sync = db.Column(db.DateTime)
    
    strategies = db.relationship('UserStrategy', back_populates='user')
    authored_strategies = db.relationship('Strategy', back_populates='author')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_balance(self):
        """Get current balance based on account type"""
        if self.account_type == 'demo':
            return self.demo_balance
        # For real accounts, balance is synced from broker
        return None
    
    def update_balance(self, amount, is_demo=True):
        """Update account balance after trade"""
        if is_demo:
            new_balance = self.demo_balance + amount
            if new_balance < 0:
                return False
            self.demo_balance = new_balance
        db.session.commit()
        return True
    
    def reset_demo_balance(self):
        """Reset demo balance to $10,000"""
        self.demo_balance = 10000.00
        db.session.commit()
        return True
    
    def link_broker_account(self, broker_name, credentials):
        """Link a broker account"""
        if broker_name not in self.broker_accounts:
            raise ValueError(f"Unsupported broker: {broker_name}")
        
        self.broker_accounts[broker_name] = credentials
        db.session.commit()
        return True