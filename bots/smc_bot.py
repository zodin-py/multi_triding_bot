"""
Bot 3: Smart Money Concepts (SMC) Bot
"""
import logging
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class SMCBot(BaseBot):
    """
    Trading bot based on Smart Money Concepts:
    - Order blocks
    - Liquidity levels
    - Fair value gaps
    """

    def __init__(self, symbol: str, timeframe: str):
        super().__init__(symbol, timeframe, "SMCBot")

    def analyze(self, data: dict) -> dict:
        """
        Analyze using Smart Money Concepts.

        Args:
            data: Market data with SMC indicators

        Returns:
            Trading signal dictionary
        """
        try:
            close_price = data.get("close", 0)
            order_block_high = data.get("order_block_high", close_price * 1.02)
            order_block_low = data.get("order_block_low", close_price * 0.98)
            liquidity_level = data.get("liquidity_level", close_price)
            fair_value_gap = data.get("fair_value_gap", 0)

            signal = "HOLD"
            strength = 0.0
            reason = "No clear SMC signals"

            # Analyze order blocks
            if close_price < order_block_low:
                signal = "BUY"
                strength = 0.7
                reason = "Price broke below order block - potential bounce"

            elif close_price > order_block_high:
                signal = "SELL"
                strength = 0.7
                reason = "Price broke above order block - potential rejection"

            # Analyze liquidity levels
            if abs(close_price - liquidity_level) < close_price * 0.005:
                if signal == "BUY":
                    strength = 0.85
                    reason += " + At liquidity level"
                elif signal == "SELL":
                    strength = 0.85
                    reason += " + At liquidity level"

            # Fair value gap analysis
            if fair_value_gap > 0 and close_price < liquidity_level:
                signal = "BUY"
                strength = 0.75
                reason = "Fair value gap detected - potential fill"

            elif fair_value_gap < 0 and close_price > liquidity_level:
                signal = "SELL"
                strength = 0.75
                reason = "Fair value gap detected - potential fill"

            return {
                "signal": signal,
                "strength": min(strength, 1.0),
                "reason": reason,
                "price_target": order_block_high if signal == "BUY" else order_block_low,
                "stop_loss": order_block_low if signal == "BUY" else order_block_high,
            }

        except Exception as e:
            logger.error(f"Error in SMCBot.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
            }
