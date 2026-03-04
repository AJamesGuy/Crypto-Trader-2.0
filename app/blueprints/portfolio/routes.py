from flask import request, jsonify
from app.extensions import limiter, cache
from . import portfolio_bp
from app.models import db, Portfolio, PortfolioAsset, User, Cryptocurrency, MarketData
from app.util.auth import token_required


# Get user's portfolio
@portfolio_bp.route('/<int:user_id>', methods=['GET'])
@limiter.limit("30 per minute")
@token_required
def get_portfolio(user_id):
    """Get user's portfolio with all holdings"""
    """
    Check if the logged in user is the same as the requested user_id in the route parameter. 
    This prevents users from accessing other users' portfolio data. 
    If they don't match, return 403 Forbidden.
    """
    if request.logged_in_user_id != user_id: 
        return jsonify({"message": "Unauthorized access"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    
    # Get all assets in portfolio
    assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    
    assets_data = []
    total_invested = 0.0
    total_current_value = 0.0
    
    for asset in assets:
        crypto = Cryptocurrency.query.get(asset.crypto_id) # Get cryptocurrency details for the asset
        market_data = MarketData.query.filter_by(crypto_id=asset.crypto_id).order_by(
            MarketData.timestamp.desc() # Get latest market data for the cryptocurrency and order by timestamp descending to get the most recent price
        ).first()
        
        # Set current price and calculate current value, invested value, gain/loss, and gain/loss percentage for the asset
        current_price = float(market_data.price) if market_data else 0.0
        current_value = float(asset.quantity) * current_price
        invested_value = float(asset.quantity) * float(asset.avg_buy_price)
        gain_loss = current_value - invested_value
        gain_loss_percent = (gain_loss / invested_value * 100) if invested_value > 0 else 0.0
        
        # Accumulate totals for invested value and current value across all assets in the portfolio
        total_invested += invested_value
        total_current_value += current_value
        
        assets_data.append({
            "id": asset.id,
            "crypto_id": asset.crypto_id,
            "symbol": crypto.symbol,
            "quantity": float(asset.quantity),
            "avg_buy_price": float(asset.avg_buy_price),
            "current_price": current_price,
            "invested_value": invested_value,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_loss_percent": gain_loss_percent
        })
    
    total_cash = float(user.cash_balance)
    total_portfolio_value = total_current_value + total_cash
    
    return jsonify({
        "portfolio_id": portfolio.portfolio_id,
        "assets": assets_data, # List of assets with details such as symbol, quantity, average buy price, current price, invested value, current value, gain/loss, and gain/loss percentage for each asset in the portfolio
        "cash_balance": total_cash, # User's current cash balance which is part of the total portfolio value
        "total_invested": total_invested, # Total amount invested across all assets in the portfolio, calculated as the sum of invested value for each asset
        "total_current_value": total_current_value, # Total current value of all assets in the portfolio, calculated as the sum of current value for each asset
        "total_portfolio_value": total_portfolio_value, # Total value of the portfolio including both the current value of assets and the cash balance
        "overall_gain_loss": total_current_value - total_invested, # Overall gain or loss for the portfolio calculated as the difference between total current value and total invested
        "overall_gain_loss_percent": ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0.0 # Overall gain or loss percentage calculated as the gain/loss divided by total invested, expressed as a percentage
    }), 200


# Get portfolio holdings (just the assets)
@portfolio_bp.route('/<int:user_id>/holdings', methods=['GET'])
@limiter.limit("30 per minute")
@token_required
def get_holdings(user_id):
    if request.logged_in_user_id != user_id: # Check if the logged in user is the same as the requested user_id in the route parameter. This prevents users from accessing other users' portfolio data. If they don't match, return 403 Forbidden.
        return jsonify({"message": "Unauthorized access"}), 403
    """Get user's cryptocurrency holdings"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    
    assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    
    holdings = []
    for asset in assets:
        crypto = Cryptocurrency.query.get(asset.crypto_id)
        market_data = MarketData.query.filter_by(crypto_id=asset.crypto_id).order_by(
            MarketData.timestamp.desc()
        ).first()
        
        current_price = float(market_data.price) if market_data else 0.0
        current_value = float(asset.quantity) * current_price
        average_cost = float(asset.avg_buy_price)
        invested_value = float(asset.quantity) * average_cost
        gain_loss = current_value - invested_value
        gain_percentage = (gain_loss / invested_value * 100) if invested_value > 0 else 0.0
        
        holdings.append({
            "id": asset.id,
            "symbol": crypto.symbol,
            "crypto_name": crypto.description,
            "crypto_image": crypto.image,
            "quantity": float(asset.quantity),
            "average_cost": average_cost,
            "current_price": current_price,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_percentage": gain_percentage
        })
    
    return jsonify(holdings), 200


# Get portfolio performance chart data
@portfolio_bp.route('/<int:user_id>/performance', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_portfolio_performance(user_id):
    if request.logged_in_user_id != user_id: # Check if the logged in user is the same as the requested user_id in the route parameter. This prevents users from accessing other users' portfolio data. If they don't match, return 403 Forbidden.
        return jsonify({"message": "Unauthorized access"}), 403
    """Get portfolio performance data for charts"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    portfolio = Portfolio.query.filter_by(user_id=user_id).first() 
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    
    assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    
    performance_data = []
    total_value = 0.0
    total_invested = 0.0
    
    for asset in assets:
        crypto = Cryptocurrency.query.get(asset.crypto_id) # Get cryptocurrency details for the asset from the PortfolioAsset entity (asset), which includes the crypto_id. This allows us to retrieve the symbol and other details of the cryptocurrency for performance calculations and display.
        market_data = MarketData.query.filter_by(crypto_id=asset.crypto_id).order_by( # Get latest Market Data for the cryptocurrency by relationship using the crypto_id from the PortfolioAsset entity. This allows us to get the most recent price for the cryptocurrency, which is essential for calculating the current value of the asset in the portfolio and its performance.
            MarketData.timestamp.desc()
        ).first()
        
        current_price = float(market_data.price) if market_data else 0.0
        current_value = float(asset.quantity) * current_price
        invested_value = float(asset.quantity) * float(asset.avg_buy_price)

        total_value += current_value
        total_invested += invested_value
        
        performance_data.append({
            "symbol": crypto.symbol,
            "value": current_value,
            "quantity": float(asset.quantity),
            "percentage": 0.0  # Will be calculated below
        })
    
    # Calculate percentages
    if total_value > 0:
        for data in performance_data:
            data['percentage'] = (data['value'] / total_value) * 100 # Calculate the percentage of each asset's current value relative to the total portfolio value, which can be used for performance charts to show the allocation of the portfolio across different assets
    
    total_gain = total_value - total_invested
    gain_percentage = (total_gain / total_invested * 100) if total_invested > 0 else 0.0

    return jsonify({
        "total_value": total_value,
        "total_gain": total_gain,
        "gain_percentage": gain_percentage,
        "assets": performance_data
    }), 200


# Get asset breakdown (allocation)
@portfolio_bp.route('/<int:user_id>/breakdown', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_asset_breakdown(user_id):
    """Get portfolio asset breakdown by allocation"""
    if request.logged_in_user_id != user_id: # Check if the logged in user is the same as the requested user_id in the route parameter. This prevents users from accessing other users' portfolio data. If they don't match, return 403 Forbidden.
        return jsonify({"message": "Unauthorized access"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    
    user = User.query.get(user_id)
    assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    
    breakdown = []
    total_value = 0.0
    
    # Add crypto holdings
    for asset in assets:
        crypto = Cryptocurrency.query.get(asset.crypto_id)
        market_data = MarketData.query.filter_by(crypto_id=asset.crypto_id).order_by(
            MarketData.timestamp.desc()
        ).first()
        
        current_price = float(market_data.price) if market_data else 0.0
        current_value = float(asset.quantity) * current_price
        total_value += current_value
        
        breakdown.append({
            "type": "crypto",
            "symbol": crypto.symbol,
            "value": current_value
        })
    
    # Add cash
    cash_value = float(user.cash_balance)
    total_value += cash_value
    breakdown.append({
        "type": "cash",
        "symbol": "USD",
        "value": cash_value
    })
    
    # Calculate percentages
    for item in breakdown:
        item['percentage'] = (item['value'] / total_value * 100) if total_value > 0 else 0.0
    
    return jsonify({
        "total_value": total_value,
        "breakdown": breakdown
    }), 200


# Get specific asset details
@portfolio_bp.route('/<int:user_id>/asset/<int:asset_id>', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_asset(user_id, asset_id):
    """Get details of a specific portfolio asset"""
    
    #Logic to ensure user can only access their own asset details. This is done by comparing the logged in user's ID (request.logged_in_user_id) with the user_id parameter in the route. If they don't match, it means the user is trying to access another user's asset details, which is not allowed, so we return a 403 Forbidden response.
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    asset = PortfolioAsset.query.get(asset_id)
    if not asset:
        return jsonify({"message": "Asset not found"}), 404
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    if asset.portfolio_id != portfolio.portfolio_id:
        return jsonify({"message": "Asset not found"}), 403
    
    crypto = Cryptocurrency.query.get(asset.crypto_id)
    market_data = MarketData.query.filter_by(crypto_id=asset.crypto_id).order_by(
        MarketData.timestamp.desc()
    ).first()
    
    current_price = float(market_data.price) if market_data else 0.0
    current_value = float(asset.quantity) * current_price
    invested_value = float(asset.quantity) * float(asset.avg_buy_price)
    gain_loss = current_value - invested_value
    gain_loss_percent = (gain_loss / invested_value * 100) if invested_value > 0 else 0.0
    
    return jsonify({
        "id": asset.id,
        "symbol": crypto.symbol,
        "quantity": float(asset.quantity),
        "avg_buy_price": float(asset.avg_buy_price),
        "current_price": current_price,
        "invested_value": invested_value,
        "current_value": current_value,
        "gain_loss": gain_loss,
        "gain_loss_percent": gain_loss_percent
    }), 200

@portfolio_bp.route('/<int:user_id>/assets', methods=['GET'])
@token_required
def get_all_assets(user_id):
    """Get all assets and their IDs for a user"""
    
    # Verify user
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Get user's portfolio
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        # Auto-create portfolio if it doesn't exist
        portfolio = Portfolio(user_id=user_id, total_value=float(user.cash_balance))
        db.session.add(portfolio)
        db.session.commit()
    
    # Get all assets
    assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).all()
    
    # Build response with asset IDs and details
    asset_list = []
    for asset in assets:
        crypto = Cryptocurrency.query.get(asset.crypto_id)
        asset_list.append({
            "asset_id": asset.id,  # ← Asset ID
            "symbol": crypto.symbol,
            "quantity": float(asset.quantity),
            "avg_buy_price": float(asset.avg_buy_price)
        })
    
    return jsonify({
        "user_id": user_id,
        "total_assets": len(assets),
        "assets": asset_list,
        "asset_ids": [asset.id for asset in assets]  # ← Just the IDs
    }), 200