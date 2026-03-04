# app/blueprints/auth/routes.py
from flask import request, jsonify
from sqlalchemy import or_
from app.extensions import limiter
from marshmallow import ValidationError
from . import auth_bp
from app.models import User, db, Portfolio
from .schemas import signup_schema, login_schema
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.util.auth import encode_token, token_required

# Create CRUD routes for login, signup, logout
@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    """Create a new user account"""
    try:
        user_data = signup_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Check if user already exists
    existing_user = (
        User.query.filter(or_(User.email == user_data['email'], User.username == user_data['username'])).first()
    )
    if existing_user:
        return jsonify({"message": "User with that email or username already exists"}), 409
    
    # Hash password and prepare data for creation
    user_data['password'] = generate_password_hash(user_data['password'])
    user_data.pop('password_confirm') # Remove password_confirm as it's not a model field
    user_data['cash_balance'] = 10000.0
    
    new_user = User(**user_data)
    db.session.add(new_user)
    db.session.flush()  # get ID

    # Create a portfolio for the new user with an initial total value equal to the starting cash balance. This ensures that every user has an associated portfolio when they sign up, which can be used to track their investments and performance.
    portfolio = Portfolio(user_id=new_user.id, total_value=10000.0)
    db.session.add(portfolio)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "cash_balance": float(new_user.cash_balance),
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return JWT token"""
    try:
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user = User.query.filter_by(email=data.get('email')).first() or User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password, data['password']):
        token = encode_token(user.id)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "cash_balance": float(user.cash_balance)
            }
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route('/<int:user_id>/logout', methods=['POST'])
@token_required
def logout(user_id):
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.is_active = False
    db.session.commit()
    """Logout user - JWT token is handled client-side"""
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route('/<int:user_id>/profile', methods=['GET'])
@token_required
def get_profile(user_id):
    """Get user profile information"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "cash_balance": float(user.cash_balance),
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }), 200
