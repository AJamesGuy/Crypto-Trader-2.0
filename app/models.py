from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Boolean, DECIMAL, JSON, TIMESTAMP
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)

# Cryptocurrency Table
class Cryptocurrency(db.Model):
    __tablename__ = 'cryptocurrency'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(200), nullable=True)
    circulating_supply: Mapped[float] = mapped_column(DECIMAL(24, 8), nullable=True)
    total_supply: Mapped[float] = mapped_column(DECIMAL(24, 8), nullable=True)
    ath: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=True)
    ath_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    market_data = relationship('MarketData', back_populates='cryptocurrency', cascade='all, delete-orphan')
    asset_metadata = relationship('AssetMetaData', back_populates='cryptocurrency', cascade='all, delete-orphan')
    portfolio_assets = relationship('PortfolioAsset', back_populates='cryptocurrency', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='cryptocurrency', cascade='all, delete-orphan')


# MarketData Table
class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    crypto_id: Mapped[int] = mapped_column(ForeignKey('cryptocurrency.id'), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    open: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=True)
    high: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=True)
    low: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=True)
    close: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=True)
    volume: Mapped[float] = mapped_column(DECIMAL(24, 8), nullable=True)
    market_cap: Mapped[float] = mapped_column(DECIMAL(24, 2), nullable=True)
    change_24h: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    change_7d: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    
    # Relationships
    cryptocurrency = relationship('Cryptocurrency', back_populates='market_data')


# User Table
class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cash_balance: Mapped[float] = mapped_column(DECIMAL(18, 2), default=10000, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    portfolios = relationship('Portfolio', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')


# Portfolio Table
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    
    portfolio_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    total_value: Mapped[float] = mapped_column(DECIMAL(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='portfolios')
    assets = relationship('PortfolioAsset', back_populates='portfolio', cascade='all, delete-orphan')


# PortfolioAsset Table
class PortfolioAsset(db.Model):
    __tablename__ = 'portfolio_asset'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey('portfolio.portfolio_id'), nullable=False)
    crypto_id: Mapped[int] = mapped_column(ForeignKey('cryptocurrency.id'), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    avg_buy_price: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    current_value: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    
    # Relationships
    portfolio = relationship('Portfolio', back_populates='assets')
    cryptocurrency = relationship('Cryptocurrency', back_populates='portfolio_assets')


# AssetMetaData Table
class AssetMetaData(db.Model):
    __tablename__ = 'asset_metadata'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    crypto_id: Mapped[int] = mapped_column(ForeignKey('cryptocurrency.id'), unique=True, nullable=False)
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cryptocurrency = relationship('Cryptocurrency', back_populates='asset_metadata')


# Order Table
class Order(db.Model):
    __tablename__ = 'order'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    crypto_id: Mapped[int] = mapped_column(ForeignKey('cryptocurrency.id'), nullable=False)
    order_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'buy' or 'sell'
    price: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    total_value: Mapped[float] = mapped_column(DECIMAL(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'pending', 'completed', 'cancelled'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    cryptocurrency = relationship('Cryptocurrency', back_populates='orders')