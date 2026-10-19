#!/usr/bin/env python3
"""
LeanTrader Signal Bus (2026 ultra-rare advanced enhancement).

The nervous system connections — routes signals between the 16 systems.

Architecture:
  SENSORS (publish) → BUS → BRAINS (process) → BUS → EXECUTORS (trade)
                                                        ↓
  OUTCOMES → BUS → LEARNERS (learn)

Uses file-based blackboard (simple, reliable, no dependencies):
  /tmp/nervous_system/signals/   — raw signals from sensors
  /tmp/nervous_system/decisions/ — processed by brains
  /tmp/nervous_system/outcomes/  — trade results from executors

Each signal is a JSON file: {timestamp, source, symbol, signal, confidence, metadata}
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SIGNAL_BUS')

BASE = Path('/tmp/nervous_system')
SIGNALS_DIR = BASE / 'signals'
DECISIONS_DIR = BASE / 'decisions'
OUTCOMES_DIR = BASE / 'outcomes'


def init_dirs():
    """Create the blackboard directories."""
    for d in [SIGNALS_DIR, DECISIONS_DIR, OUTCOMES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def publish_signal(source, symbol, signal, confidence, metadata=None):
    """Publish a raw signal from a sensor."""
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'source': source,
        'symbol': symbol,
        'signal': signal,  # BUY, SELL, HOLD
        'confidence': confidence,
        'metadata': metadata or {},
        'status': 'raw'
    }
    fname = f"{int(time.time()*1000)}_{source}_{symbol.replace('/', '_')}.json"
    with open(SIGNALS_DIR / fname, 'w') as f:
        json.dump(data, f)
    logger.info(f"📡 Signal: {source} → {symbol} {signal} ({confidence}%)")


def publish_decision(brain, symbol, signal, confidence, reasoning, metadata=None):
    """Publish a processed decision from a brain."""
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'brain': brain,
        'symbol': symbol,
        'signal': signal,
        'confidence': confidence,
        'reasoning': reasoning,
        'metadata': metadata or {},
        'status': 'processed'
    }
    fname = f"{int(time.time()*1000)}_{brain}_{symbol.replace('/', '_')}.json"
    with open(DECISIONS_DIR / fname, 'w') as f:
        json.dump(data, f)
    logger.info(f"🧠 Decision: {brain} → {symbol} {signal} ({confidence}%)")


def publish_outcome(executor, symbol, signal, price, size, success):
    """Publish a trade outcome from an executor."""
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'executor': executor,
        'symbol': symbol,
        'signal': signal,
        'price': price,
        'size': size,
        'success': success,
        'status': 'completed'
    }
    fname = f"{int(time.time()*1000)}_{executor}_{symbol.replace('/', '_')}.json"
    with open(OUTCOMES_DIR / fname, 'w') as f:
        json.dump(data, f)
    logger.info(f"✅ Outcome: {executor} {symbol} {signal} @ {price}")


def get_pending_signals():
    """Get all unprocessed signals."""
    signals = []
    for f in SIGNALS_DIR.glob('*.json'):
        with open(f) as fh:
            data = json.load(fh)
            if data.get('status') == 'raw':
                signals.append((f, data))
    return signals


def get_pending_decisions(min_confidence=85):
    """Get processed decisions above confidence threshold."""
    decisions = []
    for f in DECISIONS_DIR.glob('*.json'):
        with open(f) as fh:
            data = json.load(fh)
            if data.get('status') == 'processed' and data.get('confidence', 0) >= min_confidence:
                decisions.append((f, data))
    return decisions


def main():
    logger.info("🚌 Starting Signal Bus (ultra-rare advanced)")
    logger.info("   Connecting the 16-system nervous system...")
    
    init_dirs()
    logger.info(f"✅ Blackboard ready: {BASE}")
    logger.info("")
    logger.info("Signal flow:")
    logger.info("  SENSORS → signals/ → BRAINS → decisions/ → EXECUTORS")
    logger.info("                                              ↓")
    logger.info("  OUTCOMES → outcomes/ → LEARNERS")
    logger.info("")
    
    # Monitor loop — log bus activity
    try:
        while True:
            time.sleep(60)
            n_signals = len(list(SIGNALS_DIR.glob('*.json')))
            n_decisions = len(list(DECISIONS_DIR.glob('*.json')))
            n_outcomes = len(list(OUTCOMES_DIR.glob('*.json')))
            logger.info(f"🚌 Bus: {n_signals} signals, {n_decisions} decisions, {n_outcomes} outcomes")
    except KeyboardInterrupt:
        logger.info("🛑 Signal Bus stopped")


if __name__ == "__main__":
    # Also expose functions for import
    main()
