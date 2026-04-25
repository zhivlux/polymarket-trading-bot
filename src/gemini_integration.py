# src/gemini_integration.py
import google.generativeai as genai
from typing import Optional, Dict
from config import Config
from logging_utils import logger

class GeminiTradingAdvisor:
    """Use Gemini LLM for trading signals and analysis"""
    
    def __init__(self):
        try:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini model initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    def get_market_signal(self, market_name: str, market_data: Dict) -> Optional[str]:
        """Get trading signal from Gemini"""
        if not self.model:
            return None
        
        try:
            price = market_data.get('price', 0.5)
            bid_depth = market_data.get('bid_depth', 0)
            ask_depth = market_data.get('ask_depth', 0)
            volume_pressure = market_data.get('volume_pressure', 0)
            bid_ask_ratio = market_data.get('bid_ask_ratio', 0.5)
            
            prompt = f"""
            Analyze this market data and provide a SHORT trading signal (1-2 sentences max):
            
            Market: {market_name}
            Current Price: ${price:.4f}
            Bid Depth: {bid_depth:.2f}
            Ask Depth: {ask_depth:.2f}
            Volume Pressure: {volume_pressure:.3f} (positive = bullish, negative = bearish)
            Bid/Ask Ratio: {bid_ask_ratio:.3f} (>0.5 = more buys, <0.5 = more sells)
            
            Based on this data, should we BUY, SELL, or HOLD? Give confidence 0-100%.
            Keep response brief and actionable. Format: SIGNAL: [BUY/SELL/HOLD], Confidence: [0-100]%
            """
            
            response = self.model.generate_content(prompt)
            signal_text = response.text.strip()
            
            logger.info(f"📊 Gemini Signal: {signal_text}")
            return signal_text
        
        except Exception as e:
            logger.warning(f"⚠️ Gemini API error: {e}")
            return None
    
    def get_strategy_advice(self, wallet_stats: Dict) -> Optional[str]:
        """Get adaptive strategy advice from Gemini"""
        if not self.model:
            return None
        
        try:
            win_rate = wallet_stats.get('win_rate', 0)
            consecutive_losses = wallet_stats.get('consecutive_losses', 0)
            roi = wallet_stats.get('roi', 0)
            
            prompt = f"""
            Based on recent trading performance, provide brief strategy advice (2-3 sentences):
            
            Win Rate: {win_rate*100:.1f}%
            Consecutive Losses: {consecutive_losses}
            ROI: {roi*100:.2f}%
            
            What adjustments should be made to improve performance?
            Keep it concise and actionable.
            """
            
            response = self.model.generate_content(prompt)
            advice = response.text.strip()
            
            logger.info(f"🎯 Strategy Advice: {advice}")
            return advice
        
        except Exception as e:
            logger.warning(f"⚠️ Gemini API error: {e}")
            return None
    
    def summarize_daily_report(self, stats: Dict) -> Optional[str]:
        """Generate daily trading report"""
        if not self.model:
            return None
        
        try:
            prompt = f"""
            Create a BRIEF daily trading summary (3-4 sentences):
            
            Total Trades: {stats.get('total_trades', 0)}
            Win Rate: {stats.get('win_rate', 0)*100:.1f}%
            Total PnL: ${stats.get('total_pnl', 0):.2f}
            ROI: {stats.get('roi', 0)*100:.2f}%
            
            Focus on: performance, key patterns, next steps.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.warning(f"⚠️ Gemini API error: {e}")
            return None
