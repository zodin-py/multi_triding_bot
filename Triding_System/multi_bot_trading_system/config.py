"""
Konfigurationsdatei für das Multi-Bot Trading System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

# Binance API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "your_api_key")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "your_api_secret")
BINANCE_TESTNET = True  # Set to False for live trading

# Alpaca API
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "your_alpaca_api_key")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "your_alpaca_secret_key")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Trading Configuration
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_TIMEFRAME = "1h"
CANDLE_LIMIT = 100

# Risk Management
RISK_PERCENTAGE = 2.0  # 2% risk per trade
STOP_LOSS_PERCENTAGE = 2.0
TAKE_PROFIT_PERCENTAGE = 5.0

# Bot Configuration
BOT_CONFIG = {
    "indicator_bot": {"enabled": True, "weight": 0.2},
    "sr_bot": {"enabled": True, "weight": 0.2},
    "smc_bot": {"enabled": True, "weight": 0.2},
    "harmonic_bot": {"enabled": True, "weight": 0.2},
    "trend_bot": {"enabled": True, "weight": 0.2},
}

# Aggregator Configuration
SIGNAL_THRESHOLD = 0.6  # 60% consensus required for trade
MIN_BOTS_AGREEMENT = 3  # At least 3 bots must agree

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "trading.log"
