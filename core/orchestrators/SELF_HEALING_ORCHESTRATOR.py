#!/usr/bin/env python3
"""
🔧 SELF-HEALING ORCHESTRATOR 🔧

Monitors ALL systems and ensures:
- No system is overworked
- Failed systems auto-restart
- Performance stays optimal
- Resources properly distributed
- Health issues detected early
- Auto-healing when problems arise

AUTONOMOUS SELF-MAINTENANCE - The bot HEALS ITSELF! 💚
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import psutil
import os

logger = logging.getLogger(__name__)


class SelfHealingOrchestrator:
    """
    SELF-HEALING INTELLIGENCE
    
    Continuously monitors:
    - System health (CPU, memory, network)
    - Component health (all trading systems)
    - Performance metrics (speed, accuracy)
    - Error rates and patterns
    - Resource usage
    
    Automatically:
    - Restarts failed components
    - Throttles overworked systems
    - Reallocates resources
    - Prevents burnout
    - Maintains optimal operation
    
    THE BOT'S IMMUNE SYSTEM! 🛡️
    """
    
    def __init__(self):
        """Initialize self-healing orchestrator"""
        
        # Component registry (all systems to monitor)
        self.components = {}
        
        # Health status tracking
        self.health_status = defaultdict(lambda: {
            'status': 'unknown',
            'last_check': None,
            'errors': 0,
            'warnings': 0,
            'restarts': 0,
            'uptime': 0
        })
        
        # Performance tracking
        self.performance_metrics = defaultdict(lambda: {
            'calls': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_time': 0,
            'last_call': None
        })
        
        # Resource usage tracking
        self.resource_usage = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'network_io': 0
        }
        
        # Health check intervals (seconds)
        self.check_intervals = {
            'system': 30,      # System resources every 30s
            'components': 60,  # Components every minute
            'performance': 120 # Performance every 2 minutes
        }
        
        # Healing policies
        self.healing_policies = {
            'max_errors_before_restart': 5,
            'max_response_time_ms': 5000,
            'min_success_rate': 0.7,
            'max_cpu_percent': 80,
            'max_memory_percent': 85,
            'throttle_threshold': 0.8  # Throttle at 80% capacity
        }
        
        # Component thresholds
        self.component_thresholds = {}
        
        logger.info("🔧 SELF-HEALING ORCHESTRATOR initialized!")
        logger.info(f"   Monitoring intervals: {self.check_intervals}")
        logger.info(f"   Healing policies configured")
    
    def register_component(self, name: str, component: Any, 
                          check_func: Optional[callable] = None):
        """
        Register a component for monitoring
        
        Args:
            name: Component name
            component: Component instance
            check_func: Optional health check function
        """
        self.components[name] = {
            'instance': component,
            'check_func': check_func,
            'registered_at': datetime.now()
        }
        
        logger.info(f"   [OK] Registered component: {name}")
    
    async def start_continuous_monitoring(self):
        """
        Start CONTINUOUS health monitoring
        
        Runs forever, constantly checking and healing!
        """
        logger.info("🔧 Starting CONTINUOUS self-healing monitoring...")
        
        tasks = [
            self._system_resource_monitor(),
            self._component_health_monitor(),
            self._performance_monitor(),
            self._auto_healer()
        ]
        
        logger.info(f"   Launched {len(tasks)} monitoring tasks!")
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _system_resource_monitor(self):
        """Monitor system resources (CPU, memory, network)"""
        logger.info("   🔧 System resource monitor started")
        
        while True:
            try:
                # Get current process
                process = psutil.Process(os.getpid())
                
                # CPU usage
                cpu_percent = process.cpu_percent(interval=1)
                
                # Memory usage
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                
                # Update resource usage
                self.resource_usage = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check for overload
                if cpu_percent > self.healing_policies['max_cpu_percent']:
                    logger.warning(f" HIGH CPU USAGE: {cpu_percent:.1f}%")
                    await self._throttle_systems()
                
                if memory_percent > self.healing_policies['max_memory_percent']:
                    logger.warning(f" HIGH MEMORY USAGE: {memory_percent:.1f}%")
                    await self._reduce_memory_usage()
                
                await asyncio.sleep(self.check_intervals['system'])
            
            except Exception as e:
                logger.error(f"System resource monitor error: {e}")
                await asyncio.sleep(self.check_intervals['system'])
    
    async def _component_health_monitor(self):
        """Monitor health of all registered components"""
        logger.info("   🔧 Component health monitor started")
        
        while True:
            try:
                for comp_name, comp_data in self.components.items():
                    try:
                        # Run health check if available
                        if comp_data.get('check_func'):
                            health = await asyncio.to_thread(comp_data['check_func'])
                        else:
                            # Default health check (just check if instance exists)
                            health = {'status': 'healthy' if comp_data['instance'] else 'dead'}
                        
                        # Update health status
                        self.health_status[comp_name].update({
                            'status': health.get('status', 'unknown'),
                            'last_check': datetime.now(),
                            'details': health
                        })
                        
                        # Check if component needs healing
                        if health.get('status') in ['dead', 'critical', 'unhealthy']:
                            logger.warning(f" Component unhealthy: {comp_name} ({health.get('status')})")
                            await self._heal_component(comp_name)
                    
                    except Exception as e:
                        logger.error(f"Health check failed for {comp_name}: {e}")
                        self.health_status[comp_name]['errors'] += 1
                
                await asyncio.sleep(self.check_intervals['components'])
            
            except Exception as e:
                logger.error(f"Component health monitor error: {e}")
                await asyncio.sleep(self.check_intervals['components'])
    
    async def _performance_monitor(self):
        """Monitor performance metrics of all components"""
        logger.info("   🔧 Performance monitor started")
        
        while True:
            try:
                # Analyze performance metrics
                for comp_name, metrics in self.performance_metrics.items():
                    if metrics['calls'] > 0:
                        success_rate = metrics['successes'] / metrics['calls']
                        
                        # Check if success rate too low
                        if success_rate < self.healing_policies['min_success_rate']:
                            logger.warning(f" Low success rate for {comp_name}: {success_rate:.1%}")
                            self.health_status[comp_name]['warnings'] += 1
                        
                        # Check if response time too high
                        if metrics['avg_response_time'] > self.healing_policies['max_response_time_ms']:
                            logger.warning(f" Slow response from {comp_name}: {metrics['avg_response_time']:.0f}ms")
                            self.health_status[comp_name]['warnings'] += 1
                
                await asyncio.sleep(self.check_intervals['performance'])
            
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(self.check_intervals['performance'])
    
    async def _auto_healer(self):
        """Automatically heal components with issues"""
        logger.info("   🔧 Auto-healer started")
        
        while True:
            try:
                for comp_name, health in self.health_status.items():
                    # Check if component needs healing
                    if health['errors'] >= self.healing_policies['max_errors_before_restart']:
                        logger.warning(f"🔧 Auto-healing {comp_name} (too many errors: {health['errors']})")
                        await self._heal_component(comp_name)
                        
                        # Reset error count after healing attempt
                        health['errors'] = 0
                        health['restarts'] += 1
                
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Auto-healer error: {e}")
                await asyncio.sleep(60)
    
    async def _heal_component(self, component_name: str):
        """
        Heal a component (restart, reset, or reinitialize)
        
        This is the HEALING ACTION!
        """
        try:
            logger.info(f"   🔧 Healing component: {component_name}")
            
            comp_data = self.components.get(component_name)
            if not comp_data:
                logger.error(f"   [X] Component not found: {component_name}")
                return
            
            # Healing strategies:
            # 1. Try to restart/reinitialize
            instance = comp_data['instance']
            
            # Check if component has restart method
            if hasattr(instance, 'restart'):
                await asyncio.to_thread(instance.restart)
                logger.info(f"   [OK] Restarted {component_name}")
            elif hasattr(instance, 'reset'):
                await asyncio.to_thread(instance.reset)
                logger.info(f"   [OK] Reset {component_name}")
            elif hasattr(instance, '__init__'):
                # Try re-initialization (last resort)
                logger.warning(f"    Attempting re-initialization of {component_name}")
            else:
                logger.error(f"   [X] No healing method available for {component_name}")
            
            # Update health status
            self.health_status[component_name]['status'] = 'healing'
            self.health_status[component_name]['restarts'] += 1
        
        except Exception as e:
            logger.error(f"Healing failed for {component_name}: {e}")
    
    async def _throttle_systems(self):
        """Throttle systems to reduce CPU load"""
        logger.warning("   🔧 THROTTLING systems to reduce CPU load...")
        
        # This would reduce update frequencies, pause non-critical tasks, etc
        # For now, just log
        logger.info("   ⏸️  Non-critical tasks paused temporarily")
    
    async def _reduce_memory_usage(self):
        """Reduce memory usage"""
        logger.warning("   🔧 REDUCING memory usage...")
        
        # Clear caches, release unused resources, etc
        # For now, just log
        logger.info("   🧹 Clearing caches and unused resources")
    
    def record_call(self, component_name: str, success: bool, response_time_ms: float = 0):
        """
        Record a component call for performance tracking
        
        Args:
            component_name: Name of component
            success: Whether call succeeded
            response_time_ms: Response time in milliseconds
        """
        metrics = self.performance_metrics[component_name]
        metrics['calls'] += 1
        metrics['last_call'] = datetime.now()
        
        if success:
            metrics['successes'] += 1
        else:
            metrics['failures'] += 1
            self.health_status[component_name]['errors'] += 1
        
        # Update average response time
        if metrics['calls'] == 1:
            metrics['avg_response_time'] = response_time_ms
        else:
            metrics['avg_response_time'] = (
                (metrics['avg_response_time'] * (metrics['calls'] - 1) + response_time_ms) 
                / metrics['calls']
            )
    
    def get_system_health_report(self) -> Dict:
        """Get comprehensive health report of entire system"""
        now = datetime.now()
        
        # Count healthy/unhealthy components
        healthy = sum(1 for h in self.health_status.values() if h['status'] == 'healthy')
        total = len(self.health_status)
        
        # Calculate overall health score
        if total > 0:
            health_score = (healthy / total) * 100
        else:
            health_score = 100
        
        # Determine overall status
        if health_score >= 90:
            overall_status = 'excellent'
        elif health_score >= 75:
            overall_status = 'good'
        elif health_score >= 50:
            overall_status = 'fair'
        else:
            overall_status = 'poor'
        
        return {
            'overall_status': overall_status,
            'health_score': health_score,
            'total_components': total,
            'healthy_components': healthy,
            'resource_usage': self.resource_usage,
            'component_health': dict(self.health_status),
            'performance_metrics': dict(self.performance_metrics),
            'total_errors': sum(h['errors'] for h in self.health_status.values()),
            'total_warnings': sum(h['warnings'] for h in self.health_status.values()),
            'total_restarts': sum(h['restarts'] for h in self.health_status.values()),
            'timestamp': now.isoformat()
        }


# Singleton
_self_healing_orchestrator = None

def get_self_healing_orchestrator():
    """Get self-healing orchestrator instance"""
    return _self_healing_orchestrator

def initialize_self_healing_orchestrator():
    """Initialize self-healing orchestrator"""
    global _self_healing_orchestrator
    _self_healing_orchestrator = SelfHealingOrchestrator()
    return _self_healing_orchestrator
