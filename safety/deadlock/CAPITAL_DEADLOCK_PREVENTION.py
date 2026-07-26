#!/usr/bin/env python3
"""
CAPITAL_DEADLOCK_PREVENTION.py
Universal capital management with guaranteed release on failure
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class CapitalManager:
    """Manage capital reservations with deadlock prevention"""
    
    def __init__(self, reports_dir: str = "/root/bot/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Event log
        self.events_file = self.reports_dir / 'profit_events.jsonl'
        
        # Capital tracking
        self.reserved = {}  # trade_id -> {amount, timestamp, symbol, side}
        self.total_reserved = 0
        self.total_released = 0
        self.release_events = []
        
        # Orphan detection
        self.pending_orders = {}  # trade_id -> {timestamp, exchange_order_id}
        self.orphan_timeout = 30  # seconds
    
    def reserve_capital(self, trade_id: str, symbol: str, side: str, amount: float):
        """Reserve capital for a trade"""
        self.reserved[trade_id] = {
            'amount': amount,
            'timestamp': time.time(),
            'symbol': symbol,
            'side': side
        }
        
        self.total_reserved += amount
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'CAPITAL_RESERVED',
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'amount': amount
        }
        
        self._log_event(event)
        logger.info(f"💰 CAPITAL RESERVED: {trade_id} - ${amount:.2f}")
    
    def release_capital(self, trade_id: str, reason: str = "success"):
        """Release capital on success"""
        if trade_id not in self.reserved:
            logger.warning(f"Attempted to release non-reserved capital: {trade_id}")
            return
        
        reserved = self.reserved.pop(trade_id)
        amount = reserved['amount']
        self.total_released += amount
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'CAPITAL_RELEASED',
            'trade_id': trade_id,
            'symbol': reserved['symbol'],
            'amount': amount,
            'reason': reason
        }
        
        self._log_event(event)
        self.release_events.append(event)
        
        logger.info(f"✅ CAPITAL RELEASED: {trade_id} - ${amount:.2f} ({reason})")
    
    def release_on_failure(self, trade_id: str, reason: str, error_details: Optional[str] = None):
        """GUARANTEED release on order failure"""
        if trade_id not in self.reserved:
            logger.warning(f"Attempted to release on failure for non-reserved: {trade_id}")
            return
        
        reserved = self.reserved.pop(trade_id)
        amount = reserved['amount']
        self.total_released += amount
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'CAPITAL_RELEASED_ON_FAILURE',
            'trade_id': trade_id,
            'symbol': reserved['symbol'],
            'side': reserved['side'],
            'amount': amount,
            'reason': reason,
            'error_details': error_details
        }
        
        self._log_event(event)
        self.release_events.append(event)
        
        logger.warning(f"⚠️ CAPITAL RELEASED ON FAILURE: {trade_id} - ${amount:.2f}")
        logger.warning(f"   Reason: {reason}")
        if error_details:
            logger.warning(f"   Details: {error_details}")
    
    def register_pending_order(self, trade_id: str, exchange_order_id: Optional[str] = None):
        """Register order as pending"""
        self.pending_orders[trade_id] = {
            'timestamp': time.time(),
            'exchange_order_id': exchange_order_id
        }
    
    def confirm_order(self, trade_id: str):
        """Confirm order execution"""
        if trade_id in self.pending_orders:
            del self.pending_orders[trade_id]
    
    def check_orphaned_orders(self, exchange) -> List[str]:
        """Check for orphaned orders that never confirmed"""
        orphaned = []
        current_time = time.time()
        
        for trade_id, pending in list(self.pending_orders.items()):
            age = current_time - pending['timestamp']
            
            if age > self.orphan_timeout:
                # Order sent but no confirmation for > timeout
                logger.warning(f"🔍 ORPHAN ORDER DETECTED: {trade_id} (age: {age:.1f}s)")
                
                # Try to query exchange
                exchange_order_id = pending.get('exchange_order_id')
                if exchange_order_id:
                    try:
                        # Check if order exists on exchange
                        order = exchange.fetch_order(exchange_order_id)
                        if order['status'] == 'open' or order['status'] == 'closed':
                            # Order exists, confirm it
                            self.confirm_order(trade_id)
                            logger.info(f"✅ Orphan confirmed on exchange: {trade_id}")
                            continue
                    except:
                        pass
                
                # Order doesn't exist on exchange - release capital
                self.release_on_failure(
                    trade_id,
                    "ORPHAN_ORDER_TIMEOUT",
                    f"No confirmation after {age:.1f}s"
                )
                
                del self.pending_orders[trade_id]
                orphaned.append(trade_id)
        
        return orphaned
    
    def get_locked_capital(self) -> Dict:
        """Get currently locked capital"""
        locked = {}
        for trade_id, reserved in self.reserved.items():
            age = time.time() - reserved['timestamp']
            locked[trade_id] = {
                **reserved,
                'age_seconds': age
            }
        return locked
    
    def generate_integrity_report(self) -> Dict:
        """Generate capital integrity report"""
        locked = self.get_locked_capital()
        locked_total = sum(r['amount'] for r in locked.values())
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'reserved_total': self.total_reserved,
            'released_total': self.total_released,
            'locked_total': locked_total,
            'locked_trade_ids': list(locked.keys()),
            'locked_details': locked,
            'release_events_count': len(self.release_events),
            'last_50_releases': self.release_events[-50:],
            'orphaned_orders': len(self.pending_orders),
            'integrity_check': {
                'passes': locked_total <= self.total_reserved - self.total_released,
                'expected_locked': self.total_reserved - self.total_released,
                'actual_locked': locked_total,
                'discrepancy': (self.total_reserved - self.total_released) - locked_total
            }
        }
        
        # Save report
        report_file = self.reports_dir / 'capital_integrity_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Capital integrity report saved: {report_file}")
        
        return report
    
    def _log_event(self, event: Dict):
        """Log event to file"""
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

# Safe order placement wrapper
def safe_order_placement(exchange, capital_manager: CapitalManager,
                        trade_id: str, symbol: str, order_type: str,
                        side: str, amount: float, price: Optional[float] = None):
    """
    Universal safe order placement with guaranteed capital release
    
    Usage:
        result = safe_order_placement(
            exchange, capital_manager, trade_id,
            'BTC/USDT', 'market', 'BUY', 0.001
        )
        
        if result['success']:
            order = result['order']
            # proceed with TP logic
        else:
            # capital already released, skip
    """
    
    # Reserve capital
    cost_estimate = amount * (price if price else 50000)  # Rough estimate
    capital_manager.reserve_capital(trade_id, symbol, side, cost_estimate)
    
    # Register as pending
    capital_manager.register_pending_order(trade_id)
    
    try:
        # Place order
        order = exchange.create_order(symbol, order_type, side, amount, price)
        
        # Check response
        if not order or 'id' not in order:
            # No order ID - release capital
            capital_manager.release_on_failure(
                trade_id,
                "NO_ORDER_ID",
                f"Exchange returned: {order}"
            )
            return {'success': False, 'reason': 'no_order_id'}
        
        # Confirm order
        capital_manager.confirm_order(trade_id)
        capital_manager.register_pending_order(trade_id, order['id'])
        
        # Check if filled immediately
        if order['status'] == 'closed' or order['filled'] == order['amount']:
            # Order filled - release capital (moved to position)
            capital_manager.release_capital(trade_id, "order_filled")
        
        return {'success': True, 'order': order}
        
    except Exception as e:
        # ANY exception - release capital immediately
        error_msg = str(e)
        
        # Extract retCode/retMsg if available
        try:
            import json
            if 'retCode' in error_msg:
                error_data = json.loads(error_msg)
                ret_code = error_data.get('retCode')
                ret_msg = error_data.get('retMsg')
            else:
                ret_code = None
                ret_msg = error_msg
        except:
            ret_code = None
            ret_msg = error_msg
        
        capital_manager.release_on_failure(
            trade_id,
            "ORDER_EXCEPTION",
            f"retCode: {ret_code}, retMsg: {ret_msg}"
        )
        
        return {'success': False, 'reason': 'exception', 'error': error_msg}

# Global instance
_capital_manager = None

def get_capital_manager():
    """Get global capital manager"""
    global _capital_manager
    if _capital_manager is None:
        _capital_manager = CapitalManager()
    return _capital_manager

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    manager = CapitalManager()
    
    # Simulate reservation and release
    manager.reserve_capital('trade_001', 'BTC/USDT', 'BUY', 100.0)
    manager.release_capital('trade_001', 'success')
    
    # Simulate failure
    manager.reserve_capital('trade_002', 'ETH/USDT', 'BUY', 50.0)
    manager.release_on_failure('trade_002', 'insufficient_balance', '{"retCode":170131}')
    
    # Generate report
    report = manager.generate_integrity_report()
    print(json.dumps(report, indent=2))
