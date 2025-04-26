from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Strategy(db.Model):
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    code = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), default='1.0.0')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Float, default=0.0)
    is_public = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    performance_metrics = db.Column(JSONB)  # Stores backtest results
    min_balance = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high
    
    author = db.relationship('User', backref='authored_strategies')
    subscribers = db.relationship('UserStrategy', back_populates='strategy')
    
    def __repr__(self):
        return f'<Strategy {self.name} v{self.version}>'

class UserStrategy(db.Model):
    __tablename__ = 'user_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    custom_settings = db.Column(JSONB)  # User-specific strategy settings
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    user = db.relationship('User', back_populates='strategies')
    strategy = db.relationship('Strategy', back_populates='subscribers')
    
    def __repr__(self):
        return f'<UserStrategy user={self.user_id} strategy={self.strategy_id}>'

class StrategyRating(db.Model):
    __tablename__ = 'strategy_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    strategy = db.relationship('Strategy', backref='ratings')
    user = db.relationship('User', backref='strategy_ratings')
    
    __table_args__ = (
        db.UniqueConstraint('strategy_id', 'user_id', name='_strategy_user_uc'),
    )