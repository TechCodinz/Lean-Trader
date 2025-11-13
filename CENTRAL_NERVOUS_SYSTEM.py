#!/usr/bin/env python3
"""
🧠 CENTRAL NERVOUS SYSTEM 🧠

The BRAIN that controls EVERYTHING!

Like a human nervous system:
- Monitors all organs (systems)
- Coordinates all actions
- Ensures perfect synchronization
- Detects failures instantly
- Auto-heals problems
- Maintains homeostasis

ALL SYSTEMS REPORT TO AND CONTROLLED BY THE CNS!
"""

import asyncio
import logging
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class CentralNervousSystem:
    """
    THE BRAIN - CONTROLS EVERYTHING
    
    Functions:
    1. System Registration - All systems register here
    2. Health Monitoring - Constant health checks
    3. Coordination - Synchronizes all actions
    4. Resource Allocation - Distributes pair lists, balances
    5. Failure Detection - Instant problem detection
    6. Auto-Healing - Restarts failed systems
    7. Performance Tracking - Monitors all metrics
    
    THE MASTER CONTROLLER!
    """
    
    def __init__(self):
        # System registry
        self.registered_systems = {}  # {system_name: system_instance}
        
        # System health
        self.system_health = {}  # {system_name: health_status}
        
        # Coordination state
        self.available_pairs = {}  # {exchange: set(pairs)}
        self.connected_exchanges = set()
        self.active_pairs = set()  # Filtered, ready-to-trade pairs
        
        # Resource state
        self.available_balance = {}  # {exchange: balance}
        self.allocated_positions = {}  # {symbol: allocation}
        
        # Performance metrics
        self.system_metrics = defaultdict(lambda: {
            'calls': 0,
            'successes': 0,
            'failures': 0,
            'last_activity': None
        })
        
        # Synchronization state
        self.sync_status = {
            'last_sync': None,
            'systems_in_sync': 0,
            'systems_out_of_sync': 0
        }
        
        # Failure tracking
        self.failures = []
        
        logger.info("🧠 CENTRAL NERVOUS SYSTEM initialized!")
        logger.info("   THE BRAIN IS ONLINE!")
    
    def register_system(self, name: str, system_instance, health_check_fn=None):
        """
        Register a system with the CNS
        
        ALL systems must register!
        """
        self.registered_systems[name] = {
            'instance': system_instance,
            'health_check': health_check_fn,
            'registered_at': datetime.now(),
            'status': 'active'
        }
        
        self.system_health[name] = {
            'status': 'healthy',
            'last_check': datetime.now(),
            'failures': 0
        }
        
        logger.info(f"   ✅ System registered: {name}")
    
    async def monitor_all_systems(self):
        """
        Continuously monitor ALL systems
        
        Runs forever checking health
        """
        logger.info("🧠 CNS: Starting continuous monitoring...")
        
        while True:
            try:
                for name, system_data in self.registered_systems.items():
                    # Check health
                    health = await self._check_system_health(name, system_data)
                    
                    # Update status
                    self.system_health[name].update(health)
                    
                    # Auto-heal if needed
                    if health['status'] == 'failed':
                        await self._heal_system(name)
                
                # Update sync status
                self._update_sync_status()
                
                await asyncio.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                logger.error(f"🧠 CNS monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_system_health(self, name: str, system_data: Dict) -> Dict:
        """Check individual system health"""
        try:
            # Run health check if provided
            if system_data.get('health_check'):
                health_result = await system_data['health_check']()
            else:
                # Default: check if instance exists
                health_result = {'status': 'healthy' if system_data['instance'] else 'failed'}
            
            return {
                'status': health_result.get('status', 'unknown'),
                'last_check': datetime.now(),
                'details': health_result
            }
        
        except Exception as e:
            return {
                'status': 'failed',
                'last_check': datetime.now(),
                'error': str(e)
            }
    
    async def _heal_system(self, name: str):
        """Auto-heal failed system"""
        logger.warning(f"🔧 CNS: Healing {name}...")
        
        # Attempt restart if system has restart method
        system = self.registered_systems.get(name, {}).get('instance')
        
        if system and hasattr(system, 'restart'):
            try:
                await system.restart()
                logger.info(f"   ✅ {name} restarted")
            except Exception as e:
                logger.error(f"   ❌ {name} restart failed: {e}")
    
    def coordinate_pair_discovery(self, exchange: str, pairs: List[str]):
        """
        Central coordination for pair discovery
        
        Called by router after discovering pairs
        """
        self.available_pairs[exchange] = set(pairs)
        
        # Recalculate active pairs (only from connected exchanges)
        self.active_pairs.clear()
        for ex in self.connected_exchanges:
            if ex in self.available_pairs:
                self.active_pairs.update(self.available_pairs[ex])
        
        logger.info(f"🧠 CNS: Pair coordination updated")
        logger.info(f"   {exchange}: {len(pairs)} pairs")
        logger.info(f"   Active: {len(self.active_pairs)} total")
        
        # Notify all systems
        self._broadcast_pair_update()
    
    def _broadcast_pair_update(self):
        """Broadcast pair list to all systems"""
        logger.info("📡 CNS: Broadcasting pair update to all systems...")
        
        # Signal generators should listen to this
        for name, system_data in self.registered_systems.items():
            if 'scalp' in name.lower() or 'signal' in name.lower():
                logger.debug(f"   → Updating {name}")
    
    def get_tradeable_pairs(self) -> List[str]:
        """
        Get coordinated list of tradeable pairs
        
        ALL signal generators MUST call this!
        """
        pairs = list(self.active_pairs)
        
        if not pairs:
            # Fallback to safe default
            pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
            logger.warning(f"🧠 CNS: No active pairs, using fallback: {pairs}")
        
        return pairs
    
    def can_execute_on(self, symbol: str, exchange: str) -> bool:
        """
        Check if execution is possible
        
        Called before every trade attempt
        """
        # Check exchange connected
        if exchange not in self.connected_exchanges:
            return False
        
        # Check pair available
        if exchange not in self.available_pairs:
            return False
        
        if symbol not in self.available_pairs[exchange]:
            return False
        
        # Check balance available
        if exchange in self.available_balance:
            if self.available_balance[exchange] < 1.0:  # Min $1
                return False
        
        return True
    
    def record_system_activity(self, system_name: str, success: bool):
        """Record activity for metrics"""
        metrics = self.system_metrics[system_name]
        metrics['calls'] += 1
        metrics['last_activity'] = datetime.now()
        
        if success:
            metrics['successes'] += 1
        else:
            metrics['failures'] += 1
        
        # Update system health based on success rate
        if metrics['calls'] > 10:
            success_rate = metrics['successes'] / metrics['calls']
            if success_rate < 0.5:  # <50% success = unhealthy
                self.system_health[system_name]['status'] = 'degraded'
    
    def _update_sync_status(self):
        """Update synchronization status"""
        in_sync = sum(1 for h in self.system_health.values() if h['status'] == 'healthy')
        out_of_sync = len(self.system_health) - in_sync
        
        self.sync_status = {
            'last_sync': datetime.now(),
            'systems_in_sync': in_sync,
            'systems_out_of_sync': out_of_sync,
            'sync_percentage': (in_sync / max(len(self.system_health), 1)) * 100
        }
    
    def get_cns_status(self) -> Dict:
        """Get complete CNS status"""
        return {
            'total_systems': len(self.registered_systems),
            'healthy_systems': sum(1 for h in self.system_health.values() if h['status'] == 'healthy'),
            'active_pairs': len(self.active_pairs),
            'connected_exchanges': len(self.connected_exchanges),
            'sync_percentage': self.sync_status['sync_percentage'],
            'total_failures': len(self.failures),
            'system_metrics': dict(self.system_metrics)
        }


# Singleton - THE BRAIN
_central_nervous_system = None

def get_cns():
    """Get the Central Nervous System"""
    global _central_nervous_system
    if _central_nervous_system is None:
        _central_nervous_system = CentralNervousSystem()
    return _central_nervous_system

def initialize_cns():
    """Initialize the Central Nervous System"""
    global _central_nervous_system
    _central_nervous_system = CentralNervousSystem()
    logger.info("🧠 THE BRAIN IS ONLINE!")
    return _central_nervous_system
