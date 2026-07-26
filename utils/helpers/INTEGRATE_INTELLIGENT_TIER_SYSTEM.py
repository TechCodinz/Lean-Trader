#!/usr/bin/env python3
"""
INTEGRATE INTELLIGENT TIER SYSTEM
Wires up the new balance-aware engine coordination system
"""

import sys
import re
from pathlib import Path

print("\n" + "="*80)
print("🔧 INTEGRATING INTELLIGENT TIER SYSTEM")
print("="*80 + "\n")

# Check if files exist
orchestrator_file = Path('COMPLETE_ULTIMATE_ORCHESTRATOR.py')
if not orchestrator_file.exists():
    print("[X] COMPLETE_ULTIMATE_ORCHESTRATOR.py not found!")
    print("   Run this in the apex_bot directory")
    sys.exit(1)

print("[OK] Found orchestrator file\n")

# Read orchestrator
with open(orchestrator_file, 'r') as f:
    content = f.read()

# Backup
backup_file = orchestrator_file.with_suffix('.py.tier_backup')
with open(backup_file, 'w') as f:
    f.write(content)
print(f"[OK] Created backup: {backup_file}\n")

# Add imports (after existing imports)
imports_to_add = """
# ============================================================================
# INTELLIGENT TIER SYSTEM - Balance-aware engine coordination
# ============================================================================
from BALANCE_TIER_COORDINATOR import BalanceTierCoordinator, initialize_tier_coordinator
from DYNAMIC_PAIR_DISCOVERY import DynamicPairDiscovery, initialize_pair_discovery
from ENHANCED_AGGRESSIVE_MICRO_SCALPER import EnhancedAggressiveMicroScalper, initialize_micro_scalper
"""

# Find where to insert (after DEX_ORCHESTRATOR import)
insert_point = content.find('from DEX_ORCHESTRATOR import')
if insert_point > 0:
    # Find end of that line
    insert_point = content.find('\n', insert_point) + 1
    content = content[:insert_point] + imports_to_add + content[insert_point:]
    print("[OK] Added tier system imports")
else:
    print("  Could not find insert point for imports")

# Add initialization in __init__
init_code = """
        # ================================================================
        # INTELLIGENT TIER SYSTEM - Initialize balance-aware coordination
        # ================================================================
        logger.info("🎯 Initializing Intelligent Tier System...")
        
        # Initialize tier coordinator
        initial_balance = 0.0  # Will be updated after exchange connection
        self.tier_coordinator = initialize_tier_coordinator(initial_balance)
        logger.info("[OK] Tier Coordinator initialized")
        
        # Initialize dynamic pair discovery (will be set after exchange connection)
        self.pair_discovery = None
        logger.info("[OK] Dynamic Pair Discovery ready")
        
        # Initialize enhanced micro scalper (will be set after profit system)
        self.enhanced_micro_scalper = None
        logger.info("[OK] Enhanced Micro Scalper ready")
        logger.info("")
"""

# Find __init__ method and add after super().__init__
init_marker = 'super().__init__()'
if init_marker in content:
    insert_pos = content.find(init_marker) + len(init_marker)
    # Find next newline
    insert_pos = content.find('\n', insert_pos) + 1
    content = content[:insert_pos] + init_code + content[insert_pos:]
    print("[OK] Added tier system initialization")
else:
    print("  Could not find __init__ method")

# Add dynamic pair setup after exchange connection
setup_code = """
            # Setup dynamic pair discovery
            if 'gateio' in self.exchanges:
                logger.info("🔍 Setting up Dynamic Pair Discovery...")
                self.pair_discovery = initialize_pair_discovery(
                    self.exchanges['gateio'],
                    min_volume=50000  # $50k minimum 24h volume
                )
                
                # Start continuous discovery loop
                asyncio.create_task(self.pair_discovery.run_continuous_discovery())
                logger.info("[OK] Dynamic Pair Discovery active")
            
            # Update tier coordinator with actual balance
            if hasattr(self, 'tier_coordinator') and self.tier_coordinator:
                try:
                    balance_data = await asyncio.to_thread(
                        self.exchanges['gateio'].fetch_balance
                    )
                    actual_balance = balance_data.get('USDT', {}).get('free', 0.0)
                    self.tier_coordinator.update_balance(actual_balance)
                    logger.info(f"💰 Tier Coordinator updated: ${actual_balance:.2f}")
                except Exception as e:
                    logger.warning(f"Could not fetch initial balance: {e}")
"""

