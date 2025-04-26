from marshmallow import Schema, fields

class StrategySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    author_id = fields.Int()
    price = fields.Float()
    rating = fields.Float()
    downloads = fields.Int()
    created_at = fields.DateTime()
    category = fields.Str()

class ReviewSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    strategy_id = fields.Int()
    rating = fields.Int()
    comment = fields.Str()
    created_at = fields.DateTime()

class PurchaseSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    strategy_id = fields.Int()
    purchase_date = fields.DateTime()
    license_key = fields.Str()
    is_active = fields.Bool()