"""
Test Alpaca API Connection and Place Test Trade
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")
base_url = os.getenv("ALPACA_BASE_URL")

print("=" * 60)
print("ALPACA API CONNECTION TEST")
print("=" * 60)
print(f"API Key: {api_key[:10]}...")
print(f"Secret Key: {secret_key[:10]}...")
print(f"Base URL: {base_url}")
print()

try:
    from alpaca_trade_api import REST
    print("✓ alpaca_trade_api library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import alpaca_trade_api: {e}")
    print("Run: pip install alpaca-trade-api")
    sys.exit(1)

try:
    # Initialize Alpaca client
    client = REST(api_key, secret_key, base_url=base_url)
    print("✓ Alpaca client initialized")
    
    # Test connection - get account info
    account = client.get_account()
    print(f"✓ Connected to Alpaca!")
    print(f"  Account Status: {account.status}")
    print(f"  Equity: ${account.equity}")
    print(f"  Cash: ${account.cash}")
    print()
    
    # Check if account is trading enabled
    if account.trading_blocked:
        print("✗ Trading is blocked on this account")
        sys.exit(1)
    
    # Get existing positions
    positions = client.get_positions()
    print(f"Current Positions: {len(positions)}")
    for pos in positions:
        print(f"  - {pos.symbol}: {pos.qty} shares @ ${pos.current_price}")
    print()
    
    # Check if KITE is available
    print("Attempting to place a test BUY order for KITE...")
    try:
        # Place a market order (small quantity for testing)
        order = client.submit_order(
            symbol="KITE",
            qty=1,
            side="buy",
            type="market",
            time_in_force="gtc"
        )
        print(f"✓ ORDER PLACED SUCCESSFULLY!")
        print(f"  Order ID: {order.id}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Quantity: {order.qty}")
        print(f"  Side: {order.side}")
        print(f"  Status: {order.status}")
        print(f"  Type: {order.order_type}")
        print()
        
        # Get order details
        filled_order = client.get_order(order.id)
        print(f"Order Status Update:")
        print(f"  Status: {filled_order.status}")
        print(f"  Filled Qty: {filled_order.filled_qty}")
        print(f"  Filled Avg Price: {filled_order.filled_avg_price}")
        
    except Exception as e:
        print(f"✗ Error placing order: {e}")
        print(f"  Note: KITE might not be available for trading in Alpaca")
        print(f"  Common Alpaca symbols: AAPL, GOOGL, MSFT, TSLA, SPY, QQQ")
        
except Exception as e:
    print(f"✗ Connection Error: {e}")
    print("Check your API credentials in .env file")
    sys.exit(1)

print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