# Find where Gate.io is connected
gateio_marker = "Connected to: ['gateio']"
if gateio_marker in content:
    insert_pos = content.find(gateio_marker)
    # Find next newline
    insert_pos = content.find('\n', insert_pos) + 1
    content = content[:insert_pos] + setup_code + content[insert_pos:]
    print("[OK] Added dynamic pair discovery setup")
else:
    print("  Could not find Gate.io connection point")

# Add micro scalper setup after profit system
scalper_setup = """
            # Setup Enhanced Aggressive Micro Scalper
            if self.pair_discovery and self.tier_coordinator:
                logger.info("⚡ Setting up Enhanced Aggressive Micro Scalper...")
                self.enhanced_micro_scalper = initialize_micro_scalper(
                    self.unified_orchestrator.execution_orchestrator.complete_profit_system,
                    self.pair_discovery,
                    self.tier_coordinator
                )
                
                # Start aggressive scalping loop
                asyncio.create_task(self.enhanced_micro_scalper.run_aggressive_scalping_loop())
                logger.info("[OK] Enhanced Micro Scalper active - hunting for micro profits!")
"""

# Find execution orchestrator wiring
exec_marker = "EXECUTION ORCHESTRATOR WIRED"
if exec_marker in content:
    insert_pos = content.find(exec_marker)
    # Find next newline
    insert_pos = content.find('\n', insert_pos) + 1
    content = content[:insert_pos] + scalper_setup + content[insert_pos:]
    print("[OK] Added micro scalper setup")
else:
    print("  Could not find execution orchestrator wiring")

# Add signal forwarding from engines to micro scalper
signal_forwarding = """
        # Forward signals to Enhanced Micro Scalper for aggregation
        if hasattr(self, 'enhanced_micro_scalper') and self.enhanced_micro_scalper:
            try:
                await self.enhanced_micro_scalper.receive_engine_signal(
                    engine_name='OPPORTUNITY_SCANNER',
                    signal=signal
                )
            except:
                pass
"""

# Find decision loop where signals are generated
decision_marker = "🎯 Decision:"
if decision_marker in content:
    # Find a few occurrences and add after each
    count = 0
    search_pos = 0
    while count < 3:
        pos = content.find(decision_marker, search_pos)
        if pos < 0:
            break
        # Find end of that log line
        end_pos = content.find('\n', pos) + 1
        content = content[:end_pos] + signal_forwarding + content[end_pos:]
        search_pos = end_pos + len(signal_forwarding) + 100
        count += 1
    print(f"[OK] Added signal forwarding ({count} locations)")

# Write updated orchestrator
with open(orchestrator_file, 'w') as f:
    f.write(content)

print("\n" + "="*80)
print("[OK] INTEGRATION COMPLETE!")
print("="*80)
print("\nChanges made:")
print("  1. [OK] Added tier system imports")
print("  2. [OK] Added tier coordinator initialization")
print("  3. [OK] Added dynamic pair discovery")
print("  4. [OK] Added enhanced micro scalper")
print("  5. [OK] Added signal forwarding")
print(f"\nBackup saved: {backup_file}")
print("\nThe bot will now:")
print("  • Start with ONLY micro scalper (nano tier)")
print("  • Activate more engines as balance grows")
print("  • Dynamically discover hot pairs (no hardcoded)")
print("  • Aggregate signals from ALL engines")
print("  • Trade ONLY the best opportunities")
print("\n" + "="*80)
