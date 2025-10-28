# 🎯 MICRO WALLET - Proper Systematic Integration

## Current Problem
MICRO is getting signals but executing blindly without:
1. ❌ Stop loss / Take profit targets
2. ❌ Entry timing validation
3. ❌ Exit condition monitoring
4. ❌ Position management per timeframe
5. ❌ Profit confirmation before close

## What Other Engines Do RIGHT

### 1. Steady Profit Extractor (STEADY_PROFIT_EXTRACTOR.py)
```python
async def analyze_signal_for_extraction(signal):
    # ✅ Validates confidence >= 70%
    # ✅ Checks if pair is fast-moving
    # ✅ Calculates position size based on balance
    # ✅ Sets stop_loss and take_profit targets
    # ✅ Calculates expected_profit
    # ✅ Only executes if profit >= minimum
    
    extraction_trade = {
        'symbol': symbol,
        'side': side,
        'entry_price': price,
        'stop_loss': price * (1 - 0.008),  # 0.8% stop
        'take_profit': price * (1 + 0.012),  # 1.2% profit
        'expected_profit': position_size * 0.012,
        'confidence': confidence
    }
    return extraction_trade
```

### 2. Execution Orchestrator (EXECUTION_ORCHESTRATOR.py)
```python
# ✅ Smart Position Sizing
- Uses Kelly Criterion
- Adjusts for confidence (higher conf = bigger size)
- Adjusts for volatility
- Aggressive mode for 85%+ confidence

# ✅ Risk Management
- Max daily loss check
- Max positions check
- Correlation checks
- Per-trade risk limit

# ✅ Position Monitoring
- Tracks stop loss
- Monitors take profit
- Trailing stops
- Time-based exits
```

### 3. Smart Scalping Engine (SMART_SCALPING_ENGINE.py)
```python
# ✅ Multi-timeframe Analysis
- Checks 6 timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Requires alignment (confluence)
- Session-aware (LONDON, NY, ASIA)
- Only trades in optimal sessions

# ✅ Signal Quality
- 100% confluence signals
- Directional agreement
- Volume confirmation
- Session volatility matching
```

## What MICRO SHOULD Do

### Current MICRO Logic (WRONG):
```python
# ❌ Get signal from hub
signal = hub.get_signals()
side = signal.get('side')
confidence = signal.get('confidence')

# ❌ Execute if confidence >= 85%
if confidence >= 85:
    execute_trade(symbol, side, price)  # BLIND EXECUTION!
    
# ❌ Auto-close ANY position > $3
if position_value > 3:
    close_position()  # Might be closing at LOSS!
```

### Proper MICRO Logic (RIGHT):
```python
# ✅ 1. Get signal with FULL context
signal = hub.get_signals()
symbol = signal.get('symbol')
side = signal.get('side')
confidence = signal.get('confidence')
timeframe = signal.get('timeframe')  # IMPORTANT!
stop_loss = signal.get('stop_loss')  # From signal
take_profit = signal.get('take_profit')  # From signal

# ✅ 2. Validate entry conditions
if confidence < 85:
    skip("Low confidence")
if position_cost > 5:
    skip("Too expensive for micro wallet")
if not is_fast_moving_pair(symbol):
    skip("Not volatile enough")

# ✅ 3. Calculate position size intelligently
balance = check_balance()
risk_per_trade = balance * 0.02  # 2% risk
position_size = calculate_size(balance, price, stop_loss)

# ✅ 4. Set proper targets
entry_price = current_price
stop_loss = entry_price * (1 - 0.01)  # 1% stop for micro
take_profit = entry_price * (1 + 0.02)  # 2% profit (2:1 R/R)

# ✅ 5. Execute with full context
trade = {
    'symbol': symbol,
    'side': side,
    'entry_price': entry_price,
    'stop_loss': stop_loss,
    'take_profit': take_profit,
    'position_size': position_size,
    'confidence': confidence,
    'timeframe': timeframe,
    'entry_time': now()
}
execute_trade(trade)

# ✅ 6. Monitor position (NOT blind auto-close!)
def should_close_position(position):
    current_price = get_price(position.symbol)
    pnl_pct = (current_price - position.entry_price) / position.entry_price
    
    # Close on take profit
    if pnl_pct >= 0.02:  # 2% profit
        return True, "PROFIT"
    
    # Close on stop loss
    if pnl_pct <= -0.01:  # 1% loss
        return True, "STOP_LOSS"
    
    # Close on time (if no movement after 1 hour)
    if time_elapsed > 3600 and abs(pnl_pct) < 0.005:
        return True, "TIME_EXIT"
    
    return False, "HOLD"

# ✅ 7. Close with profit confirmation
if should_close:
    if reason == "PROFIT":
        logger.info(f"💰 PROFIT: {symbol} +{pnl_pct:.2%}")
    close_position(position)
```

