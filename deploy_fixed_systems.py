#!/usr/bin/env python3
"""
Deploy Fixed Systems to VPS
This script will copy all the fixed files to your VPS and integrate them
"""

import os
import subprocess
import sys

def run_vps_command(command):
    """Run a command on the VPS"""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 DEPLOYING FIXED SYSTEMS TO VPS")
    print("=" * 50)
    
    # VPS connection details
    vps_ip = "75.119.149.117"
    vps_user = "root"
    vps_password = "pW65Yg036RettBb7"
    
    # Files to deploy
    files_to_deploy = [
        "ULTRA_GOLDMINE_FEATURES.py",
        "DIVINE_INTELLIGENCE_FEATURES.py", 
        "AUTO_LIVE_TRIGGER.py"
    ]
    
    print("📋 Files to deploy:")
    for file in files_to_deploy:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NOT FOUND")
            return False
    
    print("\n🔧 DEPLOYMENT COMMANDS FOR VPS:")
    print("=" * 50)
    
    # Step 1: Create backup
    print("1️⃣ Create backup of existing files:")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && cp ULTRA_GOLDMINE_FEATURES.py ULTRA_GOLDMINE_FEATURES.py.backup 2>/dev/null || true'")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && cp DIVINE_INTELLIGENCE_FEATURES.py DIVINE_INTELLIGENCE_FEATURES.py.backup 2>/dev/null || true'")
    
    # Step 2: Copy files
    print("\n2️⃣ Copy fixed files to VPS:")
    for file in files_to_deploy:
        print(f"scp {file} {vps_user}@{vps_ip}:/root/trading_bot/")
    
    # Step 3: Install dependencies
    print("\n3️⃣ Install missing dependencies:")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && source venv/bin/activate && pip install numpy pandas scipy scikit-learn'")
    
    # Step 4: Test systems
    print("\n4️⃣ Test all systems:")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && source venv/bin/activate && python3 -c \"")
    print("from ULTRA_GOLDMINE_FEATURES import UltraGoldmineManager")
    print("from DIVINE_INTELLIGENCE_FEATURES import DivineIntelligenceManager") 
    print("from AUTO_LIVE_TRIGGER import AutoLiveTrigger")
    print("print(\\\"✅ All systems imported successfully\\\")")
    print("\"")
    
    print("\n5️⃣ Restart bot with new systems:")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && pkill -f RUN_BOT.py'")
    print(f"ssh {vps_user}@{vps_ip} 'cd /root/trading_bot && source venv/bin/activate && nohup python3 RUN_BOT.py --testnet --auto-confirm > bot.log 2>&1 &'")
    
    print("\n" + "=" * 50)
    print("🎯 MANUAL DEPLOYMENT STEPS:")
    print("1. Run the backup commands")
    print("2. Copy the files using scp")
    print("3. Install dependencies")
    print("4. Test the systems")
    print("5. Restart the bot")
    print("=" * 50)

if __name__ == "__main__":
    main()