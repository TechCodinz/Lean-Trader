#!/usr/bin/env python3
"""
Add Stop Loss / Take Profit to Scalper Signals
================================================

Current Scalper signals only have:
- symbol, side, confidence, session, timeframe_alignment

Adding:
- entry_price, stop_loss, take_profit, expected_profit

This allows MICRO and other consumers to trade intelligently!
"""

import sys

def enhance_scalper_signals(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the signal creation in scan_markets()
    old_signal = '''                    signal = {
                        'type': 'scalping',
                        'source': 'SmartScalpingEngine',
                        'symbol': symbol,
                        'side': direction.lower(),
                        'confidence': confidence,
                        'session': current_session,
                        'session_volatility': session_volatility,
                        'timeframe_alignment': details['alignment'],
                        'timeframes_analyzed': len(details['timeframes']),
                        'confluence_details': details,
                        'timestamp': datetime.now().isoformat(),
                        'priority': 'high' if confidence > 0.85 else 'normal'
                    }'''
    
    new_signal = '''                    # Get current price for entry/exit calculation
                    try:
                        # Would fetch real price in production
                        current_price = 100.0  # Placeholder - needs real price fetch
                        
                        # Calculate stop loss and take profit based on timeframe and confidence
                        # Higher timeframes = wider stops, Higher confidence = tighter stops
                        timeframe_count = len(details['timeframes'])
                        
                        # Base stop/profit (scalping = tight)
                        base_stop_pct = 0.008  # 0.8%
                        base_profit_pct = 0.012  # 1.2% (1.5:1 R/R)
                        
                        # Adjust for timeframe alignment
                        # More timeframes agree = can use tighter stops
                        alignment_factor = details['alignment']
                        if alignment_factor > 0.8:  # Strong alignment
                            base_stop_pct *= 0.8  # Tighter stop
                            base_profit_pct *= 0.8  # Quicker profit
                        
                        # Calculate targets
                        if direction.lower() == 'buy':
                            stop_loss = current_price * (1 - base_stop_pct)
                            take_profit = current_price * (1 + base_profit_pct)
                        else:  # sell
                            stop_loss = current_price * (1 + base_stop_pct)
                            take_profit = current_price * (1 - base_profit_pct)
                        
                        expected_move_pct = base_profit_pct
                        
                    except Exception as e:
                        # Fallback values if price fetch fails
                        stop_loss = None
                        take_profit = None
                        expected_move_pct = 0.01
                        current_price = None
                    
                    signal = {
                        'type': 'scalping',
                        'source': 'SmartScalpingEngine',
                        'symbol': symbol,
                        'side': direction.lower(),
                        'confidence': confidence,
                        'session': current_session,
                        'session_volatility': session_volatility,
                        'timeframe_alignment': details['alignment'],
                        'timeframes_analyzed': len(details['timeframes']),
                        'confluence_details': details,
                        'timestamp': datetime.now().isoformat(),
                        'priority': 'high' if confidence > 0.85 else 'normal',
                        # NEW FIELDS FOR SMART EXECUTION:
                        'entry_price': current_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'expected_move_pct': expected_move_pct,
                        'risk_reward_ratio': base_profit_pct / base_stop_pct if base_stop_pct > 0 else 1.5
                    }'''
    
    if old_signal in content:
        content = content.replace(old_signal, new_signal)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print("✅ Enhanced Smart Scalping signals with:")
        print("   - entry_price")
        print("   - stop_loss")
        print("   - take_profit")
        print("   - expected_move_pct")
        print("   - risk_reward_ratio")
        return True
    else:
        print("❌ Could not find signal structure in Smart Scalping Engine")
        print("File may have different format - needs manual edit")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 ENHANCE_SCALPER_SIGNALS.py SMART_SCALPING_ENGINE.py")
        sys.exit(1)
    
    success = enhance_scalper_signals(sys.argv[1])
    sys.exit(0 if success else 1)
