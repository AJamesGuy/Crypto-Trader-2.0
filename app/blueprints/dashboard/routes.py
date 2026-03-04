from flask import request, jsonify
from app.extensions import limiter, cache
from marshmallow import ValidationError
from . import dashboard_bp
from app.models import db, Cryptocurrency, MarketData, User
from .schemas import crypto_schema, cryptos_schema, market_data_schema, market_data_list_schema, search_query_schema
from datetime import datetime
from app.util.auth import token_required
from sqlalchemy import or_, and_


# Get all cryptocurrencies
@dashboard_bp.route('/cryptos', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=300)  # Cache for 5 minutes
@token_required
def get_cryptos():
    """Get all available cryptocurrencies"""
    cryptos = Cryptocurrency.query.filter_by(is_active=True).all()
    return cryptos_schema.jsonify(cryptos), 200


# Get market data for all cryptocurrencies
@dashboard_bp.route('/market-data', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60)  # Cache for 1 minute
@token_required
def get_market_data():
    """Get latest market data for all cryptocurrencies"""
    # Get latest timestamp for each crypto
    subquery = db.session.query( # Subquery to get latest market data timestamp for each crypto
        MarketData.crypto_id,
        db.func.max(MarketData.timestamp).label('max_timestamp') # Get max timestamp for each crypto_id
    ).group_by(MarketData.crypto_id).subquery() # Join with MarketData and Cryptocurrency

    # Join with MarketData and Cryptocurrency
    query = db.session.query(MarketData, Cryptocurrency).join( # Join with subquery to get latest market data for each crypto
        subquery, db.and_(MarketData.crypto_id == subquery.c.crypto_id, MarketData.timestamp == subquery.c.max_timestamp)).join( # Join with Cryptocurrency to get symbol and description
            Cryptocurrency, MarketData.crypto_id == Cryptocurrency.id).filter( # Only active cryptocurrencies
                Cryptocurrency.is_active == True).order_by( # Order by market cap descending
                    MarketData.market_cap.desc()) 
    latest_data = query.all() # Get all results

    # Assign ranks based on market_cap
    results = []
    rank = 1 # Start rank at 1
    for md, crypto in latest_data: # Loop through results and build response
        result = market_data_schema.dump(md)
        result['symbol'] = crypto.symbol
        result['name'] = crypto.description
        result['image'] = crypto.image
        result['market_cap_rank'] = rank
        results.append(result)
        rank += 1

    return jsonify(results), 200 # Return results as JSON


# Search cryptocurrencies
@dashboard_bp.route('/search', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def search_cryptos():
    """Search cryptocurrencies by symbol or name"""
    try:
        data = search_query_schema.load(request.args)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    query = data['query'].lower()
    limit = data.get('limit', 50)
    
    cryptos = Cryptocurrency.query.filter_by(is_active=True).filter(
        db.or_(
            Cryptocurrency.symbol.ilike(f"%{query}%"),
            Cryptocurrency.description.ilike(f"%{query}%")
        )
    ).limit(limit).all()
    
    return cryptos_schema.jsonify(cryptos), 200


# Get market data for specific cryptocurrency
@dashboard_bp.route('/market-data/<int:crypto_id>', methods=['GET'])
@limiter.limit("20 per minute")
@cache.cached(timeout=60)
@token_required
def get_crypto_market_data(crypto_id):
    """Get market data for a specific cryptocurrency"""
    crypto = Cryptocurrency.query.get(crypto_id)
    if not crypto:
        return jsonify({"message": "Cryptocurrency not found"}), 404
    
    market_data = MarketData.query.filter_by(crypto_id=crypto_id).order_by(
        MarketData.timestamp.desc()
    ).first()
    
    if not market_data:
        return jsonify({"message": "Market data not available"}), 404
    
    result = market_data_schema.dump(market_data)
    result['symbol'] = crypto.symbol
    result['name'] = crypto.description
    result['image'] = crypto.image
    result['circulating_supply'] = float(crypto.circulating_supply) if crypto.circulating_supply else None
    result['total_supply'] = float(crypto.total_supply) if crypto.total_supply else None
    result['ath'] = float(crypto.ath) if crypto.ath else None
    result['ath_date'] = crypto.ath_date.isoformat() if crypto.ath_date else None
    
    return jsonify(result), 200


# Get candlestick data for a specific cryptocurrency
@dashboard_bp.route('/market-data/<int:crypto_id>/candles', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_candlestick_data(crypto_id):
    """Get candlestick data for a specific cryptocurrency"""
    crypto = Cryptocurrency.query.get(crypto_id)
    if not crypto:
        return jsonify({"message": "Cryptocurrency not found"}), 404
    
    # Get timeframe from query params (default: 24h)
    timeframe = request.args.get('timeframe', '24h')
    
    # Query market data ordered by timestamp descending
    market_data = MarketData.query.filter_by(
        crypto_id=crypto_id
    ).filter(
        MarketData.open.isnot(None),
        MarketData.high.isnot(None),
        MarketData.low.isnot(None),
        MarketData.close.isnot(None)
    ).order_by(
        MarketData.timestamp.asc()
    ).limit(50).all()  # Get last 50 candles
    
    if not market_data:
        return jsonify([]), 200
    
    candles = []
    for data in market_data:
        candles.append({
            'time': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'open': float(data.open),
            'high': float(data.high),
            'low': float(data.low),
            'close': float(data.close),
            'volume': float(data.volume) if data.volume else 0
        })
    
    return jsonify(candles), 200


# Get user's current cash balance
@dashboard_bp.route('/<int:user_id>/cash-balance', methods=['GET'])
@limiter.limit("30 per minute")
@token_required
def get_cash_balance(user_id):
    """Get user's cash balance"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "cash_balance": float(user.cash_balance),
        "user_id": user_id
    }), 200