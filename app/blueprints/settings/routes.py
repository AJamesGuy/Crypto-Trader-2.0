from flask import request, jsonify
from app.extensions import limiter
from marshmallow import ValidationError
from . import settings_bp
from app.models import db, User, Portfolio, PortfolioAsset, Order
from .schemas import update_profile_schema, change_password_schema, reset_balance_schema, delete_account_schema
from werkzeug.security import generate_password_hash, check_password_hash
from app.util.auth import token_required


# Get user settings/profile
@settings_bp.route('/<int:user_id>/profile', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_profile(user_id):
    """Get user profile information"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only view their own profile
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "cash_balance": float(user.cash_balance),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }), 200


# Update user profile
@settings_bp.route('/<int:user_id>/update-profile', methods=['PUT'])
@limiter.limit("10 per minute")
@token_required
def update_profile(user_id):
    """Update user profile information"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only update their own profile
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        data = update_profile_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Update username if provided and not taken
    if 'username' in data and data['username'] != user.username:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({"message": "Username already taken"}), 409
        user.username = data['username']
    
    # Update email if provided and not taken
    if 'email' in data and data['email'] != user.email:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "Email already taken"}), 409
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


# Change password
@settings_bp.route('/<int:user_id>/change-password', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
def change_password(user_id):
    """Change user password"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only change their own password
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        data = change_password_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Verify current password
    if not check_password_hash(user.password, data['current_password']):
        return jsonify({"message": "Current password is incorrect"}), 401
    
    # Update password
    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({"message": "Password changed successfully"}), 200


# Reset balance
@settings_bp.route('/<int:user_id>/reset-balance', methods=['POST'])
@limiter.limit("3 per day")
@token_required
def reset_balance(user_id):
    """Reset user's balance to initial amount"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only reset their own balance
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        data = reset_balance_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Require confirmation
    if not data['confirm']:
        return jsonify({"message": "Balance reset requires confirmation"}), 400
    
    # Reset balance to $10,000
    user.cash_balance = 10000.0
    
    # Reset portfolio
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()
    if portfolio:
        # Delete all portfolio assets
        PortfolioAsset.query.filter_by(portfolio_id=portfolio.portfolio_id).delete()
        portfolio.total_value = 10000.0
    
    # Delete all user orders
    Order.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    return jsonify({
        "message": "Balance reset successfully to $10,000",
        "cash_balance": float(user.cash_balance)
    }), 200


# Delete account
@settings_bp.route('/<int:user_id>/delete-account', methods=['DELETE'])
@limiter.limit("1 per day")
@token_required
def delete_account(user_id):
    """Delete user account and all associated data"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only delete their own account
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        data = delete_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Require password confirmation
    if not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Password is incorrect"}), 401
    
    # Additional confirmation for deletion
    if not data['confirm']:
        return jsonify({"message": "Account deletion requires confirmation"}), 400
    
    # Delete all user data (cascading deletes will handle related data)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "Account deleted successfully"}), 200


# Get all settings
@settings_bp.route('/<int:user_id>', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_settings(user_id):
    """Get all user settings"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only view their own settings
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "profile": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        },
        "account": {
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        "trading": {
            "cash_balance": float(user.cash_balance)
        }
    }), 200


# Security settings - view failed login attempts (if logged)
@settings_bp.route('/<int:user_id>/security', methods=['GET'])
@limiter.limit("20 per minute")
@token_required
def get_security_settings(user_id):
    """Get security-related information"""
    if request.logged_in_user_id != user_id:
        return jsonify({"message": "Unauthorized access"}), 403 # Ensure users can only view their own security settings
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "account_security": {
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "account_active": user.is_active,
            "created_at": user.created_at.isoformat()
        },
        "available_actions": [
            "change_password",
            "reset_balance",
            "delete_account"
        ]
    }), 200