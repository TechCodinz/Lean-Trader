#!/usr/bin/env python3
"""
MICRO WALLET FIX - Use Hub Signals Properly
============================================

Changes:
1. Get signals from data hub (not re-analyze)
2. Filter for cheap coins only (< $5 per trade)
3. Filter for high confidence (>= 85%)
4. Only execute BUY/SELL signals
5. Better logging

Usage: python3 FIX_MICRO_SIGNALS.py COMPLETE_ULTIMATE_ORCHESTRATOR.py
"""

import sys
import re

def fix_micro_loop(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find and replace the MICRO trading loop
    # Look for the section that starts with "# Analyze and trade all configured pairs"
    
    old_pattern = r'''                        # Analyze and trade all configured pairs
                        for symbol in self\.micro_wallet_grower\.crypto_pairs:
                            # analyze_market returns: action, confidence, price, change, volume
                            action, confidence, price, change, volume = self\.micro_wallet_grower\.analyze_market\(symbol\)
                            
                            if action in \['BUY', 'SELL'\] and confidence >= 70:
                                # Execute micro trade \(execute_trade expects: symbol, signal, price, quantity\)
                                result = self\.micro_wallet_grower\.execute_trade\(symbol, action, price\)
                                
                                if result:
                                    logger\.info\(f"💎 MICRO TRADE: \{symbol\} \{action\} @ \$\{price:.6f\}"\)
                                    logger\.info\(f"   Change: \{change:\+\.2f\}%, Volume: \$\{volume:\.0f\}"\)
                                    logger\.info\(f"   Balance: \$\{balance:\.2f\}, Conf: \{confidence:\.0f\}%"\)'''
    
    new_code = '''                        # Get ACTUAL signals from data hub (with direction & confidence!)
                        hub_signals = self.data_hub.get_signals(limit=50)
                        trades_attempted = 0
                        
                        if not hub_signals:
                            logger.info("💤 MICRO: No signals in hub yet")
                        else:
                            logger.info(f"🔍 MICRO checking {len(hub_signals)} hub signals...")
                        
                        for signal in hub_signals:
                            symbol = signal.get('symbol')
                            side = signal.get('side', 'buy')
                            confidence = signal.get('confidence', 0) * 100 if signal.get('confidence', 0) <= 1 else signal.get('confidence', 0)
                            
                            # Filter 1: Need valid symbol and high confidence
                            if not symbol or confidence < 85:
                                continue
                            
                            # Filter 2: Only BUY/SELL signals (skip HOLD, CLOSE, HEDGE, etc.)
                            if side.upper() not in ['BUY', 'SELL']:
                                logger.debug(f"Skipping {symbol} - not a BUY/SELL signal ({side})")
                                continue
                            
                            # Filter 3: CHEAP coins only (< $5 per trade for micro wallet)
                            try:
                                ticker = self.micro_wallet_grower.get_gate_ticker(symbol)
                                if not ticker:
                                    continue
                                    
                                price = ticker['price']
                                position_size = self.micro_wallet_grower.position_sizes.get(symbol, 0.001)
                                position_cost = price * position_size
                                
                                if position_cost > 5.0:
                                    logger.debug(f"Skipping {symbol} - too expensive (${position_cost:.2f} > $5)")
                                    continue
                                
                                # Execute using signal data (not re-analysis!)
                                trades_attempted += 1
                                logger.info(f"💎 MICRO TRADE #{trades_attempted}: {side.upper()} {symbol}")
                                logger.info(f"   Price: ${price:.6f}, Cost: ${position_cost:.2f}")
                                logger.info(f"   Confidence: {confidence:.1f}%, Balance: ${balance:.2f}")
                                
                                result = self.micro_wallet_grower.execute_trade(symbol, side.upper(), price)
                                
                                if result:
                                    logger.info(f"✅ MICRO executed: {symbol} {side.upper()}")
                                else:
                                    logger.warning(f"⚠️  MICRO trade failed for {symbol}")
                                    
                            except Exception as e:
                                logger.debug(f"Error checking {symbol}: {e}")
                                continue
                        
                        if trades_attempted == 0 and hub_signals:
                            logger.info(f"💤 MICRO: No qualifying signals (checked {len(hub_signals)} signals)")'''
    
    # Try to replace
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_code, content)
        print("✅ Fixed MICRO loop - now uses hub signals with filters")
    else:
        print("❌ Could not find MICRO loop pattern - showing what to look for:")
        print("Looking for: '# Analyze and trade all configured pairs'")
        return False
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 FIX_MICRO_SIGNALS.py COMPLETE_ULTIMATE_ORCHESTRATOR.py")
        sys.exit(1)
    
    filepath = sys.argv[1]
    success = fix_micro_loop(filepath)
    
    if success:
        print(f"✅ MICRO fixed in: {filepath}")
        print("\nWhat changed:")
        print("  1. Uses hub signals (symbol, side, confidence)")
        print("  2. Filters for cheap coins (< $5 per trade)")
        print("  3. Filters for high confidence (>= 85%)")
        print("  4. Only executes BUY/SELL (ignores HOLD, CLOSE, etc.)")
        print("  5. Better logging to see what's happening")
    else:
        print("❌ Fix failed - manual edit needed")
        sys.exit(1)
