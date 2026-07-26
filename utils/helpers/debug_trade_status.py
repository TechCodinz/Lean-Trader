with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Add debug after the status check
old = """            for symbol, trades in self.intelligent_engine.active_trades_by_tf.items():
                for trade in trades:
                    if trade.get('status') == 'open':"""

new = """            for symbol, trades in self.intelligent_engine.active_trades_by_tf.items():
                logger.info(f"🔍 DEBUG: {symbol} has {len(trades)} trades")
                for trade in trades:
                    logger.info(f"🔍 DEBUG:   trade status = '{trade.get('status')}'")
                    if trade.get('status') == 'open':"""

content = content.replace(old, new)

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print("[OK] Added debug logging for trade status")
