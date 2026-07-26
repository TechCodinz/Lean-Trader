import sys
sys.path.insert(0, 'src')
# Create a script that the orchestrator will run on next startup
with open('CLEAR_TRADES_FLAG.txt', 'w') as f:
    f.write('CLEAR_ON_NEXT_STARTUP')
print("[OK] Flag created - restart will clear trades")
