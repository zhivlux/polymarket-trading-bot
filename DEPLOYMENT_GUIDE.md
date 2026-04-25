# Deployment Guide untuk run.claw.cloud

## 🔑 Setup Environment Variables

### Langkah 1: Di run.claw.cloud Dashboard

1. **Buka project kamu**
2. **Go to Settings → Environment Variables**
3. **Add semua variables ini:**

```env
# REQUIRED - API KEYS
GOOGLE_API_KEY=your_actual_gemini_api_key_here
POLYMARKET_PRIVATE_KEY=your_actual_polymarket_private_key_here

# OPTIONAL - External APIs
BINANCE_API_KEY=optional_binance_api_key
BINANCE_API_SECRET=optional_binance_secret

# TRADING CONFIGURATION
INITIAL_BALANCE=1000
CONFIDENCE_THRESHOLD=0.65
MAX_CONSECUTIVE_LOSSES=3
RISK_PERCENTAGE=0.02

# POLYMARKET
POLYMARKET_MARKET_ID=your_market_id_here
POLYMARKET_NETWORK=polygon-mainnet

# SERVER
PORT=8000
HOST=0.0.0.0
DEBUG=False
IS_PRODUCTION=True
LOG_LEVEL=INFO

# PATHS (akan dibuat otomatis)
DATABASE_PATH=./data/polymarket_bot.db
DATA_DIR=./data
MODELS_DIR=./models
LOGS_DIR=./logs
