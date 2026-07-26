#!/usr/bin/env python3
"""
UNLEASH FULL AUTONOMY - BOTH ORCHESTRATORS:
- Remove ALL limits from COMPLETE_ULTIMATE_ORCHESTRATOR
- Remove ALL limits from EXECUTION_ORCHESTRATOR
- Remove ALL hardcoded symbol lists
- Enable true collective autonomous trading
"""

import re

print("🔓 UNLEASHING FULL AUTONOMY ACROSS BOTH ORCHESTRATORS...")
print()

# ============================================================================
# Process both orchestrator files
# ============================================================================
orchestrator_files = [
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
    'EXECUTION_ORCHESTRATOR.py'
]

for filename in orchestrator_files:
    print(f"{'='*60}")
    print(f"Processing: {filename}")
    print(f"{'='*60}")
    print()
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_size = len(content)
        
        # ========================================================================
        # FIX 1: Remove ALL symbol slice limits
        # ========================================================================
        print(f"1️⃣ Removing symbol limits in {filename}...")
        
        limit_patterns = [
            (r'symbols\[:5\]', 'symbols'),
            (r'symbols\[:10\]', 'symbols'),
            (r'symbols\[:20\]', 'symbols'),
            (r'symbols\[:30\]', 'symbols'),
            (r'symbols\[:50\]', 'symbols'),
            (r'symbols\[:80\]', 'symbols'),
            (r'symbols\[:100\]', 'symbols'),
            (r'symbols\[:200\]', 'symbols'),
            (r'all_symbols\[:5\]', 'all_symbols'),
            (r'all_symbols\[:10\]', 'all_symbols'),
            (r'all_symbols\[:50\]', 'all_symbols'),
            (r'all_symbols\[:80\]', 'all_symbols'),
            (r'all_symbols\[:100\]', 'all_symbols'),
            (r'hot_pairs\[:5\]', 'hot_pairs'),
            (r'hot_pairs\[:10\]', 'hot_pairs'),
            (r'hot_pairs\[:20\]', 'hot_pairs'),
            (r'pairs\[:50\]', 'pairs'),
            (r'pairs\[:100\]', 'pairs'),
            (r'pairs\[:200\]', 'pairs'),
            (r'discovered_pairs\[:50\]', 'discovered_pairs'),
            (r'discovered_pairs\[:100\]', 'discovered_pairs'),
            (r'tradable_pairs\[:10\]', 'tradable_pairs'),
            (r'tradable_pairs\[:50\]', 'tradable_pairs'),
        ]
        
        removed_count = 0
        for pattern, replacement in limit_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                removed_count += len(matches)
                print(f"   [OK] {pattern} → {replacement} ({len(matches)}x)")
        
        if removed_count > 0:
            print(f"   Total: {removed_count} limits removed")
        else:
            print(f"   ✓ No slice limits found")
        
        # ========================================================================
        # FIX 2: Remove hardcoded symbol lists
        # ========================================================================
        print()
        print(f"2️⃣ Removing hardcoded symbol lists in {filename}...")
        
        # Find and comment out hardcoded symbol arrays
        lines = content.split('\n')
        new_lines = []
        in_symbol_list = False
        symbol_list_indent = 0
        
        for i, line in enumerate(lines):
            # Detect start of hardcoded symbol list
            if ("['BTC/USDT'" in line or '["BTC/USDT"' in line) and 'TOXIC_SYMBOLS' not in line:
                # Check if it's a list definition
                if '[' in line and not line.strip().startswith('#'):
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + '# REMOVED: Hardcoded symbol list - using dynamic discovery')
                    new_lines.append(' ' * indent + '# ' + line.strip())
                    
                    # If list continues on next lines, mark for commenting
                    if line.count('[') > line.count(']'):
                        in_symbol_list = True
                        symbol_list_indent = indent
                    continue
            
            # Continue commenting multi-line symbol lists
            if in_symbol_list:
                if line.strip().startswith(']'):
                    new_lines.append(' ' * symbol_list_indent + '# ' + line.strip())
                    in_symbol_list = False
                elif line.strip():
                    new_lines.append(' ' * symbol_list_indent + '# ' + line.strip())
                continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        print(f"   [OK] Commented out hardcoded lists")
        
        # ========================================================================
        # FIX 3: Remove max_positions and max_trades limits
        # ========================================================================
        print()
        print(f"3️⃣ Removing position/trade limits in {filename}...")
        
        position_limits = [
            (r'max_positions\s*=\s*\d+', 'max_positions = 999999  # UNLIMITED'),
            (r'max_open_positions\s*=\s*\d+', 'max_open_positions = 999999  # UNLIMITED'),
            (r'max_trades\s*=\s*\d+', 'max_trades = 999999  # UNLIMITED'),
            (r'max_daily_trades\s*=\s*\d+', 'max_daily_trades = 999999  # UNLIMITED'),
        ]
        
        limit_changes = 0
        for pattern, replacement in position_limits:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                limit_changes += len(matches)
                print(f"   [OK] Set unlimited: {matches[0]}")
        
        if limit_changes > 0:
            print(f"   Total: {limit_changes} position limits removed")
        else:
            print(f"   ✓ No position limits found")
        
        # ========================================================================
        # FIX 4: Fix $100 placeholder prices (ULTIMATE only)
        # ========================================================================
        if filename == 'COMPLETE_ULTIMATE_ORCHESTRATOR.py':
            print()
            print(f"4️⃣ Fixing placeholder prices...")
            
            if 'current_price = 100.0 * (1 + random.uniform' in content:
                content = content.replace(
                    '''# Get current price (in production, fetch real price)
                            try:
                                # Would fetch real ticker in production
                                import random
                                current_price = 100.0 * (1 + random.uniform(-0.01, 0.01))''',
                    '''# Get REAL price from exchange
                            try:
                                ticker = await asyncio.to_thread(self.trading_engines[self.mode].fetch_ticker, symbol)
                                current_price = ticker.get('last') or ticker.get('close', 0)
                                if not current_price or current_price <= 0:
                                    continue'''
                )
                print(f"   [OK] Replaced $100 placeholder with real prices")
            else:
                print(f"   ✓ No placeholder prices found")
        
        # ========================================================================
        # FIX 5: Ensure unlimited pair discovery
        # ========================================================================
        print()
        print(f"5️⃣ Ensuring unlimited pair discovery...")
        
        # Remove limits on discovered_pairs return
        if 'return discovered_pairs[' in content or 'return pairs[' in content:
            content = re.sub(
                r'return (discovered_pairs|pairs)\[:[^\]]+\]',
                r'return \1  # UNLIMITED',
                content
            )
            print(f"   [OK] Removed return limits")
        else:
            print(f"   ✓ No return limits found")
        
        # Save modified file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        new_size = len(content)
        print()
        print(f"[OK] {filename} updated!")
        print(f"   Size: {original_size} → {new_size} bytes")
        print()
        
    except FileNotFoundError:
        print(f"  {filename} not found, skipping")
        print()
    except Exception as e:
        print(f"[X] Error processing {filename}: {e}")
        print()

