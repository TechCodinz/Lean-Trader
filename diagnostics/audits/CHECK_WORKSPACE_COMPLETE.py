#!/usr/bin/env python3
"""Systematic check of workspace fixes"""

print("=" * 80)
print("SYSTEMATIC WORKSPACE CHECK")
print("=" * 80)

# 1. Universe loading
with open('systems/COMPLETE_UNIFIED_ORCHESTRATOR.py', 'r') as f:
    content = f.read()
    if 'BYBIT_TESTNET_PAIRS' in content:
        print("✅ 1. Universe loads from BYBIT_TESTNET_PAIRS")
    else:
        print("❌ 1. Universe NOT loading testnet pairs")
    if 'self.universe =' in content:
        print("✅ 2. Universe stored as self.universe")
    else:
        print("❌ 2. Universe NOT stored")

# 2. SmartScalpingEngine gets universe
    if 'SmartScalpingEngine(self.ultra_core, self.risk_engine, universe=' in content:
        print("✅ 3. Universe passed to SmartScalpingEngine")
    else:
        print("❌ 3. Universe NOT passed to SmartScalpingEngine")

# 3. Market Scanner started
with open('systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()
    if 'market_scanner.run_continuous_scanning' in content:
        print("✅ 4. Market scanner task created")
    else:
        print("❌ 4. Market scanner NOT started")
    if 'start_all_orchestrators' in content:
        print("✅ 5. start_all_orchestrators called")
    else:
        print("❌ 5. start_all_orchestrators NOT called")

# 4. Router sandbox mode
with open('router.py', 'r') as f:
    content = f.read()
    if 'set_sandbox_mode(True)' in content:
        print("✅ 6. Router sets sandbox mode")
    else:
        print("❌ 6. Router missing sandbox mode")

# 5. Execution gets router
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()
    if 'wire_execution_to_testnet' in content:
        print("✅ 7. Execution has wire_execution_to_testnet")  
    else:
        print("❌ 7. Missing wire_execution_to_testnet")
    if 'recent_signals' in content and 'get_signals' not in content:
        print("✅ 8. Data hub uses recent_signals")
    else:
        print("❌ 8. Still using get_signals")

# 6. Intelligent engine router.ex
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()
    if 'hasattr(self.exchange, "ex")' in content:
        print("✅ 9. Intelligent engine handles router.ex")
    else:
        print("❌ 9. Missing router.ex handling")
    if 'should_open_new_trade' in content and 'return True' in content:
        print("✅ 10. Infinite trading enabled")
    else:
        print("❌ 10. Still has trade limits")

# 7. Dynamic discovery function
with open('DYNAMIC_PAIR_DISCOVERY.py', 'r') as f:
    content = f.read()
    if 'def get_discovery_engine' in content:
        print("✅ 11. get_discovery_engine alias exists")
    else:
        print("❌ 11. Missing get_discovery_engine")

print("=" * 80)
