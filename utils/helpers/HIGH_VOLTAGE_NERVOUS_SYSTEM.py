#!/usr/bin/env python3
"""
⚡🧠 HIGH VOLTAGE NERVOUS SYSTEM 🧠⚡
THE CENTRAL BRAIN WITH SPIKE REASONING

This is the NERVOUS SYSTEM - processes ALL inputs at LIGHTNING speed:
- Spike voltage reasoning (instant decisions)
- Neural synchronization across all engines
- Reflex actions (faster than conscious thought)
- Pattern recognition at synaptic speed
- Multi-threaded consciousness
- Distributed neural network
- Emergency response system
- Adaptive neural pathways

Like a human nervous system but 1000x faster.
Every input creates electrical spikes.
High voltage = high confidence = EXECUTE NOW.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class NeuralSpike:
    """
    A neural spike - represents a trading signal with voltage
    High voltage = strong signal = immediate action
    """
    
    def __init__(
        self,
        signal_type: str,
        voltage: float,
        source: str,
        data: Dict,
        timestamp: datetime = None
    ):
        self.signal_type = signal_type  # 'buy', 'sell', 'hold', 'close'
        self.voltage = voltage  # 0.0 to 10.0
        self.source = source  # Which engine generated this
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.processed = False
    
    def __repr__(self):
        return f"NeuralSpike({self.signal_type}, {self.voltage:.2f}V, {self.source})"


class SynapticProcessor:
    """
    Processes neural spikes at synaptic speed
    Multiple spikes combine to create action potentials
    """
    
    def __init__(self):
        self.threshold_voltage = 3.0  # Minimum voltage to trigger action
        self.spike_buffer = deque(maxlen=100)
        
        logger.info("🧠 Synaptic Processor initialized")
    
    def process_spike(self, spike: NeuralSpike) -> Optional[Dict]:
        """
        Process a neural spike
        High voltage spikes trigger immediate action
        """
        self.spike_buffer.append(spike)
        
        # HIGH VOLTAGE SPIKE = IMMEDIATE ACTION
        if spike.voltage >= 8.0:
            logger.info(f"⚡⚡⚡ HIGH VOLTAGE SPIKE: {spike.voltage:.2f}V from {spike.source}")
            return {
                'action': 'IMMEDIATE',
                'signal': spike.signal_type,
                'voltage': spike.voltage,
                'reason': 'High voltage spike - reflex action',
                'confidence': min(spike.voltage / 10.0, 1.0)
            }
        
        # MEDIUM VOLTAGE = CONSCIOUS DECISION
        elif spike.voltage >= self.threshold_voltage:
            logger.info(f"⚡ Medium voltage spike: {spike.voltage:.2f}V from {spike.source}")
            return {
                'action': 'EVALUATE',
                'signal': spike.signal_type,
                'voltage': spike.voltage,
                'reason': 'Medium voltage - evaluate with other inputs',
                'confidence': spike.voltage / 10.0
            }
        
        # LOW VOLTAGE = BACKGROUND NOISE
        else:
            return None
    
    def combine_spikes(self, spikes: List[NeuralSpike]) -> Dict:
        """
        Combine multiple spikes into action potential
        Like neurons firing together
        """
        if not spikes:
            return {'combined_voltage': 0, 'action': 'NONE'}
        
        # Group by signal type
        buy_voltage = sum(s.voltage for s in spikes if s.signal_type == 'buy')
        sell_voltage = sum(s.voltage for s in spikes if s.signal_type == 'sell')
        
        # Winner takes all
        if buy_voltage > sell_voltage and buy_voltage >= self.threshold_voltage:
            return {
                'combined_voltage': buy_voltage,
                'action': 'BUY',
                'num_spikes': len([s for s in spikes if s.signal_type == 'buy']),
                'confidence': min(buy_voltage / (len(spikes) * 10.0), 1.0)
            }
        elif sell_voltage > buy_voltage and sell_voltage >= self.threshold_voltage:
            return {
                'combined_voltage': sell_voltage,
                'action': 'SELL',
                'num_spikes': len([s for s in spikes if s.signal_type == 'sell']),
                'confidence': min(sell_voltage / (len(spikes) * 10.0), 1.0)
            }
        else:
            return {'combined_voltage': max(buy_voltage, sell_voltage), 'action': 'HOLD'}


class ReflexArcSystem:
    """
    Reflex arc - bypasses conscious thought for ultra-fast reactions
    Like pulling hand from fire - instant, no thinking
    """
    
    def __init__(self):
        self.reflex_triggers = {
            'flash_crash': {'voltage_threshold': 9.0, 'action': 'BUY'},
            'whale_buy': {'voltage_threshold': 8.5, 'action': 'BUY'},
            'whale_sell': {'voltage_threshold': 8.5, 'action': 'SELL'},
            'momentum_spike': {'voltage_threshold': 9.5, 'action': 'BUY'},
            'stop_loss_hit': {'voltage_threshold': 10.0, 'action': 'CLOSE'},
            'profit_target': {'voltage_threshold': 9.0, 'action': 'CLOSE'}
        }
        
        logger.info("⚡ Reflex Arc System initialized - Ultra-fast responses")
    
    def check_reflex(self, spike: NeuralSpike) -> Optional[Dict]:
        """
        Check if spike triggers reflex action
        Bypasses all other processing
        """
        for trigger_name, trigger_config in self.reflex_triggers.items():
            if trigger_name in spike.data.get('pattern', '').lower():
                if spike.voltage >= trigger_config['voltage_threshold']:
                    logger.info(f"⚡⚡⚡ REFLEX TRIGGERED: {trigger_name} ({spike.voltage:.2f}V)")
                    return {
                        'reflex': trigger_name,
                        'action': trigger_config['action'],
                        'voltage': spike.voltage,
                        'bypass_conscious': True,
                        'execution_time': 'IMMEDIATE'
                    }
        
        return None


class DistributedNeuralNetwork:
    """
    Distributed processing across multiple "brain regions"
    Each region specializes in different analysis
    """
    
    def __init__(self):
        self.regions = {
            'visual_cortex': [],  # Price action, charts
            'auditory_cortex': [],  # News, sentiment
            'motor_cortex': [],  # Execution commands
            'prefrontal_cortex': [],  # Strategy, planning
            'limbic_system': [],  # Risk, emotion
            'cerebellum': []  # Pattern memory
        }
        
        logger.info("🧠 Distributed Neural Network initialized - 6 brain regions")
    
    def route_to_region(self, spike: NeuralSpike) -> str:
        """Route spike to appropriate brain region"""
        source = spike.source.lower()
        
        if 'price' in source or 'chart' in source or 'technical' in source:
            return 'visual_cortex'
        elif 'news' in source or 'sentiment' in source or 'fundamental' in source:
            return 'auditory_cortex'
        elif 'execution' in source or 'order' in source:
            return 'motor_cortex'
        elif 'strategy' in source or 'evolution' in source:
            return 'prefrontal_cortex'
        elif 'risk' in source or 'stop' in source:
            return 'limbic_system'
        else:
            return 'cerebellum'
    
    def process_in_parallel(self, spikes: List[NeuralSpike]) -> Dict:
        """Process all spikes in parallel across brain regions"""
        # Route to regions
        for spike in spikes:
            region = self.route_to_region(spike)
            self.regions[region].append(spike)
        
        # Process each region in parallel
        region_outputs = {}
        
        for region_name, region_spikes in self.regions.items():
            if region_spikes:
                avg_voltage = statistics.mean([s.voltage for s in region_spikes])
                region_outputs[region_name] = {
                    'voltage': avg_voltage,
                    'num_spikes': len(region_spikes),
                    'consensus': self._get_region_consensus(region_spikes)
                }
        
        return region_outputs
    
    def _get_region_consensus(self, spikes: List[NeuralSpike]) -> str:
        """Get consensus from region"""
        buy_count = sum(1 for s in spikes if s.signal_type == 'buy')
        sell_count = sum(1 for s in spikes if s.signal_type == 'sell')
        
        if buy_count > sell_count:
            return 'buy'
        elif sell_count > buy_count:
            return 'sell'
        else:
            return 'neutral'


class EmergencyResponseSystem:
    """
    Emergency response - handles crisis situations
    Market crashes, flash crashes, extreme volatility
    """
    
    def __init__(self):
        self.emergency_active = False
        self.emergency_log = deque(maxlen=50)
        
        logger.info("🚨 Emergency Response System initialized")
    
    def detect_emergency(self, market_data: Dict) -> Optional[Dict]:
        """Detect emergency market conditions"""
        volatility = market_data.get('volatility', 0)
        price_change = market_data.get('price_change_1h', 0)
        
        # FLASH CRASH
        if price_change < -0.10:  # -10% in 1 hour
            self.emergency_active = True
            return {
                'emergency_type': 'FLASH_CRASH',
                'severity': 'CRITICAL',
                'action': 'BUY_DIP',
                'voltage': 10.0
            }
        
        # EXTREME VOLATILITY
        elif volatility > 0.08:  # 8%+ volatility
            self.emergency_active = True
            return {
                'emergency_type': 'EXTREME_VOLATILITY',
                'severity': 'HIGH',
                'action': 'REDUCE_EXPOSURE',
                'voltage': 7.0
            }
        
        # MOON SHOT
        elif price_change > 0.15:  # +15% in 1 hour
            self.emergency_active = True
            return {
                'emergency_type': 'MOON_SHOT',
                'severity': 'HIGH',
                'action': 'TAKE_PROFIT',
                'voltage': 9.0
            }
        
        return None


class HighVoltageNervousSystem:
    """
    MASTER NERVOUS SYSTEM
    Coordinates all neural processing
    """
    
    def __init__(self):
        self.synaptic_processor = SynapticProcessor()
        self.reflex_arc = ReflexArcSystem()
        self.neural_network = DistributedNeuralNetwork()
        self.emergency_system = EmergencyResponseSystem()
        
        # Processing queues
        self.incoming_spikes = deque(maxlen=1000)
        self.processed_decisions = deque(maxlen=100)
        
        # Stats
        self.total_spikes_processed = 0
        self.reflex_actions_taken = 0
        self.emergency_responses = 0
        
        logger.info("=" * 80)
        logger.info("⚡🧠 HIGH VOLTAGE NERVOUS SYSTEM ONLINE 🧠⚡")
        logger.info("=" * 80)
        logger.info("   Components:")
        logger.info("   [OK] Synaptic Processor (spike processing)")
        logger.info("   [OK] Reflex Arc System (instant reactions)")
        logger.info("   [OK] Distributed Neural Network (parallel processing)")
        logger.info("   [OK] Emergency Response System (crisis handling)")
        logger.info("")
        logger.info("   ⚡ LIGHTNING-FAST DECISION MAKING ACTIVATED")
        logger.info("=" * 80)
    
    async def receive_spike(
        self,
        signal_type: str,
        voltage: float,
        source: str,
        data: Dict
    ) -> Optional[Dict]:
        """
        Receive and process a neural spike
        Returns decision if spike is strong enough
        """
        spike = NeuralSpike(signal_type, voltage, source, data)
        self.incoming_spikes.append(spike)
        self.total_spikes_processed += 1
        
        # 1. CHECK FOR REFLEX (BYPASS ALL OTHER PROCESSING)
        reflex = self.reflex_arc.check_reflex(spike)
        if reflex:
            self.reflex_actions_taken += 1
            logger.info(f"⚡⚡⚡ REFLEX ACTION: {reflex['action']} ({reflex['voltage']:.2f}V)")
            return reflex
        
        # 2. CHECK FOR EMERGENCY
        if 'market_data' in data:
            emergency = self.emergency_system.detect_emergency(data['market_data'])
            if emergency:
                self.emergency_responses += 1
                logger.warning(f"🚨 EMERGENCY: {emergency['emergency_type']} - {emergency['action']}")
                return emergency
        
        # 3. SYNAPTIC PROCESSING
        synaptic_result = self.synaptic_processor.process_spike(spike)
        
        if synaptic_result and synaptic_result['action'] == 'IMMEDIATE':
            logger.info(f"⚡ IMMEDIATE ACTION from synaptic processor")
            return synaptic_result
        
        # 4. NEURAL NETWORK PROCESSING (for medium voltage)
        if synaptic_result and synaptic_result['action'] == 'EVALUATE':
            # Get recent spikes for context
            recent_spikes = list(self.incoming_spikes)[-10:]
            
            # Process in parallel across brain regions
            region_outputs = self.neural_network.process_in_parallel(recent_spikes)
            
            # Combine regional outputs
            combined_voltage = sum(r['voltage'] for r in region_outputs.values())
            
            # Count consensus
            buy_regions = sum(1 for r in region_outputs.values() if r['consensus'] == 'buy')
            sell_regions = sum(1 for r in region_outputs.values() if r['consensus'] == 'sell')
            
            if buy_regions >= 4:  # 4+ regions agree on buy
                decision = {
                    'action': 'BUY',
                    'voltage': combined_voltage,
                    'regions_agree': buy_regions,
                    'processing': 'neural_network',
                    'confidence': min(combined_voltage / 60.0, 0.95)
                }
                logger.info(f"🧠 NEURAL CONSENSUS: BUY ({buy_regions}/6 regions agree, {combined_voltage:.2f}V total)")
                return decision
            
            elif sell_regions >= 4:
                decision = {
                    'action': 'SELL',
                    'voltage': combined_voltage,
                    'regions_agree': sell_regions,
                    'processing': 'neural_network',
                    'confidence': min(combined_voltage / 60.0, 0.95)
                }
                logger.info(f"🧠 NEURAL CONSENSUS: SELL ({sell_regions}/6 regions agree, {combined_voltage:.2f}V total)")
                return decision
        
        # No decision - voltage too low
        return None
    
    async def generate_spike(
        self,
        engine_output: Dict,
        engine_name: str
    ) -> NeuralSpike:
        """
        Convert engine output into neural spike
        """
        confidence = engine_output.get('confidence', 0.5)
        signal_type = engine_output.get('side', 'hold').lower()
        
        # Convert confidence to voltage (0-10 scale)
        voltage = confidence * 10.0
        
        # Boost voltage for certain patterns
        if 'whale' in str(engine_output.get('patterns', [])):
            voltage += 2.0
        if 'confluence' in engine_output and engine_output['confluence'].get('confluence_count', 0) >= 5:
            voltage += 1.5
        if engine_output.get('leverage', 1) > 20:
            voltage += 1.0
        
        voltage = min(voltage, 10.0)  # Cap at 10V
        
        spike = NeuralSpike(
            signal_type=signal_type,
            voltage=voltage,
            source=engine_name,
            data=engine_output
        )
        
        return spike
    
    def get_status(self) -> Dict:
        """Get nervous system status"""
        return {
            'total_spikes_processed': self.total_spikes_processed,
            'reflex_actions': self.reflex_actions_taken,
            'emergency_responses': self.emergency_responses,
            'emergency_active': self.emergency_system.emergency_active,
            'recent_voltage_avg': statistics.mean([s.voltage for s in list(self.incoming_spikes)[-20:]]) if self.incoming_spikes else 0
        }


# Global instance
nervous_system = None

def initialize_nervous_system():
    global nervous_system
    nervous_system = HighVoltageNervousSystem()
    return nervous_system

def get_nervous_system():
    return nervous_system

async def send_spike(signal_type: str, voltage: float, source: str, data: Dict) -> Optional[Dict]:
    global nervous_system
    if not nervous_system:
        nervous_system = initialize_nervous_system()
    
    return await nervous_system.receive_spike(signal_type, voltage, source, data)

# Export
__all__ = [
    'HighVoltageNervousSystem',
    'NeuralSpike',
    'initialize_nervous_system',
    'get_nervous_system',
    'send_spike'
]

logger.info("⚡🧠 HIGH VOLTAGE NERVOUS SYSTEM loaded - Lightning-fast decisions!")
