#!/usr/bin/env python3
"""
Generate multiple historical candlesticks for each cryptocurrency
"""
from app import create_app
from app.models import db, Cryptocurrency, MarketData
from datetime import datetime, timedelta
import random

app = create_app('DevelopmentConfig')

with app.app_context():
    cryptos = db.session.query(Cryptocurrency).filter_by(is_active=True).all()
    
    print(f"Generating candlestick data for {len(cryptos)} cryptocurrencies...\n")
    
    for crypto in cryptos:
        # Get the current market data to use as base
        latest = db.session.query(MarketData).filter_by(crypto_id=crypto.id).order_by(
            MarketData.timestamp.desc()
        ).first()
        
        if not latest or not latest.price:
            print(f"Skipping {crypto.symbol} - no price data")
            continue
        
        # Clear old data for this crypto (keep only latest)
        old_data = db.session.query(MarketData).filter_by(crypto_id=crypto.id).all()
        for d in old_data:
            db.session.delete(d)
        
        base_price = float(latest.price)
        current_time = datetime.utcnow()
        
        # Generate 48 candlesticks (2 days @ 1 hour intervals)
        for i in range(48):
            timestamp = current_time - timedelta(hours=48-i)
            
            # Random walk for prices
            volatility = base_price * 0.02  # 2% volatility per candle
            
            open_price = base_price + random.uniform(-volatility, volatility)
            close_price = open_price + random.uniform(-volatility, volatility)
            high_price = max(open_price, close_price) + abs(random.uniform(0, volatility))
            low_price = min(open_price, close_price) - abs(random.uniform(0, volatility))
            volume = random.uniform(1000000, 10000000)
            
            candle = MarketData(
                crypto_id=crypto.id,
                timestamp=timestamp,
                price=close_price,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                market_cap=base_price * 100000000 * (1 + random.uniform(-0.01, 0.01)),
                change_24h=random.uniform(-5, 5),
                change_7d=random.uniform(-10, 10)
            )
            db.session.add(candle)
            
            # Update base price for next iteration for realistic walk
            base_price = close_price
        
        print(f"✓ Generated 48 candlesticks for {crypto.symbol}")
    
    db.session.commit()
    print("\n✓ All candlestick data generated successfully!")
    
    # Verify
    total = db.session.query(MarketData).count()
    print(f"\nTotal market data records: {total}")
