# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management"""
    
    # API Keys (SECURE!)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    POLYMARKET_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    
    # Trading Settings
    INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "1000"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3"))
    RISK_PERCENTAGE = float(os.getenv("RISK_PERCENTAGE", "0.02"))
    
    # Polymarket
    POLYMARKET_MARKET_ID = os.getenv("POLYMARKET_MARKET_ID", "")
    POLYMARKET_NETWORK = os.getenv("POLYMARKET_NETWORK", "polygon-mainnet")
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/polymarket_bot.db")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Server
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Paths
    DATA_DIR = "./data"
    MODELS_DIR = "./models"
    LOGS_DIR = "./logs"
    
    @staticmethod
    def validate():
        """Validate critical config"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("❌ GOOGLE_API_KEY not set in .env")
        if not Config.POLYMARKET_PRIVATE_KEY:
            raise ValueError("❌ POLYMARKET_PRIVATE_KEY not set in .env")
        print("✅ Configuration validated")

# Create necessary directories
os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs(Config.MODELS_DIR, exist_ok=True)
os.makedirs(Config.LOGS_DIR, exist_ok=True)
