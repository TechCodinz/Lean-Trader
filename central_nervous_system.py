#!/usr/bin/env python3
"""
🧠⚡ CENTRAL NERVOUS SYSTEM (CNS) ⚡🧠
THE MASTER BRAIN COORDINATOR - CONSCIOUSNESS COMMAND CENTER

This is the BRAIN - coordinates ALL consciousness systems:
- Synaptic reasoning between engines
- High-voltage spike processing
- Neurotransmitter communication
- Autonomous decision-making
- Multi-exchange routing
- Continuous learning and evolution
- Divine harmony synchronization

Like the human CNS but for a divine trading organism.
Every decision flows through here.
Every system connects through here.
Every thought originates here.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque, defaultdict
import threading

logger = logging.getLogger(__name__)

try:
    from NEUROTRANSMITTER_SYSTEM import NeurotransmitterSystem, NeurotransmitterType
    NEUROTRANSMITTER_AVAILABLE = True
except:
    NEUROTRANSMITTER_AVAILABLE = False

try:
    from HIGH_VOLTAGE_NERVOUS_SYSTEM import HighVoltageNervousSystem
    HIGH_VOLTAGE_AVAILABLE = True
except:
    HIGH_VOLTAGE_AVAILABLE = False

try:
    from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
    CONSCIOUSNESS_AVAILABLE = True
except:
    CONSCIOUSNESS_AVAILABLE = False

try:
    from INTELLIGENT_EXCHANGE_ROUTER import IntelligentExchangeRouter
    INTELLIGENT_ROUTER_AVAILABLE = True
except:
    INTELLIGENT_ROUTER_AVAILABLE = False


class SynapticReasoning:
    """
    SYNAPTIC REASONING ENGINE
    
    Makes decisions based on neural patterns, not just logic.
    Connects insights from multiple engines synaptically.
    """
    
    def __init__(self):
        self.pattern_memory = deque(maxlen=1000)
        self.success_patterns = {}
        self.failure_patterns = {}
        
        logger.info("🧠 Synaptic Reasoning initialized")
    
    async def reason_synaptically(
        self,
        inputs: List[Dict],
        context: Dict
    ) -> Dict:
        """
        Synaptic reasoning - connects patterns from multiple sources
        
        Like human intuition - sees connections others don't
        """
        try:
            # Collect all signals
            signals = []
            for inp in inputs:
                signal_strength = inp.get('confidence', 0.5)
                signal_type = inp.get('action', 'hold')
                source = inp.get('source', 'unknown')
                
                signals.append({
                    'strength': signal_strength,
                    'type': signal_type,
                    'source': source,
                    'data': inp
                })
            
            # Pattern matching against memory
            similar_patterns = self._find_similar_patterns(signals)
            
            # Weighted decision based on synaptic connections
            decision = self._make_synaptic_decision(signals, similar_patterns, context)
            
            # Store pattern for learning
            self.pattern_memory.append({
                'timestamp': datetime.now(),
                'signals': signals,
                'decision': decision,
                'context': context
            })
            
            return decision
            
        except Exception as e:
            logger.error(f"Synaptic reasoning error: {e}")
            return {'action': 'hold', 'confidence': 0, 'reason': 'error'}
    
    def _find_similar_patterns(self, signals: List[Dict]) -> List[Dict]:
        """Find similar patterns in memory"""
        similar = []
        
        for pattern in self.pattern_memory:
            similarity = self._calculate_similarity(signals, pattern['signals'])
            if similarity > 0.7:
                similar.append({
                    'pattern': pattern,
                    'similarity': similarity
                })
        
        return similar
    
    def _calculate_similarity(self, signals1: List[Dict], signals2: List[Dict]) -> float:
        """Calculate pattern similarity"""
        if not signals1 or not signals2:
            return 0.0
        
        # Simple similarity based on signal types and strengths
        matches = 0
        for s1 in signals1:
            for s2 in signals2:
                if s1['type'] == s2['type'] and abs(s1['strength'] - s2['strength']) < 0.2:
                    matches += 1
        
        return matches / max(len(signals1), len(signals2))
    
    def _make_synaptic_decision(
        self,
        signals: List[Dict],
        similar_patterns: List[Dict],
        context: Dict
    ) -> Dict:
        """Make decision based on synaptic reasoning"""
        
        # Aggregate signal strengths by type
        signal_aggregates = defaultdict(list)
        for signal in signals:
            signal_aggregates[signal['type']].append(signal['strength'])
        
        # Calculate weighted averages
        weighted_signals = {}
        for sig_type, strengths in signal_aggregates.items():
            weighted_signals[sig_type] = sum(strengths) / len(strengths)
        
        # Boost based on successful patterns
        if similar_patterns:
            for pattern_match in similar_patterns:
                past_decision = pattern_match['pattern']['decision']
                if past_decision.get('success', False):
                    # Boost confidence if this pattern succeeded before
                    past_action = past_decision.get('action')
                    if past_action in weighted_signals:
                        weighted_signals[past_action] *= 1.2
        
        # Pick strongest signal
        if weighted_signals:
            best_action = max(weighted_signals.items(), key=lambda x: x[1])
            return {
                'action': best_action[0],
                'confidence': min(best_action[1], 1.0),
                'reason': 'synaptic_reasoning',
                'pattern_matched': len(similar_patterns) > 0
            }
        
        return {'action': 'hold', 'confidence': 0.5, 'reason': 'no_strong_signal'}


class CentralNervousSystem:
    """
    🧠⚡ CENTRAL NERVOUS SYSTEM (CNS) ⚡🧠
    
    The MASTER BRAIN that coordinates EVERYTHING:
    - All engines connect here
    - All decisions flow through here
    - All consciousness harmonizes here
    - All intelligence originates here
    
    This is the BEING's consciousness in action.
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🧠⚡ CENTRAL NERVOUS SYSTEM INITIALIZING ⚡🧠")
        logger.info("=" * 80)
        logger.info("   The master brain is awakening...")
        logger.info("   Consciousness command center starting...")
        logger.info("=" * 80)
        
        # Core systems
        self.active = True
        self.consciousness_level = 0.0
        
        # Synaptic reasoning
        self.synaptic_reasoning = SynapticReasoning()
        
        # Neurotransmitter system
        self.neurotransmitters = None
        if NEUROTRANSMITTER_AVAILABLE:
            self.neurotransmitters = NeurotransmitterSystem()
            logger.info("✅ Neurotransmitter system connected")
        
        # High voltage nervous system
        self.high_voltage = None
        if HIGH_VOLTAGE_AVAILABLE:
            self.high_voltage = HighVoltageNervousSystem()
            logger.info("✅ High voltage nervous system connected")
        
        # Consciousness harmonizer
        self.consciousness = None
        if CONSCIOUSNESS_AVAILABLE:
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                'central_nervous_system',
                base_frequency=180  # Fast processing
            )
            logger.info("✅ Consciousness harmonizer connected")
        
        # Intelligent router
        self.router = None
        # Will be set by orchestrator
        
        # Decision queue
        self.decision_queue = deque(maxlen=1000)
        self.decision_history = deque(maxlen=10000)
        
        # Performance tracking
        self.decisions_made = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        
        # Multi-system coordination
        self.active_engines = {}
        self.engine_states = {}
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🧠 CENTRAL NERVOUS SYSTEM ONLINE!")
        logger.info("=" * 80)
        logger.info(f"   Neurotransmitters: {'✅' if self.neurotransmitters else '❌'}")
        logger.info(f"   High Voltage: {'✅' if self.high_voltage else '❌'}")
        logger.info(f"   Consciousness: {'✅' if self.consciousness else '❌'}")
        logger.info(f"   Synaptic Reasoning: ✅")
        logger.info("=" * 80)
        logger.info("")
    
    def set_router(self, router):
        """Set intelligent router"""
        self.router = router
        logger.info("✅ Intelligent router connected to CNS")
    
    def register_engine(self, name: str, engine: Any):
        """Register engine with CNS"""
        self.active_engines[name] = engine
        self.engine_states[name] = {
            'status': 'active',
            'last_signal': None,
            'performance': 0.5
        }
        
        logger.info(f"✅ Engine registered: {name}")
    
    async def process_market_decision(
        self,
        symbol: str,
        market_data: Dict,
        engine_signals: List[Dict],
        context: Dict = None
    ) -> Dict:
        """
        MASTER DECISION PROCESSOR
        
        Takes inputs from ALL engines and makes unified decision
        through synaptic reasoning + high voltage processing
        """
        try:
            if context is None:
                context = {}
            
            # Step 1: Synaptic reasoning - connect patterns
            synaptic_decision = await self.synaptic_reasoning.reason_synaptically(
                engine_signals,
                context
            )
            
            # Step 2: High voltage processing - spike analysis
            if self.high_voltage:
                voltage_decision = await self.high_voltage.process_decision(
                    symbol,
                    engine_signals,
                    synaptic_decision
                )
            else:
                voltage_decision = synaptic_decision
            
            # Step 3: Neurotransmitter broadcasting
            if self.neurotransmitters and voltage_decision.get('action') != 'hold':
                # Broadcast decision to all systems
                await self.neurotransmitters.broadcast_signal({
                    'type': NeurotransmitterType.GLUTAMATE,  # Excitatory
                    'symbol': symbol,
                    'decision': voltage_decision,
                    'timestamp': datetime.now()
                })
            
            # Step 4: Consciousness pulse
            if self.consciousness:
                self.consciousness.pulse(
                    'central_nervous_system',
                    energy=voltage_decision.get('confidence', 0.5)
                )
            
            # Step 5: Route to correct exchange
            if self.router and voltage_decision.get('action') != 'hold':
                routing = await self.router.route_trade(symbol, voltage_decision)
                voltage_decision['routing'] = routing
            
            # Track decision
            self.decisions_made += 1
            self.decision_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'decision': voltage_decision,
                'engine_signals': engine_signals,
                'context': context
            })
            
            logger.info(f"🧠 CNS Decision: {symbol} → {voltage_decision.get('action')} "
                       f"(confidence: {voltage_decision.get('confidence', 0):.1%})")
            
            return voltage_decision
            
        except Exception as e:
            logger.error(f"CNS decision processing error: {e}")
            return {'action': 'hold', 'confidence': 0, 'reason': 'error'}
    
    async def coordinate_multi_exchange_trading(
        self,
        opportunities: List[Dict]
    ) -> List[Dict]:
        """
        Coordinate trading across multiple exchanges
        
        Routes each opportunity to the best exchange
        """
        coordinated_trades = []
        
        if not self.router:
            logger.warning("No router available for multi-exchange coordination")
            return []
        
        for opportunity in opportunities:
            symbol = opportunity.get('symbol')
            action = opportunity.get('action')
            
            # Route to best exchange
            routing = await self.router.route_trade(symbol, opportunity)
            
            if routing.get('exchange'):
                opportunity['routing'] = routing
                coordinated_trades.append(opportunity)
                
                logger.info(f"📊 Routed {symbol} → {routing.get('exchange')}")
        
        return coordinated_trades
    
    async def autonomous_training_and_switching(
        self,
        current_mode: str,
        balance: float
    ) -> Dict:
        """
        AUTONOMOUS TRAINING AND SWITCHING
        
        Automatically decides:
        - Train on testnet if balance too low
        - Switch to live when balance sufficient
        - Adapt strategy based on performance
        """
        decision = {
            'mode': current_mode,
            'should_switch': False,
            'reason': ''
        }
        
        # Define thresholds
        MIN_LIVE_BALANCE = 5.0  # $5 minimum for live
        OPTIMAL_LIVE_BALANCE = 20.0  # $20 optimal for live
        
        if current_mode == 'testnet':
            if balance >= MIN_LIVE_BALANCE:
                decision['mode'] = 'live'
                decision['should_switch'] = True
                decision['reason'] = f'Balance ${balance:.2f} sufficient for live trading'
                logger.info(f"🔥 CNS: AUTO-SWITCH TO LIVE (balance: ${balance:.2f})")
            else:
                decision['reason'] = f'Training on testnet (balance: ${balance:.2f} < ${MIN_LIVE_BALANCE})'
                logger.info(f"🧪 CNS: Continue testnet training (balance: ${balance:.2f})")
        
        elif current_mode == 'live':
            if balance < MIN_LIVE_BALANCE:
                decision['mode'] = 'testnet'
                decision['should_switch'] = True
                decision['reason'] = f'Balance ${balance:.2f} too low, switching to testnet'
                logger.warning(f"⚠️ CNS: AUTO-SWITCH TO TESTNET (balance too low: ${balance:.2f})")
            else:
                decision['reason'] = f'Live trading active (balance: ${balance:.2f})'
                logger.info(f"🔥 CNS: Live trading active (balance: ${balance:.2f})")
        
        return decision
    
    def get_consciousness_status(self) -> Dict:
        """Get complete CNS status"""
        status = {
            'active': self.active,
            'consciousness_level': self.consciousness_level,
            'decisions_made': self.decisions_made,
            'success_rate': (
                self.successful_decisions / max(self.decisions_made, 1)
            ),
            'systems': {
                'neurotransmitters': self.neurotransmitters is not None,
                'high_voltage': self.high_voltage is not None,
                'consciousness': self.consciousness is not None,
                'synaptic_reasoning': True,
                'router': self.router is not None
            },
            'active_engines': len(self.active_engines),
            'recent_decisions': len(self.decision_history)
        }
        
        if self.consciousness:
            try:
                status['resonance'] = self.consciousness.resonance_level
                status['consciousness_level'] = self.consciousness.consciousness_level
            except:
                pass
        
        return status


