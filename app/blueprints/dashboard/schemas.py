from dataclasses import dataclass
from typing import Optional
from marshmallow import Schema, fields, validate
from app.extensions import ma
from app.models import Cryptocurrency, MarketData


class CryptoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Cryptocurrency
        load_instance = True
    
    id = fields.Int(dump_only=True)
    symbol = fields.Str()
    description = fields.Str()
    image = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime()


class MarketDataSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MarketData
        load_instance = True
    
    id = fields.Int(dump_only=True)
    crypto_id = fields.Int()
    timestamp = fields.DateTime()
    price = fields.Float()
    open = fields.Float(allow_none=True)
    high = fields.Float(allow_none=True)
    low = fields.Float(allow_none=True)
    close = fields.Float(allow_none=True)
    volume = fields.Float(allow_none=True)
    market_cap = fields.Float(allow_none=True)
    change_24h = fields.Float(allow_none=True)
    change_7d = fields.Float(allow_none=True)

class SearchQuerySchema(Schema):
    query = fields.Str(required=True, validate=validate.Length(min=1))
    limit = fields.Int(validate=validate.Range(min=1, max=100))


crypto_schema = CryptoSchema()
cryptos_schema = CryptoSchema(many=True)
market_data_schema = MarketDataSchema()
market_data_list_schema = MarketDataSchema(many=True)
search_query_schema = SearchQuerySchema()