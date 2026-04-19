"""
Bot 1: Technical Indicators (RSI, MACD)
Vereinfacht: Nur RSI und MACD Indikatoren
"""
import logging
from .base_bot import BaseBot

logger = logging.getLogger(__name__)


class IndicatorBot(BaseBot):
    """
    Trading bot based on two key technical indicators:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    """

    def __init__(self, symbol: str, timeframe: str):
        super().__init__(symbol, timeframe, "IndicatorBot")

    def _analyze_rsi(self, rsi: float) -> dict:
        """
        Analysiere RSI (Relative Strength Index).
        
        Args:
            rsi: RSI Wert (0-100)
            
        Returns:
            {'signal': str, 'strength': float, 'reason': str, 'value': float}
        """
        signal = "HOLD"
        strength = 0.0
        reason = "RSI neutral"

        if rsi < 30:
            signal = "BUY"
            strength = 0.7
            reason = "RSI oversold"
        elif rsi > 70:
            signal = "SELL"
            strength = 0.7
            reason = "RSI overbought"
        else:
            reason = "RSI neutral"
        
        logger.debug(f"RSI: {rsi:.1f} → {signal} (strength: {strength})")
        return {
            "signal": signal, 
            "strength": strength, 
            "reason": reason,
            "value": rsi
        }

    def _analyze_macd(self, macd: float, macd_signal: float) -> dict:
        """
        Analysiere MACD (Moving Average Convergence Divergence).
        
        Args:
            macd: MACD Linie
            macd_signal: Signal Linie
            
        Returns:
            {'signal': str, 'strength': float, 'reason': str, 'macd': float, 'signal': float}
        """
        signal = "HOLD"
        strength = 0.0
        reason = "MACD neutral"

        if macd > macd_signal:
            signal = "BUY"
            strength = 0.6
            reason = "MACD bullish"
        elif macd < macd_signal:
            signal = "SELL"
            strength = 0.6
            reason = "MACD bearish"
        
        logger.debug(f"MACD: {macd:.4f}, Signal: {macd_signal:.4f} → {signal}")
        return {
            "signal": signal, 
            "strength": strength, 
            "reason": reason,
            "macd_value": macd,
            "signal_value": macd_signal
        }

    def analyze(self, data: dict) -> dict:
        """
        Hauptanalysemethode - Analysiere RSI und MACD.

        Args:
            data: Market data mit Indikatoren

        Returns:
            Trading signal dictionary
        """
        try:
            # Extrahiere Daten
            close_price = data.get("close", 0)
            rsi = data.get("rsi", 50)
            macd = data.get("macd", 0)
            macd_signal = data.get("macd_signal", 0)

            logger.info(f"IndicatorBot analyzing {self.symbol} on {self.timeframe}")

            # Analysiere RSI und MACD
            rsi_result = self._analyze_rsi(rsi)
            macd_result = self._analyze_macd(macd, macd_signal)

            # Kombiniere Signale
            signals = [rsi_result["signal"], macd_result["signal"]]
            buy_count = signals.count("BUY")
            sell_count = signals.count("SELL")
            
            # Finales Signal
            if buy_count > sell_count:
                final_signal = "BUY"
                final_strength = (rsi_result["strength"] + macd_result["strength"]) / 2
            elif sell_count > buy_count:
                final_signal = "SELL"
                final_strength = (rsi_result["strength"] + macd_result["strength"]) / 2
            else:
                final_signal = "HOLD"
                final_strength = 0.3

            reason = f"RSI: {rsi_result['reason']} | MACD: {macd_result['reason']}"

            return {
                "signal": final_signal,
                "strength": min(final_strength, 1.0),
                "reason": reason,
                "price_target": close_price * 1.05 if final_signal == "BUY" else close_price * 0.95,
                "stop_loss": close_price * 0.98 if final_signal == "BUY" else close_price * 1.02,
                # Detaillierte Werte für HTML Anzeige
                "indicators": {
                    "rsi": {
                        "value": rsi,
                        "signal": rsi_result["signal"],
                        "reason": rsi_result["reason"]
                    },
                    "macd": {
                        "value": macd,
                        "signal_line": macd_signal,
                        "signal": macd_result["signal"],
                        "reason": macd_result["reason"]
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error in IndicatorBot.analyze(): {str(e)}")
            return {
                "signal": "HOLD",
                "strength": 0,
                "reason": f"Error: {str(e)}",
                "price_target": None,
                "stop_loss": None,
                "indicators": {}
            }
