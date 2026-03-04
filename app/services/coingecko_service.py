"""
CoinGecko API Service
Fetches cryptocurrency market data from CoinGecko API and upserts to database
"""

from pycoingecko import CoinGeckoAPI
from app.models import db, Cryptocurrency, MarketData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

cg = CoinGeckoAPI()


def update_market_data(limit=100, vs_currency='usd'):
    """
    Fetch cryptocurrency market data from CoinGecko API and upsert to database
    
    Args:
        limit (int): Number of cryptocurrencies to fetch (max 250 per request)
        vs_currency (str): Target currency
    
    Returns:
        dict: Status and update information
    """
    try:
        total_updated = 0
        pages_needed = (limit + 249) // 250  # CoinGecko max per_page=250
        
        for page in range(1, pages_needed + 1):
            per_page = min(250, limit - (page - 1) * 250)
            data = cg.get_coins_markets(
                vs_currency=vs_currency,
                order='market_cap_desc',
                per_page=per_page,
                page=page,
                sparkline=False,
                locale='en',
                price_change_percentage='7d'
            )
            
            if not data:
                continue
                
            for item in data:
                try:
                    # Find or create Cryptocurrency
                    crypto = Cryptocurrency.query.filter_by(symbol=item['symbol'].upper()).first()
                    if not crypto:
                        crypto = Cryptocurrency(
                            symbol=item['symbol'].upper(),
                            description=item['name'],
                            image=item.get('image'),
                            is_active=True
                        )
                        db.session.add(crypto)
                        db.session.flush()
                    
                    # Update ATH if necessary
                    new_ath = item.get('ath')
                    if new_ath and (not crypto.ath or new_ath > crypto.ath):
                        crypto.ath = new_ath
                        crypto.ath_date = datetime.fromisoformat(item['ath_date'].replace('Z', '+00:00'))
                    
                    # Update supplies
                    crypto.circulating_supply = item.get('circulating_supply')
                    crypto.total_supply = item.get('total_supply')
                    
                    # Get OHLC data from CoinGecko
                    ohlc_data = get_ohlc_data(crypto)
                    open_price = ohlc_data['open'] if ohlc_data else item.get('current_price')
                    close_price = item.get('current_price')
                    
                    # Create new MarketData entry
                    market_data = MarketData(
                        crypto_id=crypto.id,
                        timestamp=datetime.utcnow(),
                        price=item.get('current_price'),
                        open=open_price,
                        high=item.get('high_24h'),
                        low=item.get('low_24h'),
                        close=close_price,
                        volume=item.get('total_volume'),
                        market_cap=item.get('market_cap'),
                        change_24h=item.get('price_change_percentage_24h'),
                        change_7d=item.get('price_change_percentage_7d_in_currency')
                    )
                    db.session.add(market_data)
                    
                    total_updated += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {item.get('id')}: {str(e)}")
                    continue
            
            db.session.commit()
        
        return {
            "status": "success",
            "message": f"Updated market data for {total_updated} cryptocurrencies",
            "total_updated": total_updated
        }
    
    except Exception as e:
        logger.error(f"Error updating market data: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "total_updated": 0
        }


def get_ohlc_data(crypto):
    """
    Fetch OHLC data for a cryptocurrency from CoinGecko
    
    Args:
        crypto: Cryptocurrency object
    
    Returns:
        dict: OHLC data or None if not available
    """
    try:
        # Get OHLC data (only available for pro users, may return limited data for free tier)
        ohlc_list = cg.get_coin_ohlc_by_dates(
            id=crypto.description.lower(),
            vs_currency='usd',
            days=7
        )
        
        if not ohlc_list or len(ohlc_list) == 0:
            return None
        
        # Get the most recent OHLC data
        latest_ohlc = ohlc_list[-1]  # [timestamp, open, high, low, close]
        
        return {
            'open': latest_ohlc[1],
            'high': latest_ohlc[2],
            'low': latest_ohlc[3],
            'close': latest_ohlc[4]
        }
    except Exception as e:
        logger.warning(f"Could not fetch OHLC data for {crypto.symbol}: {str(e)}")
        return None


