from flask import Flask
from .blueprints import auth_bp, dashboard_bp, portfolio_bp, trade_bp, settings_bp
from .extensions import ma, limiter, cache
from .models import db
from flask_cors import CORS

def create_app(config_name):
    """
    Flask app factory
    """
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Initialize extensions
    CORS(app)  # Enable CORS for all routes
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dash")
    app.register_blueprint(trade_bp, url_prefix="/trade")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
    app.register_blueprint(settings_bp, url_prefix="/settings")

    return app


