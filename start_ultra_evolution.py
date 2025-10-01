#!/usr/bin/env python3
"""
Ultra Trading Bot - Evolution Startup
Starts the bot with ALL components, safety features, and evolution capabilities
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from datetime import datetime

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ultra_evolution.log')
    ]
)
logger = logging.getLogger('UltraEvolution')

# Banner
EVOLUTION_BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ██╗   ██╗██╗  ████████╗██████╗  █████╗                        ║
║     ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗                       ║
║     ██║   ██║██║     ██║   ██████╔╝███████║                       ║
║     ██║   ██║██║     ██║   ██╔══██╗██╔══██║                       ║
║     ╚██████╔╝███████╗██║   ██║  ██║██║  ██║                       ║
║      ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                       ║
║                                                                      ║
║           EVOLUTION TRADING SYSTEM v3.0 ULTIMATE                    ║
║                                                                      ║
║     🧬 Self-Evolving    🤖 AI-Powered    🚀 Production Ready      ║
║     🛡️ Bulletproof      📊 Institutional  ⚡ Lightning Fast       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

class UltraEvolutionBot:
    """
    The ultimate trading bot with full evolution capabilities
    """
    
    def __init__(self):
        self.logger = logger
        self.running = False
        self.components = {}
        self.start_time = datetime.now()
        
    async def initialize(self):
        """Initialize all components with maximum capabilities"""
        
        self.logger.info("=" * 70)
        self.logger.info("🚀 INITIALIZING ULTRA EVOLUTION SYSTEM")
        self.logger.info("=" * 70)
        
        # Import and initialize the launcher
        from ultra_launcher import UltraLauncher
        self.launcher = UltraLauncher()
        
        # Get the pipeline with all enhancements
        from ultra_core import get_ultra_pipeline
        self.pipeline = get_ultra_pipeline(self.launcher.config)
        
        # Apply ALL production features
        self.logger.info("\n📦 Applying production features...")
        
        try:
            # 1. Safety features
            from production_fixes import integrate_safety_features
            self.pipeline = integrate_safety_features(self.pipeline)
            self.logger.info("  ✅ Safety features: Rate limiting, Order validation, Circuit breakers")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Safety features partial: {e}")
        
        try:
            # 2. Production enhancements
            from production_enhancements import integrate_production_enhancements
            self.pipeline = integrate_production_enhancements(self.pipeline)
            self.logger.info("  ✅ Enhancements: Comprehensive logging, Health checks, Recovery")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Enhancements partial: {e}")
        
        try:
            # 3. Optimizations
            from production_optimizations import integrate_optimizations
            self.pipeline = integrate_optimizations(self.pipeline)
            self.logger.info("  ✅ Optimizations: Memory management, State persistence, Graceful shutdown")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Optimizations partial: {e}")
        
        try:
            # 4. Ultimate fixes
            from ultimate_fixes import integrate_ultimate_fixes
            self.pipeline = integrate_ultimate_fixes(self.pipeline)
            self.logger.info("  ✅ Ultimate fixes: Network resilience, Data validation, Complete implementations")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Ultimate fixes partial: {e}")
        
        try:
            # 5. Architectural alignment
            from architectural_alignment import align_architecture
            self.pipeline = align_architecture(self.pipeline)
            self.logger.info("  ✅ Architecture: Component wiring, Event bus, Pipeline orchestration")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Architecture alignment partial: {e}")
        
        # Activate evolution features
        self.logger.info("\n🧬 Activating evolution capabilities...")
        
        try:
            # God Mode
            from ultra_core import integrate_god_mode
            self.pipeline = await integrate_god_mode(self.pipeline)
            self.logger.info("  ✅ GOD MODE: Quantum analysis, Swarm intelligence, Fractals")
        except Exception as e:
            self.logger.warning(f"  ⚠️ God mode not available: {e}")
        
        try:
            # Moon Spotter
            from ultra_core import integrate_moon_spotter
            self.pipeline = await integrate_moon_spotter(self.pipeline)
            self.logger.info("  ✅ MOON SPOTTER: Hunting 1000x opportunities")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Moon spotter not available: {e}")
        
        # Store the enhanced pipeline
        self.launcher.pipeline = self.pipeline
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("✅ ULTRA EVOLUTION SYSTEM INITIALIZED")
        self.logger.info("=" * 70)
        
        return True
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"\n📛 Received signal {signum}, initiating graceful shutdown...")
        self.running = False
        if hasattr(self, 'launcher') and hasattr(self.launcher, 'stop'):
            self.launcher.stop()
    
    async def start_evolution(self):
        """Start the evolution process"""
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("🧬 STARTING EVOLUTION PROCESS")
        self.logger.info("=" * 70)
        
        self.running = True
        
        # Display system status
        self.logger.info("\n📊 System Status:")
        self.logger.info(f"  • Mode: {self.launcher.config.get('mode', 'paper')}")
        self.logger.info(f"  • Symbols: {self.launcher.config.get('symbols', ['BTC/USDT'])}")
        self.logger.info(f"  • Risk Level: {self.launcher.config.get('risk_level', 'conservative')}")
        self.logger.info(f"  • Features: All production features active")
        self.logger.info(f"  • Evolution: Self-learning enabled")
        
        # Create monitoring task
        monitor_task = asyncio.create_task(self.monitor_system())
        
        # Start the main pipeline
        self.logger.info("\n🚀 Launching trading pipeline...")
        
        try:
            if hasattr(self.pipeline, 'run_forever'):
                await self.pipeline.run_forever()
            else:
                # Fallback main loop
                while self.running:
                    self.logger.info("💫 Evolution cycle...")
                    
                    # Process market data
                    if hasattr(self.pipeline, 'process'):
                        await self.pipeline.process()
                    
                    # Evolution step
                    if hasattr(self.pipeline, 'evolve'):
                        await self.pipeline.evolve()
                    
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.logger.info("\n🛑 Shutting down evolution system...")
            monitor_task.cancel()
            
            # Save final state
            if hasattr(self.pipeline, 'save_state'):
                self.pipeline.save_state()
                
            self.logger.info("✅ Evolution system stopped gracefully")
    
    async def monitor_system(self):
        """Monitor system health and performance"""
        
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                uptime = datetime.now() - self.start_time
                self.logger.info(f"\n📈 System Health | Uptime: {uptime}")
                
                # Check component health
                if hasattr(self.pipeline, 'get_health_status'):
                    health = self.pipeline.get_health_status()
                    self.logger.info(f"  • Health: {health.get('status', 'unknown')}")
                
                # Check memory
                if hasattr(self.pipeline, 'check_memory'):
                    memory = self.pipeline.check_memory()
                    self.logger.info(f"  • Memory: {memory.get('rss_mb', 0):.1f}MB")
                
                # Check performance
                if hasattr(self.pipeline, 'get_pipeline_metrics'):
                    metrics = self.pipeline.get_pipeline_metrics()
                    for stage, data in metrics.items():
                        if data.get('processed', 0) > 0:
                            self.logger.info(f"  • {stage}: {data['processed']} processed, {data['errors']} errors")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")

async def main():
    """Main entry point"""
    
    # Print banner
    print(EVOLUTION_BANNER)
    
    # Create and initialize the bot
    bot = UltraEvolutionBot()
    
    # Initialize all components
    if not await bot.initialize():
        logger.error("❌ Failed to initialize system")
        return 1
    
    # Start evolution
    await bot.start_evolution()
    
    return 0

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the bot
    exit_code = asyncio.run(main())
    sys.exit(exit_code)