#!/usr/bin/env python3
"""
ENGINE DARWINISM - Complete Implementation
Adaptive execution priority through natural selection of influence

Phases D0-D7: From baseline discovery to transparent evolution
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE D0: DISCOVERY & BASELINE
# ============================================================================

@dataclass
class EngineBaseline:
    """Phase D0: Engine baseline metrics"""
    engine_id: str
    engine_name: str
    signal_count: int = 0
    trade_count: int = 0
    total_pnl: float = 0.0
    avg_holding_time_sec: float = 0.0
    volatility_contexts: List[str] = field(default_factory=list)
    venues: List[str] = field(default_factory=list)
    market_types: List[str] = field(default_factory=list)

class EngineBaselineDiscovery:
    """Phase D0: Discover and baseline all engines (READ-ONLY)"""
    
    def __init__(self):
        self.engine_baselines = {}
        
    def generate_engine_id(self, engine_name: str) -> str:
        """Generate stable hash-based engine ID"""
        return hashlib.md5(engine_name.encode()).hexdigest()[:12]
    
    def record_signal(self, engine_name: str, signal: Dict):
        """Record signal emission (baseline only)"""
        engine_id = self.generate_engine_id(engine_name)
        
        if engine_id not in self.engine_baselines:
            self.engine_baselines[engine_id] = EngineBaseline(
                engine_id=engine_id,
                engine_name=engine_name
            )
        
        self.engine_baselines[engine_id].signal_count += 1
    
    def record_trade(self, engine_name: str, trade: Dict):
        """Record trade participation (baseline only)"""
        engine_id = self.generate_engine_id(engine_name)
        
        if engine_id in self.engine_baselines:
            baseline = self.engine_baselines[engine_id]
            baseline.trade_count += 1
            baseline.total_pnl += trade.get('pnl', 0)
            
            if 'holding_time' in trade:
                baseline.avg_holding_time_sec = (
                    (baseline.avg_holding_time_sec * (baseline.trade_count - 1) + trade['holding_time']) 
                    / baseline.trade_count
                )
    
    def save_baseline(self, filepath='/root/bot/logs/ENGINE_DARWIN_BASELINE.json'):
        """Save baseline (NO behavior changes)"""
        try:
            baseline_data = {eid: asdict(baseline) for eid, baseline in self.engine_baselines.items()}
            with open(filepath, 'w') as f:
                json.dump(baseline_data, f, indent=2)
            logger.info(f"📊 Baseline saved: {len(self.engine_baselines)} engines")
        except Exception as e:
            logger.warning(f"Could not save baseline: {e}")

# ============================================================================
# PHASE D1: PERFORMANCE ATTRIBUTION
# ============================================================================

@dataclass
class EngineContribution:
    """Phase D1: Quantify engine contribution"""
    engine_id: str
    entry_weight: float = 0.0
    exit_weight: float = 0.0
    sizing_weight: float = 0.0
    tp_contribution: float = 0.0
    sl_contribution: float = 0.0
    pnl: float = 0.0
    trade_count: int = 0

class EngineContributionTracker:
    """Phase D1: Track performance attribution (NO judgment)"""
    
    def __init__(self):
        self.contributions = defaultdict(lambda: EngineContribution(engine_id=""))
        self.rolling_window = deque(maxlen=250)  # Last 250 trades
        
    def record_contribution(self, engine_id: str, contribution_type: str, value: float, pnl: float = 0):
        """Record engine contribution"""
        contrib = self.contributions[engine_id]
        contrib.engine_id = engine_id
        
        if contribution_type == 'entry':
            contrib.entry_weight += value
        elif contribution_type == 'exit':
            contrib.exit_weight += value
        elif contribution_type == 'sizing':
            contrib.sizing_weight += value
        elif contribution_type == 'tp':
            contrib.tp_contribution += value
        elif contribution_type == 'sl':
            contrib.sl_contribution += value
        
        contrib.pnl += pnl
        contrib.trade_count += 1
        
        # Rolling window
        self.rolling_window.append({
            'engine_id': engine_id,
            'type': contribution_type,
            'value': value,
            'pnl': pnl,
            'timestamp': time.time()
        })
    
    def get_performance_matrix(self) -> Dict:
        """Generate performance matrix"""
        matrix = {}
        for engine_id, contrib in self.contributions.items():
            if contrib.trade_count > 0:
                matrix[engine_id] = {
                    'avg_entry_weight': contrib.entry_weight / contrib.trade_count,
                    'avg_exit_weight': contrib.exit_weight / contrib.trade_count,
                    'avg_sizing_weight': contrib.sizing_weight / contrib.trade_count,
                    'total_pnl': contrib.pnl,
                    'avg_pnl_per_trade': contrib.pnl / contrib.trade_count,
                    'trade_count': contrib.trade_count
                }
        return matrix
    
    def save_attribution(self, filepath='/root/bot/logs/ENGINE_ATTRIBUTION.jsonl'):
        """Save attribution log (append-only)"""
        try:
            with open(filepath, 'a') as f:
                record = {
                    'timestamp': time.time(),
                    'matrix': self.get_performance_matrix()
                }
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            logger.warning(f"Could not save attribution: {e}")

# ============================================================================
# PHASE D2: INFLUENCE VECTOR
# ============================================================================

@dataclass
class EngineInfluenceVector:
    """Phase D2: Convert performance to influence (NOT permission)"""
    engine_id: str
    confidence_weight: float = 1.0  # 0.5 - 2.0
    sizing_bias: float = 1.0  # 0.8 - 1.5
    execution_priority_delta: int = 0  # -2 to +2
    decay_half_life_hours: float = 6.0
    last_updated: float = field(default_factory=time.time)
    
    def apply_decay(self):
        """Decay influence toward baseline"""
        hours_elapsed = (time.time() - self.last_updated) / 3600
        decay_factor = 0.5 ** (hours_elapsed / self.decay_half_life_hours)
        
        # Decay toward 1.0 baseline
        self.confidence_weight = 1.0 + (self.confidence_weight - 1.0) * decay_factor
        self.sizing_bias = 1.0 + (self.sizing_bias - 1.0) * decay_factor
        self.execution_priority_delta = int(self.execution_priority_delta * decay_factor)
        
        self.last_updated = time.time()

class EngineInfluenceManager:
    """Phase D2: Manage influence vectors"""
    
    def __init__(self):
        self.influence_vectors = {}
    
    def calculate_influence(self, engine_id: str, performance_data: Dict) -> EngineInfluenceVector:
        """Calculate influence from performance (floors and ceilings prevent collapse)"""
        
        avg_pnl = performance_data.get('avg_pnl_per_trade', 0)
        trade_count = performance_data.get('trade_count', 0)
        
        # Confidence weight based on PnL
        if avg_pnl > 0:
            confidence_weight = min(2.0, 1.0 + (avg_pnl / 10.0))  # Cap at 2.0x
        else:
            confidence_weight = max(0.5, 1.0 + (avg_pnl / 10.0))  # Floor at 0.5x
        
        # Sizing bias based on consistency
        sizing_bias = 1.0 + (min(trade_count, 50) / 100.0) * 0.5  # Up to 1.5x
        sizing_bias = max(0.8, min(1.5, sizing_bias))
        
        # Priority delta based on recent performance
        if avg_pnl > 5:
            priority_delta = 2
        elif avg_pnl > 1:
            priority_delta = 1
        elif avg_pnl < -5:
            priority_delta = -2
        elif avg_pnl < -1:
            priority_delta = -1
        else:
            priority_delta = 0
        
        return EngineInfluenceVector(
            engine_id=engine_id,
            confidence_weight=confidence_weight,
            sizing_bias=sizing_bias,
            execution_priority_delta=priority_delta
        )
    
    def update_influences(self, performance_matrix: Dict):
        """Update all influence vectors"""
        for engine_id, perf_data in performance_matrix.items():
            influence = self.calculate_influence(engine_id, perf_data)
            self.influence_vectors[engine_id] = influence
        
        # Apply decay to existing influences
        for influence in self.influence_vectors.values():
            influence.apply_decay()
    
    def get_influence(self, engine_id: str) -> EngineInfluenceVector:
        """Get influence vector (defaults to neutral)"""
        return self.influence_vectors.get(
            engine_id,
            EngineInfluenceVector(engine_id=engine_id)
        )
    
    def save_influence_vectors(self, filepath='/root/bot/logs/ENGINE_INFLUENCE_VECTOR.json'):
        """Save influence vectors"""
        try:
            vectors = {eid: asdict(iv) for eid, iv in self.influence_vectors.items()}
            with open(filepath, 'w') as f:
                json.dump(vectors, f, indent=2)
            logger.info(f"📊 Influence vectors saved: {len(vectors)} engines")
        except Exception as e:
            logger.warning(f"Could not save influence vectors: {e}")

# ============================================================================
# PHASE D3-D7: Integration methods (simplified for initial deployment)
# ============================================================================

class EngineDarwinismSystem:
    """Complete Engine Darwinism System integrating all phases"""
    
    def __init__(self):
        self.baseline = EngineBaselineDiscovery()
        self.attribution = EngineContributionTracker()
        self.influence = EngineInfluenceManager()
        
    def record_signal(self, engine_name: str, signal: Dict):
        """Record signal (Phase D0)"""
        self.baseline.record_signal(engine_name, signal)
    
    def record_trade(self, engine_name: str, trade: Dict):
        """Record trade (Phase D0-D1)"""
        engine_id = self.baseline.generate_engine_id(engine_name)
        self.baseline.record_trade(engine_name, trade)
        
        # Attribution
        self.attribution.record_contribution(
            engine_id,
            'entry',
            1.0,
            trade.get('pnl', 0)
        )
    
    def update_system(self):
        """Update all darwinism components"""
        # Update influences from performance
        perf_matrix = self.attribution.get_performance_matrix()
        self.influence.update_influences(perf_matrix)
    
    def get_engine_priority_order(self, contributing_engines: List[str]) -> List[str]:
        """Phase D3: Get priority-sorted engine list (ALL still execute)"""
        engine_priorities = []
        
        for engine_name in contributing_engines:
            engine_id = self.baseline.generate_engine_id(engine_name)
            influence = self.influence.get_influence(engine_id)
            engine_priorities.append((engine_name, influence.execution_priority_delta))
        
        # Sort by priority (descending)
        sorted_engines = sorted(engine_priorities, key=lambda x: x[1], reverse=True)
        
        return [e[0] for e in sorted_engines]
    
    def calculate_weighted_size(self, base_size: float, contributing_engines: List[str]) -> float:
        """Phase D4: Calculate size with influence bias (NOT limiting)"""
        if not contributing_engines:
            return base_size
        
        # Get all sizing biases
        biases = []
        for engine_name in contributing_engines:
            engine_id = self.baseline.generate_engine_id(engine_name)
            influence = self.influence.get_influence(engine_id)
            biases.append(influence.sizing_bias)
        
        # Weighted mean
        avg_bias = sum(biases) / len(biases)
        
        return base_size * avg_bias
    
    def save_all_reports(self):
        """Save all darwinism reports"""
        self.baseline.save_baseline()
        self.attribution.save_attribution()
        self.influence.save_influence_vectors()
        
        # Generate darwinism report
        report = {
            'timestamp': time.time(),
            'total_engines': len(self.baseline.engine_baselines),
            'engines_with_influence': len(self.influence.influence_vectors),
            'performance_matrix': self.attribution.get_performance_matrix(),
            'top_performers': self._get_top_performers(),
            'influence_gainers': self._get_influence_movers('gain'),
            'influence_losers': self._get_influence_movers('loss')
        }
        
        try:
            with open('/root/bot/logs/ENGINE_DARWINISM_REPORT.json', 'w') as f:
                json.dump(report, f, indent=2)
            logger.info("📊 Darwinism report generated")
        except Exception as e:
            logger.warning(f"Could not save darwinism report: {e}")
    
    def _get_top_performers(self, limit=10) -> List[Dict]:
        """Get top performing engines"""
        perf_matrix = self.attribution.get_performance_matrix()
        sorted_perfs = sorted(
            perf_matrix.items(),
            key=lambda x: x[1].get('total_pnl', 0),
            reverse=True
        )
        return [{'engine_id': eid, **data} for eid, data in sorted_perfs[:limit]]
    
    def _get_influence_movers(self, direction='gain', limit=10) -> List[Dict]:
        """Get engines gaining or losing influence"""
        movers = []
        for engine_id, influence in self.influence.influence_vectors.items():
            delta = influence.confidence_weight - 1.0
            if (direction == 'gain' and delta > 0) or (direction == 'loss' and delta < 0):
                movers.append({
                    'engine_id': engine_id,
                    'confidence_delta': delta,
                    'sizing_bias': influence.sizing_bias,
                    'priority_delta': influence.execution_priority_delta
                })
        
        movers.sort(key=lambda x: abs(x['confidence_delta']), reverse=True)
        return movers[:limit]

# Singleton instance
_darwinism_system = None

def get_darwinism_system() -> EngineDarwinismSystem:
    """Get global darwinism system"""
    global _darwinism_system
    if _darwinism_system is None:
        _darwinism_system = EngineDarwinismSystem()
    return _darwinism_system
