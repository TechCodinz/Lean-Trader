#!/usr/bin/env python3
"""
ELITE STACK RUNNER

Simple wrapper to run Elite Stack alongside existing orchestrator.
Uses singleton access pattern to hook into orchestrator without modifying 6800 lines.

Usage:
    python3 ELITE_STACK_RUNNER.py

Or integrate directly in orchestrator start() method.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from elite_stack.integration import EliteStackIntegration
from elite_stack.telemetry import EliteTelemetry
from elite_stack.models import SymbolClass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EliteStackRunner:
    """Elite Stack integration runner"""
    
    def __init__(self):
        """Initialize Elite Stack"""
        logger.info("=" * 80)
        logger.info("INITIALIZING ELITE STACK - GOD MODE DECISION FRAMEWORK")
        logger.info("=" * 80)
        
        try:
            # Initialize Elite Stack
            self.elite_stack = EliteStackIntegration(
                enable_elite_stack=True,
                enable_intent=True,
                enable_liquidity=True,
                enable_oce=True,
                enable_sps=True,
                enable_rmf=True,
                enable_afe=True,
                enable_crm=True,
                enable_heat=True,
                enable_blending=True
            )
            
            # Initialize Telemetry
            self.elite_telemetry = EliteTelemetry(
                enable_csv_export=True,
                csv_base_path="./data"
            )
            
            logger.info("[OK] ELITE STACK INITIALIZED SUCCESSFULLY")
            logger.info("   All 9 engines ready for god mode trading")
            
        except Exception as e:
            logger.error(f"[X] Elite Stack initialization failed: {e}")
            raise
    
    def get_symbol_class(self, symbol: str) -> SymbolClass:
        """Determine symbol class"""
        symbol_upper = symbol.upper()
        
        if "BTC" in symbol_upper or "ETH" in symbol_upper:
            return SymbolClass.CRYPTO_LARGE
        elif "XAU" in symbol_upper or "XAG" in symbol_upper:
            return SymbolClass.METAL
        elif any(x in symbol_upper for x in ["EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]):
            return SymbolClass.FX_MAJOR
        else:
            return SymbolClass.CRYPTO_ALT
    
    async def test_elite_stack(self):
        """Test Elite Stack with sample data"""
        import pandas as pd
        import numpy as np
        
        logger.info("\n" + "=" * 80)
        logger.info("TESTING ELITE STACK WITH SAMPLE DATA")
        logger.info("=" * 80)
        
        # Create sample OHLCV
        dates = pd.date_range('2024-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        close = 100 + np.cumsum(np.random.randn(100) * 0.5)
        high = close + np.abs(np.random.randn(100) * 0.3)
        low = close - np.abs(np.random.randn(100) * 0.3)
        
        sample_ohlcv = pd.DataFrame({
            'timestamp': dates,
            'open': close,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Test evaluation
        try:
            elite_context = self.elite_stack.evaluate_elite_context(
                ohlcv=sample_ohlcv,
                current_price=100.0,
                wave_state="IMPULSE",
                wave_flow_score=0.7,
                chaos_score=0.3,
                pitch_value=0.6,
                pitch_regime="normal",
                volatility=0.02,
                baseline_volatility=0.015,
                symbol="BTC/USDT",
                venue_type="CEX",
                symbol_class=SymbolClass.CRYPTO_LARGE,
                portfolio_size=10000.0,
                proposed_entry=100.0,
                proposed_size=1000.0,
                proposed_direction=1,
                stop_loss_pct=0.02,
                take_profit_pct=0.03
            )
            
            # Get decision
            final_action = elite_context.get_final_action()
            size_multiplier = elite_context.get_size_multiplier()
            
            logger.info(f"\n[OK] Elite Context Evaluated:")
            logger.info(f"   Final Action: {final_action}")
            logger.info(f"   Size Multiplier: {size_multiplier:.2f}")
            
            if elite_context.intent:
                logger.info(f"   Intent Bias: {elite_context.intent.intent_bias:+.2f}")
                logger.info(f"   Trap Risk: {elite_context.intent.trap_risk:.2f}")
            
            if elite_context.oce:
                logger.info(f"   OCE Decision: {elite_context.oce.oce_decision}")
                logger.info(f"   OCE Score: {elite_context.oce.oce_score:.2f}")
            
            if elite_context.rmf:
                logger.info(f"   RMF Action: {elite_context.rmf.final_action}")
                logger.info(f"   Regret TAKE: {elite_context.rmf.regret_take:.2f}")
                logger.info(f"   Regret SKIP: {elite_context.rmf.regret_skip:.2f}")
            
            # Log to telemetry
            self.elite_telemetry.log_elite_context(
                context=elite_context,
                symbol="BTC/USDT",
                venue="CEX",
                final_action=final_action
            )
            
            logger.info("\n[OK] Telemetry logged successfully")
            logger.info(f"   Check: ./data/elite_context_BTC_USDT_CEX.csv")
            
            return True
            
        except Exception as e:
            logger.error(f"[X] Elite Stack test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main entry point"""
    try:
        runner = EliteStackRunner()
        
        # Run test
        success = await runner.test_elite_stack()
        
        if success:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 ELITE STACK IS OPERATIONAL - GOD MODE READY 🎉")
            logger.info("=" * 80)
            logger.info("Next: Integrate into COMPLETE_ULTIMATE_ORCHESTRATOR.py")
            logger.info("Add these lines in the trading loop:")
            logger.info("")
            logger.info("# Initialize (in __init__):")
            logger.info("self.elite_runner = EliteStackRunner()")
            logger.info("")
            logger.info("# In trading loop (before trade):")
            logger.info("elite_context = self.elite_runner.elite_stack.evaluate_elite_context(...)")
            logger.info("final_action = elite_context.get_final_action()")
            logger.info("if final_action == 'SKIP': continue")
            logger.info("size *= elite_context.get_size_multiplier()")
        else:
            logger.error("Elite Stack test failed - check errors above")
    
    except Exception as e:
        logger.error(f"[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
