from marshmallow import Schema, fields, validate
from app.extensions import ma
from app.models import Portfolio, PortfolioAsset


class PortfolioAssetSchema(ma.SQLAlchemySchema):
    class Meta:
        model = PortfolioAsset
        load_instance = True
    
    id = fields.Int(dump_only=True)
    portfolio_id = fields.Int(dump_only=True)
    crypto_id = fields.Int()
    quantity = fields.Float()
    avg_buy_price = fields.Float()
    current_value = fields.Float()


class PortfolioSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Portfolio
        load_instance = True
    
    portfolio_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    total_value = fields.Float()
    created_at = fields.DateTime()
    assets = fields.Nested(PortfolioAssetSchema, many=True, dump_only=True)


class PortfolioSummarySchema(Schema):
    portfolio_id = fields.Int()
    assets = fields.List(fields.Dict())
    cash_balance = fields.Float()
    total_invested = fields.Float()
    total_current_value = fields.Float()
    total_portfolio_value = fields.Float()
    overall_gain_loss = fields.Float()
    overall_gain_loss_percent = fields.Float()


class AssetDetailsSchema(Schema):
    id = fields.Int()
    symbol = fields.Str()
    quantity = fields.Float()
    current_price = fields.Float()
    current_value = fields.Float()


portfolio_schema = PortfolioSchema()
portfolios_schema = PortfolioSchema(many=True)
portfolio_asset_schema = PortfolioAssetSchema()
portfolio_assets_schema = PortfolioAssetSchema(many=True)
portfolio_summary_schema = PortfolioSummarySchema()
asset_details_schema = AssetDetailsSchema()
assets_details_schema = AssetDetailsSchema(many=True)