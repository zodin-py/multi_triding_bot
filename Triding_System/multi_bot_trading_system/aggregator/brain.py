"""
Aggregator Brain - Combines signals from all bots
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AggregatorBrain:
    """
    Aggregates signals from multiple trading bots.
    Uses weighted voting to determine final trading signal.
    """

    def __init__(self, bot_weights: Dict[str, float] = None):
        """
        Initialize the aggregator brain.

        Args:
            bot_weights: Dictionary with bot names and their weights
        """
        self.bot_weights = bot_weights or {}
        self.signal_history = []
        logger.info("Aggregator Brain initialized")

    def aggregate_signals(self, bot_signals: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Aggregate signals from multiple bots.

        Args:
            bot_signals: Dictionary with bot names as keys and signal dicts as values

        Returns:
            Aggregated signal dictionary with consensus decision
        """
        try:
            if not bot_signals:
                return self._create_empty_signal("No bot signals received")

            # Calculate weighted consensus
            buy_votes = 0
            sell_votes = 0
            hold_votes = 0
            total_weight = 0
            reasons = []
            price_targets = []
            stop_losses = []

            for bot_name, signal in bot_signals.items():
                weight = self.bot_weights.get(bot_name, 1.0 / len(bot_signals))
                signal_type = signal.get("signal", "HOLD")
                strength = signal.get("strength", 0)
                weighted_strength = strength * weight

                if signal_type == "BUY":
                    buy_votes += weighted_strength
                elif signal_type == "SELL":
                    sell_votes += weighted_strength
                else:
                    hold_votes += weighted_strength

                total_weight += weight
                reasons.append(f"{bot_name}: {signal.get('reason', 'N/A')}")

                if signal.get("price_target"):
                    price_targets.append(signal["price_target"])
                if signal.get("stop_loss"):
                    stop_losses.append(signal["stop_loss"])

            # Normalize votes
            if total_weight > 0:
                buy_consensus = buy_votes / total_weight
                sell_consensus = sell_votes / total_weight
                hold_consensus = hold_votes / total_weight
            else:
                return self._create_empty_signal("No valid weights")

            # Determine final signal
            max_consensus = max(buy_consensus, sell_consensus, hold_consensus)

            if max_consensus == buy_consensus and buy_consensus > 0.3:
                final_signal = "BUY"
                final_strength = buy_consensus
            elif max_consensus == sell_consensus and sell_consensus > 0.3:
                final_signal = "SELL"
                final_strength = sell_consensus
            else:
                final_signal = "HOLD"
                final_strength = hold_consensus

            # Calculate average price targets and stop losses
            avg_price_target = sum(price_targets) / len(price_targets) if price_targets else None
            avg_stop_loss = sum(stop_losses) / len(stop_losses) if stop_losses else None

            aggregated_signal = {
                "signal": final_signal,
                "strength": min(final_strength, 1.0),
                "consensus": {
                    "buy": buy_consensus,
                    "sell": sell_consensus,
                    "hold": hold_consensus,
                },
                "reason": f"Aggregated from {len(bot_signals)} bots",
                "bot_reasons": reasons,
                "price_target": avg_price_target,
                "stop_loss": avg_stop_loss,
                "timestamp": datetime.now().isoformat(),
                "num_bots": len(bot_signals),
            }

            self.signal_history.append(aggregated_signal)
            logger.info(
                f"Aggregated signal: {final_signal} (strength: {final_strength:.2f})"
            )

            return aggregated_signal

        except Exception as e:
            logger.error(f"Error in aggregate_signals: {str(e)}")
            return self._create_empty_signal(f"Error: {str(e)}")

    def _create_empty_signal(self, reason: str) -> Dict[str, Any]:
        """Create an empty/hold signal."""
        return {
            "signal": "HOLD",
            "strength": 0,
            "consensus": {"buy": 0, "sell": 0, "hold": 1.0},
            "reason": reason,
            "bot_reasons": [],
            "price_target": None,
            "stop_loss": None,
            "timestamp": datetime.now().isoformat(),
            "num_bots": 0,
        }

    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """Get recent signal history."""
        return self.signal_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregator statistics."""
        if not self.signal_history:
            return {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "hold_signals": 0,
                "avg_strength": 0,
            }

        signals = self.signal_history
        buy_count = sum(1 for s in signals if s["signal"] == "BUY")
        sell_count = sum(1 for s in signals if s["signal"] == "SELL")
        hold_count = sum(1 for s in signals if s["signal"] == "HOLD")
        avg_strength = sum(s["strength"] for s in signals) / len(signals)

        return {
            "total_signals": len(signals),
            "buy_signals": buy_count,
            "sell_signals": sell_count,
            "hold_signals": hold_count,
            "avg_strength": avg_strength,
        }
