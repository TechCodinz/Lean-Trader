#!/usr/bin/env python3
"""
Production Runner - Runs the bot continuously with auto-restart
"""

import subprocess
import time
import sys
import os
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    🚀 ULTRA BOT PRODUCTION RUNNER 🚀                ║
║                                                                      ║
║  Status: READY FOR DEPLOYMENT                                       ║
║  Mode: Full Production with Evolution                               ║
║  Features: ALL ENABLED                                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

def run_bot():
    """Run the bot with auto-restart on failure"""
    
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        try:
            print(f"\n{'='*70}")
            print(f"🚀 Starting Ultra Evolution Bot (Attempt {restart_count + 1})")
            print(f"⏰ Time: {datetime.now()}")
            print(f"{'='*70}\n")
            
            # Run the bot
            process = subprocess.Popen(
                [sys.executable, 'start_ultra_evolution.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                print(line, end='')
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                print("\n✅ Bot exited normally")
                break
            else:
                print(f"\n⚠️ Bot exited with code {return_code}")
                restart_count += 1
                
                if restart_count < max_restarts:
                    wait_time = min(60 * restart_count, 300)  # Max 5 minutes
                    print(f"🔄 Restarting in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested by user")
            if process:
                process.terminate()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            restart_count += 1
            time.sleep(60)
    
    if restart_count >= max_restarts:
        print(f"\n❌ Max restarts ({max_restarts}) reached. Manual intervention required.")
        return 1
    
    return 0

if __name__ == "__main__":
    # Set environment for production
    os.environ['PRODUCTION'] = 'true'
    os.environ['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Ensure we're in paper mode if no API keys
    if not os.environ.get('BYBIT_API_KEY'):
        print("ℹ️ No API keys found - running in PAPER TRADING mode")
        os.environ['TRADING_MODE'] = 'paper'
    else:
        print("✅ API keys found - running in LIVE mode")
        os.environ['TRADING_MODE'] = 'live'
    
    print(f"\n📊 Configuration:")
    print(f"  Mode: {os.environ.get('TRADING_MODE')}")
    print(f"  Log Level: {os.environ.get('LOG_LEVEL')}")
    print(f"  Production: {os.environ.get('PRODUCTION')}")
    
    # Run the bot
    exit_code = run_bot()
    sys.exit(exit_code)