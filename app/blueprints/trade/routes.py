from flask import request, jsonify
from app.extensions import limiter, cache
from marshmallow import ValidationError
from . import trade_bp
from app.models import db, Order, User, Cryptocurrency, MarketData, PortfolioAsset, Portfolio
from .schemas import place_order_schema, order_list_schema
from datetime import datetime
from app.util.auth import token_required


def make_orders_key(user_id):
    args = str(hash(frozenset(request.args.items()))) # Create a hash of the query parameters to use as part of the cache key


# Place a new order (buy or sell)
@trade_bp.route('/<int:user_id>/order', methods=['POST'])
@limiter.limit("20 per minute")
@token_required
def place_order(user_id):
    """Place a buy or sell order"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403 # Ensure users can only place orders for themselves
    try:
        data = place_order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    crypto_id = data['crypto_id']
    order_type = data['order_type'].lower()
    quantity = data['quantity']
    
    # Check if cryptocurrency exists
    crypto = Cryptocurrency.query.get(crypto_id)
    if not crypto:
        return jsonify({"message": "Cryptocurrency not found"}), 404
    
    # Get latest market price
    market_data = MarketData.query.filter_by(crypto_id=crypto_id).order_by(
        MarketData.timestamp.desc()
    ).first()
    
    if not market_data:
        return jsonify({"message": "Market data not available for this cryptocurrency"}), 404
    
    price = float(market_data.price)
    total_value = quantity * price
    user = User.query.get(user_id)
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        return jsonify({"message": "Portfolio not found"}), 404
    
    if order_type == 'buy':
        # Check if user has enough cash balance
        if user.cash_balance < total_value:
            return jsonify({
                "message": "Insufficient cash balance",
                "required": total_value,
                "available": float(user.cash_balance)
            }), 400
    
    elif order_type == 'sell':
        # Check if user owns the cryptocurrency
        portfolio_asset = PortfolioAsset.query.filter_by(
            portfolio_id=portfolio.portfolio_id,
            crypto_id=crypto_id
        ).first()
        
        if not portfolio_asset or portfolio_asset.quantity < quantity:
            available = float(portfolio_asset.quantity) if portfolio_asset else 0.0
            return jsonify({
                "message": "Insufficient cryptocurrency holdings",
                "requested": quantity,
                "available": available
            }), 400
    
    # Create order
    new_order = Order(
        user_id=user_id,
        crypto_id=crypto_id,
        order_type=order_type,
        price=price,
        quantity=quantity,
        total_value=total_value,
        status='pending'
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({
        "message": "Order placed successfully",
        "order": {
            "id": new_order.id,
            "type": new_order.order_type,
            "symbol": crypto.symbol,
            "quantity": float(new_order.quantity),
            "price": float(new_order.price),
            "total_value": float(new_order.total_value),
            "status": new_order.status,
            "created_at": new_order.created_at.isoformat()
        },
        "new_cash_balance": float(user.cash_balance)
    }), 201


# Execute an order
@trade_bp.route('/<int:user_id>/order/<int:order_id>/execute', methods=['POST'])
@limiter.limit("20 per minute")
@token_required
def execute_order(user_id, order_id):
    """Execute a pending order"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    if order.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403 # Ensure only the owner can execute their order
    
    if order.status != 'pending':
        return jsonify({"message": f"Order is already {order.status}"}), 400
    
    user = User.query.get(user_id)
    # Get or create portfolio asset
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if not portfolio:
        return jsonify({"message": "Portfolio not found"}), 404
    
    portfolio_asset = PortfolioAsset.query.filter_by(
        portfolio_id=portfolio.portfolio_id,
        crypto_id=order.crypto_id
    ).first()
    
    if order.order_type == 'buy':
        if user.cash_balance < order.total_value:
            return jsonify({"message": "Insufficient cash balance"}), 400
        user.cash_balance -= order.total_value
        if portfolio_asset:
            # Update existing holding
            total_cost = (float(portfolio_asset.quantity) * float(portfolio_asset.avg_buy_price)) + float(order.total_value)
            portfolio_asset.quantity += order.quantity
            portfolio_asset.avg_buy_price = total_cost / float(portfolio_asset.quantity)
            portfolio_asset.current_value = float(portfolio_asset.quantity) * float(order.price)
        else:
            # Create new holding
            portfolio_asset = PortfolioAsset(
                portfolio_id=portfolio.portfolio_id,
                crypto_id=order.crypto_id,
                quantity=order.quantity,
                avg_buy_price=order.price,
                current_value=order.total_value
            )
            db.session.add(portfolio_asset)
    
    elif order.order_type == 'sell':
        if not portfolio_asset or float(portfolio_asset.quantity) < order.quantity:
            return jsonify({"message": "Insufficient holdings"}), 400
        user.cash_balance += order.total_value
        portfolio_asset.quantity -= order.quantity
        if float(portfolio_asset.quantity) > 0:
            portfolio_asset.current_value = float(portfolio_asset.quantity) * float(order.price)
        else:
            db.session.delete(portfolio_asset)
    
    # Update portfolio total value
    total_portfolio_value = sum(
        float(asset.current_value) for asset in PortfolioAsset.query.filter_by(
            portfolio_id=portfolio.portfolio_id
        ).all()
    )
    portfolio.total_value = total_portfolio_value + float(user.cash_balance)
    
    # Mark order as completed
    order.status = 'completed'
    order.executed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        "message": "Order executed successfully",
        "order": {
            "id": order.id,
            "status": order.status,
            "executed_at": order.executed_at.isoformat()
        }
    }), 200


# Get user's orders
@trade_bp.route('/<int:user_id>/orders', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_orders(user_id):
    """Get all orders for the user"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    
    try:
        data = order_list_schema.load(request.args)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)
    status = data.get('status')
    
    # JOIN with Cryptocurrency to avoid N+1 queries
    query = db.session.query(Order, Cryptocurrency).join(
        Cryptocurrency, Order.crypto_id == Cryptocurrency.id
    ).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    
    # Get paginated results - ONE query, not N+1
    orders_data = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    # Build response
    orders_list = [{
        "id": order.id,
        "crypto_id": order.crypto_id,
        "symbol": crypto.symbol,  # Already fetched in join!
        "type": order.order_type,
        "quantity": float(order.quantity),
        "price": float(order.price),
        "total_value": float(order.total_value),
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "executed_at": order.executed_at.isoformat() if order.executed_at else None
    } for order, crypto in orders_data]
    
    return jsonify({
        "orders": orders_list,
        "total": total,
        "page": page,
        "per_page": per_page
    }), 200

# Get specific order
@trade_bp.route('/<int:user_id>/order/<int:order_id>', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_order(user_id, order_id):
    """Get details of a specific order"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    if order.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403 # Ensure only the owner can view their order details
    
    crypto = Cryptocurrency.query.get(order.crypto_id)
    
    return jsonify({
        "id": order.id,
        "crypto_id": order.crypto_id,
        "symbol": crypto.symbol,
        "type": order.order_type,
        "quantity": float(order.quantity),
        "price": float(order.price),
        "total_value": float(order.total_value),
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "executed_at": order.executed_at.isoformat() if order.executed_at else None
    }), 200


# Cancel order
@trade_bp.route('/<int:user_id>/order/<int:order_id>/cancel', methods=['POST'])
@limiter.limit("20 per minute")
@token_required
def cancel_order(user_id, order_id):
    """Cancel a pending order"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    if order.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403 # Ensure only the owner can cancel their order
    
    if order.status != 'pending':
        return jsonify({"message": f"Cannot cancel a {order.status} order"}), 400
    
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify({"message": "Order cancelled successfully"}), 200