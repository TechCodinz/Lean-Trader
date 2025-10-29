#!/usr/bin/env python3
"""
🧠 SENTIENT SCALPING COORDINATOR 🧠

When engines find high-volatility/fast-moving pairs:
1. They signal the coordinator
2. Coordinator alerts all scalping engines
3. Scalpers analyze and master the pair's movements
4. Collective intelligence guides scalping
5. Continuous profit extraction from each micro-movement

This is how professional trading desks operate!
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class HotPairTracker:
    """
    Tracks high-volatility and fast-moving pairs
    Signals when pairs become "hot" for scalping
    """
    
    def __init__(self):
        # Track volatility for each pair
        self.volatility_history = defaultdict(lambda: deque(maxlen=20))
        
        # Track price movements
        self.price_changes = defaultdict(lambda: deque(maxlen=50))
        
        # Track volume surges
        self.volume_spikes = defaultdict(lambda: deque(maxlen=20))
        
        # Current hot pairs
        self.hot_pairs = {}  # symbol -> hot_data
        
        # Alert history (avoid duplicate alerts)
        self.alert_history = defaultdict(lambda: datetime.min)
        
        logger.info("🔥 Hot Pair Tracker initialized")
    
    def register_volatility(self, symbol: str, volatility_pct: float, source: str):
        """
        Register volatility reading from any engine
        
        Args:
            symbol: Trading pair
            volatility_pct: Current volatility (%)
            source: Which engine detected it
        """
        self.volatility_history[symbol].append({
            'volatility': volatility_pct,
            'time': datetime.now(),
            'source': source
        })
        
        # Check if pair is getting hot
        self._check_if_hot(symbol)
    
    def register_price_movement(self, symbol: str, move_pct: float, timeframe: str, source: str):
        """
        Register significant price movement
        
        Args:
            symbol: Trading pair
            move_pct: Price change (%)
            timeframe: Time period (e.g., '1m', '5m')
            source: Which engine detected it
        """
        self.price_changes[symbol].append({
            'move_pct': move_pct,
            'timeframe': timeframe,
            'time': datetime.now(),
            'source': source
        })
        
        # Check if pair is getting hot
        self._check_if_hot(symbol)
    
    def register_volume_spike(self, symbol: str, volume_multiplier: float, source: str):
        """
        Register volume surge
        
        Args:
            symbol: Trading pair
            volume_multiplier: Volume vs average (e.g., 3.5 = 3.5x normal)
            source: Which engine detected it
        """
        self.volume_spikes[symbol].append({
            'multiplier': volume_multiplier,
            'time': datetime.now(),
            'source': source
        })
        
        # Check if pair is getting hot
        self._check_if_hot(symbol)
    
    def _check_if_hot(self, symbol: str):
        """
        Determine if a pair is "hot" for scalping
        
        Hot criteria:
        - High volatility (>2% in last 5 min)
        - Fast movements (multiple 0.5%+ moves)
        - Volume surge (2x+ normal)
        """
        # Get recent data
        recent_vol = [v['volatility'] for v in list(self.volatility_history[symbol])[-5:]]
        recent_moves = [m['move_pct'] for m in list(self.price_changes[symbol])[-10:]]
        recent_volume = [v['multiplier'] for v in list(self.volume_spikes[symbol])[-5:]]
        
        # Calculate scores
        vol_score = statistics.mean(recent_vol) if recent_vol else 0
        move_score = sum(1 for m in recent_moves if abs(m) > 0.5) if recent_moves else 0
        volume_score = statistics.mean(recent_volume) if recent_volume else 1
        
        # Determine if hot
        is_hot = False
        heat_level = 'COLD'
        reasons = []
        
        if vol_score > 2.0:
            is_hot = True
            heat_level = 'HOT'
            reasons.append(f"High volatility: {vol_score:.1f}%")
        
        if move_score >= 5:
            is_hot = True
            if heat_level == 'HOT':
                heat_level = 'VERY_HOT'
            reasons.append(f"Fast moves: {move_score} in 10 samples")
        
        if volume_score > 2.0:
            is_hot = True
            if heat_level == 'VERY_HOT':
                heat_level = 'BLAZING'
            reasons.append(f"Volume surge: {volume_score:.1f}x")
        
        # Update hot pairs
        if is_hot:
            self.hot_pairs[symbol] = {
                'heat_level': heat_level,
                'volatility': vol_score,
                'fast_moves': move_score,
                'volume': volume_score,
                'reasons': reasons,
                'updated_at': datetime.now(),
                'detected_by': list(set([
                    v.get('source') for v in self.volatility_history[symbol]
                ] + [
                    m.get('source') for m in self.price_changes[symbol]
                ] + [
                    v.get('source') for v in self.volume_spikes[symbol]
                ]))
            }
            
            # Alert if not alerted recently (avoid spam)
            last_alert = self.alert_history[symbol]
            if (datetime.now() - last_alert).total_seconds() > 300:  # 5 min cooldown
                self._send_hot_alert(symbol, self.hot_pairs[symbol])
                self.alert_history[symbol] = datetime.now()
        
        else:
            # Remove from hot pairs if cooled down
            if symbol in self.hot_pairs:
                del self.hot_pairs[symbol]
    
    def _send_hot_alert(self, symbol: str, hot_data: Dict):
        """
        Alert that a pair is HOT for scalping!
        """
        heat = hot_data['heat_level']
        reasons = ', '.join(hot_data['reasons'])
        detected_by = ', '.join(hot_data['detected_by'][:3])
        
        logger.info(f"🔥 HOT PAIR ALERT: {symbol} [{heat}]")
        logger.info(f"   Reasons: {reasons}")
        logger.info(f"   Detected by: {detected_by}")
        logger.info(f"   → SCALPERS: Focus on this pair NOW!")
    
    def get_hot_pairs(self, min_heat: str = 'HOT') -> List[Tuple[str, Dict]]:
        """
        Get currently hot pairs
        
        Args:
            min_heat: Minimum heat level ('HOT', 'VERY_HOT', 'BLAZING')
        
        Returns:
            List of (symbol, hot_data) tuples, sorted by heat
        """
        heat_levels = ['COLD', 'WARM', 'HOT', 'VERY_HOT', 'BLAZING']
        min_index = heat_levels.index(min_heat)
        
        hot = [
            (symbol, data)
            for symbol, data in self.hot_pairs.items()
            if heat_levels.index(data['heat_level']) >= min_index
        ]
        
        # Sort by heat level (hottest first)
        hot.sort(key=lambda x: heat_levels.index(x[1]['heat_level']), reverse=True)
        
        return hot


class MovementAnalyzer:
    """
    Analyzes a specific pair's micro-movements
    Learns patterns for precise scalping
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.movement_patterns = deque(maxlen=100)
        self.support_resistance = []
        self.typical_moves = deque(maxlen=50)
        
        logger.info(f"📊 Movement Analyzer initialized for {symbol}")
    
    def analyze_movement(self, price: float, timestamp: datetime) -> Dict:
        """
        Analyze current price movement
        Returns scalping opportunities
        """
        self.movement_patterns.append({
            'price': price,
            'time': timestamp
        })
        
        if len(self.movement_patterns) < 10:
            return None
        
        # Calculate recent movement characteristics
        prices = [p['price'] for p in self.movement_patterns]
        recent_10 = prices[-10:]
        
        # Movement speed (how fast is it moving?)
        move_range = max(recent_10) - min(recent_10)
        move_pct = (move_range / prices[-1]) * 100
        
        # Direction (up or down?)
        trend = 'up' if prices[-1] > prices[-10] else 'down'
        
        # Find micro support/resistance
        local_high = max(recent_10)
        local_low = min(recent_10)
        current = prices[-1]
        
        # Generate scalp opportunity
        opportunity = None
        
        if trend == 'up' and current < local_high * 0.998:
            # Pullback in uptrend - BUY opportunity
            opportunity = {
                'type': 'micro_pullback',
                'symbol': self.symbol,
                'side': 'buy',
                'entry': current,
                'target': local_high,
                'stop': local_low,
                'confidence': 0.65,
                'reasoning': f"Pullback in uptrend - target recent high {local_high:.2f}",
                'expected_move': ((local_high - current) / current) * 100
            }
        
        elif trend == 'down' and current > local_low * 1.002:
            # Bounce in downtrend - SELL opportunity
            opportunity = {
                'type': 'micro_bounce',
                'symbol': self.symbol,
                'side': 'sell',
                'entry': current,
                'target': local_low,
                'stop': local_high,
                'confidence': 0.65,
                'reasoning': f"Bounce in downtrend - target recent low {local_low:.2f}",
                'expected_move': ((current - local_low) / current) * 100
            }
        
        return opportunity


