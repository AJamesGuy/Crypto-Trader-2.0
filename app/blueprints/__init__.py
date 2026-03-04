# app/blueprints/__init__.py  (optional — nice for cleaner imports elsewhere)
from .auth import auth_bp
from .dashboard import dashboard_bp
from .portfolio import portfolio_bp
from .trade import trade_bp
from .settings import settings_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'portfolio_bp',
    'trade_bp',
    'settings_bp',
]