# Multi-Bot Trading System 🤖📈

Ein automatisiertes Trading-System mit mehreren unabhängigen Analyse-Bots, die ihre Signale aggregieren und Trades ausführen.

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [System-Architektur](#system-architektur)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [API-Referenz](#api-referenz)
- [Bots](#bots)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

✓ **5 unabhängige Trading Bots** - Jeder mit eigener Analyse-Strategie  
✓ **Signal-Aggregation** - Gewichtete Voting-System für Konsensentscheidungen  
✓ **Web-Dashboard** - Live-Überwachung aller Bot-Signale  
✓ **Alpaca Trading API Integration** - Paper & Live Trading Support  
✓ **Risk Management** - Automatische Stop-Loss und Take-Profit Berechnung  
✓ **Testnet-Modus** - Sicher testen ohne echte Geldverluste  
✓ **Umfassendes Logging** - Alle Aktionen werden protokolliert

---

## 🏗 System-Architektur

```
┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard (Port 5000)              │
│              Real-time Signal Visualization              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      Flask API                          │
│  /api/data  /api/signals  /api/execute  /api/trades     │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │DataManager   │ │ Aggregator   │ │TradeExecutor │
  │(Market Data) │ │ (Consensus)  │ │(Orders)      │
  └──────┬───────┘ └──────────────┘ └──────────────┘
         │
    ┌────▼────────────────────────────────────────────┐
    │         5 Independent Analysis Bots             │
    ├────────────────────────────────────────────────┤
    │ 1. Indicator Bot    - RSI, MACD, SMA           │
    │ 2. Support/Resist   - Level-basierte Analyse   │
    │ 3. SMC Bot          - Order Blocks, Liquidity  │
    │ 4. Harmonic Patterns- Pattern Recognition      │
    │ 5. Trend Bot        - Higher Highs/Lows        │
    └────────────────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │      Alpaca Trading API             │
    │  Paper Trading | Live Trading        │
    └─────────────────────────────────────┘
```

---

## 🚀 Installation

### 1. Voraussetzungen

- Python 3.8+
- Alpaca Trading Account (kostenlos für Paper Trading)
- Git (optional)

### 2. Repository klonen oder Dateien downloaden

```bash
cd d:\Triding_System\multi_bot_trading_system
```

### 3. Dependencies installieren

```powershell
pip install -r requirements.txt
```

**Wichtige Packages:**
- Flask 2.3.0 - Web Framework
- alpaca-trade-api 3.2.0 - Trading API
- pandas 2.0.0 - Datenanalyse
- numpy 1.24.0 - Numerische Operationen
- python-dotenv 1.0.0 - Umgebungsvariablen

### 4. Alpaca Account erstellen

1. Gehe zu [https://alpaca.markets](https://alpaca.markets)
2. Erstelle einen kostenlosen Paper Trading Account
3. Gehe zu Dashboard → API Keys
4. Kopiere `API Key` und `Secret Key`

### 5. .env Datei konfigurieren

Erstelle/bearbeite `d:\Triding_System\multi_bot_trading_system\.env`:

```env
ALPACA_API_KEY=dein_api_key_hier
ALPACA_SECRET_KEY=dein_secret_key_hier
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

> **Wichtig:** Verwende `paper-api.alpaca.markets` für Paper Trading, nicht `/v2`

---

## ⚙️ Konfiguration

### config.py anpassen

```python
# Trading-Symbole
DEFAULT_SYMBOL = "AAPL"        # Standardsymbol
DEFAULT_TIMEFRAME = "1h"        # 1m, 5m, 15m, 30m, 1h, 4h, 1d

# Daten
CANDLE_LIMIT = 100             # Anzahl der Kerzen zum Abrufen

# Risk Management
RISK_PERCENTAGE = 2.0          # Risk pro Trade (%)
STOP_LOSS_PERCENTAGE = 2.0     # Stop Loss Abstand (%)
TAKE_PROFIT_PERCENTAGE = 5.0   # Take Profit Abstand (%)

# Aggregator
SIGNAL_THRESHOLD = 0.6         # 60% Konsensschwelle
MIN_BOTS_AGREEMENT = 3         # Min. 3 Bots stimmen überein

# Server
HOST = "0.0.0.0"               # Localhost
PORT = 5000                    # Port für Dashboard
DEBUG = True                   # Debug-Modus
```

---

## 💡 Verwendung

### Option 1: Web-Dashboard (Empfohlen für visuelle Überwachung)

```powershell
# Terminal öffnen
cd d:\Triding_System\multi_bot_trading_system

# App starten
python app.py
```

Dann öffne im Browser:
```
http://localhost:5000
```

**Im Dashboard:**
1. Wähle ein Symbol (z.B. AAPL, MSFT, BTCUSD)
2. Wähle Timeframe (1h, 4h, 1d)
3. Drücke "Apply Configuration"
4. Drücke "Refresh Data"
5. Beobachte die Bot-Signale in Echtzeit

---

### Option 2: Command-Line Test (Schnelle Analyse)

```powershell
cd d:\Triding_System\multi_bot_trading_system

# Komplettes System testen
python main.py
```

**Ausgabe:**
- Account-Informationen (Equity, Cash)
- Bot-Signale für AAPL
- Bot-Signale für MSFT
- Aggregierte Ergebnisse
- Test-Trade (Testnet)

---

### Option 3: Alpaca-Verbindung testen

```powershell
cd d:\Triding_System\multi_bot_trading_system

# API-Verbindung prüfen
python test_alpaca_connection.py
```

**Überprüft:**
- ✓ API-Credentials
- ✓ Account-Status
- ✓ Verfügbare Positionen
- ✓ Order-Platzierung

---

## 📡 API-Referenz

### `/api/data` - Marktdaten abrufen

```bash
GET /api/data?symbol=AAPL&interval=1h&limit=100
```

**Response:**
```json
{
  "success": true,
  "symbol": "AAPL",
  "interval": "1h",
  "data": {
    "close": 150.25,
    "sma20": 149.80,
    "rsi": 65.5,
    "atr": 2.10,
    "support": 148.50,
    "resistance": 151.75,
    ...
  }
}
```

---

### `/api/signals` - Bot-Signale analysieren

```bash
POST /api/signals
Content-Type: application/json

{
  "market_data": {
    "close": 150.25,
    "sma20": 149.80,
    "rsi": 65.5,
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "bot_signals": {
    "indicator_bot": {
      "signal": "BUY",
      "strength": 0.75,
      "reason": "RSI oversold + MACD bullish"
    },
    ...
  },
  "aggregated_signal": {
    "signal": "BUY",
    "strength": 0.68,
    "consensus": {
      "buy": 0.65,
      "sell": 0.15,
      "hold": 0.20
    }
  }
}
```

---

### `/api/execute` - Trade ausführen

```bash
POST /api/execute
Content-Type: application/json

{
  "symbol": "AAPL",
  "signal": {
    "signal": "BUY",
    "strength": 0.68
  },
  "quantity": 1.0
}
```

---

### `/api/bots/status` - Bot-Status

```bash
GET /api/bots/status
```

---

### `/api/executor/trades` - Trade-History

```bash
GET /api/executor/trades?limit=50
```

---

## 🤖 Bots

### 1. **Indicator Bot** 📊
- **Strategie:** Technische Indikatoren
- **Verwendet:** RSI, MACD, SMA, ATR
- **Signal:** BUY wenn RSI < 30 + MACD bullish
- **Gewicht:** 20%

```python
from bots import IndicatorBot
bot = IndicatorBot("AAPL", "1h")
signal = bot.generate_signal(market_data)
```

---

### 2. **Support/Resistance Bot** 🔧
- **Strategie:** Preisniveaus
- **Verwendet:** Unterstützungs- und Widerstandslinien
- **Signal:** BUY wenn Preis nahe Support
- **Gewicht:** 20%

---

### 3. **Smart Money Bot (SMC)** 💡
- **Strategie:** Order Blocks & Liquidity
- **Verwendet:** Fair Value Gaps, Order Blocks
- **Signal:** BUY wenn Price nahe Order Block High
- **Gewicht:** 20%

---

### 4. **Harmonic Patterns Bot** 🎯
- **Strategie:** Geometrische Muster
- **Verwendet:** Fibonacci, Harmonic Patterns
- **Signal:** BUY wenn Pattern erkannt
- **Gewicht:** 20%

---

### 5. **Trend Bot** 📈
- **Strategie:** Trend-Richtung
- **Verwendet:** Higher Highs/Lows
- **Signal:** BUY im Uptrend
- **Gewicht:** 20%

---

## 📊 Dashboard Features

### Configuration Panel
- Symbol eingeben oder aus Presets wählen (BTC, ETH, AAPL, GOOGL, MSFT, TSLA)
- Timeframe auswählen (1m bis 1d)
- Candle Limit einstellen

### Live Signals
- Jeder Bot zeigt sein Signal + Stärke
- Strength-Bar für visuelle Übersicht
- Grund für das Signal anzeigen

### Aggregator Brain
- Finales Signal (BUY/SELL/HOLD)
- Konsens-Prozentsatz für jeden Signal-Typ
- Kombinierte Strength

### Statistics
- Total Trades
- Gewinn-Trades
- Win Rate
- Total P&L

---

## 🔧 Troubleshooting

### Problem: "unauthorized" Fehler

**Lösung:**
```
1. Prüfe .env Datei - API Keys müssen korrekt sein
2. .env muss im gleichen Ordner wie app.py sein
3. Starte App neu nach .env Änderungen
```

### Problem: Daten laden nicht

**Lösung:**
```
1. Prüfe internet-Verbindung
2. Alpaca API könnte offline sein
3. Symbol könnte nicht unterstützt werden
   - Nutze: AAPL, MSFT, GOOGL, TSLA, SPY
   - Nicht: KITE, BTCUSDT (nicht auf Alpaca)
```

### Problem: Dashboard zeigt keinen Status

**Lösung:**
```
1. Browser Console öffnen (F12)
2. Prüfe auf Fehler (rot)
3. Prüfe Network Tab für API-Responses
4. App-Terminal auf Fehler prüfen
```

### Problem: Trade wird nicht ausgeführt

**Lösung:**
```
1. Signal muss mindestens 50% Strength haben
2. Im Testnet-Modus simuliert (nicht echt)
3. Prüfe config.py - BINANCE_TESTNET = True
```

---

## 📝 Logging

Alle Ereignisse werden protokolliert in `trading.log`:

```
2026-04-19 14:23:45 - DataManager - INFO - DataManager initialized
2026-04-19 14:23:46 - IndicatorBot - INFO - BUY signal generated
2026-04-19 14:23:47 - AggregatorBrain - INFO - Aggregated signal: BUY
2026-04-19 14:23:48 - TradeExecutor - INFO - Trade executed
```

---

## 🎯 Häufige Workflows

### Workflow 1: Schneller Bot-Test

```powershell
python main.py
```

→ Testet automatisch AAPL und MSFT mit allen 5 Bots

---

### Workflow 2: Visuelles Monitoring

```powershell
python app.py
# Browser: http://localhost:5000
```

→ Wähle Symbole, sehe Live-Signale

---

### Workflow 3: API-Verbindung prüfen

```powershell
python test_alpaca_connection.py
```

→ Zeigt Account-Info, platziert Test-Order

---

## 📊 Performance Metrics

Nach Trades kannst du in `/api/executor/trades` sehen:

- **Win Rate:** % der profitablen Trades
- **Avg P&L:** Durchschnittlicher Gewinn/Verlust
- **Total P&L:** Gesamter Gewinn/Verlust
- **Active Trades:** Offene Positionen

---

## ⚠️ WICHTIG: Risk Management

**Vor Live Trading:**

1. **Starte mit TESTNET:**
   ```python
   BINANCE_TESTNET = True  # In config.py
   ```

2. **Setze angemessene Risk-Level:**
   ```python
   RISK_PERCENTAGE = 2.0  # 2% pro Trade
   STOP_LOSS_PERCENTAGE = 2.0
   TAKE_PROFIT_PERCENTAGE = 5.0
   ```

3. **Teste mit wenigen Symbolen:**
   - Nicht alle Symbole gleichzeitig
   - Beginne mit großen, liquiden Symbolen (AAPL, MSFT)

4. **Überwache regelmäßig:**
   - Dashboard mehrmals täglich prüfen
   - Log-Dateien reviewen
   - Performance analysieren

---

## 🤝 Support

**Probleme?**

1. Prüfe `trading.log` auf Fehler
2. Öffne Browser DevTools (F12) → Console
3. Teste `python test_alpaca_connection.py`
4. Prüfe config.py Settings

---

## 📄 Lizenz

Dieses Projekt ist für Bildungszwecke. Verwende nur mit vorsichtigem Risk Management.

---

**Version:** 1.0  
**Datum:** April 2026  
**Status:** Production Ready
