"""
Example: Complete integration showing data flow

Data Feed → Strategy Signal → Pitch Engine → Risk/Execution
"""

import asyncio
from pitch_bent.integration import initialize_pitch_system
from pitch_bent.models import MarketState, VenueType

# ============================================
# STEP 1: Initialize Pitch System (once at startup)
# ============================================

pitch_system = initialize_pitch_system(
    enable=True,  # Set to False to disable bending
    seed=None     # Set to integer for deterministic backtests
)

print("[OK] Pitch-Bent System initialized")

# ============================================  
# STEP 2: Simulated Trading Loop
# ============================================

async def trading_loop_example():
    """
    Example showing complete call chain from data → execution
    """
    
    # === DATA FEED ===
    # Simulate receiving OHLCV data (in real bot, this comes from exchange)
    symbol = "BTC/USDT"
    recent_closes = [50000, 50100, 50050, 50200, 50150, 50180, 50120]
    current_spread = 10.0  # $10 bid-ask spread
    funding_rate = 0.0001  # 0.01% funding
    
    # === STRATEGY SIGNAL ===
    # Simulate strategy generating a signal (in real bot, from your strategy engines)
    signal = {
        'symbol': symbol,
        'side': 'BUY',
        'confidence': 0.75,
        'strategy': 'momentum'
    }
    
    print(f"\n📊 Signal: {signal['side']} {symbol} (confidence: {signal['confidence']:.0%})")
    
    # === PITCH ENGINE ===
    # Create market state from available data
    market_state = MarketState(
        symbol=symbol,
        venue_type=VenueType.CEX,
        timeframe="5m",
        price_series=recent_closes,
        spread=current_spread,
        funding_rate=funding_rate
    )
    
    # Base parameters (your normal trading params)
    base_params = {
        'lot_size': 100,    # $100 USD
        'sl_pct': 0.01,     # 1% stop loss
        'tp_pct': 0.02,     # 2% take profit
        'max_positions': 3
    }
    
    # Get bent parameters
    bent_params = pitch_system.get_bent_params(
        market_state,
        base_params,
        symbol_class="BTC_majors"
    )
    
    print(f"\n🎯 Pitch Analysis:")
    print(f"  Pitch Value: {bent_params.pitch_value:.3f}")
    pitch_output = pitch_system.get_current_pitch(symbol)
    if pitch_output:
        print(f"  Regime: {pitch_output.regime}")
        print(f"  Confidence: {pitch_output.confidence:.2%}")
    
    # === RISK MANAGER (Apply Bending) ===
    actual_lot = base_params['lot_size'] * bent_params.lot_multiplier
    actual_sl = base_params['sl_pct'] * bent_params.sl_multiplier
    actual_tp = base_params['tp_pct'] * bent_params.tp_multiplier
    
    print(f"\n⚙️  Parameter Bending:")
    print(f"  Position Size: ${base_params['lot_size']} → ${actual_lot:.2f} ({bent_params.lot_multiplier:.2f}x)")
    print(f"  Stop Loss: {base_params['sl_pct']*100:.1f}% → {actual_sl*100:.2f}% ({bent_params.sl_multiplier:.2f}x)")
    print(f"  Take Profit: {base_params['tp_pct']*100:.1f}% → {actual_tp*100:.2f}% ({bent_params.tp_multiplier:.2f}x)")
    print(f"  Confirmations: {bent_params.confirmation_multiplier}")
    print(f"  Entry Delay: {bent_params.entry_delay_multiplier:.1f}x")
    
    # === EXECUTION ===
    # In real bot, this would call exchange API
    entry_price = recent_closes[-1]
    sl_price = entry_price * (1 - actual_sl)
    tp_price = entry_price * (1 + actual_tp)
    
    print(f"\n>> Execution (Simulated):")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Stop Loss: ${sl_price:.2f}")
    print(f"  Take Profit: ${tp_price:.2f}")
    print(f"  Position Size: ${actual_lot:.2f}")
    
    # Risk/Reward
    risk_usd = actual_lot * actual_sl
    reward_usd = actual_lot * actual_tp
    rr = reward_usd / risk_usd if risk_usd > 0 else 0
    print(f"  Risk: ${risk_usd:.2f} | Reward: ${reward_usd:.2f} | R:R = 1:{rr:.1f}")

# Run example
if __name__ == "__main__":
    asyncio.run(trading_loop_example())
    
    print("\n" + "="*60)
    print("[OK] Example complete!")
    print("="*60)
    print("\nIntegration Points:")
    print("1. Data Feed → MarketState (adapt your OHLCV to MarketState)")
    print("2. Strategy → Signal (your existing strategy engines)")
    print("3. Pitch Engine → BentParams (pitch_system.get_bent_params)")
    print("4. Risk Manager → Apply multipliers (size *= lot_mult, etc.)")
    print("5. Execution → Place orders (your exchange adapter)")
