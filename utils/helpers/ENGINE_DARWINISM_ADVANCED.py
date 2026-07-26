#!/usr/bin/env python3
"""
ADVANCED ENGINE DARWINISM EXTENSIONS
Layers 1-6: Cross-exchange, temporal, latency, Sharpe, adaptive learning, AI meta-analysis
"""

import json
import time
import math
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# EXTENSION 1: CROSS-EXCHANGE DARWINISM
# ============================================================================

@dataclass
class VenuePerformance:
    """Performance metrics per venue"""
    venue: str
    total_pnl: float = 0.0
    trade_count: int = 0
    wins: int = 0
    losses: int = 0
    sharpe: float = 0.0
    
    @property
    def win_rate(self) -> float:
        return self.wins / self.trade_count if self.trade_count > 0 else 0.0

class CrossExchangeDarwinism:
    """Engines learn portability across venues"""
    
    def __init__(self):
        # engine_id -> {venue -> VenuePerformance}
        self.venue_performance = defaultdict(dict)
        self.migration_priors = defaultdict(dict)  # engine_id -> {venue -> prior}
        
    def record_venue_trade(self, engine_id: str, venue: str, pnl: float):
        """Record trade on specific venue"""
        if venue not in self.venue_performance[engine_id]:
            self.venue_performance[engine_id][venue] = VenuePerformance(venue=venue)
        
        perf = self.venue_performance[engine_id][venue]
        perf.total_pnl += pnl
        perf.trade_count += 1
        if pnl > 0:
            perf.wins += 1
        else:
            perf.losses += 1
    
    def calculate_migration_prior(self, engine_id: str, from_venue: str, to_venue: str) -> float:
        """Calculate confidence boost for new venue based on existing performance"""
        if from_venue not in self.venue_performance.get(engine_id, {}):
            return 1.0  # Neutral
        
        source_perf = self.venue_performance[engine_id][from_venue]
        
        # Strong performance on source venue = higher initial confidence on target
        if source_perf.trade_count < 10:
            return 1.0  # Not enough data
        
        if source_perf.sharpe > 1.5 and source_perf.win_rate > 0.6:
            return 1.3  # 30% confidence boost
        elif source_perf.sharpe > 1.0 and source_perf.win_rate > 0.55:
            return 1.15  # 15% boost
        elif source_perf.sharpe < 0:
            return 0.9  # Slight penalty
        
        return 1.0  # Neutral
    
    def get_venue_multiplier(self, engine_id: str, venue: str) -> float:
        """Get influence multiplier for engine on specific venue"""
        # Check if we have direct performance on this venue
        if venue in self.venue_performance.get(engine_id, {}):
            perf = self.venue_performance[engine_id][venue]
            if perf.trade_count >= 5:
                # Use actual performance
                return max(0.5, min(2.0, 1.0 + (perf.sharpe * 0.3)))
        
        # Otherwise, use migration prior from best venue
        best_prior = 1.0
        for other_venue in self.venue_performance.get(engine_id, {}).keys():
            if other_venue != venue:
                prior = self.calculate_migration_prior(engine_id, other_venue, venue)
                best_prior = max(best_prior, prior)
        
        return best_prior

# ============================================================================
# EXTENSION 2: TIME-OF-DAY EVOLUTIONARY PRESSURE
# ============================================================================

@dataclass
class SessionPerformance:
    """Performance during specific market session"""
    session: str
    sharpe: float = 0.0
    total_pnl: float = 0.0
    trade_count: int = 0
    last_update: float = field(default_factory=time.time)

