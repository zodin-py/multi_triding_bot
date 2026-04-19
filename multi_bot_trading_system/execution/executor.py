"""
Trade Executor - Handles order execution
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TradeExecutor:
    """
    Executes trades based on aggregated signals from the brain.
    Manages order placement, risk management, and trade tracking.
    """

    def __init__(self, api_client=None, testnet: bool = True):
        """
        Initialize trade executor.

        Args:
            api_client: API client for order execution (e.g., Binance API)
            testnet: Whether to use testnet mode
        """
        self.api_client = api_client
        self.testnet = testnet
        self.active_trades = {}
        self.trade_history = []
        logger.info(f"Trade Executor initialized (testnet={testnet})")

    def execute_signal(
        self, signal: Dict[str, Any], symbol: str, quantity: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a trading signal.

        Args:
            signal: Trading signal from aggregator brain
            symbol: Trading pair
            quantity: Order quantity

        Returns:
            Order execution result
        """
        try:
            signal_type = signal.get("signal", "HOLD")

            if signal_type == "HOLD":
                logger.info(f"Signal is HOLD for {symbol}, skipping execution")
                return None

            if signal_type not in ["BUY", "SELL"]:
                logger.warning(f"Unknown signal type: {signal_type}")
                return None

            # Check signal strength threshold
            strength = signal.get("strength", 0)
            if strength < 0.5:
                logger.info(
                    f"Signal strength too low ({strength}) for {symbol}, skipping"
                )
                return None

            # Prepare trade
            trade = {
                "id": f"{symbol}_{datetime.now().timestamp()}",
                "symbol": symbol,
                "side": signal_type,
                "quantity": quantity,
                "entry_price": signal.get("price_target"),
                "stop_loss": signal.get("stop_loss"),
                "take_profit": signal.get("price_target"),
                "signal_strength": strength,
                "timestamp": datetime.now().isoformat(),
                "status": "PENDING",
            }

            # Execute order via Alpaca if available, otherwise simulate
            if self.api_client and hasattr(self.api_client, "submit_order"):
                try:
                    order = self.api_client.submit_order(
                        symbol=symbol,
                        qty=quantity,
                        side=signal_type.lower(),
                        type="market",
                        time_in_force="gtc",
                    )
                    trade["status"] = "SUBMITTED"
                    trade["order_id"] = getattr(order, "id", None)
                    entry_price = getattr(order, "filled_avg_price", None)
                    if entry_price is not None:
                        trade["entry_price"] = float(entry_price)
                    logger.info(
                        f"ORDER SUBMITTED: {signal_type} {quantity} {symbol} order_id={trade['order_id']}"
                    )
                except Exception as e:
                    logger.error(f"Error submitting Alpaca order: {str(e)}")
                    return None
            elif self.testnet:
                trade["status"] = "EXECUTED_TESTNET"
                logger.info(
                    f"TESTNET: {signal_type} {quantity} {symbol} at {trade['entry_price']}"
                )
            else:
                trade["status"] = "EXECUTED"
                logger.info(
                    f"LIVE: {signal_type} {quantity} {symbol} at {trade['entry_price']}"
                )

            self.active_trades[trade["id"]] = trade
            self.trade_history.append(trade)

            return trade

        except Exception as e:
            logger.error(f"Error executing signal: {str(e)}")
            return None

    def close_trade(self, trade_id: str, close_price: float) -> Optional[Dict]:
        """
        Close an active trade.

        Args:
            trade_id: Trade ID
            close_price: Closing price

        Returns:
            Trade closure information
        """
        try:
            if trade_id not in self.active_trades:
                logger.warning(f"Trade {trade_id} not found")
                return None

            trade = self.active_trades[trade_id]
            entry_price = trade.get("entry_price", 0)
            quantity = trade.get("quantity", 0)

            # Calculate P&L
            if trade["side"] == "BUY":
                pnl = (close_price - entry_price) * quantity
            else:
                pnl = (entry_price - close_price) * quantity

            pnl_pct = (pnl / (entry_price * quantity)) * 100 if entry_price else 0

            closed_trade = {
                **trade,
                "status": "CLOSED",
                "close_price": close_price,
                "pnl": pnl,
                "pnl_percentage": pnl_pct,
                "close_timestamp": datetime.now().isoformat(),
            }

            del self.active_trades[trade_id]
            self.trade_history.append(closed_trade)

            logger.info(
                f"Trade {trade_id} closed: PnL={pnl:.2f} ({pnl_pct:.2f}%)"
            )

            return closed_trade

        except Exception as e:
            logger.error(f"Error closing trade: {str(e)}")
            return None

    def get_active_trades(self) -> Dict:
        """Get all active trades."""
        return self.active_trades.copy()

    def get_trade_history(self, limit: int = 50) -> list:
        """Get trade history."""
        return self.trade_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate trading statistics."""
        closed_trades = [t for t in self.trade_history if t["status"] == "CLOSED"]

        if not closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
            }

        total_pnl = sum(t.get("pnl", 0) for t in closed_trades)
        winning_trades = sum(1 for t in closed_trades if t.get("pnl", 0) > 0)
        losing_trades = sum(1 for t in closed_trades if t.get("pnl", 0) < 0)

        return {
            "total_trades": len(closed_trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": winning_trades / len(closed_trades) if closed_trades else 0,
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / len(closed_trades) if closed_trades else 0,
        }
