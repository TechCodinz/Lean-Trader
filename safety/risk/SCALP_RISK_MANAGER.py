
import time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ScalpRiskManager:
    def __init__(self):
        self.per_symbol_cooldown_seconds = 30
        self.max_open_trades_per_venue = 3
        self._last_trade_time: Dict[str, float] = {}
        self._open_trades: Dict[str, int] = {}
        
    def should_allow_new_trade(self, venue_id: str, symbol: str, side: str) -> Tuple[bool, str]:
        cooldown_key = f"{venue_id}_{symbol}_{side}"
        last_time = self._last_trade_time.get(cooldown_key, 0)
        time_since = time.time() - last_time
        
        if time_since < self.per_symbol_cooldown_seconds:
            return False, f"COOLDOWN ({self.per_symbol_cooldown_seconds - int(time_since)}s remaining)"
        
        open_count = self._open_trades.get(venue_id, 0)
        if open_count >= self.max_open_trades_per_venue:
            return False, f"MAX_OPEN ({open_count}/{self.max_open_trades_per_venue})"
        
        return True, "OK"
    
    def record_trade_open(self, venue_id: str, symbol: str, side: str, order_id: str):
        cooldown_key = f"{venue_id}_{symbol}_{side}"
        self._last_trade_time[cooldown_key] = time.time()
        self._open_trades[venue_id] = self._open_trades.get(venue_id, 0) + 1
        logger.debug(f"📊 Open trades on {venue_id}: {self._open_trades[venue_id]}")
    
    def record_trade_close(self, venue_id: str):
        if venue_id in self._open_trades and self._open_trades[venue_id] > 0:
            self._open_trades[venue_id] -= 1

_risk_manager = ScalpRiskManager()

def get_scalp_risk_manager() -> ScalpRiskManager:
    return _risk_manager

