"""
Hauptanwendung - Flask Web-Interface für das Multi-Bot Trading System
"""
import logging
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

import config
try:
    from alpaca_trade_api import REST
except ImportError:
    REST = None

from bots import (
    IndicatorBot,
    SRBot,
    SMCBot,
    HarmonicBot,
    TrendBot,
)
from aggregator import AggregatorBrain
from execution import TradeExecutor
from data import DataManager

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)

# Initialize Alpaca client and components
alpaca_client = None
if REST is not None:
    alpaca_client = REST(
        config.ALPACA_API_KEY,
        config.ALPACA_SECRET_KEY,
        base_url=config.ALPACA_BASE_URL,
    )

data_manager = DataManager(api_client=alpaca_client)

# Initialize all bots
bots = {
    "indicator_bot": IndicatorBot(config.DEFAULT_SYMBOL, config.DEFAULT_TIMEFRAME),
    "sr_bot": SRBot(config.DEFAULT_SYMBOL, config.DEFAULT_TIMEFRAME),
    "smc_bot": SMCBot(config.DEFAULT_SYMBOL, config.DEFAULT_TIMEFRAME),
    "harmonic_bot": HarmonicBot(config.DEFAULT_SYMBOL, config.DEFAULT_TIMEFRAME),
    "trend_bot": TrendBot(config.DEFAULT_SYMBOL, config.DEFAULT_TIMEFRAME),
}

# Initialize aggregator brain
aggregator = AggregatorBrain(
    bot_weights={
        "indicator_bot": 0.2,
        "sr_bot": 0.2,
        "smc_bot": 0.2,
        "harmonic_bot": 0.2,
        "trend_bot": 0.2,
    }
)

# Initialize executor
executor = TradeExecutor(api_client=alpaca_client, testnet=config.BINANCE_TESTNET)

logger.info("Multi-Bot Trading System initialized")


@app.route("/")
def dashboard():
    """Render the main dashboard."""
    return render_template("dashboard.html")


@app.route("/api/data", methods=["GET"])
def get_market_data():
    """Fetch and return current market data."""
    try:
        symbol = request.args.get("symbol", config.DEFAULT_SYMBOL)
        interval = request.args.get("interval", config.DEFAULT_TIMEFRAME)
        limit = request.args.get("limit", config.CANDLE_LIMIT, type=int)

        # Fetch OHLCV data
        klines = data_manager.fetch_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )

        if not klines:
            return jsonify({"error": "Failed to fetch data"}), 500

        # Parse data
        market_data = data_manager.parse_klines(klines)

        return jsonify({
            "success": True,
            "symbol": symbol,
            "interval": interval,
            "data": market_data,
        })

    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/signals", methods=["POST"])
def analyze_signals():
    """Analyze all bots and aggregate signals."""
    try:
        data = request.json or {}
        market_data = data.get("market_data", {})

        # Get signals from all bots
        bot_signals = {}
        for bot_name, bot in bots.items():
            if config.BOT_CONFIG.get(bot_name, {}).get("enabled", True):
                signal = bot.generate_signal(market_data)
                bot_signals[bot_name] = signal
                logger.info(f"{bot_name}: {signal.get('signal')} (strength: {signal.get('strength')})")

        # Aggregate signals
        aggregated_signal = aggregator.aggregate_signals(bot_signals)

        return jsonify({
            "success": True,
            "bot_signals": bot_signals,
            "aggregated_signal": aggregated_signal,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error analyzing signals: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/execute", methods=["POST"])
def execute_trade():
    """Execute a trade based on aggregated signal."""
    try:
        data = request.json or {}
        signal = data.get("signal", {})
        symbol = data.get("symbol", config.DEFAULT_SYMBOL)
        quantity = data.get("quantity", 1.0)

        # Execute trade
        trade = executor.execute_signal(signal, symbol, quantity)

        if trade:
            return jsonify({
                "success": True,
                "trade": trade,
                "message": f"Trade executed: {trade['side']} {trade['quantity']} {symbol}",
            })
        else:
            return jsonify({
                "success": False,
                "message": "Trade execution failed or skipped",
            })

    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/bots/status", methods=["GET"])
def get_bots_status():
    """Get status of all bots."""
    try:
        status = {
            bot_name: bot.get_status()
            for bot_name, bot in bots.items()
        }

        return jsonify({
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/aggregator/stats", methods=["GET"])
def get_aggregator_stats():
    """Get aggregator statistics."""
    try:
        stats = aggregator.get_stats()
        history = aggregator.get_signal_history(limit=10)

        return jsonify({
            "success": True,
            "stats": stats,
            "history": history,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error getting aggregator stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/executor/trades", methods=["GET"])
def get_trades():
    """Get trade history."""
    try:
        limit = request.args.get("limit", 50, type=int)
        trades = executor.get_trade_history(limit=limit)
        active_trades = executor.get_active_trades()
        stats = executor.get_statistics()

        return jsonify({
            "success": True,
            "active_trades": active_trades,
            "trade_history": trades,
            "statistics": stats,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error getting trades: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration."""
    return jsonify({
        "success": True,
        "config": {
            "symbol": config.DEFAULT_SYMBOL,
            "timeframe": config.DEFAULT_TIMEFRAME,
            "testnet": config.BINANCE_TESTNET,
            "risk_percentage": config.RISK_PERCENTAGE,
            "signal_threshold": config.SIGNAL_THRESHOLD,
            "bot_config": config.BOT_CONFIG,
        },
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info(f"Starting Multi-Bot Trading System on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