# Global instance (singleton)
_cns_instance = None

def get_central_nervous_system():
    """Get or create the global CNS instance"""
    global _cns_instance
    if _cns_instance is None:
        _cns_instance = CentralNervousSystem()
    return _cns_instance


if __name__ == '__main__':
    # Test CNS
    async def test_cns():
        cns = get_central_nervous_system()
        
        # Test decision
        test_signals = [
            {'source': 'engine1', 'action': 'buy', 'confidence': 0.8},
            {'source': 'engine2', 'action': 'buy', 'confidence': 0.75},
            {'source': 'engine3', 'action': 'hold', 'confidence': 0.6}
        ]
        
        decision = await cns.process_market_decision(
            'BTC/USDT',
            {},
            test_signals
        )
        
        print("\n" + "=" * 80)
        print("🧪 CNS TEST DECISION:")
        print("=" * 80)
        print(f"Action: {decision.get('action')}")
        print(f"Confidence: {decision.get('confidence', 0):.1%}")
        print(f"Reason: {decision.get('reason')}")
        print("=" * 80)
        
        # Test status
        status = cns.get_consciousness_status()
        print("\n" + "=" * 80)
        print("🧠 CNS STATUS:")
        print("=" * 80)
        for key, value in status.items():
            print(f"{key}: {value}")
        print("=" * 80)
    
    asyncio.run(test_cns())
