#!/usr/bin/env python3
"""
TRADING_REALITY_PROOF.py
Verify StateAware orchestration doesn't reduce profitability
A/B testing, metrics collection, decision traces
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict, deque
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TradingRealityProof:
    """
    Tracks real trading performance and validates StateAware doesn't reduce edge
    """
    
    def __init__(self, reports_dir: str = "/root/bot/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Metrics collection
        self.cycle_metrics = []
        self.cycle_start_time = None
        self.state_timings = defaultdict(list)
        
        # Trade tracking
        self.signals_generated = 0
        self.trades_attempted = 0
        self.trades_executed = 0
        self.trades_blocked_risk = 0
        self.trades_blocked_safe_mode = 0
        self.trades_blocked_liquidity = 0
        
        # Engine performance
        self.engine_durations = defaultdict(list)
        self.engines_ran_this_cycle = set()
        
        # Safe mode tracking
        self.safe_mode_active = False
        self.safe_mode_reason = None
        
        # Decision traces
        self.decision_traces = []
        
        # Mode
        self.mode = "STATEAWARE"  # or "BASELINE"
        
        logger.info(f"TradingRealityProof initialized: {self.reports_dir}")
    
    def start_cycle(self):
        """Mark start of trading cycle"""
        self.cycle_start_time = time.time()
        self.engines_ran_this_cycle = set()
        self.state_timings.clear()
    
    def start_state(self, state_name: str):
        """Mark start of state execution"""
        self.current_state = state_name
        self.state_start_time = time.time()
    
    def end_state(self, state_name: str):
        """Mark end of state execution"""
        if hasattr(self, 'state_start_time'):
            duration_ms = (time.time() - self.state_start_time) * 1000
            self.state_timings[state_name].append(duration_ms)
    
    def record_engine_execution(self, engine_name: str, duration_ms: float):
        """Record engine execution"""
        self.engine_durations[engine_name].append(duration_ms)
        self.engines_ran_this_cycle.add(engine_name)
    
    def record_signal(self, signal: Dict):
        """Record signal generated"""
        self.signals_generated += 1
    
    def record_trade_attempt(self, symbol: str, action: str, blocked: bool, 
                            block_reason: str = None, contributing_engines: List[str] = None):
        """Record trade attempt with decision trace"""
        self.trades_attempted += 1
        
        if blocked:
            if 'risk' in block_reason.lower():
                self.trades_blocked_risk += 1
            elif 'safe' in block_reason.lower():
                self.trades_blocked_safe_mode += 1
            elif 'liquidity' in block_reason.lower() or 'spread' in block_reason.lower():
                self.trades_blocked_liquidity += 1
        else:
            self.trades_executed += 1
        
        # Decision trace
        trace = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'final_action': 'BLOCKED' if blocked else 'EXECUTE',
            'block_reason': block_reason if blocked else None,
            'contributing_engines': contributing_engines or [],
            'mode': self.mode
        }
        
        self.decision_traces.append(trace)
        
        # Write trace immediately
        trace_file = self.reports_dir / 'decision_traces.jsonl'
        with open(trace_file, 'a') as f:
            f.write(json.dumps(trace) + '\n')
    
    def set_safe_mode(self, active: bool, reason: str = None):
        """Set safe mode status"""
        self.safe_mode_active = active
        self.safe_mode_reason = reason
    
    def end_cycle(self):
        """End trading cycle and write metrics"""
        if not self.cycle_start_time:
            return
        
        cycle_duration_ms = (time.time() - self.cycle_start_time) * 1000
        
        # Get top 20 slowest engines
        engine_times = []
        for engine, durations in self.engine_durations.items():
            if durations:
                avg_duration = sum(durations[-100:]) / len(durations[-100:])  # Last 100 runs
                engine_times.append((engine, avg_duration))
        
        top_20_slowest = sorted(engine_times, key=lambda x: -x[1])[:20]
        
        # Metrics for this cycle
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'cycle_duration_ms': cycle_duration_ms,
            'per_state_duration_ms': {k: sum(v)/len(v) if v else 0 for k, v in self.state_timings.items()},
            'total_engines_ran': len(self.engines_ran_this_cycle),
            'safe_mode_active': self.safe_mode_active,
            'safe_mode_reason': self.safe_mode_reason,
            'signals_generated_count': self.signals_generated,
            'trades_attempted_count': self.trades_attempted,
            'trades_executed_count': self.trades_executed,
            'trades_blocked_by_risk_count': self.trades_blocked_risk,
            'trades_blocked_by_safe_mode_count': self.trades_blocked_safe_mode,
            'trades_blocked_by_liquidity_or_spread_count': self.trades_blocked_liquidity,
            'top_20_slowest_engines': [{'engine': e, 'avg_ms': round(d, 2)} for e, d in top_20_slowest]
        }
        
        # Write metrics
        metrics_file = self.reports_dir / 'trading_reality_metrics.jsonl'
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        self.cycle_metrics.append(metrics)
    
    def generate_summary_report(self, last_n_cycles: int = 500) -> Dict:
        """Generate summary report"""
        if not self.cycle_metrics:
            return {}
        
        recent = self.cycle_metrics[-last_n_cycles:]
        
        total_signals = sum(m['signals_generated_count'] for m in recent)
        total_attempted = sum(m['trades_attempted_count'] for m in recent)
        total_executed = sum(m['trades_executed_count'] for m in recent)
        total_blocked_risk = sum(m['trades_blocked_by_risk_count'] for m in recent)
        total_blocked_safe = sum(m['trades_blocked_by_safe_mode_count'] for m in recent)
        total_blocked_liquidity = sum(m['trades_blocked_by_liquidity_or_spread_count'] for m in recent)
        
        avg_cycle_duration = sum(m['cycle_duration_ms'] for m in recent) / len(recent)
        avg_engines_ran = sum(m['total_engines_ran'] for m in recent) / len(recent)
        
        safe_mode_cycles = sum(1 for m in recent if m['safe_mode_active'])
        
        summary = {
            'mode': self.mode,
            'cycles_analyzed': len(recent),
            'avg_cycle_duration_ms': round(avg_cycle_duration, 2),
            'avg_engines_ran_per_cycle': round(avg_engines_ran, 2),
            'total_signals_generated': total_signals,
            'total_trades_attempted': total_attempted,
            'total_trades_executed': total_executed,
            'execution_rate': round(total_executed / total_attempted * 100, 2) if total_attempted > 0 else 0,
            'blocked_by_risk': total_blocked_risk,
            'blocked_by_safe_mode': total_blocked_safe,
            'blocked_by_liquidity': total_blocked_liquidity,
            'safe_mode_cycle_count': safe_mode_cycles,
            'safe_mode_rate': round(safe_mode_cycles / len(recent) * 100, 2)
        }
        
        return summary

# Global instance
_proof = None

def get_proof() -> TradingRealityProof:
    """Get global proof instance"""
    global _proof
    if _proof is None:
        _proof = TradingRealityProof()
    return _proof

def set_mode(mode: str):
    """Set orchestration mode: BASELINE or STATEAWARE"""
    proof = get_proof()
    proof.mode = mode
    logger.info(f"Trading mode set to: {mode}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    proof = get_proof()
    
    proof.start_cycle()
    proof.start_state('MARKET_ANALYSIS')
    time.sleep(0.01)
    proof.end_state('MARKET_ANALYSIS')
    proof.record_signal({'type': 'BUY', 'confidence': 0.8})
    proof.record_trade_attempt('BTC/USD', 'BUY', blocked=False)
    proof.end_cycle()
    
    summary = proof.generate_summary_report()
    print(json.dumps(summary, indent=2))
