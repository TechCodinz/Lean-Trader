import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Dict, List
class ScalpingCoordinator:
    """
    Coordinates aggressive scalping with risk management
    
    Ensures:
    - Not too many simultaneous scalps
    - Proper position sizing
    - Fast execution
    - Quick exits
    """
    
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
        self.active_scalps = []  # List of active scalp positions
        self.completed_scalps = []  # List of completed scalps
        
        logger.info(f"📊 Scalping Coordinator initialized")
        logger.info(f"   Max concurrent scalps: {max_concurrent}")
    
    def can_take_scalp(self) -> bool:
        """Check if we can take another scalp"""
        return len(self.active_scalps) < self.max_concurrent
    
    def add_scalp(self, signal: Dict):
        """Track new scalp"""
        self.active_scalps.append({
            'signal': signal,
            'opened_at': datetime.now(),
            'symbol': signal.get('symbol')
        })
    
    def close_scalp(self, symbol: str, profit_pct: float):
        """Mark scalp as closed"""
        # Remove from active
        self.active_scalps = [s for s in self.active_scalps if s['symbol'] != symbol]
        
        # Add to completed
        self.completed_scalps.append({
            'symbol': symbol,
            'closed_at': datetime.now(),
            'profit_pct': profit_pct
        })
    
    def get_performance(self) -> Dict:
        """Get scalping performance"""
        if not self.completed_scalps:
            return {
                'total_scalps': 0,
                'avg_profit': 0,
                'win_rate': 0
            }
        
        total = len(self.completed_scalps)
        wins = len([s for s in self.completed_scalps if s['profit_pct'] > 0])
