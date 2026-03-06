# Data Population Guide

## Populating Historical Candlestick Data

The CandlestickChart component requires historical OHLCV (Open, High, Low, Close, Volume) data in the `MarketData` table. To populate this data:

### Method 1: Using the Population Script (Recommended)

1. **Ensure dependencies are installed:**
   ```bash
   pip install requests pycoingecko
   ```

2. **Run the population script from the project root:**
   ```bash
   python populate_candles.py
   ```

3. **What this does:**
   - Fetches 30 days of historical OHLCV data from CoinGecko API
   - Populates the `MarketData` table with hourly candlestick data
   - Supports the following cryptocurrencies by default:
     - Bitcoin (BTC)
     - Ethereum (ETH)
     - Tether (USDT)
     - BNB (BNB)
     - XRP (XRP)
     - Solana (SOL)
     - Cardano (ADA)
     - Dogecoin (DOGE)
     - Polkadot (DOT)
     - Litecoin (LTC)

### Method 2: Using the CoinGecko Service

You can also manually call the CoinGecko service within your Flask app:

```python
from app.services.coingecko_service import update_market_data

# Update market data from CoinGecko
result = update_market_data(limit=100)
print(result)
```

### Continuous Data Updates

For production, set up a scheduled task using Celery or APScheduler:

```python
# Example with APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.coingecko_service import update_market_data

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_market_data, trigger="interval", minutes=1)
scheduler.start()
```

## API Response Formats

### GET /dash/cryptos
Returns basic cryptocurrency information (used for dropdowns):
```json
[
  {
    "id": 1,
    "symbol": "BTC",
    "description": "Bitcoin",
    "image": "https://...",
    "is_active": true,
    "created_at": "2026-03-06T06:07:32.211436",
    "circulating_supply": 21000000,
    "total_supply": 21000000,
    "ath": 69000,
    "ath_date": "2025-10-13T08:41:24.131000"
  }
]
```

### GET /dash/market-data
Returns latest market data for all cryptocurrencies (ranked by market cap):
```json
[
  {
    "id": 5601,
    "crypto_id": 1,
    "timestamp": "2026-03-06T06:21:32.115456",
    "price": 70340.0,
    "open": 70340.0,
    "high": 73434.0,
    "low": 70178.0,
    "close": 70340.0,
    "volume": 52508167942.0,
    "market_cap": 1405517585378.0,
    "change_24h": -2.63,
    "change_7d": 3.84,
    "symbol": "BTC",
    "name": "Bitcoin",
    "image": "https://...",
    "market_cap_rank": 1
  }
]
```

### GET /dash/market-data/{cryptoId}
Returns detailed market data for a specific cryptocurrency:
```json
{
  "id": 6404,
  "crypto_id": 4,
  "timestamp": "2026-03-06T06:23:32.138325",
  "price": 644.8,
  "open": 644.8,
  "high": 664.51,
  "low": 642.96,
  "close": 644.8,
  "volume": 1046253947.0,
  "market_cap": 87919893837.0,
  "change_24h": -1.24,
  "change_7d": 2.05,
  "symbol": "BNB",
  "name": "BNB",
  "image": "https://...",
  "circulating_supply": 136358504.87,
  "total_supply": 136358504.87,
  "ath": 1369.99,
  "ath_date": "2025-10-13T08:41:24.131000"
}
```

### GET /dash/market-data/{cryptoId}/candles?timeframe=24h
Returns candlestick data for a cryptocurrency:
```json
[
  {
    "time": "2026-03-06 06:00:00",
    "open": 70340.0,
    "high": 73434.0,
    "low": 70178.0,
    "close": 70500.0,
    "volume": 52508167942.0
  }
]
```

## Troubleshooting

### "No candle data available" error
- Run `python populate_candles.py` to populate historical data
- Ensure the MarketData table has entries with different timestamps
- Check that `crypto_id` matches valid cryptocurrencies in the Cryptocurrency table

### Chart shows "Failed to load chart data"
1. Check browser console (F12) for detailed error messages
2. Verify the cryptocurrency ID is valid
3. Ensure MarketData has entries for the selected cryptocurrency
4. Check backend logs for API errors

### Rate limiting from CoinGecko
- CoinGecko free API has rate limits (~10-50 calls/minute)
- Consider using an API key for higher limits
- Implement caching and request throttling