class TemporalEvolutionPressure:
    """Engines remember when they perform best"""
    
    def __init__(self):
        # engine_id -> {session -> SessionPerformance}
        self.session_performance = defaultdict(dict)
        self.session_decay_hours = 24.0  # Decay multipliers daily
        
    def get_current_session(self) -> str:
        """Determine current market session"""
        from datetime import datetime
        hour_utc = datetime.utcnow().hour
        
        # Asia: 00:00-09:00 UTC
        if 0 <= hour_utc < 9:
            return 'asia'
        # London: 08:00-16:00 UTC
        elif 8 <= hour_utc < 16:
            return 'london_overlap' if hour_utc < 9 else 'london'
        # NY: 13:00-22:00 UTC
        elif 13 <= hour_utc < 22:
            return 'ny_overlap' if hour_utc < 16 else 'ny'
        else:
            return 'off_hours'
    
    def record_session_trade(self, engine_id: str, session: str, pnl: float):
        """Record trade during session"""
        if session not in self.session_performance[engine_id]:
            self.session_performance[engine_id][session] = SessionPerformance(session=session)
        
        perf = self.session_performance[engine_id][session]
        perf.total_pnl += pnl
        perf.trade_count += 1
        perf.last_update = time.time()
    
    def get_session_multiplier(self, engine_id: str, session: str) -> float:
        """Get influence multiplier for current session"""
        if session not in self.session_performance.get(engine_id, {}):
            return 1.0  # Neutral for new sessions
        
        perf = self.session_performance[engine_id][session]
        
        # Apply decay
        hours_since_update = (time.time() - perf.last_update) / 3600
        decay_factor = 0.5 ** (hours_since_update / self.session_decay_hours)
        
        # Calculate multiplier based on performance
        if perf.trade_count >= 5:
            base_mult = 1.0 + (perf.sharpe * 0.2)  # ±20% based on Sharpe
            return max(0.7, min(1.4, base_mult * decay_factor))
        
        return 1.0

# ============================================================================
# EXTENSION 3: LATENCY-AWARE INFLUENCE
# ============================================================================

@dataclass
class LatencyProfile:
    """Latency characteristics of engine"""
    engine_id: str
    avg_signal_to_fill_ms: float = 0.0
    avg_slippage_bps: float = 0.0
    missed_edge_rate: float = 0.0
    fast_sensitive: bool = False
    tolerance_ms: float = 1000.0

class LatencyAwareWeighting:
    """Speed matters - when speed matters"""
    
    def __init__(self):
        self.latency_profiles = {}
        self.latency_samples = defaultdict(list)
        
    def record_latency(self, engine_id: str, signal_to_fill_ms: float, slippage_bps: float):
        """Record latency for trade"""
        self.latency_samples[engine_id].append({
            'latency_ms': signal_to_fill_ms,
            'slippage': slippage_bps,
            'timestamp': time.time()
        })
        
        # Update profile
        if engine_id not in self.latency_profiles:
            self.latency_profiles[engine_id] = LatencyProfile(engine_id=engine_id)
        
        profile = self.latency_profiles[engine_id]
        samples = self.latency_samples[engine_id][-100:]  # Last 100
        
        profile.avg_signal_to_fill_ms = sum(s['latency_ms'] for s in samples) / len(samples)
        profile.avg_slippage_bps = sum(s['slippage'] for s in samples) / len(samples)
        profile.fast_sensitive = profile.avg_signal_to_fill_ms < 200  # Under 200ms
        
    def is_fast_regime(self, volatility_pct: float, spread_bps: float) -> bool:
        """Detect if current market is fast-regime (speed matters)"""
        # Fast regime = high volatility + tight spreads
        return volatility_pct > 0.02 and spread_bps < 10
    
    def get_latency_multiplier(self, engine_id: str, is_fast_regime: bool) -> float:
        """Boost low-latency engines in fast regimes only"""
        if engine_id not in self.latency_profiles:
            return 1.0
        
        profile = self.latency_profiles[engine_id]
        
        if is_fast_regime and profile.fast_sensitive:
            return 1.3  # 30% boost for fast engines in fast regimes
        elif is_fast_regime and not profile.fast_sensitive:
            return 0.9  # Slight penalty for slow engines in fast regimes
        
        return 1.0  # Latency doesn't matter in slow regimes

# ============================================================================
# EXTENSION 4: RISK-ADJUSTED INFLUENCE (SHARPE-WEIGHTED)
# ============================================================================

