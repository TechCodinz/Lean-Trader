#!/usr/bin/env python3
"""
Signal Bus Bridge - connects async systems to sync trader.

Async systems publish signals via signal_bus.
Sync trader (zoo_paper_trader) reads them.
This bridge ensures the format is correct.
"""
import sys
sys.path.insert(0, '/app')

from signal_bus import publish_signal, get_pending_signals
import logging

logger = logging.getLogger('BUS_BRIDGE')

def publish_async_signal(source, symbol, signal, confidence, metadata=None):
    """Async systems call this to publish signals."""
    publish_signal(source, symbol, signal, confidence, metadata)
    logger.info(f"Signal published: {source} {symbol} {signal} {confidence}%")

def get_signals_for_trader(min_confidence=70):
    """Sync trader calls this to get signals."""
    signals = get_pending_signals()
    # Filter by confidence
    filtered = [s for s in signals if s.get('confidence', 0) >= min_confidence]
    return filtered

if __name__ == '__main__':
    print("Signal Bus Bridge ready")
