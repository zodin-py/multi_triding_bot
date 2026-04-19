"""
Data Manager - Fetches and manages market data from Binance
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages market data from Binance API.
    Fetches OHLCV data, indicators, and market information.
    """

    def __init__(self, api_client=None):
        """
        Initialize data manager.

        Args:
            api_client: Binance API client (optional)
        """
        self.api_client = api_client
        self.cache = {}
        logger.info("DataManager initialized")

    def fetch_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100
    ) -> Optional[List[List[Any]]]:
        """
        Fetch candlestick data from the configured market data API.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1h', '4h')
            limit: Number of candles to fetch

        Returns:
            List of OHLCV candles
        """
        try:
            cache_key = f"{symbol}_{interval}_{limit}"

            if cache_key in self.cache:
                return self.cache[cache_key]

            if self.api_client:
                try:
                    if hasattr(self.api_client, "get_klines"):
                        klines = self.api_client.get_klines(
                            symbol=symbol, interval=interval, limit=limit
                        )
                    elif hasattr(self.api_client, "get_bars"):
                        klines = self._fetch_alpaca_klines(symbol, interval, limit)
                    else:
                        logger.warning(
                            f"API client does not support kline or bar fetching for {symbol}"
                        )
                        klines = self._generate_dummy_klines(limit)
                except Exception as e:
                    logger.warning(
                        f"API fetch failed for {symbol}: {str(e)} - using dummy data"
                    )
                    klines = self._generate_dummy_klines(limit)
            else:
                logger.warning(f"No API client available, returning dummy data for {symbol}")
                klines = self._generate_dummy_klines(limit)

            self.cache[cache_key] = klines
            return klines

        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {str(e)}")
            return None

    def parse_klines(self, klines: List[List[Any]]) -> Dict[str, Any]:
        """
        Parse OHLCV data into a structured format.

        Args:
            klines: Raw kline data from API

        Returns:
            Dictionary with parsed OHLCV data
        """
        if not klines:
            return self._create_empty_data()

        try:
            # Extract latest candle
            latest = klines[-1]
            open_price = float(latest[1])
            high_price = float(latest[2])
            low_price = float(latest[3])
            close_price = float(latest[4])
            volume = float(latest[5])

            # Calculate indicators
            all_closes = [float(k[4]) for k in klines]
            sma20 = self._calculate_sma(all_closes, 20)
            sma50 = self._calculate_sma(all_closes, 50)
            rsi = self._calculate_rsi(all_closes, 14)
            atr = self._calculate_atr(klines, 14)

            # Support and Resistance
            high_prices = [float(k[2]) for k in klines]
            low_prices = [float(k[3]) for k in klines]
            support = min(low_prices[-10:]) if len(low_prices) >= 10 else min(low_prices)
            resistance = max(high_prices[-10:]) if len(high_prices) >= 10 else max(high_prices)

            return {
                "timestamp": datetime.now().isoformat(),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "sma20": sma20,
                "sma50": sma50,
                "rsi": rsi,
                "atr": atr,
                "support": support,
                "resistance": resistance,
                "recent_high": max(high_prices[-5:]) if len(high_prices) >= 5 else high_price,
                "recent_low": min(low_prices[-5:]) if len(low_prices) >= 5 else low_price,
                "avg_price": sum(all_closes[-20:]) / min(20, len(all_closes)),
                "macd": 0,  # Placeholder
                "macd_signal": 0,  # Placeholder
                "order_block_high": resistance,
                "order_block_low": support,
                "liquidity_level": (support + resistance) / 2,
                "fair_value_gap": 0,
                "harmonic_pattern": None,
                "pattern_confidence": 0,
                "completion_level": 0,
                "trend": "NEUTRAL",
                "trend_strength": 0.5,
                "higher_highs": False,
                "lower_lows": False,
                "higher_lows": False,
                "lower_highs": False,
            }

        except Exception as e:
            logger.error(f"Error parsing klines: {str(e)}")
            return self._create_empty_data()

    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50  # Default neutral value

        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(self, klines: List[List[Any]], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(klines) < 2:
            return 0

        true_ranges = []
        for i in range(1, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            prev_close = float(klines[i - 1][4])

            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)

        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges)

        return sum(true_ranges[-period:]) / period

    def _fetch_alpaca_klines(
        self, symbol: str, interval: str, limit: int
    ) -> List[List[Any]]:
        """Fetch OHLCV bars from Alpaca and convert to kline format."""
        timeframe = self._get_alpaca_timeframe(interval)
        bars = self.api_client.get_bars(symbol, timeframe, limit=limit)
        return self._convert_alpaca_bars_to_klines(bars)

    def _get_alpaca_timeframe(self, interval: str) -> str:
        """Convert Binance-style interval to Alpaca timeframe string."""
        mapping = {
            "1m": "1Min",
            "5m": "5Min",
            "15m": "15Min",
            "30m": "30Min",
            "1h": "1Hour",
            "2h": "2Hour",
            "4h": "4Hour",
            "1d": "1Day",
        }
        if interval in mapping:
            return mapping[interval]
        if interval.endswith("m"):
            return f"{interval[:-1]}Min"
        if interval.endswith("h"):
            return f"{interval[:-1]}Hour"
        if interval.endswith("d"):
            return f"{interval[:-1]}Day"
        return interval

    def _convert_alpaca_bars_to_klines(self, bars: Any) -> List[List[Any]]:
        """Convert Alpaca bar objects to OHLCV klines."""
        klines = []
        if hasattr(bars, "df"):
            import pandas as pd

            df = bars.df
            for timestamp, row in df.iterrows():
                timestamp_ms = int(pd.to_datetime(timestamp).timestamp() * 1000)
                klines.append(
                    [
                        timestamp_ms,
                        float(row["open"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["close"]),
                        float(row["volume"]),
                    ]
                )
            return klines

        for bar in bars:
            timestamp = getattr(bar, "t", None) or getattr(bar, "timestamp", None) or getattr(bar, "time", None)
            if hasattr(timestamp, "timestamp"):
                timestamp_ms = int(timestamp.timestamp() * 1000)
            else:
                timestamp_ms = int(timestamp)

            open_price = float(getattr(bar, "o", getattr(bar, "open", 0)))
            high_price = float(getattr(bar, "h", getattr(bar, "high", 0)))
            low_price = float(getattr(bar, "l", getattr(bar, "low", 0)))
            close_price = float(getattr(bar, "c", getattr(bar, "close", 0)))
            volume = float(getattr(bar, "v", getattr(bar, "volume", 0)))

            klines.append(
                [timestamp_ms, open_price, high_price, low_price, close_price, volume]
            )

        return klines

    def _generate_dummy_klines(self, limit: int) -> List[List[Any]]:
        """Generate dummy candlestick data for testing."""
        import time
        import random

        klines = []
        base_price = 100.0
        timestamp = int(time.time() * 1000) - (limit * 3600000)

        for i in range(limit):
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + random.uniform(-1, 1)
            high_price = max(open_price, close_price) + random.uniform(0, 1)
            low_price = min(open_price, close_price) - random.uniform(0, 1)
            volume = random.uniform(1000, 5000)

            klines.append(
                [timestamp, open_price, high_price, low_price, close_price, volume]
            )

            timestamp += 3600000
            base_price = close_price

        return klines

    def _create_empty_data(self) -> Dict[str, Any]:
        """Create empty data structure."""
        return {
            "timestamp": datetime.now().isoformat(),
            "open": 0,
            "high": 0,
            "low": 0,
            "close": 0,
            "volume": 0,
            "sma20": 0,
            "sma50": 0,
            "rsi": 50,
            "atr": 0,
            "support": 0,
            "resistance": 0,
            "recent_high": 0,
            "recent_low": 0,
            "avg_price": 0,
            "macd": 0,
            "macd_signal": 0,
            "order_block_high": 0,
            "order_block_low": 0,
            "liquidity_level": 0,
            "fair_value_gap": 0,
            "harmonic_pattern": None,
            "pattern_confidence": 0,
            "completion_level": 0,
            "trend": "NEUTRAL",
            "trend_strength": 0,
            "higher_highs": False,
            "lower_lows": False,
            "higher_lows": False,
            "lower_highs": False,
        }
