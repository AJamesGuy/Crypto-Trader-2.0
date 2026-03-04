#!/usr/bin/env python3
"""Test if candlestick endpoint works"""
from app import create_app
from app.models import db, Cryptocurrency, MarketData

app = create_app('DevelopmentConfig')

with app.app_context():
    # Find BTC
    btc = db.session.query(Cryptocurrency).filter_by(symbol='BTC').first()
    if btc:
        print(f"Found BTC with ID: {btc.id}")
        
        # Get recent market data
        data = db.session.query(MarketData).filter_by(crypto_id=btc.id).filter(
            MarketData.open.isnot(None),
            MarketData.high.isnot(None),
            MarketData.low.isnot(None),
            MarketData.close.isnot(None)
        ).order_by(MarketData.timestamp.asc()).limit(50).all()
        
        print(f"Found {len(data)} candlesticks for BTC")
        
        if data:
            print("\nFirst candle:")
            d = data[0]
            print(f"  Time: {d.timestamp}")
            print(f"  Open: {d.open}")
            print(f"  High: {d.high}")
            print(f"  Low: {d.low}")
            print(f"  Close: {d.close}")
            
            print("\nLast candle:")
            d = data[-1]
            print(f"  Time: {d.timestamp}")
            print(f"  Open: {d.open}")
            print(f"  High: {d.high}")
            print(f"  Low: {d.low}")
            print(f"  Close: {d.close}")
    else:
        print("BTC not found in database")
