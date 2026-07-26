import re

# Read the file
with open('ANTI_CLOCKWISE_TRADING_ENGINE.py', 'r') as f:
    content = f.read()

# 1. Add imports if missing
if "import ccxt" not in content:
    content = "import ccxt\nimport numpy as np\n" + content

# 2. Replace _fetch_market_data method
new_method = '''    async def _fetch_market_data(self, pair: str) -> Optional[Dict]:
        """
        Fetch REAL market data using CCXT
        """
        try:
            # Initialize exchange (lightweight for fetching)
            if not hasattr(self, '_ccxt_exchange'):
                self._ccxt_exchange = ccxt.bybit({'options': {'defaultType': 'spot'}})
            
            # Fetch ticker and ohlcv
            ticker = self._ccxt_exchange.fetch_ticker(pair)
            ohlcv = self._ccxt_exchange.fetch_ohlcv(pair, '1h', limit=24)
            
            if not ticker or not ohlcv:
                return None
                
            # Calculate basic metrics
            closes = [c[4] for c in ohlcv]
            current_price = ticker['last']
            price_change_24h = ticker['percentage']
            volume_24h = ticker['quoteVolume']
            
            # Simple RSI logic
            delta = np.diff(closes)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = np.mean(gain[-14:]) if len(gain) > 0 else 0
            avg_loss = np.mean(loss[-14:]) if len(loss) > 0 else 0
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            # Momentum
            momentum = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
            
            return {
                'pair': pair,
                'rsi': rsi,
                'momentum': momentum * 100,
                'price_change_24h': price_change_24h or 0,
                'trend_strength': 0.8 if abs(momentum) > 0.02 else 0.2,
                'volume_ratio': 1.2, # Placeholder for volume avg
                'correlation_score': 0.5,
                'divergence_pct': 0,
                'volatility': (max(closes) - min(closes)) / min(closes),
                'volume_spike': volume_24h > 1000000,
                'recent_direction': 1 if price_change_24h > 0 else -1,
                'long_short_ratio': 1.0, # Needs futures API
                'fear_greed': 50, # Needs external API
                'social_sentiment': 0,
                'breakout': abs(price_change_24h) > 5,
                'breakout_direction': 'up' if price_change_24h > 0 else 'down',
                'distance_from_breakout': 0
            }
        except Exception as e:
            print(f"Error fetching data for {pair}: {e}")
            return None
'''

# Regex to replace the method
# We look for "async def _fetch_market_data" until the next "def" or class end
pattern = r"async def _fetch_market_data\(self, pair: str\) -> Optional\[Dict\]:.*?return \{.*?\}"
# This regex is tricky for multi-line. Better to just replace the header and known random block.

if "import random" in content and "random.uniform" in content:
    # Manual replacement since we know the content exactly from previous `cat`
    # We will just rewrite the file content if we find the placeholder comment
    if "# Placeholder: Generate mock data" in content:
        # Find start of method
        start_idx = content.find("async def _fetch_market_data")
        # Find end of method (next class or method)
        end_idx = content.find("class QuantumTimeReversalEngine")
        if start_idx != -1 and end_idx != -1:
             content = content[:start_idx] + new_method + "\n\n\n" + content[end_idx:]
             
             with open('ANTI_CLOCKWISE_TRADING_ENGINE.py', 'w') as f:
                 f.write(content)
             print("[OK] Replaced mock data with CCXT fetcher in ANTI_CLOCKWISE_TRADING_ENGINE.py")
        else:
             print("  Could not locate method boundaries")
    else:
        print("ℹ️  Placeholder comment not found, maybe already fixed?")
else:
    print("ℹ️  Random module not found, maybe already fixed?")
