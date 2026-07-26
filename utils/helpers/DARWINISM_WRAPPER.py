#!/usr/bin/env python3
"""
DARWINISM_WRAPPER - Simple integration wrapper
Makes it easy to add Darwinism to any code
"""

from ENGINE_DARWINISM import get_darwinism_system
import logging

logger = logging.getLogger(__name__)

# Initialize once
_darwin = None

def get_darwin():
    global _darwin
    if _darwin is None:
        try:
            _darwin = get_darwinism_system()
            logger.info("[DARWINISM] System initialized")
        except Exception as e:
            logger.error(f"[DARWINISM] Init failed: {e}")
            _darwin = None
    return _darwin

def record_signal_safe(engine_name, symbol, confidence):
    """Safe wrapper that never crashes"""
    try:
        darwin = get_darwin()
        if darwin:
            darwin.record_signal(engine_name, symbol, confidence)
            logger.debug(f"[DARWINISM] Recorded signal: {engine_name} {symbol} {confidence:.0%}")
    except Exception as e:
        logger.debug(f"[DARWINISM] record_signal error (non-fatal): {e}")

def record_trade_safe(engine_name, symbol, outcome, profit_pct):
    """Safe wrapper that never crashes"""
    try:
        darwin = get_darwin()
        if darwin:
            darwin.record_trade(engine_name, symbol, outcome, profit_pct)
            logger.info(f"[DARWINISM] Recorded trade: {engine_name} {symbol} {outcome} {profit_pct:.2%}")
    except Exception as e:
        logger.debug(f"[DARWINISM] record_trade error (non-fatal): {e}")

def get_engine_influence_safe(engine_name):
    """Safe wrapper that returns 1.0 on error"""
    try:
        darwin = get_darwin()
        if darwin:
            influence = darwin.get_engine_influence(engine_name)
            return influence if influence else 1.0
        return 1.0
    except Exception as e:
        logger.debug(f"[DARWINISM] get_influence error (non-fatal): {e}")
        return 1.0
