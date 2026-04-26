# src/market_scorer.py
from typing import List, Dict, Tuple
from logging_utils import logger
import numpy as np

class MarketScorer:
    """Score and rank markets for trading opportunity"""
    
    def __init__(self):
        self.weights = {
            'liquidity': 0.25,
            'volatility': 0.20,
            'sentiment': 0.25,
            'trend': 0.15,
            'odds': 0.15
        }
    
    def score_market(
        self,
        market: Dict,
        sentiment_data: Dict = None,
        trend_data: Dict = None
    ) -> Tuple[float, Dict]:
        """
        Calculate overall score for a market (0-100)
        
        Args:
            market: Market data from Polymarket
            sentiment_data: Sentiment analysis results
            trend_data: Trend analysis results
        
        Returns:
            Tuple of (score, breakdown)
        """
        
        scores = {}
        
        # 1. Liquidity Score (volume-based)
        volume = float(market.get('volume', 0))
        liquidity_score = min(100, (volume / 100000) * 100)  # Normalize
        scores['liquidity'] = liquidity_score
        
        # 2. Volatility Score (price movement)
        price = float(market.get('price', 0.5))
        price_volatility = abs(price - 0.5)  # Distance from 0.5
        volatility_score = price_volatility * 100  # 0-100
        scores['volatility'] = volatility_score
        
        # 3. Sentiment Score
        sentiment_score = 50  # Default neutral
        if sentiment_data:
            sentiment_score = sentiment_data.get('sentiment_score', 0.5) * 100
        scores['sentiment'] = sentiment_score
        
        # 4. Trend Score
        trend_score = 50  # Default neutral
        if trend_data:
            trend_score = min(100, len(trend_data.get('articles', [])) * 20)
        scores['trend'] = trend_score
        
        # 5. Odds Score (how balanced are the probabilities)
        yes_price = float(market.get('price', 0.5))
        no_price = 1.0 - yes_price
        odds_balance = min(yes_price, no_price) * 200  # 0-100
        scores['odds'] = odds_balance
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        logger.info(f"🎯 Market Score: {total_score:.1f}/100 - {scores}")
        
        return total_score, scores
    
    def rank_markets(
        self,
        markets: List[Dict],
        sentiment_data_map: Dict[str, Dict] = None,
        trend_data_map: Dict[str, Dict] = None,
        top_n: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Rank multiple markets by score
        
        Returns:
            List of (market, score) tuples sorted by score desc
        """
        
        scored_markets = []
        
        for market in markets:
            market_id = market.get('id')
            sentiment_data = (sentiment_data_map or {}).get(market_id)
            trend_data = (trend_data_map or {}).get(market_id)
            
            score, breakdown = self.score_market(
                market,
                sentiment_data,
                trend_data
            )
            
            scored_markets.append((market, score, breakdown))
        
        # Sort by score descending
        ranked = sorted(scored_markets, key=lambda x: x[1], reverse=True)
        
        logger.info(f"✅ Top {top_n} markets ranked")
        
        return [(m, s) for m, s, _ in ranked[:top_n]]
    
    def get_best_market(
        self,
        markets: List[Dict],
        sentiment_data_map: Dict[str, Dict] = None,
        min_score: float = 60.0
    ) -> Dict:
        """Get the single best market above min_score threshold"""
        
        ranked = self.rank_markets(
            markets,
            sentiment_data_map=sentiment_data_map,
            top_n=1
        )
        
        if ranked and ranked[0][1] >= min_score:
            market, score = ranked[0]
            logger.info(f"✅ Best market selected with score {score:.1f}")
            return market
        
        logger.warning("⚠️ No market met minimum score threshold")
        return None
