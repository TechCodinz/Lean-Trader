#!/usr/bin/env python3
"""
🚀 LEAN-TRADER ONE-CLICK ROOT LAUNCHER
═══════════════════════════════════════════════════════════════════
Launches the autonomous trading entity directly from the root workspace directory.

Usage:
  python RUN_LEAN_TRADER.py --testnet   # Run with simulated testnet funds (0 risk)
  python RUN_LEAN_TRADER.py --live      # Run live trading
"""

import sys
import subprocess
from pathlib import Path

def main():
    bot_script = Path(__file__).parent / "utils" / "helpers" / "RUN_BOT.py"
    args = [sys.executable, str(bot_script)] + sys.argv[1:]
    sys.exit(subprocess.call(args))

if __name__ == "__main__":
    main()