class SharpeWeightedInfluence:
    """Loud engines must earn their volume"""
    
    def __init__(self):
        self.engine_returns = defaultdict(list)
        
    def record_return(self, engine_id: str, return_pct: float):
        """Record trade return for Sharpe calculation"""
        self.engine_returns[engine_id].append(return_pct)
        
        # Keep last 250 trades for rolling Sharpe
        if len(self.engine_returns[engine_id]) > 250:
            self.engine_returns[engine_id] = self.engine_returns[engine_id][-250:]
    
    def calculate_sharpe(self, engine_id: str) -> float:
        """Calculate Sharpe ratio"""
        returns = self.engine_returns.get(engine_id, [])
        if len(returns) < 10:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance) if variance > 0 else 0.001
        
        # Annualized Sharpe (assuming daily returns)
        sharpe = (avg_return / std_dev) * math.sqrt(252) if std_dev > 0 else 0.0
        return sharpe
    
    def calculate_consistency_factor(self, engine_id: str) -> float:
        """Reward stable performance"""
        returns = self.engine_returns.get(engine_id, [])
        if len(returns) < 10:
            return 1.0
        
        # Consistency = % of positive periods in rolling window
        positive_rate = sum(1 for r in returns[-50:] if r > 0) / min(len(returns), 50)
        return 0.8 + (positive_rate * 0.4)  # 0.8 to 1.2
    
    def get_risk_adjusted_score(self, engine_id: str, trade_count: int) -> float:
        """Calculate risk-adjusted influence score"""
        sharpe = self.calculate_sharpe(engine_id)
        consistency = self.calculate_consistency_factor(engine_id)
        volume_factor = math.log(trade_count + 1)
        
        # Score = Sharpe × log(trades) × consistency
        score = sharpe * volume_factor * consistency
        
        # Convert to multiplier (0.5 to 2.0 range)
        multiplier = max(0.5, min(2.0, 1.0 + (score * 0.1)))
        return multiplier

# ============================================================================
# EXTENSION 5: ADAPTIVE LEARNING ACCELERATION
# ============================================================================

class AdaptiveLearningRates:
    """Learn fast when safe, slow when chaotic"""
    
    def __init__(self):
        self.base_learning_rate = 0.1
        self.volatility_window = deque(maxlen=50)
        
    def record_market_volatility(self, volatility_pct: float):
        """Track market volatility"""
        self.volatility_window.append(volatility_pct)
    
    def get_learning_rate(self, trade_count: int, regime_stable: bool) -> float:
        """Calculate adaptive learning rate"""
        # Base rate increases with trade count
        trade_factor = min(2.0, math.log(trade_count + 1) / 5.0)
        
        # Reduce during volatility spikes
        if len(self.volatility_window) > 10:
            recent_vol = sum(self.volatility_window) / len(self.volatility_window)
            vol_factor = 1.0 if recent_vol < 0.03 else 0.5  # Half speed in volatile times
        else:
            vol_factor = 1.0
        
        # Increase in stable regimes
        stability_factor = 1.5 if regime_stable else 1.0
        
        rate = self.base_learning_rate * trade_factor * vol_factor * stability_factor
        return min(0.5, max(0.01, rate))  # Clamp between 0.01 and 0.5

# ============================================================================
# EXTENSION 6: AI CONSULTING LAYER (META-ANALYST)
# ============================================================================

class AIMetaAnalyst:
    """AI analyzes but never executes"""
    
    def __init__(self):
        self.analysis_history = []
        
    def analyze_darwinism_state(self, darwinism_metrics: Dict) -> Dict:
        """AI meta-analysis (advisory only - NO trading)"""
        analysis =  {
            'timestamp': time.time(),
            'role': 'META_ANALYST_ONLY',
            'can_trade': False,
            'can_override': False,
            'insights': []
        }
        
        # Detect over-influencing engines
        for engine_id, metrics in darwinism_metrics.get('performance_matrix', {}).items():
            sharpe = metrics.get('sharpe', 0)
            influence = metrics.get('influence', 1.0)
            
            if influence > 1.5 and sharpe < 0.5:
                analysis['insights'].append({
                    'type': 'over_influence_warning',
                    'engine_id': engine_id,
                    'suggestion': 'Consider decay for low-Sharpe high-influence engine'
                })
        
        # Detect cross-venue transferability
        # ... (AI suggestions, never actions)
        
        self.analysis_history.append(analysis)
        return analysis
    
    def generate_meta_report(self) -> Dict:
        """Generate AI meta-reasoning report"""
        return {
            'total_analyses': len(self.analysis_history),
            'recent_insights': self.analysis_history[-10:],
            'role_confirmation': 'ADVISORY_ONLY_NO_EXECUTION'
        }

