
# Read cleanup class
with open('/root/bot/POSITION_CLEANUP_CLASS.py', 'r') as f:
    cleanup_class = f.read()

# Read orchestrator
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    orchestrator = f.read()

# Insert cleanup class before CompleteUltimateOrchestrator
if 'class AutomaticPositionCleanup:' not in orchestrator:
    orchestrator = orchestrator.replace(
        'class CompleteUltimateOrchestrator(',
        cleanup_class + '\n\nclass CompleteUltimateOrchestrator('
    )
    print("[OK] Cleanup class added")
else:
    print("  Cleanup class already exists")

# Add to __init__ if not already there
if 'self.position_cleanup' not in orchestrator:
    orchestrator = orchestrator.replace(
        'self.auto_profit_taker = AutoProfitTaker(',
        'self.auto_profit_taker = AutoProfitTaker(' + '\n        \n        # Automatic position cleanup\n        self.position_cleanup = AutomaticPositionCleanup(self.exchange, logger)\n        '
    )
    print("[OK] Initialization added")

# Add to start() if not already there
if 'self.position_cleanup.cleanup_loop()' not in orchestrator:
    orchestrator = orchestrator.replace(
        'asyncio.create_task(self.auto_profit_taker.check_and_close_positions())',
        'asyncio.create_task(self.auto_profit_taker.check_and_close_positions())' + '\n                asyncio.create_task(self.position_cleanup.cleanup_loop())'
    )
    print("[OK] Background task added")

# Write back
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(orchestrator)

print("[OK] Integration complete!")
