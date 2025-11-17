#!/bin/bash
# Complete systematic fix for VPS

cd ~/apex_bot
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR

echo "Applying ALL fixes..."

# FIX 1: Router testnet bypass
sed -i '526a\        # Bypass for testnet - safe to trade!\n        if self.testnet:\n            lg.info("[router] Testnet mode - orders allowed")\n            return\n' router.py

# FIX 2: Scanner await fix
sed -i 's/tickers = await exchange.fetch_tickers()/tickers = await asyncio.to_thread(exchange.fetch_tickers)/' DYNAMIC_MARKET_SCANNER.py

# FIX 3: Execution data hub fix (if not done)
grep -q "recent_signals\[:20\]" EXECUTION_ORCHESTRATOR.py || sed -i 's/self.data_hub.get_signals(limit=20)/list(self.data_hub.recent_signals)[:20]/' EXECUTION_ORCHESTRATOR.py

# FIX 4: Route variable initialization
grep -q "route = None" EXECUTION_ORCHESTRATOR.py || sed -i '698a\            route = None' EXECUTION_ORCHESTRATOR.py

# FIX 5: Optimal variable (if exists)
sed -i 's/optimal.get/{"exchange": "bybit_testnet"}.get/g' INTELLIGENT_EXECUTION_ENGINE.py 2>/dev/null || true

# FIX 6: Router.ex calls
sed -i 's/self.exchange.fetch_ticker/self.exchange.ex.fetch_ticker if hasattr(self.exchange, "ex") else self.exchange.fetch_ticker/g' INTELLIGENT_EXECUTION_ENGINE.py
sed -i 's/self.exchange.fetch_balance/self.exchange.ex.fetch_balance/g' INTELLIGENT_EXECUTION_ENGINE.py
sed -i 's/self.exchange.create_market_buy_order/self.exchange.ex.create_market_buy_order/g' INTELLIGENT_EXECUTION_ENGINE.py  
sed -i 's/self.exchange.create_market_sell_order/self.exchange.ex.create_market_sell_order/g' INTELLIGENT_EXECUTION_ENGINE.py

# Export ALL keys
export BYBIT_TESTNET=true
export ENABLE_LIVE=true
export ALLOW_LIVE=true
export API_KEY=N8BMgWdfisCtkvfZk8
export API_SECRET=BIu7c65FQnDsd6kBmctU7gK9bBbzY15vi8oe
export MEXC_API_KEY=mx0vgl7ytNbnU44V5G
export MEXC_SECRET=68562da9963e4666a32a4a73cda61062
export GATE_API_KEY=eddc6317aa4f702302f69f875971fb03
export GATE_SECRET=af14b34a638f22b744cba0b7e13f5b88bb4622f3427d0999584a7a526493e8d8
export BINANCE_API_KEY=uxMw38StLFlWpqzi9OpFMMj4H7m3dWy8jnR2EAl2raL0n465jtxnlK9S2CYBflyf
export BINANCE_SECRET=k6dCSRQfCiNYHn3PjWtORNUKP69EvnbyAHmEIio9my8qRBHbzNHbXdWV2HilzRrO

# Clear cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ All fixes applied!"
echo "Starting bot..."

source apex_venv/bin/activate
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_FINAL_WORKING.log 2>&1 &

sleep 25
echo "Watching for results..."
tail -f apex_FINAL_WORKING.log | grep -E "orders allowed|Order ID|Balance.*8454|Profit|Total Trades.*[1-9]" --color=always
