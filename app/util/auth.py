from datetime import datetime, timedelta, timezone
from functools import wraps
from jose import jwt
import jose
from flask import request, jsonify
import os

SECRET_KEY = os.getenv("SECRET_KEY") or "testing_secret_key"

def encode_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Expecting "Bearer <token>"
        
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) # This does not overwrite request context, just returns the payload
            request.logged_in_user_id = payload['user_id'] # Store user_id in request context for access in routes (e. g. request.logged_in_user_id) If token is valid, we can access the user_id in the route functions via request.logged_in_user_id
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jose.exceptions.JWTError:
            return jsonify({"message": "Invalid token!"}), 401
        
        return f(*args, **kwargs)
    
    return decorated