# src/market_discovery.py
import requests
import pandas as pd
from typing import List, Dict, Optional
from logging_utils import logger
from datetime import datetime

class MarketDiscovery:
    """Discover and fetch available markets from Polymarket"""
    
    # Public Polymarket API endpoints (no auth needed)
    GAMMA_API_BASE = "https://gamma-api.polymarket.com"
    POLYMARKET_API_BASE = "https://api.polymarket.com"
    
    def __init__(self):
        self.markets_cache = {}
        self.last_fetch_time = None
    
    def get_all_active_markets(self, limit: int = 100) -> List[Dict]:
        """Fetch all active markets from Polymarket"""
        try:
            markets = []
            offset = 0
            
            while len(markets) < limit:
                url = f"{self.GAMMA_API_BASE}/markets"
                params = {
                    'active': 'true',
                    'limit': min(100, limit - len(markets)),
                    'offset': offset
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                markets.extend(data)
                offset += 100
                
                if len(data) < 100:
                    break
            
            logger.info(f"✅ Found {len(markets)} active markets")
            self.markets_cache = markets
            self.last_fetch_time = datetime.now()
            
            return markets[:limit]
        
        except Exception as e:
            logger.error(f"❌ Error fetching markets: {e}")
            return []
    
    def filter_markets_by_category(self, markets: List[Dict], category: str) -> List[Dict]:
        """Filter markets by category (e.g., 'politics', 'crypto', 'sports')"""
        try:
            filtered = []
            for market in markets:
                market_question = (market.get('question') or "").lower()
                if category.lower() in market_question:
                    filtered.append(market)
            
            logger.info(f"✅ Filtered {len(filtered)} markets for category: {category}")
            return filtered
        
        except Exception as e:
            logger.error(f"❌ Error filtering markets: {e}")
            return []
    
    def rank_markets_by_liquidity(self, markets: List[Dict], top_n: int = 10) -> List[Dict]:
        """Rank markets by liquidity (volume)"""
        try:
            # Sort by volume if available
            ranked = sorted(
                markets,
                key=lambda x: float(x.get('volume', 0)),
                reverse=True
            )
            
            result = ranked[:top_n]
            logger.info(f"✅ Top {len(result)} markets by liquidity")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error ranking markets: {e}")
            return markets[:top_n]
    
    def get_market_details(self, market_id: str) -> Optional[Dict]:
        """Get detailed info for a specific market"""
        try:
            url = f"{self.GAMMA_API_BASE}/markets/{market_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"❌ Error fetching market details for {market_id}: {e}")
            return None
    
    def find_trending_markets(self, markets: List[Dict], time_window: str = "24h") -> List[Dict]:
        """Find trending markets (highest volume change)"""
        try:
            # Sort by recent volume/activity
            trending = sorted(
                markets,
                key=lambda x: float(x.get('volume24h', 0) or 0),
                reverse=True
            )
            
            return trending[:10]
        
        except Exception as e:
            logger.error(f"❌ Error finding trending markets: {e}")
            return []
    
    def export_markets_to_csv(self, markets: List[Dict], filepath: str = "markets.csv"):
        """Export discovered markets to CSV"""
        try:
            if not markets:
                logger.warning("⚠️ No markets to export")
                return
            
            df = pd.DataFrame(markets)
            df.to_csv(filepath, index=False)
            logger.info(f"✅ Exported {len(markets)} markets to {filepath}")
        
        except Exception as e:
            logger.error(f"❌ Error exporting markets: {e}")
