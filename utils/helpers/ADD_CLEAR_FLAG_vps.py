with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Add check for clear flag after engine initialization
old = """        # Start monitoring loop"""
new = """        # Check for clear flag
        import os
        if os.path.exists('CLEAR_TRADES_FLAG.txt'):
            logger.info("🧹 CLEAR FLAG DETECTED - Wiping all active trades!")
            self.intelligent_engine.active_trades_by_tf.clear()
            os.remove('CLEAR_TRADES_FLAG.txt')
            logger.info("[OK] Active trades cleared!")
        
        # Start monitoring loop"""

if old in content:
    content = content.replace(old, new)
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    print("[OK] Orchestrator will clear on restart")
else:
    print(" Could not find insertion point")
