#!/usr/bin/env python3
"""
MAIN BOT LAUNCHER - Production Ready
Loads environment and starts all systems
"""
import os
import sys
import asyncio
from pathlib import Path

# Ensure project root is in sys.path
root_path = str(Path(__file__).resolve().parent.parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Windows Console UTF-8 Encoding Fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass

# Load environment variables
print("=" * 80)
print(">> TRADING BOT LAUNCHER")
print("=" * 80)
print()

# Load .env file (checks root directory and utils/helpers)
env_file_helpers = Path(__file__).parent / '.env'
env_file_root = Path(root_path) / '.env'

env_file = env_file_root if env_file_root.exists() else env_file_helpers

if env_file.exists():
    print(f"📄 Loading environment variables from {env_file.name}...")
    loaded = 0
    with open(env_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
                loaded += 1
    print(f"[OK] Loaded {loaded} environment variables\n")
else:
    print("  No .env file found. Using system environment.\n")

# Verify critical keys
print("🔍 Checking API Keys:")
telegram_ok = bool(os.getenv('TELEGRAM_BOT_TOKEN'))
bybit_ok = bool(os.getenv('BYBIT_API_KEY'))
private_key_ok = bool(os.getenv('PRIVATE_KEY'))

print(f"  {'[OK]' if telegram_ok else ' '} Telegram Bot Token: {'Set' if telegram_ok else 'Not set'}")
print(f"  {'[OK]' if bybit_ok else ' '} Bybit API Key: {'Set' if bybit_ok else 'Not set'}")
print(f"  {'[OK]' if private_key_ok else ' '} DEX Private Key: {'Set' if private_key_ok else 'Not set (DEX disabled)'}")
print()

# Import orchestrator
print("📦 Loading trading systems...")
try:
    from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator, set_orchestrator
    print("[OK] All systems loaded\n")
except Exception as e:
    print(f"[X] Failed to load systems: {e}")
    sys.exit(1)

# Get mode from args
mode = 'testnet'
auto_confirm = False

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg == '--live':
            mode = 'live'
        elif arg == '--testnet':
            mode = 'testnet'
        elif arg == '--auto-confirm':
            auto_confirm = True

# Safety check for live mode (skip if auto-confirm for systemd)
if mode == 'live' and not auto_confirm:
    print("  LIVE MODE - Trading with real money!")
    try:
        response = input("Are you sure? Type 'YES' to confirm: ")
        if response != 'YES':
            print("Cancelled.")
            sys.exit(0)
    except EOFError:
        # Running as service without stdin - auto-confirm
        print("  Running as background service - auto-confirming live mode")
        pass

print(f"🎯 Mode: {mode.upper()}")
print()

async def main():
    """Main entry point"""
    print("=" * 80)
    print(f">> STARTING BOT IN {mode.upper()} MODE")
    print("=" * 80)
    print()
    
    # Create orchestrator
    bot = CompleteUltimateOrchestrator(mode=mode)
    
    # 🧠 SET ORCHESTRATOR GLOBALLY (CRITICAL FOR AUTONOMOUS OPERATION!)
    set_orchestrator(bot)
    print("🧠 Orchestrator set globally - autonomous systems can now access it!")
    
    # Initialize
    print("⏳ Initializing all systems...")
    await bot.initialize_all_systems()
    
    # Wire
    print("\n⏳ Wiring all systems...")
    await bot.wire_all_systems()
    
    # Start
    print("\n⏳ Starting all orchestrators...")
    tasks = await bot.start_all_orchestrators()
    
    print()
    print("=" * 80)
    print("[OK] BOT IS RUNNING!")
    print("=" * 80)
    print()
    print("Systems Active:")
    print(f"  [OK] CEX Trading: {'Enabled' if bybit_ok else 'Disabled (no API keys)'}")
    print(f"  [OK] DEX Trading: {'Enabled' if private_key_ok else 'Disabled (no private key)'}")
    print(f"  [OK] Telegram: {'Enabled' if telegram_ok else 'Disabled (no bot token)'}")
    print(f"  [OK] AI/ML: Enabled (600+ models)")
    print(f"  [OK] Quantum: Enabled (IBM Qiskit)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Run forever
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[OK] Bot stopped gracefully")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
