#!/usr/bin/env python3
"""
Script to check and populate market data with candlestick OHLC data
"""
from app import create_app
from app.models import db, MarketData, Cryptocurrency
from datetime import datetime, timedelta
import random

app = create_app('DevelopmentConfig')

with app.app_context():
    # Check existing data
    total_records = db.session.query(MarketData).count()
    ohlc_records = db.session.query(MarketData).filter(
        MarketData.open.isnot(None),
        MarketData.high.isnot(None),
        MarketData.low.isnot(None),
        MarketData.close.isnot(None)
    ).count()
    
    print(f"Total market data records: {total_records}")
    print(f"Records with OHLC data: {ohlc_records}")
    
    # If no OHLC data exists, populate with sample data
    if ohlc_records == 0 and total_records > 0:
        print("\nPopulating OHLC data for existing records...")
        
        # Get all market data records without OHLC
        records_to_update = db.session.query(MarketData).filter(
            MarketData.open.isnot(None) | MarketData.open.is_(None)
        ).all()
        
        for record in records_to_update:
            if record.price and not record.open:
                # Generate realistic OHLC based on current price
                base_price = float(record.price)
                volatility = base_price * 0.05  # 5% volatility
                
                # Generate OHLC
                open_price = base_price + random.uniform(-volatility, volatility)
                close_price = base_price + random.uniform(-volatility, volatility)
                high_price = max(open_price, close_price) + abs(random.uniform(0, volatility * 0.5))
                low_price = min(open_price, close_price) - abs(random.uniform(0, volatility * 0.5))
                
                record.open = open_price
                record.close = close_price
                record.high = high_price
                record.low = low_price
        
        db.session.commit()
        print(f"Updated {len(records_to_update)} records with OHLC data")
        
        # Verify
        verified = db.session.query(MarketData).filter(
            MarketData.open.isnot(None),
            MarketData.high.isnot(None),
            MarketData.low.isnot(None),
            MarketData.close.isnot(None)
        ).count()
        print(f"Verified records with OHLC: {verified}")
    else:
        print("\nOHLC data already exists!")
        
        # Show sample OHLC data
        sample = db.session.query(MarketData).filter(
            MarketData.open.isnot(None),
            MarketData.high.isnot(None),
            MarketData.low.isnot(None),
            MarketData.close.isnot(None)
        ).first()
        
        if sample:
            crypto = db.session.query(Cryptocurrency).get(sample.crypto_id)
            print(f"\nSample OHLC data for {crypto.symbol}:")
            print(f"  Open: ${sample.open}")
            print(f"  High: ${sample.high}")
            print(f"  Low: ${sample.low}")
            print(f"  Close: ${sample.close}")
            print(f"  Time: {sample.timestamp}")
