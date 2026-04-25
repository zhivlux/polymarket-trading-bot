# src/config_template.py
"""
Default configuration template.
Real configuration loads from environment variables set in run.claw.cloud dashboard.
"""

import os
from dotenv import load_dotenv

# Load .env if it exists (for local development ONLY)
load_dotenv()

class Config:
    """Configuration - reads from environment variables"""
    
    # ===== API KEYS (SET IN DASHBOARD/ENV) =====
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    POLYMARKET_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    
    # ===== TRADING SETTINGS =====
    INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "1000"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3"))
    RISK_PERCENTAGE = float(os.getenv("RISK_PERCENTAGE", "0.02"))
    
    # ===== POLYMARKET SETTINGS =====
    POLYMARKET_MARKET_ID = os.getenv("POLYMARKET_MARKET_ID", "")
    POLYMARKET_NETWORK = os.getenv("POLYMARKET_NETWORK", "polygon-mainnet")
    
    # ===== DATABASE =====
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/polymarket_bot.db")
    
    # ===== LOGGING =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ===== SERVER =====
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # ===== PATHS =====
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    MODELS_DIR = os.getenv("MODELS_DIR", "./models")
    LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
    
    # ===== DEPLOYMENT MODE =====
    IS_PRODUCTION = os.getenv("IS_PRODUCTION", "False").lower() == "true"
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        errors = []
        
        if not Config.GOOGLE_API_KEY:
            errors.append("❌ GOOGLE_API_KEY not set")
        
        if not Config.POLYMARKET_PRIVATE_KEY:
            errors.append("❌ POLYMARKET_PRIVATE_KEY not set")
        
        if errors:
            print("\n".join(errors))
            print("\n⚠️  Missing required environment variables!")
            print("Please set them in your .env file (local) or dashboard (production)")
            raise ValueError("Configuration validation failed")
        
        print("✅ Configuration validated successfully")
    
    @staticmethod
    def create_directories():
        """Create necessary directories"""
        for directory in [Config.DATA_DIR, Config.MODELS_DIR, Config.LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)

# Initialize on import
Config.create_directories()
