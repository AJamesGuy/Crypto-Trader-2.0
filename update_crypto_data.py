"""
Script to initialize and update cryptocurrency data from CoinGecko
Run this with: python update_crypto_data.py
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.services.coingecko_service import update_market_data


def main():
    """Main function to update cryptocurrency data"""
    print("=" * 60)
    print("CryptoTemple - CoinGecko Data Update")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create Flask app context
    app = create_app('DevelopmentConfig')
    
    with app.app_context():
        try:
            print("Fetching top 200 cryptocurrencies from CoinGecko...")
            print()
            
            # Update market data for top 200 cryptocurrencies
            result = update_market_data(limit=200, vs_currency='usd')
            
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            
            if result['status'] == 'success':
                print(f"Total Updated: {result['total_updated']}")
                print()
                print("✓ Cryptocurrency data successfully updated!")
            else:
                print()
                print("✗ Error updating cryptocurrency data")
                return 1
        
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
