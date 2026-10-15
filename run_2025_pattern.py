#!/usr/bin/env python3
"""
LeanTrader 2025 Pattern Runner — Orchestrator Master.

2025 pattern (correct):
- RPB.analyze_market() → signals (RPB does NOT execute)
- Orchestrator.execute_trade() → smart execution (MASTER)

Fixes v3 mistake where RPB executed directly.
"""

import asyncio
import logging
import sys
import time

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('2025_RUNNER')


async def main():
    logger.info("🌟 LeanTrader 2025 Pattern Runner")
    logger.info("   RPB: signal generator (does NOT execute)")
    logger.info("   Orchestrator: master execution")
    
    # Initialize RPB as signal generator
    from REAL_PROFIT_BOT import RealProfitBot
    rpb = RealProfitBot(mode='testnet')
    logger.info(f"✅ RPB initialized (9 pairs, signal only)")
    
    # Initialize Orchestrator as master
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    
    class SimpleDataHub:
        def __init__(self):
            self.alert_queue = asyncio.Queue()
        async def publish_trade(self, trade):
            pass
    
    orchestrator = ExecutionOrchestrator(
        data_hub=SimpleDataHub(),
        trading_engines={'rpb': rpb},
        risk_engine=None,
        ledger=[],
        mode='testnet'
    )
    logger.info(f"✅ Orchestrator initialized (master, testnet)")
    
    # 2025 trading loop: RPB signals → Orchestrator executes
    cycle = 0
    while True:
        cycle += 1
        logger.info(f"🔄 Cycle {cycle}: RPB signals → Orchestrator executes")
        
        for pair in rpb.crypto_pairs:
            try:
                # RPB generates signal (does NOT execute)
                signal, confidence, price, change, volume = rpb.analyze_market(pair)
                
                # 85% gate (2025)
                if signal in ('BUY', 'SELL') and confidence >= 85:
                    logger.info(f"📡 Signal: {pair} {signal} @ {confidence}%")
                    
                    # Orchestrator executes with smart sizing (MASTER)
                    signal_dict = {
                        'price': price,
                        'change': change,
                        'volume': volume,
                        'source': 'rpb'
                    }
                    result = await orchestrator.execute_trade(
                        symbol=pair,
                        side=signal,
                        confidence=confidence / 100.0,
                        signal=signal_dict
                    )
                    if result:
                        logger.info(f"✅ Orchestrator executed: {pair}")
                
            except Exception as e:
                logger.error(f"Error on {pair}: {e}")
        
        logger.info(f"✅ Cycle {cycle} complete")
        await asyncio.sleep(15)  # 2025 cadence


if __name__ == '__main__':
    asyncio.run(main())
