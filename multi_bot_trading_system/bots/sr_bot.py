"""
Bot 2: Support and Resistance Bot
"""
import logging
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class SRBot(BaseBot):
    """
    Trading bot based on Support and Resistance levels
    """

    def __init__(self, symbol: str, timeframe: str):
        super().__init__(symbol, timeframe, "SRBot")

    def analyze(self, data: dict) -> dict:
        """
        Analyze support and resistance levels.

        Args:
            data: Market data with price history

        Returns:
            Trading signal dictionary
        """
        try:
            close_price = data.get("close", 0)
            support = data.get("support", close_price * 0.98)
            resistance = data.get("resistance", close_price * 1.02)
            recent_high = data.get("recent_high", close_price)
            recent_low = data.get("recent_low", close_price)

            signal = "HOLD"
            strength = 0.0
            reason = "Price neutral"

            # Check if price is near support
            support_distance = (close_price - support) / support if support != 0 else 0
            if support_distance < 0.01:  # Less than 1% above support
                signal = "BUY"
                strength = 0.75
                reason = "Price near support level"

            # Check if price is near resistance
            resistance_distance = (resistance - close_price) / resistance if resistance != 0 else 0
            if resistance_distance < 0.01:  # Less than 1% below resistance
                signal = "SELL"
                strength = 0.75
                reason = "Price near resistance level"

            # Check for breakouts
            if close_price > recent_high * 1.001:
                signal = "BUY"
                strength = 0.8
                reason = "Breakout above recent high"

            elif close_price < recent_low * 0.999:
                signal = "SELL"
                strength = 0.8
                reason = "Breakdown below recent low"

            return {
                "signal": signal,
                "strength": min(strength, 1.0),
                "reason": reason,
                "price_target": resistance if signal == "BUY" else support,
                "stop_loss": support if signal == "BUY" else resistance,
            }

        except Exception as e:
            logger.error(f"Error in SRBot.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
            }