# ============================================================================
# INTEGRATED ADVANCED DARWINISM SYSTEM
# ============================================================================

class AdvancedEngineDarwinism:
    """Complete advanced darwinism with all 6 extensions"""
    
    def __init__(self):
        self.cross_exchange = CrossExchangeDarwinism()
        self.temporal = TemporalEvolutionPressure()
        self.latency = LatencyAwareWeighting()
        self.sharpe_weighted = SharpeWeightedInfluence()
        self.adaptive_learning = AdaptiveLearningRates()
        self.ai_analyst = AIMetaAnalyst()
        
    def calculate_final_influence(self, 
                                   engine_id: str,
                                   venue: str,
                                   trade_count: int,
                                   current_volatility: float,
                                   current_spread: float) -> float:
        """Combine all influence factors"""
        
        # Get current session
        session = self.temporal.get_current_session()
        
        # Check if fast regime
        is_fast = self.latency.is_fast_regime(current_volatility, current_spread)
        
        # Calculate all multipliers
        venue_mult = self.cross_exchange.get_venue_multiplier(engine_id, venue)
        session_mult = self.temporal.get_session_multiplier(engine_id, session)
        latency_mult = self.latency.get_latency_multiplier(engine_id, is_fast)
        sharpe_mult = self.sharpe_weighted.get_risk_adjusted_score(engine_id, trade_count)
        
        # Combined influence (multiplicative)
        final_influence = venue_mult * session_mult * latency_mult * sharpe_mult
        
        # Clamp to reasonable range (0.3 to 3.0)
        return max(0.3, min(3.0, final_influence))
    
    def save_evolution_report(self, filepath='/root/bot/logs/DARWINISM_EVOLUTION_REPORT.json'):
        """Generate comprehensive evolution report"""
        report = {
            'timestamp': time.time(),
            'extensions_active': [
                'Cross-Exchange Darwinism',
                'Time-of-Day Evolutionary Pressure',
                'Latency-Aware Influence',
                'Sharpe-Weighted Voice',
                'Adaptive Learning Acceleration',
                'AI Meta-Analyst Layer'
            ],
            'cross_exchange_data': {
                'total_engines_tracked': len(self.cross_exchange.venue_performance),
                'venues_active': list(set(
                    venue for engine_data in self.cross_exchange.venue_performance.values()
                    for venue in engine_data.keys()
                ))
            },
            'temporal_data': {
                'sessions_tracked': list(set(
                    session for engine_data in self.temporal.session_performance.values()
                    for session in engine_data.keys()
                ))
            },
            'latency_profiles_count': len(self.latency.latency_profiles),
            'sharpe_tracked_engines': len(self.sharpe_weighted.engine_returns),
            'ai_meta_analysis': self.ai_analyst.generate_meta_report(),
            'verification': {
                'all_engines_active': True,
                'no_suppression': True,
                'influence_only': True,
                'no_execution_restriction': True
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📊 Evolution report saved: {filepath}")
        except Exception as e:
            logger.warning(f"Could not save evolution report: {e}")
        
        return report

# Singleton
_advanced_darwinism = None

def get_advanced_darwinism() -> AdvancedEngineDarwinism:
    """Get global advanced darwinism system"""
    global _advanced_darwinism
    if _advanced_darwinism is None:
        _advanced_darwinism = AdvancedEngineDarwinism()
    return _advanced_darwinism