class SentientScalpingCoordinator:
    """
    🧠 SENTIENT SCALPING COORDINATOR 🧠
    
    Coordinates all engines for collective scalping intelligence:
    1. Receives hot pair alerts from any engine
    2. Activates movement analyzers for hot pairs
    3. Coordinates scalping across all scalping engines
    4. Shares learnings and patterns
    5. Extracts maximum profit from each micro-movement
    """
    
    def __init__(self, data_hub, swarm_intelligence):
        self.data_hub = data_hub
        self.swarm = swarm_intelligence
        
        # Hot pair tracking
        self.hot_tracker = HotPairTracker()
        
        # Movement analyzers (one per hot pair)
        self.analyzers = {}  # symbol -> MovementAnalyzer
        
        # Performance tracking
        self.scalps_by_pair = defaultdict(int)
        self.profits_by_pair = defaultdict(float)
        
        # Active monitoring
        self.monitored_pairs = set()
        
        logger.info("🧠 Sentient Scalping Coordinator initialized")
        logger.info("   → Ready to coordinate collective scalping!")
    
    def alert_hot_pair(self, symbol: str, alert_type: str, value: float, source: str):
        """
        Any engine can alert about a hot pair
        
        Args:
            symbol: Trading pair
            alert_type: 'volatility', 'movement', 'volume'
            value: Numeric value (%, multiplier, etc)
            source: Engine name that detected it
        """
        if alert_type == 'volatility':
            self.hot_tracker.register_volatility(symbol, value, source)
        elif alert_type == 'movement':
            self.hot_tracker.register_price_movement(symbol, value, '1m', source)
        elif alert_type == 'volume':
            self.hot_tracker.register_volume_spike(symbol, value, source)
        
        # Start monitoring if hot
        if symbol in self.hot_tracker.hot_pairs:
            self._start_monitoring(symbol)
    
    def _start_monitoring(self, symbol: str):
        """
        Start intensive monitoring and analysis of hot pair
        """
        if symbol not in self.monitored_pairs:
            self.monitored_pairs.add(symbol)
            self.analyzers[symbol] = MovementAnalyzer(symbol)
            
            hot_data = self.hot_tracker.hot_pairs[symbol]
            logger.info(f"🎯 MONITORING ACTIVATED: {symbol}")
            logger.info(f"   Heat: {hot_data['heat_level']}")
            logger.info(f"   All scalpers will focus on this pair!")
    
    async def analyze_and_scalp(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        Analyze hot pair and generate scalping signal
        
        This is the COLLECTIVE INTELLIGENCE:
        - Movement analyzer studies the pattern
        - Swarm intelligence validates the opportunity
        - Returns high-precision scalp signal
        """
        if symbol not in self.analyzers:
            return None
        
        # Analyze movement
        analyzer = self.analyzers[symbol]
        opportunity = analyzer.analyze_movement(current_price, datetime.now())
        
        if not opportunity:
            return None
        
        # Convert to full signal
        signal = {
            'type': 'sentient_scalp',
            'strategy': 'COLLECTIVE_MOVEMENT_MASTER',
            'symbol': symbol,
            'side': opportunity['side'],
            'entry': opportunity['entry'],
            'take_profit': opportunity['target'],
            'stop_loss': opportunity['stop'],
            'confidence': opportunity['confidence'],
            'reasoning': opportunity['reasoning'],
            'source': 'SentientScalpingCoordinator',
            'timestamp': datetime.now().isoformat(),
            'heat_level': self.hot_tracker.hot_pairs[symbol]['heat_level'],
            'expected_move_pct': opportunity['expected_move'],
            'urgency': 'CRITICAL'  # Hot pairs move fast!
        }
        
        # Share with swarm for collective validation
        signal_with_votes = await self.swarm.share_signal('SENTIENT_SCALPER', signal)
        
        return signal_with_votes
    
    def get_hot_pairs_for_scalping(self) -> List[str]:
        """
        Get list of hot pairs that scalpers should focus on
        """
        hot = self.hot_tracker.get_hot_pairs(min_heat='HOT')
        return [symbol for symbol, data in hot]
    
    def record_scalp_result(self, symbol: str, profit_pct: float):
        """
        Record result of scalp on hot pair
        Used to learn which pairs are most profitable
        """
        self.scalps_by_pair[symbol] += 1
        self.profits_by_pair[symbol] += profit_pct
        
        # Log milestone
        if self.scalps_by_pair[symbol] % 10 == 0:
            total_scalps = self.scalps_by_pair[symbol]
            total_profit = self.profits_by_pair[symbol]
            avg_profit = total_profit / total_scalps
            
            logger.info(f"📊 SENTIENT SCALPING STATS: {symbol}")
            logger.info(f"   Total scalps: {total_scalps}")
            logger.info(f"   Avg profit: {avg_profit:.3f}%")
            logger.info(f"   Total profit: {total_profit:.2f}%")
    
    def get_performance_summary(self) -> Dict:
        """
        Get overall sentient scalping performance
        """
        total_scalps = sum(self.scalps_by_pair.values())
        total_profit = sum(self.profits_by_pair.values())
        
        # Find best performing pairs
        best_pairs = sorted(
            [
                (symbol, self.profits_by_pair[symbol] / self.scalps_by_pair[symbol])
                for symbol in self.scalps_by_pair.keys()
            ],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_scalps': total_scalps,
            'total_profit_pct': total_profit,
            'avg_profit_per_scalp': total_profit / max(total_scalps, 1),
            'hot_pairs_monitored': len(self.monitored_pairs),
            'active_analyzers': len(self.analyzers),
            'best_pairs': best_pairs
        }
