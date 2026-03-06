from apscheduler.schedulers.background import BackgroundScheduler
from .services.coingecko_service import update_market_data
from .models import db, Cryptocurrency, MarketData
import logging
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# CoinGecko API endpoint for historical data
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Mapping of symbols to CoinGecko IDs
CRYPTO_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'SOL': 'solana',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'DOT': 'polkadot',
    'LTC': 'litecoin',
}


def fetch_historical_data(coin_id, days=30):
    """
    Fetch historical OHLCV data from CoinGecko
    
    Args:
        coin_id (str): CoinGecko coin ID (e.g., 'bitcoin')
        days (int): Number of days of historical data to fetch
    
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
    Populate candlestick data from CoinGecko for all cryptocurrencies
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        logger.info("=" * 60)
        logger.info("Starting candlestick data population...")
        logger.info("=" * 60)
        
        total_added = 0
        
        for symbol, coin_id in CRYPTO_MAP.items():
            try:
                # Get crypto from database
                crypto = Cryptocurrency.query.filter_by(symbol=symbol).first()
                if not crypto:
                    logger.warning(f"Cryptocurrency {symbol} not found in database. Skipping...")
                    continue
                
                # Check existing data count
                existing_count = MarketData.query.filter_by(crypto_id=crypto.id).count()
                
                # Only fetch if we don't have recent data (less than 24 hours old)
                if existing_count > 0:
                    latest_entry = MarketData.query.filter_by(
                        crypto_id=crypto.id
                    ).order_by(MarketData.timestamp.desc()).first()
                    
                    if latest_entry and (datetime.utcnow() - latest_entry.timestamp).total_seconds() < 86400:
                        logger.info(f"  {symbol}: Has recent data ({existing_count} points). Skipping...")
                        continue
                
                logger.info(f"  Fetching historical data for {symbol}...")
                ohlcv_data = fetch_historical_data(coin_id, days=30)
                
                if not ohlcv_data:
                    logger.warning(f"  No data received for {symbol}")
                    continue
                
                # Add to database
                count = 0
                for candle in ohlcv_data:
                    try:
                        timestamp_ms, open_price, high_price, low_price, close_price = candle
                        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                        
                        # Check if already exists
                        existing = MarketData.query.filter_by(
                            crypto_id=crypto.id,
                            timestamp=timestamp
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Create new entry
                        market_data = MarketData(
                            crypto_id=crypto.id,
                            timestamp=timestamp,
                            price=close_price,
                            open=open_price,
                            high=high_price,
                            low=low_price,
                            close=close_price,
                            volume=0,
                            market_cap=None,
                            change_24h=None,
                            change_7d=None
                        )
                        
                        db.session.add(market_data)
                        count += 1
                        
                    except (ValueError, IndexError) as e:
                        logger.warning(f"  Error processing candle data: {e}")
                        continue
                
                # Commit for this crypto
                if count > 0:
                    try:
                        db.session.commit()
                        logger.info(f"  ✓ Added {count} data points for {symbol}")
                        total_added += count
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"  Error committing data for {symbol}: {e}")
                else:
                    logger.info(f"  {symbol}: No new data points to add")
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        logger.info("=" * 60)
        logger.info(f"Candle data population completed. Total new entries: {total_added}")
        logger.info("=" * 60)


def schedule_market_data_update(app):
    """Update market data from CoinGecko"""
    with app.app_context():
        update_market_data(limit=200, vs_currency='usd')


def start_scheduler(app):
    """Initialize and start the background scheduler for market data updates""" 
    # Initial market data update on startup
    scheduler.add_job(
        func=schedule_market_data_update,
        args=[app],
        trigger='date',
        run_date=None,
        id='initial_market_data_update',
        name='Initial CoinGecko Market Data Update',
        replace_existing=True,
    )
    
    # Populate candles on startup (only if needed)
    scheduler.add_job(
        func=populate_candle_data,
        args=[app],
        trigger='date',
        run_date=None,
        id='initial_candle_population',
        name='Initial Candlestick Data Population',
        replace_existing=True,
    )
    
    # Update market data every 1 minute
    scheduler.add_job(
        func=schedule_market_data_update,
        args=[app],
        trigger="interval",
        minutes=1,
        id="update_market_data",
        name="Update CoinGecko Market Data",
        replace_existing=True,
    )
    
    # Rescan and populate missing candle data daily (e.g., 2 AM UTC)
    scheduler.add_job(
        func=populate_candle_data,
        args=[app],
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_candle_check",
        name="Daily Candlestick Data Check",
        replace_existing=True,
    )

    def handle_job_error(event):
        if event.exception:
            logger.error(f"Error in scheduled job '{event.job_id}': {event.exception}")
        else:
            logger.info(f"Scheduled job '{event.job_id}' completed successfully")
    
    scheduler.add_listener(handle_job_error, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    scheduler.start()

    logger.info("Background scheduler started")
    logger.info("  - Market data updates every 1 minute")
    logger.info("  - Candlestick data populated on startup")
    logger.info("  - Daily candle data check at 2:00 AM UTC")