# src/polymarket_client.py
import asyncio
from typing import Dict, Optional
from py_clob_client import ClobClient
import ccxt
from config import Config
from logging_utils import logger

class PolymarketDataFetcher:
    """Fetch data from Polymarket"""
    
    def __init__(self):
        try:
            self.clob_client = ClobClient(
                private_key=Config.POLYMARKET_PRIVATE_KEY,
                network=Config.POLYMARKET_NETWORK
            )
            logger.info("✅ Polymarket client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Polymarket client: {e}")
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
            if not self.clob_client:
                return None
            
            market_id = market_id or Config.POLYMARKET_MARKET_ID
            if not market_id:
                logger.error("❌ Market ID not provided")
                return None
            
            # Get orderbook
            orderbook = self.clob_client.get_orderbook(market_id)
            
            # Get market info
            market_info = self.clob_client.get_market(market_id)
            
            return {
                'market_id': market_id,
                'orderbook': orderbook,
                'market_info': market_info,
                'timestamp': None  # Will be set by caller
            }
        
        except Exception as e:
            logger.error(f"❌ Error fetching Polymarket data: {e}")
            return None
    
    def get_external_market_data(self) -> Dict:
        """Get external market data (BTC price, etc)"""
        data = {}
        
        try:
            if not self.exchange:
                return {'btc_price': 50000}
            
            # Get BTC/USDT
            btc_ticker = self.exchange.fetch_ticker('BTC/USDT')
            data['btc_price'] = btc_ticker['last']
            data['btc_volume'] = btc_ticker.get('quoteVolume', 0)
            
            logger.debug(f"✅ BTC Price: ${data['btc_price']:.2f}")
        
        except Exception as e:
            logger.warning(f"⚠️ Error fetching external data: {e}")
            data['btc_price'] = 50000
        
        return data
    
    def get_market_list(self) -> list:
        """Get list of available markets"""
        try:
            if not self.clob_client:
                return []
            
            markets = self.clob_client.get_markets()
            logger.info(f"✅ Found {len(markets)} markets")
            return markets
        
        except Exception as e:
            logger.error(f"❌ Error fetching markets: {e}")
            return []
