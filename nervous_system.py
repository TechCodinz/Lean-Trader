#!/usr/bin/env python3
"""
LeanTrader Nervous System Launcher (2025 pattern + 2026 enhancement).

Starts all 14 intelligent systems as microservices.
Monitors them and restarts any that die — keeps the being ALIVE.

This is the missing piece: the 2025 system used systemd for persistence.
The 2026 container has no supervisor, so services die on restart.

Usage: python3 nervous_system.py
"""

import subprocess
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NERVOUS_SYSTEM')

# The 14 intelligent systems
SERVICES = [
    # PARKED 2026-10-19: separate exit-manager trial later (Peters 2026-10-19)
    #("profit_taker", "/app/profit_taker_service.py", "/tmp/apt_service.log"),
    # PARKED 2026-10-19: needs langchain + LLM API decision - Phase D
    #("evolution", "/app/evolution_service.py", "/tmp/evo_service.log"),
    ("scanner", "/app/scanner_service.py", "/tmp/scanner_service.log"),
    ("scalper", "/app/scalp_service.py", "/tmp/scalp_service.log"),
    ("ultra_ai", "/app/ultra_ai_service.py", "/tmp/ultra_ai_service.log"),
    ("strategy_brain", "/app/strategy_brain_service.py", "/tmp/strategy_brain_service.log"),
    ("sentient_brain", "/app/sentient_brain_service.py", "/tmp/sentient_brain_service.log"),
    ("hivemind", "/app/hivemind_service.py", "/tmp/hivemind_service.log"),
    ("risk", "/app/risk_service.py", "/tmp/risk_service.log"),
    ("online_learner", "/app/online_learner_service.py", "/tmp/online_learner_service.log"),
    ("paper_broker", "/app/paper_broker_service.py", "/tmp/paper_broker_service.log"),
    ("moon_spotter", "/app/moon_spotter_service.py", "/tmp/moon_spotter_service.log"),
    ("pattern_memory", "/app/pattern_memory_service.py", "/tmp/pattern_memory_service.log"),
    ("divine_core", "/app/divine_core_service.py", "/tmp/divine_core_service.log"),
]


def is_running(name):
    """Check if a service is running (container has no ps - scan /proc)."""
    import os
    script = {n: sc for n, sc, _ in SERVICES}[name]
    needle = script.encode()
    for pid in os.listdir('/proc'):
        if not pid.isdigit() or int(pid) == os.getpid():
            continue
        try:
            with open(f'/proc/{pid}/cmdline', 'rb') as f:
                if needle in f.read():
                    return True
        except Exception:
            pass
    return False


def start_service(name, script, logfile):
    """Start a service with nohup."""
    logger.info(f"🚀 Starting {name}...")
    subprocess.Popen(
        ["bash", "-c", f"nohup python3 {script} > {logfile} 2>&1 &"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)


def main():
    logger.info("🧬 LeanTrader Nervous System Launcher")
    logger.info(f"   Managing {len(SERVICES)} intelligent systems")
    
    # Start all services
    for name, script, logfile in SERVICES:
        if not is_running(name):
            start_service(name, script, logfile)
        else:
            logger.info(f"✅ {name} already running")
    
    logger.info("✅ All systems launched. Monitoring...")
    
    # Monitor loop — restart dead services
    try:
        while True:
            time.sleep(60)
            for name, script, logfile in SERVICES:
                if not is_running(name):
                    logger.warning(f"⚠️ {name} died — restarting...")
                    start_service(name, script, logfile)
    except KeyboardInterrupt:
        logger.info("🛑 Nervous System shutdown")


if __name__ == "__main__":
    main()