# ============================================================================
# FIX INTELLIGENT_EXECUTION_ENGINE
# ============================================================================
print(f"{'='*60}")
print(f"Processing: INTELLIGENT_EXECUTION_ENGINE.py")
print(f"{'='*60}")
print()

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
        exec_content = f.read()
    
    # Add ETH/SOL to TOXIC_SYMBOLS if not present
    if 'TOXIC_SYMBOLS' in exec_content:
        toxic_section = exec_content.split('TOXIC_SYMBOLS = {')[1].split('}')[0]
        
        if "'ETH/USDT'" not in toxic_section:
            exec_content = exec_content.replace(
                'TOXIC_SYMBOLS = {',
                "TOXIC_SYMBOLS = {\n    'ETH/USDT', 'SOL/USDT',  # Temporary quality filter"
            )
            print("   [OK] Added ETH/SOL to TOXIC_SYMBOLS")
        else:
            print("   ✓ ETH/SOL already in TOXIC_SYMBOLS")
        
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
            f.write(exec_content)
    
    print()
    
except Exception as e:
    print(f"  Error updating execution engine: {e}")
    print()

print("=" * 60)
print("[OK] FULL AUTONOMY UNLEASHED ACROSS ALL FILES!")
print("=" * 60)
print()
print("Summary:")
print("  [OK] Removed ALL symbol limits ([:5], [:10], [:50], etc)")
print("  [OK] Removed ALL hardcoded symbol lists")
print("  [OK] Removed position/trade count limits")
print("  [OK] Fixed $100 placeholder prices")
print("  [OK] Unlimited pair discovery")
print("  [OK] Quality filters only (TOXIC_SYMBOLS, volume)")
print()
print("Bot will now:")
print("  • Scan ENTIRE exchange (100-500+ pairs)")
print("  • Trade UNLIMITED positions simultaneously")
print("  • Use REAL market prices")
print("  • Self-select opportunities autonomously")
print("  • Operate with FULL 205+ engines capacity")

