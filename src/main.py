# src/main.py
import asyncio
import time
import numpy as np
import pickle
import os
from datetime import datetime
from typing import Dict
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ✅ CORRECT IMPORTS
from config_template import Config
from logging_utils import logger
from data_manager import DataManager
from polymarket_client import PolymarketDataFetcher
from feature_engineering import FeatureEngineer
from virtual_wallet import VirtualWallet
from models import ModelManager
from gemini_integration import GeminiTradingAdvisor

class PolyMarketAutoTradingBot:
    """Main Trading Bot"""
    
    def __init__(self):
        # Validate config (akan throw error jika ada yang missing)
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            if not Config.IS_PRODUCTION:
                logger.warning("⚠️  Running in demo mode without API keys")
                self.demo_mode = True
            else:
                raise
        
        self.data_manager = DataManager()
        self.data_fetcher = PolymarketDataFetcher()
        self.wallet = VirtualWallet(Config.INITIAL_BALANCE)
        self.model_manager = ModelManager()
        self.gemini_advisor = GeminiTradingAdvisor()
        self.feature_engineer = FeatureEngineer()
        
        self.iteration = 0
        self.market_id = Config.POLYMARKET_MARKET_ID
        
        logger.info("🚀 PolyMarket Trading Bot Initialized")
    
    def get_all_features(self) -> Dict:
        """Get combined features from all sources"""
        features = {}
        
        # Get Polymarket data
        poly_data = self.data_fetcher.get_polymarket_data(self.market_id)
        if poly_data:
            orderbook_features = self.feature_engineer.extract_orderbook_features(
                poly_data['orderbook']
            )
            features.update(orderbook_features)
        
        # Get external market data
        external_data = self.data_fetcher.get_external_market_data()
        external_features = self.feature_engineer.extract_external_features(external_data)
        features.update(external_features)
        
        # Add wallet state features
        stats = self.wallet.get_stats()
        features['consecutive_losses'] = float(stats['consecutive_losses'])
        features['roi'] = float(stats['roi'])
        
        return features
    
    def make_trading_decision(self, features: Dict, market_price: float) -> tuple:
        """Make trading decision based on models + LLM"""
        
        # Get ML prediction
        ml_confidence, model_used = self.model_manager.predict_ensemble(features)
        
        # Get Gemini LLM insight
        gemini_signal = self.gemini_advisor.get_market_signal(
            "PolyMarket",
            features
        )
        
        logger.info(f"🤖 ML Confidence: {ml_confidence:.2%} ({model_used})")
        logger.info(f"📊 Gemini Signal: {gemini_signal}")
        
        # Decision logic
        action = "HOLD"
        reason = ""
        
        # Check LLM signal
        gemini_buy = gemini_signal and "BUY" in gemini_signal.upper()
        gemini_sell = gemini_signal and "SELL" in gemini_signal.upper()
        
        # Combine ML + LLM
        if ml_confidence > Config.CONFIDENCE_THRESHOLD and gemini_buy:
            if self.wallet.consecutive_losses < Config.MAX_CONSECUTIVE_LOSSES:
                action = "BUY"
                reason = f"ML:{ml_confidence:.2%}+Gemini:BUY"
        
        elif ml_confidence < (1 - Config.CONFIDENCE_THRESHOLD) and gemini_sell:
            if self.wallet.positions:
                action = "SELL"
                reason = f"ML:{ml_confidence:.2%}+Gemini:SELL"
        
        # Adaptive: if too many losses, become more conservative
        if self.wallet.consecutive_losses >= Config.MAX_CONSECUTIVE_LOSSES:
            logger.warning(f"⚠️ Too many losses ({self.wallet.consecutive_losses}), reducing activity")
            action = "HOLD"
        
        return action, reason, ml_confidence
    
    def execute_trade(self, action: str, reason: str, market_price: float):
        """Execute trade"""
        
        if action == "BUY":
            quantity = 1.0
            success, msg = self.wallet.buy(
                'POLYMARKET_YES',
                quantity,
                market_price,
                reason=reason
            )
            if success:
                self.data_manager.insert_trade({
                    'side': 'BUY',
                    'quantity': quantity,
                    'entry_price': market_price,
                    'reason': reason
                })
        
        elif action == "SELL" and self.wallet.positions:
            quantity = 1.0
            success, msg = self.wallet.sell(
                'POLYMARKET_YES',
                quantity,
                market_price
            )
            if success:
                trade_record = self.wallet.trade_history[-1]
                self.data_manager.insert_trade({
                    'side': 'SELL',
                    'quantity': quantity,
                    'entry_price': trade_record.entry_price,
                    'exit_price': market_price,
                    'pnl': trade_record.pnl,
                    'outcome': trade_record.outcome
                })
                
                # Learn from trade outcome
                features = self.get_all_features()
                outcome = 1 if trade_record.pnl > 0 else 0
                self.model_manager.learn_from_trade(features, outcome)
    
    def run_iteration(self):
        """Run single trading iteration"""
        self.iteration += 1
        
        print(f"\n{'='*70}")
        print(f"ITERATION {self.iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        try:
            # Get features
            features = self.get_all_features()
            
            # Get current price
            poly_data = self.data_fetcher.get_polymarket_data(self.market_id)
            if not poly_data:
                logger.error("❌ Could not fetch market data")
                return
            
            market_price = poly_data['market_info'].get('price', 0.5)
            logger.info(f"💰 Current Price: ${market_price:.4f}")
            
            # Store market data
            self.data_manager.insert_market_data(self.market_id, features)
            
            # Make decision
            action, reason, confidence = self.make_trading_decision(features, market_price)
            logger.info(f"🎯 Decision: {action} - {reason}")
            
            # Execute
            if action != "HOLD":
                self.execute_trade(action, reason, market_price)
            
            # Print stats
            stats = self.wallet.get_stats()
            print(f"\n📊 WALLET STATS:")
            print(f"   Balance: ${stats['balance']:.2f}")
            print(f"   Total Trades: {stats['total_trades']}")
            print(f"   Win Rate: {stats['win_rate']*100:.1f}%")
            print(f"   Total PnL: ${stats['total_pnl']:.2f}")
            print(f"   ROI: {stats['roi']*100:.2f}%")
            print(f"   Consecutive Losses: {stats['consecutive_losses']}")
            
            # Get strategy advice every 10 iterations
            if self.iteration % 10 == 0:
                advice = self.gemini_advisor.get_strategy_advice(stats)
            
            # Save models periodically
            if self.iteration % 20 == 0:
                self.model_manager.save_models()
        
        except Exception as e:
            logger.error(f"❌ Error in iteration: {e}", exc_info=True)
    
    def run_paper_trading(self, iterations: int = 100, interval: int = 60):
        """Run paper trading loop"""
        logger.info(f"🏃 Starting paper trading for {iterations} iterations (interval: {interval}s)")
        
        try:
            for i in range(iterations):
                self.run_iteration()
                
                if i < iterations - 1:
                    logger.info(f"⏳ Waiting {interval} seconds before next iteration...")
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.warning("\n⏹️  Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        logger.info("🛑 Shutting down...")
        self.model_manager.save_models()
        
        # Print final report
        stats = self.wallet.get_stats()
        print(f"\n{'='*70}")
        print(f"FINAL REPORT")
        print(f"{'='*70}")
        print(f"Initial Balance: ${stats['initial_balance']:.2f}")
        print(f"Final Balance: ${stats['balance']:.2f}")
        print(f"Total PnL: ${stats['total_pnl']:.2f}")
        print(f"ROI: {stats['roi']*100:.2f}%")
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Win Rate: {stats['win_rate']*100:.1f}%")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    bot = PolyMarketAutoTradingBot()
    bot.run_paper_trading(iterations=100, interval=60)
