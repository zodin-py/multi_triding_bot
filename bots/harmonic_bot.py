"""
Bot 4: Harmonic Patterns Bot
"""
import logging
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class HarmonicBot(BaseBot):
    """
    Trading bot based on Harmonic Patterns:
    - Gartley
    - Butterfly
    - Bat
    - Crab
    """

    def __init__(self, symbol: str, timeframe: str):
        super().__init__(symbol, timeframe, "HarmonicBot")

    def analyze(self, data: dict) -> dict:
        """
        Analyze harmonic patterns.

        Args:
            data: Market data with pattern information

        Returns:
            Trading signal dictionary
        """
        try:
            close_price = data.get("close", 0)
            pattern = data.get("harmonic_pattern", None)
            pattern_confidence = data.get("pattern_confidence", 0.0)
            completion_level = data.get("completion_level", 0.0)

            signal = "HOLD"
            strength = 0.0
            reason = "No harmonic pattern detected"

            if pattern and pattern_confidence > 0.7:
                if pattern == "GARTLEY" or pattern == "BUTTERFLY":
                    signal = "BUY"
                    strength = pattern_confidence
                    reason = f"{pattern} pattern at D point - reversal expected"

                elif pattern == "BAT" or pattern == "CRAB":
                    if completion_level > 0.95:
                        signal = "BUY"
                        strength = pattern_confidence * 0.95
                        reason = f"{pattern} pattern nearly complete - BUY setup"
                    else:
                        signal = "HOLD"
                        strength = pattern_confidence * 0.5
                        reason = f"{pattern} pattern forming - {completion_level*100:.1f}% complete"

            # Inverted patterns (sell signals)
            if pattern and pattern_confidence > 0.7:
                if pattern == "GARTLEY_INV" or pattern == "BUTTERFLY_INV":
                    signal = "SELL"
                    strength = pattern_confidence
                    reason = f"Inverted {pattern} pattern at D point - reversal expected"

            price_target = close_price * 1.10 if signal == "BUY" else close_price * 0.90
            stop_loss = close_price * 0.95 if signal == "BUY" else close_price * 1.05

            return {
                "signal": signal,
                "strength": min(strength, 1.0),
                "reason": reason,
                "price_target": price_target,
                "stop_loss": stop_loss,
            }

        except Exception as e:
            logger.error(f"Error in HarmonicBot.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
            }
