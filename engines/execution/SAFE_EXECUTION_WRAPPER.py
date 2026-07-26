#!/usr/bin/env python3
# SAFE_EXECUTION_WRAPPER.py
# Wraps execution to handle and bypass errors

import logging
logger = logging.getLogger(__name__)

def safe_execute_with_bridge(orchestrator_self, signals):
    '''Safely execute signals using Bybit bridge'''
    if not signals:
        return
    
    try:
        # Import bridge
        from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge
        bridge = get_bybit_bridge()
        
        # Execute each signal
        for signal in signals[:3]:  # Max 3 per cycle
            try:
                result = bridge.execute_signal(signal)
                if result:
                    logger.info(f"Bridge execution successful: {signal.get('symbol')}")
            except Exception as e:
                logger.error(f"Bridge execution failed for {signal.get('symbol')}: {e}")
                
    except Exception as e:
        logger.error(f"Safe execution wrapper error: {e}")

def get_safe_executor():
    return safe_execute_with_bridge
