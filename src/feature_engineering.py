# src/feature_engineering.py
import numpy as np
from typing import Dict
from logging_utils import logger

class FeatureEngineer:
    """Extract features from market data"""
    
    @staticmethod
    def extract_orderbook_features(orderbook: Dict) -> Dict:
        """Extract features from orderbook"""
        features = {}
        
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            # Depth
            features['bid_depth'] = sum([x[1] for x in bids]) if bids else 0
            features['ask_depth'] = sum([x[1] for x in asks]) if asks else 0
            
            # Best prices
            if bids and asks:
                best_bid = bids[0][0]
                best_ask = asks[0][0]
                features['spread'] = (best_ask - best_bid) / best_bid if best_bid > 0 else 0.01
                features['mid_price'] = (best_bid + best_ask) / 2
            else:
                features['spread'] = 0.01
                features['mid_price'] = 0.5
            
            # Imbalance
            total_depth = features['bid_depth'] + features['ask_depth']
            features['bid_ask_ratio'] = (
                features['bid_depth'] / total_depth if total_depth > 0 else 0.5
            )
            
            # Volume pressure
            features['volume_pressure'] = (
                features['bid_depth'] - features['ask_depth']
            ) / max(total_depth, 1)
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting orderbook features: {e}")
        
        return features
    
    @staticmethod
    def extract_market_features(market_data: Dict) -> Dict:
        """Extract features from market data"""
        features = {}
        
        try:
            # Price momentum (simplified)
            if 'price_history' in market_data:
                prices = market_data['price_history']
                if len(prices) >= 2:
                    features['price_momentum'] = (
                        (prices[-1] - prices[-2]) / prices[-2]
                    ) if prices[-2] > 0 else 0
            
            # Volatility
            if 'price_history' in market_data and len(market_data['price_history']) > 1:
                prices = np.array(market_data['price_history'][-20:])
                features['volatility'] = np.std(prices) if len(prices) > 1 else 0
            else:
                features['volatility'] = 0
            
            # Volume
            features['volume'] = market_data.get('volume', 0)
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting market features: {e}")
        
        return features
    
    @staticmethod
    def extract_external_features(external_data: Dict) -> Dict:
        """Extract features from external sources (BTC price, etc)"""
        features = {}
        
        try:
            # Bitcoin correlation
            btc_price = external_data.get('btc_price', 50000)
            features['btc_correlation'] = btc_price / 50000
            
            # Bitcoin volatility
            btc_volatility = external_data.get('btc_volatility', 0.02)
            features['market_volatility_external'] = btc_volatility
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting external features: {e}")
        
        return features
    
    @staticmethod
    def combine_features(orderbook_feat: Dict, market_feat: Dict, external_feat: Dict) -> Dict:
        """Combine all features"""
        combined = {
            **orderbook_feat,
            **market_feat,
            **external_feat
        }
        
        # Ensure all features are floats and finite
        for key in combined:
            try:
                val = float(combined[key])
                combined[key] = val if np.isfinite(val) else 0.0
            except:
                combined[key] = 0.0
        
        return combined
