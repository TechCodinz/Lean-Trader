import sys; sys.path.insert(0, '/app')
import asyncio, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NERVOUS')

class NervousSystem:
    """Central intelligence bus. All systems publish/subscribe here."""
    def __init__(self):
        self.subscribers = []  # Engines that want market data
        self.memories = {}     # Shared Pattern/Brain/Core
        self.performance = {}  # Track which engine wins
        self.signals = asyncio.Queue()
        
    def subscribe(self, engine):
        self.subscribers.append(engine)
        logger.info(f"🧠 {engine.__class__.__name__} joined the nervous system")
    
    async def broadcast_market(self, trending):
        """One scan, all engines see it. No duplicate work."""
        for engine in self.subscribers:
            try:
                await engine.on_market(trending)
            except Exception as e:
                logger.error(f"{engine.__class__.__name__}: {e}")
    
    def record_outcome(self, engine_name, symbol, pnl):
        """All learnings flow to shared memory."""
        if engine_name not in self.performance:
            self.performance[engine_name] = {'trades': 0, 'pnl': 0.0}
        self.performance[engine_name]['trades'] += 1
        self.performance[engine_name]['pnl'] += pnl
        logger.info(f"📝 {engine_name}: {pnl:+.2f}% | Total: {self.performance[engine_name]['pnl']:+.2f}%")

# Global instance - import this in all components
nervous = NervousSystem()