## Signal Structure We Need

Signals from data hub should have:
```python
signal = {
    # Basic
    'symbol': 'DOGE/USDT',
    'side': 'BUY',
    'confidence': 0.89,  # 89%
    
    # Entry/Exit (CRITICAL!)
    'entry_price': 0.1450,
    'stop_loss': 0.1435,  # -1%
    'take_profit': 0.1480,  # +2%
    
    # Context
    'timeframe': '5m',
    'session': 'LONDON_NY_OVERLAP',
    'volatility': 'HIGH',
    'confluence': True,  # Multi-timeframe agreement
    
    # Source
    'source': 'SmartScalpingEngine',
    'strategy': 'ConflueceScalp',
    'priority': 'high'
}
```

## Engines That Should Feed MICRO

1. **Smart Scalping Engine** ✅
   - Multi-timeframe confluence
   - Session-aware
   - High confidence (100%)
   
2. **Steady Profit Extractor** ✅
   - Stop loss / take profit set
   - Expected profit calculated
   - Fast-moving pairs
   
3. **Execution Orchestrator** ✅
   - Smart position sizing
   - Risk validation
   - Advanced actions (scale in/out, hedge)
   
4. **Session Clock** ✅
   - Best session timing
   - Volatility matching
   - Confidence boosts

5. **Market Regime Detector** (Need to wire)
   - TRENDING vs RANGING
   - BULLISH vs BEARISH
   - HIGH_VOL vs LOW_VOL
   - Adjust strategy per regime

## Next Steps - Systematic Wiring

### Step 1: Check What Signals Contain
```bash
# Run on VPS
python3 << 'EOF'
from COMPLETE_UNIFIED_ORCHESTRATOR import CentralDataHub
hub = CentralDataHub()
# Wait for signals to populate
import time; time.sleep(30)
signals = hub.get_signals(limit=10)
for s in signals:
    print(f"Signal keys: {s.keys()}")
    print(f"Full signal: {s}")
    print()
EOF
```

### Step 2: Enhance Signal Creation
Make sure Smart Scalping Engine includes:
- `stop_loss` field
- `take_profit` field  
- `expected_move` field
- `timeframe` field
- `entry_timing` field

### Step 3: Update MICRO to Use Full Signal
Not just symbol + side, but ALL signal context

### Step 4: Add Position Monitoring
Track each position with:
- Entry price
- Stop loss target
- Take profit target
- Entry time
- Current P&L

### Step 5: Close on PROFIT Not Value
```python
# WRONG
if position_value > 3: close()

# RIGHT
if pnl_pct > 2%: close("PROFIT")
if pnl_pct < -1%: close("STOP_LOSS")
```

## Expected Result

**Before (Blind Trading):**
```
💎 MICRO TRADE: BUY BTC/USDT
✅ MICRO executed
[price drops 5%]
🔄 CLOSING: BTC/USDT ($11 → $10.45)
❌ Lost $0.55
```

**After (Smart Trading):**
```
💎 MICRO ANALYZING: DOGE/USDT signal
   Confidence: 89%, Timeframe: 5m, Session: LONDON
   Entry: $0.145, SL: $0.1435 (-1%), TP: $0.148 (+2%)
   Position: $3.50, Expected profit: $0.07
✅ MICRO ENTERED: DOGE/USDT @ $0.145

[monitoring...]

🎯 TAKE PROFIT HIT: DOGE/USDT @ $0.148 (+2.07%)
💰 PROFIT: $0.07 (2% return)
Balance: $1.89 → $1.96
```

This is professional, systematic trading! 🚀
