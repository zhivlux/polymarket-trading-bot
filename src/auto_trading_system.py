# src/auto_trading_system.py
import os
from typing import List, Dict, Optional
from datetime import datetime
from logging_utils import logger

from market_discovery import MarketDiscovery
from data_collector import DataCollector
from market_scorer import MarketScorer
from scheduler import TaskScheduler
from polymarket_client import PolymarketDataFetcher
from gemini_integration import GeminiTradingAdvisor
from virtual_wallet import VirtualWallet
from models import ModelManager
from data_manager import DataManager
from feature_engineering import FeatureEngineer
from config_template import Config

class AutoTradingSystem:
    """Fully automated trading system with market discovery & data collection"""
    
    def __init__(self):
        logger.info("🚀 Initializing Automated Trading System...")
        
        # Core components
        self.market_discovery = MarketDiscovery()
        self.data_collector = DataCollector()
        self.market_scorer = MarketScorer()
        self.scheduler = TaskScheduler()
        
        # Trading components
        self.data_fetcher = PolymarketDataFetcher()
        self.gemini_advisor = GeminiTradingAdvisor()
        self.wallet = VirtualWallet(Config.INITIAL_BALANCE)
        self.model_manager = ModelManager()
        self.data_manager = DataManager()
        self.feature_engineer = FeatureEngineer()
        
        # State
        self.available_markets: List[Dict] = []
        self.selected_market: Optional[Dict] = None
        self.market_sentiment_cache: Dict = {}
        self.iteration = 0
        
        logger.info("✅ Auto Trading System initialized")
    
    def discover_markets(self):
        """Task: Discover and filter available markets"""
        try:
            logger.info("🔍 Discovering markets...")
            
            # Get all active markets
            markets = self.market_discovery.get_all_active_markets(limit=50)
            
            # Filter by category (optional - you can set via env var)
            category = os.getenv("MARKET_CATEGORY", "")
            if category:
                markets = self.market_discovery.filter_markets_by_category(markets, category)
            
            # Rank by liquidity
            markets = self.market_discovery.rank_markets_by_liquidity(markets, top_n=20)
            
            self.available_markets = markets
            logger.info(f"📊 Found {len(markets)} markets to analyze")
            
        except Exception as e:
            logger.error(f"❌ Error discovering markets: {e}", exc_info=True)
    
    def collect_market_data(self):
        """Task: Collect external data for markets"""
        try:
            logger.info("📡 Collecting market data...")
            
            # Get crypto data
            crypto_data = self.data_collector.get_cryptocurrency_data("bitcoin")
            
            # Get macro data
            macro_data = self.data_collector.get_macroeconomic_data()
            
            # Analyze sentiment for top markets
            for market in self.available_markets[:10]:
                market_id = market.get('id')
                question = market.get('question', '')
                
                sentiment = self.data_collector.analyze_market_sentiment(
                    question,
                    market
                )
                
                self.market_sentiment_cache[market_id] = sentiment
            
            logger.info("✅ Market data collected")
            
        except Exception as e:
            logger.error(f"❌ Error collecting data: {e}", exc_info=True)
    
    def score_and_select_market(self):
        """Task: Score markets and select best one"""
        try:
            logger.info("🎯 Scoring markets...")
            
            if not self.available_markets:
                logger.warning("⚠️ No markets available")
                return
            
            # Score all markets
            ranked = self.market_scorer.rank_markets(
                self.available_markets,
                sentiment_data_map=self.market_sentiment_cache,
                top_n=5
            )
            
            if ranked:
                best_market, score = ranked[0]
                self.selected_market = best_market
                
                logger.info(f"🏆 Selected market: {best_market.get('question', 'Unknown')}")
                logger.info(f"   Score: {score:.1f}/100")
                logger.info(f"   ID: {best_market.get('id')}")
                logger.info(f"   Price: ${best_market.get('price', 0):.4f}")
                logger.info(f"   Volume: ${best_market.get('volume', 0):.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error scoring markets: {e}", exc_info=True)
    
    def run_trading_iteration(self):
        """Main trading iteration with selected market"""
        try:
            if not self.selected_market:
                logger.warning("⚠️ No market selected for trading")
                return
            
            self.iteration += 1
            market_id = self.selected_market.get('id')
            
            print(f"\n{'='*70}")
            print(f"TRADING ITERATION {self.iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Market: {self.selected_market.get('question', 'Unknown')}")
            print(f"{'='*70}\n")
            
            # Get market orderbook
            orderbook = self.data_fetcher.clob_client.get_orderbook(market_id)
            
            # Extract features
            orderbook_features = self.feature_engineer.extract_orderbook_features(orderbook)
            external_features = self.feature_engineer.extract_external_features(
                self.data_collector.get_cryptocurrency_data("bitcoin")
            )
            sentiment_features = {
                'sentiment': self.market_sentiment_cache.get(
                    market_id, {}
                ).get('sentiment_score', 0.5)
            }
            
            all_features = {**orderbook_features, **external_features, **sentiment_features}
            
            # Get ML prediction
            ml_confidence, model_used = self.model_manager.predict_ensemble(all_features)
            
            # Get Gemini signal
            market_price = self.selected_market.get('price', 0.5)
            gemini_signal = self.gemini_advisor.get_market_signal(
                self.selected_market.get('question', ''),
                all_features
            )
            
            logger.info(f"🤖 ML: {ml_confidence:.2%} | 📊 Gemini: {gemini_signal}")
            
            # Make decision
            action = self._make_decision(ml_confidence, gemini_signal)
            logger.info(f"🎯 Action: {action}")
            
            # Print wallet stats
            stats = self.wallet.get_stats()
            print(f"\n📊 WALLET STATS:")
            print(f"   Balance: ${stats['balance']:.2f}")
            print(f"   Trades: {stats['total_trades']} (Win: {stats['win_rate']*100:.1f}%)")
            print(f"   PnL: ${stats['total_pnl']:.2f} ({stats['roi']*100:.2f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error in trading iteration: {e}", exc_info=True)
    
    def _make_decision(self, ml_confidence: float, gemini_signal: str) -> str:
        """Make trading decision from ML + LLM"""
        
        gemini_buy = gemini_signal and "BUY" in gemini_signal.upper()
        gemini_sell = gemini_signal and "SELL" in gemini_signal.upper()
        
        if ml_confidence > Config.CONFIDENCE_THRESHOLD and gemini_buy:
            if self.wallet.consecutive_losses < Config.MAX_CONSECUTIVE_LOSSES:
                return "BUY"
        
        elif ml_confidence < (1 - Config.CONFIDENCE_THRESHOLD) and gemini_sell:
            if self.wallet.positions:
                return "SELL"
        
        return "HOLD"
    
    def start_auto_trading(self, discovery_interval: int = 60, trading_interval: int = 30):
        """Start fully automated trading system"""
        
        logger.info(f"🚀 Starting automated trading system")
        logger.info(f"   Market discovery: every {discovery_interval}s")
        logger.info(f"   Trading iteration: every {trading_interval}s")
        
        # Schedule tasks
        self.scheduler.add_interval_job(
            self.discover_markets,
            minutes=discovery_interval // 60,
            job_id="discover_markets"
        )
        
        self.scheduler.add_interval_job(
            self.collect_market_data,
            minutes=discovery_interval // 60,
            job_id="collect_market_data"
        )
        
        self.scheduler.add_interval_job(
            self.score_and_select_market,
            minutes=discovery_interval // 60,
            job_id="score_and_select_market"
        )
        
        self.scheduler.add_interval_job(
            self.run_trading_iteration,
            minutes=trading_interval // 60,
            job_id="run_trading_iteration"
        )
        
        # Start scheduler
        self.scheduler.start()
        self.scheduler.list_jobs()
        
        # Run initial discovery
        self.discover_markets()
        self.collect_market_data()
        self.score_and_select_market()
        
        logger.info("✅ Auto trading system running!")
        
        # Keep running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("⏹️ Auto trading system stopped")
            self.scheduler.stop()
