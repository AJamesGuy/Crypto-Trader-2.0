"""
Script to populate historical candlestick (OHLCV) data into the MarketData table.
This script fetches historical data from CoinGecko and stores it in the database.

Usage: python populate_candles.py
"""

import os
import sys
from datetime import datetime, timedelta
import requests
import logging

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, Cryptocurrency, MarketData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CoinGecko API endpoint for historical data
COINGECKO_API = "https://api.coingecko.com/api/v3"


def get_crypto_symbol_to_id_map():
    """Get mapping of symbols to CoinGecko IDs"""
    crypto_map = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether',
        'BNB': 'binancecoin',
        'XRP': 'ripple',
        'SOL': 'solana',
        'ADA': 'cardano',
        'DOGE': 'dogecoin',
        'POLKADOT': 'polkadot',
        'LITECOIN': 'litecoin',
    }
    return crypto_map


def fetch_historical_data(coin_id, days=30):
    """
    Fetch historical OHLCV data from CoinGecko
    
    Args:
        coin_id (str): CoinGecko coin ID (e.g., 'bitcoin')
        days (int): Number of days of historical data to fetch (max 90000)
    
    Returns:
        list: Historical OHLCV data points
    """
    try:
        url = f"{COINGECKO_API}/coins/{coin_id}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'precision': 8
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching historical data for {coin_id}: {e}")
        return []


def populate_candle_data(app):
    """
    Main function to populate candlestick data
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        crypto_map = get_crypto_symbol_to_id_map()
        
        for symbol, coin_id in crypto_map.items():
            logger.info(f"\nProcessing {symbol} ({coin_id})...")
            
            # Get crypto from database
            crypto = Cryptocurrency.query.filter_by(symbol=symbol).first()
            if not crypto:
                logger.warning(f"Cryptocurrency {symbol} not found in database. Skipping...")
                continue
            
            # Check if we already have data for this crypto
            existing_count = MarketData.query.filter_by(crypto_id=crypto.id).count()
            if existing_count > 0:
                logger.info(f"  {symbol}: Already has {existing_count} data points. Skipping...")
                continue
            
            # Fetch historical data
            logger.info(f"  Fetching historical data for {symbol}...")
            ohlcv_data = fetch_historical_data(coin_id, days=30)
            
            if not ohlcv_data:
                logger.warning(f"  No data received for {symbol}")
                continue
            
            # Add to database
            count = 0
            for candle in ohlcv_data:
                try:
                    # candle format: [timestamp, open, high, low, close]
                    timestamp_ms, open_price, high_price, low_price, close_price = candle
                    
                    # Convert milliseconds to datetime
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                    
                    # Check if this data point already exists
                    existing = MarketData.query.filter_by(
                        crypto_id=crypto.id,
                        timestamp=timestamp
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Create new MarketData entry
                    market_data = MarketData(
                        crypto_id=crypto.id,
                        timestamp=timestamp,
                        price=close_price,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=0,  # CoinGecko OHLC endpoint doesn't include volume
                        market_cap=None,
                        change_24h=None,
                        change_7d=None
                    )
                    
                    db.session.add(market_data)
                    count += 1
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"  Error processing candle data: {e}")
                    continue
            
            # Commit changes for this crypto
            try:
                db.session.commit()
                logger.info(f"  ✓ Added {count} data points for {symbol}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"  Error committing data for {symbol}: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("Populating Historical Candlestick Data")
    print("=" * 60)
    
    app = create_app()
    
    try:
        populate_candle_data(app)
        print("\n✓ Candle data population completed successfully!")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Fatal error during population: {e}")
        print(f"\n✗ Error: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
