#!/usr/bin/env python3
"""
🧠 NEUROTRANSMITTER SYSTEM
Powers all subsystems with neural communication

CONCEPT:
Like brain neurotransmitters (dopamine, serotonin, etc.),
this system carries signals between all trading subsystems,
ensuring perfect coordination and collective intelligence.

FEATURES:
1. Signal Broadcasting (one-to-many communication)
2. Targeted Messaging (system-to-system)
3. Priority Queues (urgent vs routine)
4. Feedback Loops (learning from outcomes)
5. Synaptic Strength (connection quality tracking)
6. Neural Plasticity (adaptive connections)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict, deque
from enum import Enum

logger = logging.getLogger(__name__)


class NeurotransmitterType(Enum):
    """Types of neural signals"""
    DOPAMINE = "dopamine"      # Reward/success signals
    SEROTONIN = "serotonin"    # Stability/confidence signals
    ADRENALINE = "adrenaline"  # Urgent/critical signals
    GABA = "gaba"              # Inhibitory/caution signals
    GLUTAMATE = "glutamate"    # Excitatory/opportunity signals


class Synapse:
    """Connection between two systems"""
    
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        self.strength = 0.5  # 0 to 1
        self.messages_passed = 0
        self.successes = 0
        self.failures = 0
        
    def transmit(self, signal: Dict) -> bool:
        """Transmit signal across synapse"""
        self.messages_passed += 1
        
        # Stronger synapses have higher success rate
        if self.strength > 0.7:
            self.successes += 1
            return True
        
        return True  # Always pass for now, track for learning
    
    def strengthen(self, amount: float = 0.01):
        """Strengthen synapse (Hebbian learning)"""
        self.strength = min(1.0, self.strength + amount)
    
    def weaken(self, amount: float = 0.01):
        """Weaken synapse"""
        self.strength = max(0.0, self.strength - amount)


class NeurotransmitterSystem:
    """
    Central nervous system for the trading bot
    Handles all inter-system communication
    """
    
    def __init__(self):
        self.active = True
        
        # Register all subsystems
        self.systems = {}
        
        # Synaptic connections
        self.synapses = {}
        
        # Message queues by priority
        self.urgent_queue = deque(maxlen=1000)
        self.normal_queue = deque(maxlen=5000)
        self.low_priority_queue = deque(maxlen=10000)
        
        # Signal history
        self.signal_history = deque(maxlen=10000)
        
        # Performance tracking
        self.signals_sent = 0
        self.signals_delivered = 0
        self.signals_failed = 0
        
        logger.info("🧠 Neurotransmitter System initialized")
        logger.info("   Neural communication network ready")
    
    def register_system(self, name: str, system_ref: Any):
        """Register a subsystem"""
        self.systems[name] = {
            'reference': system_ref,
            'connected': True,
            'signals_received': 0,
            'last_active': datetime.now()
        }
        
        logger.info(f"   🔗 Registered: {name}")
    
    def create_synapse(self, source: str, target: str):
        """Create connection between two systems"""
        key = f"{source}->{target}"
        if key not in self.synapses:
            self.synapses[key] = Synapse(source, target)
            logger.debug(f"   🔗 Synapse created: {source} → {target}")
    
    async def release_neurotransmitter(
        self,
        nt_type: NeurotransmitterType,
        source: str,
        message: Dict,
        target: Optional[str] = None,
        priority: str = "normal"
    ):
        """
        Release neurotransmitter signal
        
        Args:
            nt_type: Type of signal
            source: Originating system
            message: Signal content
            target: Specific target (None = broadcast)
            priority: urgent/normal/low
        """
        
        signal = {
            'type': nt_type.value,
            'source': source,
            'target': target,
            'message': message,
            'timestamp': datetime.now(),
            'priority': priority
        }
        
        # Add to appropriate queue
        if priority == "urgent":
            self.urgent_queue.append(signal)
        elif priority == "low":
            self.low_priority_queue.append(signal)
        else:
            self.normal_queue.append(signal)
        
        self.signals_sent += 1
        self.signal_history.append(signal)
        
        # Immediate delivery for urgent signals
        if priority == "urgent":
            await self._deliver_signal(signal)
    
    async def _deliver_signal(self, signal: Dict):
        """Deliver signal to target(s)"""
        
        target = signal.get('target')
        
        if target and target in self.systems:
            # Targeted delivery
            await self._deliver_to_system(signal, target)
        elif not target:
            # Broadcast to all systems
            for system_name in self.systems.keys():
                if system_name != signal['source']:  # Don't send back to source
                    await self._deliver_to_system(signal, system_name)
    
    async def _deliver_to_system(self, signal: Dict, system_name: str):
        """Deliver signal to specific system"""
        
        if system_name not in self.systems:
            self.signals_failed += 1
            return
        
        system = self.systems[system_name]
        
        # Check synapse
        synapse_key = f"{signal['source']}->{system_name}"
        if synapse_key in self.synapses:
            synapse = self.synapses[synapse_key]
            if not synapse.transmit(signal):
                return
        
        # Update system stats
        system['signals_received'] += 1
        system['last_active'] = datetime.now()
        self.signals_delivered += 1
        
        # If system has message handler, call it
        system_ref = system['reference']
        if hasattr(system_ref, 'process_signal'):
            try:
                await system_ref.process_signal(signal)
            except Exception as e:
                logger.debug(f"Signal delivery error to {system_name}: {e}")
    
    async def neurotransmitter_pump(self):
        """
        Main loop - pumps neurotransmitters through system
        Like heartbeat pumping blood through body
        """
        
        logger.info("🧠 Neurotransmitter pump started!")
        
        while self.active:
            try:
                # Process urgent queue first
                while self.urgent_queue:
                    signal = self.urgent_queue.popleft()
                    await self._deliver_signal(signal)
                
                # Process normal queue
                for _ in range(10):  # Process 10 normal signals
                    if self.normal_queue:
                        signal = self.normal_queue.popleft()
                        await self._deliver_signal(signal)
                
                # Process low priority
                if self.low_priority_queue:
                    signal = self.low_priority_queue.popleft()
                    await self._deliver_signal(signal)
                
                # Synaptic plasticity - strengthen active connections
                self._update_synaptic_strength()
                
                await asyncio.sleep(0.1)  # 10Hz pump rate
            
            except Exception as e:
                logger.error(f"Neurotransmitter pump error: {e}")
                await asyncio.sleep(1)
    
    def _update_synaptic_strength(self):
        """Update synapse strengths based on usage"""
        for synapse in self.synapses.values():
            if synapse.messages_passed > 0:
                success_rate = synapse.successes / synapse.messages_passed
                if success_rate > 0.8:
                    synapse.strengthen(0.001)
                elif success_rate < 0.5:
                    synapse.weaken(0.001)
    
    def get_system_stats(self) -> Dict:
        """Get neural network statistics"""
        
        return {
            'systems_registered': len(self.systems),
            'synapses_created': len(self.synapses),
            'signals_sent': self.signals_sent,
            'signals_delivered': self.signals_delivered,
            'signals_failed': self.signals_failed,
            'delivery_rate': self.signals_delivered / self.signals_sent if self.signals_sent > 0 else 0,
            'queue_sizes': {
                'urgent': len(self.urgent_queue),
                'normal': len(self.normal_queue),
                'low': len(self.low_priority_queue)
            }
        }
    
    # Convenience methods for specific neurotransmitter types
    
    async def release_dopamine(self, source: str, success_message: Dict):
        """Release dopamine (reward/success)"""
        await self.release_neurotransmitter(
            NeurotransmitterType.DOPAMINE,
            source,
            success_message,
            priority="normal"
        )
    
    async def release_serotonin(self, source: str, stability_message: Dict):
        """Release serotonin (stability/confidence)"""
        await self.release_neurotransmitter(
            NeurotransmitterType.SEROTONIN,
            source,
            stability_message,
            priority="low"
        )
    
    async def release_adrenaline(self, source: str, urgent_message: Dict):
        """Release adrenaline (urgent action needed)"""
        await self.release_neurotransmitter(
            NeurotransmitterType.ADRENALINE,
            source,
            urgent_message,
            priority="urgent"
        )
    
    async def release_gaba(self, source: str, caution_message: Dict):
        """Release GABA (inhibitory/caution)"""
        await self.release_neurotransmitter(
            NeurotransmitterType.GABA,
            source,
            caution_message,
            priority="normal"
        )
    
    async def release_glutamate(self, source: str, opportunity_message: Dict):
        """Release glutamate (excitatory/opportunity)"""
        await self.release_neurotransmitter(
            NeurotransmitterType.GLUTAMATE,
            source,
            opportunity_message,
            priority="normal"
        )


async def integrate_neurotransmitter_system(orchestrator):
    """
    Integrate neurotransmitter system with orchestrator
    """
    
    neuro = NeurotransmitterSystem()
    
    # Register all major subsystems
    if hasattr(orchestrator, 'data_hub'):
        neuro.register_system('DataHub', orchestrator.data_hub)
    
    if hasattr(orchestrator, 'execution_orchestrator'):
        neuro.register_system('Execution', orchestrator.execution_orchestrator)
    
    if hasattr(orchestrator, 'evolution_engine'):
        neuro.register_system('Evolution', orchestrator.evolution_engine)
    
    if hasattr(orchestrator, 'ai_collective'):
        neuro.register_system('AICollective', orchestrator.ai_collective)
    
    # Create key synapses
    neuro.create_synapse('AICollective', 'DataHub')
    neuro.create_synapse('DataHub', 'Execution')
    neuro.create_synapse('Execution', 'Evolution')
    neuro.create_synapse('Evolution', 'AICollective')
    
    # Start neurotransmitter pump
    await neuro.neurotransmitter_pump()
    
    return neuro
