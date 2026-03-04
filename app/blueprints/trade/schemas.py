from marshmallow import Schema, fields, validate
from app.extensions import ma
from app.models import Order


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order
        load_instance = True
    
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    crypto_id = fields.Int(required=True)
    order_type = fields.Str(required=True, validate=validate.OneOf(['buy', 'sell']))
    price = fields.Float(dump_only=True)
    quantity = fields.Float(required=True, validate=validate.Range(min=0.00000001))
    total_value = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    executed_at = fields.DateTime(dump_only=True, allow_none=True)


class PlaceOrderSchema(Schema):
    crypto_id = fields.Int(required=True)
    order_type = fields.Str(required=True, validate=validate.OneOf(['buy', 'sell']))
    quantity = fields.Float(required=True, validate=validate.Range(min=0.00000001))


class OrderListSchema(Schema):
    page = fields.Int(validate=validate.Range(min=1))
    per_page = fields.Int(validate=validate.Range(min=1, max=100))
    status = fields.Str(allow_none=True, validate=validate.OneOf(['pending', 'completed', 'cancelled']))


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
place_order_schema = PlaceOrderSchema()
order_list_schema = OrderListSchema()