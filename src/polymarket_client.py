# src/polymarket_client.py
import asyncio
from typing import Dict, Optional
from config_template import Config
from logging_utils import logger
import ccxt

class PolymarketDataFetcher:
    """Fetch data from Polymarket"""
    
    def __init__(self):
        # Try to initialize Polymarket client (optional)
        try:
            if Config.POLYMARKET_PRIVATE_KEY and not Config.DEMO_MODE:
                from py_clob_client.client import ClobClient
                
                # Correct initialization for py-clob-client 0.34.6
                self.clob_client = ClobClient(
                    private_key=Config.POLYMARKET_PRIVATE_KEY,
                    chain_id=137  # Polygon mainnet
                )
                logger.info("✅ Polymarket client initialized")
            else:
                logger.info("⚠️  Polymarket client not initialized (demo mode or no private key)")
                self.clob_client = None
        
        except Exception as e:
            logger.warning(f"⚠️  Polymarket client initialization failed: {e}")
            logger.info("   Continuing in demo mode with mock data")
            self.clob_client = None
        
        # Binance for external market data
        try:
            self.exchange = ccxt.binance()
            logger.info("✅ Binance exchange initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance: {e}")
            self.exchange = None
    
    def get_polymarket_data(self, market_id: str = None) -> Optional[Dict]:
        """Get Polymarket market data"""
        
        try:
            if not self.clob_client or not market_id:
                # Return mock data for demo
                return self._get_mock_polymarket_data(market_id)
            
            # Real API call
            orderbook = self.clob_client.get_orderbook(market_id)
            market_info = self.clob_client.get_market(market_id)
            
            return {
                'market_id': market_id,
                'orderbook': orderbook,
                'market_info': market_info,
                'timestamp': None
            }
        
        except Exception as e:
            logger.warning(f"⚠️  Error fetching Polymarket data: {e}, using mock data")
            return self._get_mock_polymarket_data(market_id)
    
    def _get_mock_polymarket_data(self, market_id: str = None) -> Dict:
        """Generate realistic mock Polymarket data for demo mode"""
        
        import numpy as np
        from datetime import datetime
        
        # Simulate realistic orderbook
        price = np.random.uniform(0.3, 0.7)
        
        mock_data = {
            'market_id': market_id or 'demo-market-id',
            'orderbook': {
                'bids': [
                    (price - 0.01, np.random.uniform(100, 1000)),
                    (price - 0.02, np.random.uniform(50, 500)),
                    (price - 0.03, np.random.uniform(10, 100))
                ],
                'asks': [
                    (price + 0.01, np.random.uniform(100, 1000)),
                    (price + 0.02, np.random.uniform(50, 500)),
                    (price + 0.03, np.random.uniform(10, 100))
                ]
            },
            'market_info': {
                'question': 'Demo Market: Will BTC reach $50k by end of year?',
                'price': price,
                'volume': np.random.uniform(10000, 100000),
                'liquidity': np.random.uniform(5000, 50000)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return mock_data
    
    def get_external_market_data(self) -> Dict:
        """Get external market data (BTC price, etc)"""
        
        data = {}
        
        try:
            if not self.exchange:
                return self._get_mock_external_data()
            
            # Get BTC/USDT
            btc_ticker = self.exchange.fetch_ticker('BTC/USDT')
            data['btc_price'] = btc_ticker['last']
            data['btc_volume'] = btc_ticker.get('quoteVolume', 0)
            
            logger.debug(f"✅ BTC Price: ${data['btc_price']:.2f}")
        
        except Exception as e:
            logger.warning(f"⚠️  Error fetching external data: {e}, using mock data")
            return self._get_mock_external_data()
        
        return data
    
    def _get_mock_external_data(self) -> Dict:
        """Generate mock external market data"""
        import numpy as np
        
        return {
            'btc_price': np.random.uniform(45000, 55000),
            'btc_volume': np.random.uniform(10e9, 20e9)
        }
    
    def get_market_list(self) -> list:
        """Get list of available markets"""
        
        try:
            if not self.clob_client:
                # Return mock markets
                return [
                    {
                        'id': f'demo-market-{i}',
                        'question': f'Demo Market {i}: Will event X happen?',
                        'price': 0.5,
                        'volume': 10000
                    }
                    for i in range(5)
                ]
            
            markets = self.clob_client.get_markets()
            logger.info(f"✅ Found {len(markets)} markets")
            return markets
        
        except Exception as e:
            logger.warning(f"⚠️  Error fetching markets: {e}")
            # Return mock markets on error
            return self._get_mock_market_list()
    
    def _get_mock_market_list(self) -> list:
        """Generate mock market list"""
        return [
            {
                'id': f'demo-market-{i}',
                'question': f'Demo Market {i}',
                'price': 0.5,
                'volume': 10000
            }
            for i in range(10)
        ]
