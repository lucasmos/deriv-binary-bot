from .models import Strategy, StrategyReview, UserPurchase
from app import db
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename
from config import Config

class MarketplaceService:
    def get_available_strategies(self):
        """Get all active strategies available for purchase"""
        return Strategy.query.filter_by(is_active=True).order_by(Strategy.rating.desc()).all()
    
    def get_strategy_by_id(self, strategy_id):
        """Get strategy by ID"""
        return Strategy.query.get_or_404(strategy_id)
    
    def get_strategy_reviews(self, strategy_id):
        """Get reviews for a strategy"""
        return StrategyReview.query.filter_by(strategy_id=strategy_id)\
                                 .order_by(StrategyReview.created_at.desc()).all()
    
    def has_purchased(self, user_id, strategy_id):
        """Check if user has purchased a strategy"""
        return UserPurchase.query.filter_by(
            user_id=user_id,
            strategy_id=strategy_id,
            is_active=True
        ).first() is not None
    
    def purchase_strategy(self, user_id, strategy_id):
        """Process strategy purchase"""
        strategy = self.get_strategy_by_id(strategy_id)
        
        if self.has_purchased(user_id, strategy_id):
            return False, "You already own this strategy"
        
        # In a real app, you would integrate with payment processing here
        license_key = str(uuid.uuid4())
        
        purchase = UserPurchase(
            user_id=user_id,
            strategy_id=strategy_id,
            amount_paid=strategy.price,
            license_key=license_key
        )
        
        db.session.add(purchase)
        db.session.commit()
        
        return True, "Purchase successful! Strategy added to your account."
    
    def upload_strategy(self, user_id, name, description, price, category, strategy_file):
        """Handle strategy upload"""
        try:
            # Save the strategy file
            filename = secure_filename(strategy_file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, 'strategies', filename)
            strategy_file.save(filepath)
            
            strategy = Strategy(
                name=name,
                description=description,
                author_id=user_id,
                price=price,
                category=category,
                strategy_file=filename
            )
            
            db.session.add(strategy)
            db.session.commit()
            
            return True, strategy
        except Exception as e:
            db.session.rollback()
            return False, None
    
    def get_user_purchases(self, user_id):
        """Get strategies purchased by user"""
        return UserPurchase.query.filter_by(user_id=user_id, is_active=True)\
                               .order_by(UserPurchase.purchase_date.desc()).all()
    
    def get_user_uploaded_strategies(self, user_id):
        """Get strategies uploaded by user"""
        return Strategy.query.filter_by(author_id=user_id)\
                           .order_by(Strategy.created_at.desc()).all()
    
    def add_review(self, user_id, strategy_id, rating, comment):
        """Add a review for a strategy"""
        review = StrategyReview(
            user_id=user_id,
            strategy_id=strategy_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Update strategy rating
        self._update_strategy_rating(strategy_id)
        
        return True
    
    def _update_strategy_rating(self, strategy_id):
        """Recalculate strategy rating based on reviews"""
        reviews = StrategyReview.query.filter_by(strategy_id=strategy_id).all()
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
            strategy = Strategy.query.get(strategy_id)
            strategy.rating = avg_rating
            db.session.commit()