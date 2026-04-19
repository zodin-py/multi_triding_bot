"""
Basisklasse für alle Trading Bots
"""
from abc import ABC, abstractmethod
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    """Abstrakte Basisklasse für alle Trading Bots"""

    def __init__(self, symbol: str, timeframe: str, name: str):
        """
        Initialize the base bot.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Candle timeframe (e.g., '1h', '4h')
            name: Name of the bot
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.name = name
        self.last_signal = None
        self.last_update = None
        logger.info(f"Initialized {self.name} for {symbol} ({timeframe})")

    @abstractmethod
    def analyze(self, data: dict) -> dict:
        """
        Analyze market data and generate trading signal.

        Args:
            data: Dictionary containing OHLCV data

        Returns:
            Dictionary with signal information:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'strength': float (0-1),
                'reason': str,
                'price_target': float,
                'stop_loss': float
            }
        """
        pass

    def generate_signal(self, data: dict) -> dict:
        """
        Generate trading signal from market data.

        Args:
            data: Market data dictionary

        Returns:
            Signal dictionary
        """
        try:
            signal = self.analyze(data)
            self.last_signal = signal
            self.last_update = datetime.now()
            return signal
        except Exception as e:
            logger.error(f"Error in {self.name}.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
            }

    def get_status(self) -> dict:
        """Get bot status information."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "last_signal": self.last_signal,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }
