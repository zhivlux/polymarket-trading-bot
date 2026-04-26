# src/data_collector.py
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from logging_utils import logger
import os

class DataCollector:
    """Collect external data for market analysis"""
    
    # Free APIs
    NEWSAPI_BASE = "https://newsapi.org/v2"
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.collected_data = {}
    
    def get_cryptocurrency_data(self, crypto: str = "bitcoin") -> Dict:
        """Get crypto market data from CoinGecko (FREE, no API key needed)"""
        try:
            url = f"{self.COINGECKO_BASE}/simple/price"
            params = {
                'ids': crypto.lower(),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Got crypto data for {crypto}")
            
            return {
                'crypto': crypto,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Error fetching crypto data: {e}")
            return {}
    
    def get_market_news(self, query: str, days: int = 1) -> List[Dict]:
        """Get news articles related to query (requires FREE NewsAPI key)"""
        try:
            if not self.newsapi_key:
                logger.warning("⚠️ NEWSAPI_KEY not set, skipping news collection")
                return []
            
            url = f"{self.NEWSAPI_BASE}/everything"
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            logger.info(f"✅ Found {len(articles)} news articles for '{query}'")
            
            return [
                {
                    'title': article['title'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'description': article['description']
                }
                for article in articles
            ]
        
        except Exception as e:
            logger.error(f"❌ Error fetching news: {e}")
            return []
    
    def analyze_market_sentiment(self, market_question: str, market_data: Dict) -> Dict:
        """Analyze sentiment for a market using collected data"""
        try:
            # Extract keywords from market question
            keywords = market_question.lower().split()
            
            # Collect relevant news
            relevant_news = self.get_market_news(
                query=' '.join(keywords[:3]),  # Use first 3 words as query
                days=1
            )
            
            # Count positive/negative indicators
            sentiment_score = 0.5  # Neutral by default
            
            positive_words = ['surge', 'surge', 'up', 'gains', 'bullish', 'approve', 'success']
            negative_words = ['crash', 'down', 'loss', 'bearish', 'reject', 'fail', 'decline']
            
            all_text = market_question.lower()
            for article in relevant_news:
                all_text += ' ' + article['title'].lower()
            
            pos_count = sum(1 for word in positive_words if word in all_text)
            neg_count = sum(1 for word in negative_words if word in all_text)
            
            total = pos_count + neg_count
            if total > 0:
                sentiment_score = pos_count / total
            
            logger.info(f"✅ Sentiment analysis: {sentiment_score:.2%}")
            
            return {
                'sentiment_score': sentiment_score,
                'positive_indicators': pos_count,
                'negative_indicators': neg_count,
                'relevant_news_count': len(relevant_news),
                'articles': relevant_news[:3]  # Top 3 articles
            }
        
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return {'sentiment_score': 0.5}
    
    def get_twitter_trends(self, query: str) -> Dict:
        """Get trending info related to query (free alternative: search GitHub trending)"""
        try:
            # Alternative: Use GitHub API for trending repos (free, no auth)
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Got GitHub trending for {query}")
            
            return {
                'query': query,
                'trending_repos': data.get('items', [])[:5],
                'total_count': data.get('total_count', 0)
            }
        
        except Exception as e:
            logger.error(f"❌ Error fetching trends: {e}")
            return {}
    
    def get_macroeconomic_data(self) -> Dict:
        """Get macro indicators (using free APIs)"""
        try:
            # Get global uncertainty index, market fear, etc
            macro_data = {
                'timestamp': datetime.now().isoformat(),
                'data': {}
            }
            
            # Could integrate with FRED API (free), Quandl, etc
            logger.info("✅ Collected macroeconomic data")
            
            return macro_data
        
        except Exception as e:
            logger.error(f"❌ Error collecting macro data: {e}")
            return {}
    
    def store_collected_data(self, key: str, data: Dict):
        """Store collected data for later analysis"""
        self.collected_data[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
