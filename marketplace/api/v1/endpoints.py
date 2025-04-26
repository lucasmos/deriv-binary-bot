from flask_restx import Resource, fields
from flask import request
from flask_login import current_user
from ...services import MarketplaceService
from . import ns
from ...models import Strategy

service = MarketplaceService()

# API Models
strategy_model = ns.model('Strategy', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'author_id': fields.Integer,
    'price': fields.Float,
    'rating': fields.Float,
    'downloads': fields.Integer,
    'category': fields.String
})

review_model = ns.model('Review', {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'rating': fields.Integer,
    'comment': fields.String,
    'created_at': fields.DateTime
})

purchase_model = ns.model('Purchase', {
    'id': fields.Integer,
    'strategy_id': fields.Integer,
    'purchase_date': fields.DateTime,
    'license_key': fields.String
})

@ns.route('/strategies')
class StrategyList(Resource):
    @ns.marshal_list_with(strategy_model)
    def get(self):
        """Get list of available strategies"""
        return service.get_available_strategies()

@ns.route('/strategies/<int:strategy_id>')
class StrategyDetail(Resource):
    @ns.marshal_with(strategy_model)
    def get(self, strategy_id):
        """Get strategy details"""
        return service.get_strategy_by_id(strategy_id)

@ns.route('/strategies/<int:strategy_id>/reviews')
class StrategyReviews(Resource):
    @ns.marshal_list_with(review_model)
    def get(self, strategy_id):
        """Get reviews for a strategy"""
        return service.get_strategy_reviews(strategy_id)
    
    @ns.expect(review_model)
    def post(self, strategy_id):
        """Add a review for a strategy"""
        data = request.json
        success = service.add_review(
            current_user.id,
            strategy_id,
            data.get('rating'),
            data.get('comment')
        )
        return {'success': success}, 201 if success else 400

@ns.route('/purchases')
class UserPurchases(Resource):
    @ns.marshal_list_with(purchase_model)
    def get(self):
        """Get user's purchased strategies"""
        return service.get_user_purchases(current_user.id)

@ns.route('/purchases', methods=['POST'])
class MakePurchase(Resource):
    @ns.expect(purchase_model)
    @ns.marshal_with(purchase_model, code=201)
    def post(self):
        """Purchase a strategy"""
        data = request.json
        success, message = service.purchase_strategy(
            current_user.id,
            data.get('strategy_id')
        )
        if success:
            return message, 201
        return {'error': message}, 400