#!/usr/bin/env python3
"""
EVENT_BASED_PROFIT_TRACER.py
Event-based profit verification with PnL attribution
MUST BE INTEGRATED INTO ORCHESTRATOR
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class EventType:
    """Trading event types"""
    SIGNAL_CREATED = "SIGNAL_CREATED"
    SIGNAL_BLOCKED = "SIGNAL_BLOCKED"
    ORDER_SENT = "ORDER_SENT"
    ORDER_FILLED = "ORDER_FILLED"
    POSITION_OPENED = "POSITION_OPENED"
    PARTIAL_TP = "PARTIAL_TP"
    FINAL_EXIT = "FINAL_EXIT"
    STOP_LOSS = "STOP_LOSS"
    ARB_EXECUTED = "ARB_EXECUTED"

class EventBasedProfitTracer:
    """Event-based profit tracking with engine attribution"""
    
    def __init__(self, reports_dir: str = "/root/bot/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Event log
        self.events_file = self.reports_dir / 'profit_events.jsonl'
        
        # Trade tracking
        self.active_trades = {}  # trade_id -> trade_info
        self.completed_trades = []
        
        # Engine attribution
        self.engine_pnl = defaultdict(lambda: {'gross': 0, 'net': 0, 'trades': 0, 'wins': 0, 'losses': 0})
        self.engine_triggers = defaultdict(int)
        self.engine_executions = defaultdict(int)
        self.engine_blocks = defaultdict(int)
        
        logger.info("EventBasedProfitTracer initialized")
    
    def log_event(self, event_type: str, data: Dict):
        """Log trading event to JSONL"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **data
        }
        
        # Write to file
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def signal_created(self, symbol: str, signal_type: str, engines_involved: List[str],
                       confidence: float, market_type: str = "spot"):
        """Log SIGNAL_CREATED event"""
        self.log_event(EventType.SIGNAL_CREATED, {
            'symbol': symbol,
            'signal_type': signal_type,
            'market_type': market_type,
            'engines_involved': engines_involved,
            'confidence': confidence,
            'state': 'SIGNAL_GENERATION'
        })
        
        # Track triggers
        for engine in engines_involved:
            self.engine_triggers[engine] += 1
    
    def signal_blocked(self, symbol: str, signal_type: str, engines_involved: List[str],
                       block_reason: str, blocker_engine: str = None):
        """Log SIGNAL_BLOCKED event"""
        self.log_event(EventType.SIGNAL_BLOCKED, {
            'symbol': symbol,
            'signal_type': signal_type,
            'engines_involved': engines_involved,
            'block_reason': block_reason,
            'blocker_engine': blocker_engine,
            'state': 'RISK_EVALUATION'
        })
        
        # Track blocks
        for engine in engines_involved:
            self.engine_blocks[engine] += 1
    
    def order_sent(self, trade_id: str, symbol: str, side: str, quantity: float,
                   price: float, entry_engines: List[str], sizing_engines: List[str],
                   market_type: str = "spot"):
        """Log ORDER_SENT event"""
        self.log_event(EventType.ORDER_SENT, {
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'market_type': market_type,
            'entry_engines': entry_engines,
            'sizing_engines': sizing_engines,
            'state': 'EXECUTION'
        })
        
        # Initialize trade tracking
        self.active_trades[trade_id] = {
            'symbol': symbol,
            'side': side,
            'entry_price': price,
            'quantity': quantity,
            'entry_engines': entry_engines,
            'sizing_engines': sizing_engines,
            'exit_engines': [],
            'tp_engines': [],
            'market_type': market_type,
            'pnl': 0
        }
    
    def order_filled(self, trade_id: str, fill_price: float, fill_quantity: float,
                     execution_engine: str):
        """Log ORDER_FILLED event"""
        self.log_event(EventType.ORDER_FILLED, {
            'trade_id': trade_id,
            'fill_price': fill_price,
            'fill_quantity': fill_quantity,
            'execution_engine': execution_engine,
            'state': 'EXECUTION'
        })
        
        if trade_id in self.active_trades:
            # Record execution engine
            self.engine_executions[execution_engine] += 1
    
    def position_opened(self, trade_id: str, position_id: str):
        """Log POSITION_OPENED event"""
        self.log_event(EventType.POSITION_OPENED, {
            'trade_id': trade_id,
            'position_id': position_id,
            'state': 'POST_EXECUTION'
        })
    
    def partial_tp(self, trade_id: str, exit_price: float, exit_quantity: float,
                   pnl: float, tp_engines: List[str]):
        """Log PARTIAL_TP event"""
        self.log_event(EventType.PARTIAL_TP, {
            'trade_id': trade_id,
            'exit_price': exit_price,
            'exit_quantity': exit_quantity,
            'pnl': pnl,
            'tp_engines': tp_engines,
            'state': 'POST_EXECUTION'
        })
        
        if trade_id in self.active_trades:
            self.active_trades[trade_id]['tp_engines'].extend(tp_engines)
            self.active_trades[trade_id]['pnl'] += pnl
    
    def final_exit(self, trade_id: str, exit_price: float, exit_quantity: float,
                   pnl: float, exit_engines: List[str], exit_reason: str):
        """Log FINAL_EXIT event"""
        self.log_event(EventType.FINAL_EXIT, {
            'trade_id': trade_id,
            'exit_price': exit_price,
            'exit_quantity': exit_quantity,
            'pnl': pnl,
            'exit_engines': exit_engines,
            'exit_reason': exit_reason,
            'state': 'POST_EXECUTION'
        })
        
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            trade['exit_engines'] = exit_engines
            trade['pnl'] += pnl
            
            # Attribute PnL to engines
            self._attribute_pnl(trade)
            
            # Move to completed
            self.completed_trades.append(trade)
            del self.active_trades[trade_id]
    
    def stop_loss(self, trade_id: str, stop_price: float, pnl: float, 
                  stop_engine: str):
        """Log STOP_LOSS event"""
        self.log_event(EventType.STOP_LOSS, {
            'trade_id': trade_id,
            'stop_price': stop_price,
            'pnl': pnl,
            'stop_engine': stop_engine,
            'state': 'RISK_EVALUATION'
        })
        
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            trade['exit_engines'] = [stop_engine]
            trade['pnl'] += pnl
            
            # Attribute PnL
            self._attribute_pnl(trade)
            
            # Move to completed
            self.completed_trades.append(trade)
            del self.active_trades[trade_id]
    
    def arb_executed(self, arb_id: str, venue1: str, venue2: str,
                     spread: float, pnl: float, arb_engines: List[str]):
        """Log ARB_EXECUTED event"""
        self.log_event(EventType.ARB_EXECUTED, {
            'arb_id': arb_id,
            'venue1': venue1,
            'venue2': venue2,
            'spread': spread,
            'pnl': pnl,
            'arb_engines': arb_engines,
            'state': 'EXECUTION'
        })
        
        # Direct PnL attribution for arbitrage
        for engine in arb_engines:
            weight = 1.0 / len(arb_engines)
            self.engine_pnl[engine]['gross'] += pnl * weight
            self.engine_pnl[engine]['net'] += pnl * weight
            self.engine_pnl[engine]['trades'] += 1
            if pnl > 0:
                self.engine_pnl[engine]['wins'] += 1
            else:
                self.engine_pnl[engine]['losses'] += 1
    
    def _attribute_pnl(self, trade: Dict):
        """Attribute PnL to contributing engines"""
        pnl = trade['pnl']
        
        # Collect all contributing engines
        all_engines = (
            trade.get('entry_engines', []) +
            trade.get('sizing_engines', []) +
            trade.get('exit_engines', []) +
            trade.get('tp_engines', [])
        )
        
        if not all_engines:
            logger.warning(f"Trade {trade.get('symbol')} has no engine attribution!")
            return
        
        # Proportional allocation
        # Entry: 40%, Sizing: 20%, Exit: 30%, TP: 10%
        allocations = []
        
        for engine in trade.get('entry_engines', []):
            allocations.append((engine, 0.4 / len(trade.get('entry_engines', [1]))))
        
        for engine in trade.get('sizing_engines', []):
            allocations.append((engine, 0.2 / len(trade.get('sizing_engines', [1]))))
        
        for engine in trade.get('exit_engines', []):
            allocations.append((engine, 0.3 / len(trade.get('exit_engines', [1]))))
        
        for engine in trade.get('tp_engines', []):
            allocations.append((engine, 0.1 / len(trade.get('tp_engines', [1]))))
        
        # Distribute PnL
        for engine, weight in allocations:
            attributed_pnl = pnl * weight
            self.engine_pnl[engine]['gross'] += attributed_pnl
            self.engine_pnl[engine]['net'] += attributed_pnl
            self.engine_pnl[engine]['trades'] += 1
            
            if pnl > 0:
                self.engine_pnl[engine]['wins'] += 1
            else:
                self.engine_pnl[engine]['losses'] += 1
    
    def save_pnl_attribution(self):
        """Save PnL attribution to file"""
        output_file = self.reports_dir / 'engine_pnl_attribution.json'
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'engine_pnl': dict(self.engine_pnl),
            'engine_triggers': dict(self.engine_triggers),
            'engine_executions': dict(self.engine_executions),
            'engine_blocks': dict(self.engine_blocks),
            'total_completed_trades': len(self.completed_trades)
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"PnL attribution saved: {output_file}")

# Global instance
_tracer = None

def get_event_tracer() -> EventBasedProfitTracer:
    """Get global event tracer"""
    global _tracer
    if _tracer is None:
        _tracer = EventBasedProfitTracer()
    return _tracer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    tracer = get_event_tracer()
    
    # Simulate events
    tracer.signal_created('BTC/USD', 'BUY', ['ScalpEngine1', 'TrendFollower'], 0.85, 'spot')
    tracer.order_sent('trade_001', 'BTC/USD', 'BUY', 0.1, 50000, ['ScalpEngine1'], ['RiskManager'], 'spot')
    tracer.order_filled('trade_001', 50010, 0.1, 'ExecutionEngine')
    tracer.position_opened('trade_001', 'pos_001')
    tracer.final_exit('trade_001', 50500, 0.1, 49, ['ExitEngine'], 'take_profit')
    
    tracer.save_pnl_attribution()
    
    print("[OK] Event-based tracing test complete")
    print(f"Events logged to: {tracer.events_file}")
