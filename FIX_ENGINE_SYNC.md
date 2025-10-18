# 🔧 ENGINE SYNCHRONIZATION FIX

## Problem Identified
1. **Scalper** generates 47 signals → `signal_queue` ✅
2. **UnifiedDecisionEngine** should process signals → `alert_queue` ❌ **NOT RUNNING!**
3. **ExecutionOrchestrator** waits for alerts in `alert_queue` ✅ **STARVING!**
4. **REAL_PROFIT_BOT** runs independently, trades only BTC/USDT ✅

## Root Cause
The `decision` orchestrator (UnifiedDecisionEngine) is NOT started in `start_all_orchestrators()`!

## The Fix
Add UnifiedDecisionEngine to the startup sequence so it processes scalper signals and routes them to ExecutionOrchestrator.

## Expected Result After Fix
```
Scalper → signal_queue → UnifiedDecisionEngine → alert_queue → ExecutionOrchestrator → TRADES!
```

All engines will trade through ExecutionOrchestrator, not just REAL_PROFIT_BOT.
