"""
Bot 5: Trend and Market Structure Bot
"""
import logging
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class TrendBot(BaseBot):
    """
    Trading bot based on Trend Analysis and Market Structure:
    - Trend direction
    - Higher highs/lows (uptrend)
    - Lower highs/lows (downtrend)
    - Trend changes
    """

    def __init__(self, symbol: str, timeframe: str):
        super().__init__(symbol, timeframe, "TrendBot")

    def analyze(self, data: dict) -> dict:
        """
        Analyze trend and market structure.

        Args:
            data: Market data with trend information

        Returns:
            Trading signal dictionary
        """
        try:
            close_price = data.get("close", 0)
            trend = data.get("trend", "NEUTRAL")  # UPTREND, DOWNTREND, NEUTRAL
            trend_strength = data.get("trend_strength", 0.0)  # 0-1
            higher_highs = data.get("higher_highs", False)
            lower_lows = data.get("lower_lows", False)
            higher_lows = data.get("higher_lows", False)
            lower_highs = data.get("lower_highs", False)

            signal = "HOLD"
            strength = 0.0
            reason = "Trend neutral"

            if trend == "UPTREND":
                if higher_highs and higher_lows:
                    signal = "BUY"
                    strength = min(trend_strength, 1.0)
                    reason = "Strong uptrend with higher highs and lows"
                elif higher_highs:
                    signal = "BUY"
                    strength = trend_strength * 0.8
                    reason = "Uptrend with higher highs"

            elif trend == "DOWNTREND":
                if lower_highs and lower_lows:
                    signal = "SELL"
                    strength = min(trend_strength, 1.0)
                    reason = "Strong downtrend with lower highs and lows"
                elif lower_highs:
                    signal = "SELL"
                    strength = trend_strength * 0.8
                    reason = "Downtrend with lower highs"

            else:  # NEUTRAL
                if higher_lows and close_price > data.get("recent_high", close_price) * 0.99:
                    signal = "BUY"
                    strength = 0.6
                    reason = "Potential trend reversal to uptrend"

                elif lower_highs and close_price < data.get("recent_low", close_price) * 1.01:
                    signal = "SELL"
                    strength = 0.6
                    reason = "Potential trend reversal to downtrend"

            avg_price = data.get("avg_price", close_price)
            price_target = avg_price * 1.05 if signal == "BUY" else avg_price * 0.95
            stop_loss = avg_price * 0.97 if signal == "BUY" else avg_price * 1.03

            return {
                "signal": signal,
                "strength": min(strength, 1.0),
                "reason": reason,
                "price_target": price_target,
                "stop_loss": stop_loss,
            }

        except Exception as e:
            logger.error(f"Error in TrendBot.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
            }