def search_cryptos(query, limit=10):
    """
    Search cryptocurrencies by symbol or name
    
    Args:
        query (str): Search query
        limit (int): Max results to return
    
    Returns:
        list: List of matching cryptocurrencies with latest data
    """
    search_term = f"%{query.lower()}%"
    cryptos = Cryptocurrency.query.filter(
        db.or_(
            Cryptocurrency.symbol.ilike(search_term),
            Cryptocurrency.description.ilike(search_term)
        )
    ).filter_by(is_active=True).limit(limit).all()
    
    results = []
    for crypto in cryptos:
        latest_md = MarketData.query.filter_by(crypto_id=crypto.id).order_by(
            MarketData.timestamp.desc()
        ).first()
        
        result = {
            "id": crypto.id,
            "symbol": crypto.symbol,
            "name": crypto.description,
            "image": crypto.image,
            "current_price": float(latest_md.price) if latest_md else None,
            "market_cap_rank": None  # Can compute if needed
        }
        results.append(result)
    
    return results


def get_crypto_data(crypto_id):
    """
    Get specific cryptocurrency data with latest market info
    
    Args:
        crypto_id (int): Cryptocurrency ID
    
    Returns:
        dict: Cryptocurrency data or None if not found
    """
    crypto = Cryptocurrency.query.get(crypto_id)
    if not crypto:
        return None
    
    latest_md = MarketData.query.filter_by(crypto_id=crypto_id).order_by(
        MarketData.timestamp.desc()
    ).first()
    
    return {
        "id": crypto.id,
        "symbol": crypto.symbol,
        "name": crypto.description,
        "image": crypto.image,
        "current_price": float(latest_md.price) if latest_md else None,
        "market_cap": float(latest_md.market_cap) if latest_md else None,
        "total_volume": float(latest_md.volume) if latest_md else None,
        "high_24h": float(latest_md.high) if latest_md else None,
        "low_24h": float(latest_md.low) if latest_md else None,
        "price_change_24h": float(latest_md.change_24h) if latest_md else None,
        "price_change_percentage_24h": float(latest_md.change_24h) if latest_md else None,
        "circulating_supply": float(crypto.circulating_supply) if crypto.circulating_supply else None,
        "total_supply": float(crypto.total_supply) if crypto.total_supply else None,
        "ath": float(crypto.ath) if crypto.ath else None,
        "ath_date": crypto.ath_date.isoformat() if crypto.ath_date else None,
        "last_updated": latest_md.timestamp.isoformat() if latest_md else None
    }


def get_top_gainers(limit=10):
    """
    Get top gaining cryptocurrencies based on latest 24h change
    
    Args:
        limit (int): Max results to return
    
    Returns:
        list: Top gaining cryptocurrencies
    """
    # Get latest for each crypto
    subquery = db.session.query(
        MarketData.crypto_id,
        db.func.max(MarketData.timestamp).label('max_timestamp')
    ).group_by(MarketData.crypto_id).subquery()

    query = db.session.query(MarketData, Cryptocurrency).join(
        subquery,
        db.and_(
            MarketData.crypto_id == subquery.c.crypto_id,
            MarketData.timestamp == subquery.c.max_timestamp
        )
    ).join(
        Cryptocurrency,
        MarketData.crypto_id == Cryptocurrency.id
    ).filter(
        MarketData.change_24h.isnot(None),
        Cryptocurrency.is_active == True
    ).order_by(
        MarketData.change_24h.desc()
    ).limit(limit)

    results = []
    for md, crypto in query.all():
        results.append({
            "id": crypto.id,
            "symbol": crypto.symbol,
            "name": crypto.description,
            "current_price": float(md.price),
            "price_change_percentage_24h": float(md.change_24h)
        })
    
    return results


def get_top_losers(limit=10):
    """
    Get top losing cryptocurrencies based on latest 24h change
    
    Args:
        limit (int): Max results to return
    
    Returns:
        list: Top losing cryptocurrencies
    """
    # Get latest for each crypto
    subquery = db.session.query(
        MarketData.crypto_id,
        db.func.max(MarketData.timestamp).label('max_timestamp')
    ).group_by(MarketData.crypto_id).subquery()

    query = db.session.query(MarketData, Cryptocurrency).join(
        subquery,
        db.and_(
            MarketData.crypto_id == subquery.c.crypto_id,
            MarketData.timestamp == subquery.c.max_timestamp
        )
    ).join(
        Cryptocurrency,
        MarketData.crypto_id == Cryptocurrency.id
    ).filter(
        MarketData.change_24h.isnot(None),
        Cryptocurrency.is_active == True
    ).order_by(
        MarketData.change_24h.asc()
    ).limit(limit)

    results = []
    for md, crypto in query.all():
        results.append({
            "id": crypto.id,
            "symbol": crypto.symbol,
            "name": crypto.description,
            "current_price": float(md.price),
            "price_change_percentage_24h": float(md.change_24h)
        })
    
    return results