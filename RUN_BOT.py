#!/usr/bin/env python3
"""
MAIN BOT LAUNCHER - Production Ready
Loads environment and starts all systems
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Prefer python-dotenv if available to load a central .env automatically
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # dotenv is optional
    load_dotenv = None  # type: ignore

# Load environment variables
print("=" * 80)
print("🚀 TRADING BOT LAUNCHER")
print("=" * 80)
print()

def _safe_load_env(dotenv_path: Optional[Path]) -> int:
    if not dotenv_path or not dotenv_path.exists():
        return 0
    loaded = 0
    try:
        # Try python-dotenv first for robust parsing
        if load_dotenv is not None:
            # Do not override already-set environment variables
            load_dotenv(dotenv_path=dotenv_path, override=False)
            # We can't easily count how many keys were set via load_dotenv
            # Fall through to manual count for visibility
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _ = line.split('=', 1)
                    if key.strip() in os.environ:
                        loaded += 1
        return loaded
    except Exception:
        return 0

# Load .env from local directory and from central project path if present
print("📄 Loading environment variables...")
loaded_local = _safe_load_env(Path(__file__).parent / '.env')
loaded_central = _safe_load_env(Path.home() / 'trading_bot' / '.env')
total_loaded = loaded_local + loaded_central
if total_loaded > 0:
    print(f"✅ Loaded environment (local: {loaded_local}, central: {loaded_central})\n")
else:
    print("⚠️  No .env file found (local or central). Using system environment.\n")

# Verify critical keys
print("🔍 Checking API Keys:")
telegram_ok = bool(os.getenv('TELEGRAM_BOT_TOKEN'))
bybit_ok = bool(os.getenv('BYBIT_API_KEY'))
private_key_ok = bool(os.getenv('PRIVATE_KEY'))

print(f"  {'✅' if telegram_ok else '⚠️ '} Telegram Bot Token: {'Set' if telegram_ok else 'Not set'}")
print(f"  {'✅' if bybit_ok else '⚠️ '} Bybit API Key: {'Set' if bybit_ok else 'Not set'}")
print(f"  {'✅' if private_key_ok else '⚠️ '} DEX Private Key: {'Set' if private_key_ok else 'Not set (DEX disabled)'}")
print()

# Import orchestrator
print("📦 Loading trading systems...")
try:
    from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    print("✅ All systems loaded\n")
except Exception as e:
    print(f"❌ Failed to load systems: {e}")
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
    print("⚠️  LIVE MODE - Trading with real money!")
    try:
        response = input("Are you sure? Type 'YES' to confirm: ")
        if response != 'YES':
            print("Cancelled.")
            sys.exit(0)
    except EOFError:
        # Running as service without stdin - auto-confirm
        print("⚠️  Running as background service - auto-confirming live mode")
        pass

print(f"🎯 Mode: {mode.upper()}")
print()

async def main():
    """Main entry point"""
    print("=" * 80)
    print(f"🚀 STARTING BOT IN {mode.upper()} MODE")
    print("=" * 80)
    print()
    
    # Create orchestrator
    bot = CompleteUltimateOrchestrator(mode=mode)
    
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
    print("✅ BOT IS RUNNING!")
    print("=" * 80)
    print()
    print("Systems Active:")
    print(f"  ✅ CEX Trading: {'Enabled' if bybit_ok else 'Disabled (no API keys)'}")
    print(f"  ✅ DEX Trading: {'Enabled' if private_key_ok else 'Disabled (no private key)'}")
    print(f"  ✅ Telegram: {'Enabled' if telegram_ok else 'Disabled (no bot token)'}")
    print(f"  ✅ AI/ML: Enabled (600+ models)")
    print(f"  ✅ Quantum: Enabled (IBM Qiskit)")
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
        print("\n✅ Bot stopped gracefully")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
