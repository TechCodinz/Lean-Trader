#!/usr/bin/env python3
"""
💰 PROFIT-READY INTEGRATION 💰
Seamlessly integrates COMPLETE_PROFIT_SYSTEM into the existing bot

This patches EXECUTION_ORCHESTRATOR to use direct Gate.io execution
instead of delegation that was failing.
"""

import asyncio
import logging
from typing import Dict, Optional
from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem

logger = logging.getLogger(__name__)


class ProfitReadyIntegration:
    """
    Patches the execution orchestrator to use COMPLETE_PROFIT_SYSTEM
    
    This replaces the broken delegation logic (self.engines['real_profit'].execute_trade())
    with DIRECT Gate.io execution that ACTUALLY works.
    """
    
    def __init__(self, execution_orchestrator, api_key: str = None, api_secret: str = None):
        self.orchestrator = execution_orchestrator
        self.profit_system = CompleteProfitSystem(api_key, api_secret)
        
        logger.info("=" * 80)
        logger.info("💰 PROFIT-READY INTEGRATION")
        logger.info("=" * 80)
        logger.info("   Patching execution orchestrator...")
        logger.info("   [OK] Direct Gate.io execution")
        logger.info("   [OK] Auto-adaptive position sizing")
        logger.info("   [OK] Active position monitoring")
        logger.info("   [OK] Intelligent profit-taking")
        logger.info("=" * 80)
    
    async def initialize(self):
        """Initialize profit system"""
        success = await self.profit_system.initialize()
        
        if success:
            # Patch the orchestrator
            self._patch_orchestrator()
            
            # Start monitoring loop in background
            asyncio.create_task(self.profit_system.run_monitoring_loop())
            
            logger.info("[OK] PROFIT-READY INTEGRATION COMPLETE!")
            logger.info(f"   Starting balance: ${self.profit_system.current_balance:.2f}")
            logger.info(f"   Current tier: {self.profit_system.current_tier.upper()}")
        else:
            logger.error("[X] Failed to initialize profit system!")
        
        return success
    
    def _patch_orchestrator(self):
        """Patch orchestrator's execute_trade method"""
        
        # Save original method
        original_execute = self.orchestrator.execute_trade
        
        # Create new method that uses COMPLETE_PROFIT_SYSTEM
        async def patched_execute_trade(symbol: str, side: str, confidence: float, signal: Dict) -> Optional[Dict]:
            """
            PATCHED execution - uses COMPLETE_PROFIT_SYSTEM directly!
            """
            logger.debug(f"🔧 Using COMPLETE_PROFIT_SYSTEM for {symbol}")
            
            # Use profit system for ACTUAL execution
            signal_data = {
                'symbol': symbol,
                'side': side,
                'confidence': confidence
            }
            
            result = await self.profit_system.execute_signal(signal_data)
            
            if result:
                logger.info(f"[OK] PROFIT SYSTEM executed: {symbol}")
            else:
                logger.debug(f" PROFIT SYSTEM skipped: {symbol}")
            
            return result
        
        # Replace method
        self.orchestrator.execute_trade = patched_execute_trade
        
        logger.info("[OK] Orchestrator patched - now uses COMPLETE_PROFIT_SYSTEM!")
    
    def get_stats(self) -> Dict:
        """Get comprehensive stats"""
        return {
            'profit_system': self.profit_system.get_stats(),
            'orchestrator': self.orchestrator.get_stats()
        }


async def integrate_profit_system(execution_orchestrator, api_key: str = None, api_secret: str = None):
    """
    Main integration function
    
    Usage:
        # In main orchestrator:
        integration = await integrate_profit_system(execution_orchestrator)
    """
    integration = ProfitReadyIntegration(execution_orchestrator, api_key, api_secret)
    success = await integration.initialize()
    
    if success:
        logger.info(">> PROFIT SYSTEM FULLY INTEGRATED AND ACTIVE!")
        return integration
    else:
        logger.error("[X] PROFIT SYSTEM INTEGRATION FAILED!")
        return None


# Export
__all__ = [
    'ProfitReadyIntegration',
    'integrate_profit_system'
]
