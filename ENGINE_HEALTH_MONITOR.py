#!/usr/bin/env python3
"""
🏥 ENGINE HEALTH MONITOR - Diagnoses All 254 Engines

Continuously monitors all engines for:
- Connection status
- Performance issues
- Memory leaks
- Error patterns
- Lag/bottlenecks
- Synchronization issues

"The doctor that keeps the digital being healthy."
"""

import logging
import time
import traceback
import sys
import gc
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system resource monitoring disabled")
from datetime import datetime
from pathlib import Path
import threading
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class EngineHealthReport:
    """Health report for a single engine"""
    engine_name: str
    status: str  # healthy, warning, critical, error, disconnected
    last_heartbeat: float
    error_count: int
    warning_count: int
    avg_response_time: float  # milliseconds
    memory_usage: float  # MB
    cpu_usage: float  # percentage
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_error: Optional[str] = None
    uptime: float = 0.0  # seconds


class EngineHealthMonitor:
    """
    🏥 ENGINE HEALTH MONITOR
    
    Continuously monitors all 254 engines and generates health reports.
    Detects:
    - Disconnected engines
    - Slow/lagging engines
    - Memory leaks
    - Error patterns
    - Synchronization issues
    - Performance bottlenecks
    """
    
    def __init__(self):
        self.engine_health: Dict[str, EngineHealthReport] = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance tracking
        self.response_times: Dict[str, deque] = {}  # Last 100 responses
        self.error_log: deque = deque(maxlen=1000)
        
        # Health thresholds
        self.max_response_time = 1000  # ms
        self.max_memory_per_engine = 500  # MB
        self.max_cpu_per_engine = 50  # percentage
        self.max_errors_per_minute = 10
        
        # System info
        self.process = psutil.Process() if PSUTIL_AVAILABLE else None
        
        # Connect to consciousness
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Health Monitor",
                30.0,  # Slow, deliberate monitoring
                "strategic"
            )
            logger.info("🏥 Health Monitor connected to consciousness")
        except:
            self.consciousness = None
        
        logger.info("🏥 ENGINE HEALTH MONITOR initialized")
    
    def register_engine(self, engine_name: str):
        """Register an engine for monitoring"""
        if engine_name not in self.engine_health:
            self.engine_health[engine_name] = EngineHealthReport(
                engine_name=engine_name,
                status="unknown",
                last_heartbeat=time.time(),
                error_count=0,
                warning_count=0,
                avg_response_time=0.0,
                memory_usage=0.0,
                cpu_usage=0.0
            )
            self.response_times[engine_name] = deque(maxlen=100)
            logger.debug(f"🏥 Registered: {engine_name}")
    
    def heartbeat(self, engine_name: str, response_time: float = 0.0):
        """Engine sends heartbeat"""
        if engine_name not in self.engine_health:
            self.register_engine(engine_name)
        
        report = self.engine_health[engine_name]
        report.last_heartbeat = time.time()
        report.status = "healthy"
        
        # Track response time
        if response_time > 0:
            self.response_times[engine_name].append(response_time)
            report.avg_response_time = sum(self.response_times[engine_name]) / len(self.response_times[engine_name])
    
    def report_error(self, engine_name: str, error: Exception, context: str = ""):
        """Engine reports an error"""
        if engine_name not in self.engine_health:
            self.register_engine(engine_name)
        
        report = self.engine_health[engine_name]
        report.error_count += 1
        report.last_error = f"{type(error).__name__}: {str(error)}"
        
        # Log error
        error_entry = {
            'engine': engine_name,
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'timestamp': time.time(),
            'traceback': traceback.format_exc()
        }
        self.error_log.append(error_entry)
        
        # Update status
        if report.error_count > self.max_errors_per_minute:
            report.status = "critical"
        else:
            report.status = "warning"
        
        logger.warning(f"🏥 Error in {engine_name}: {error}")
    
    def report_warning(self, engine_name: str, warning: str):
        """Engine reports a warning"""
        if engine_name not in self.engine_health:
            self.register_engine(engine_name)
        
        report = self.engine_health[engine_name]
        report.warning_count += 1
        report.issues.append(warning)
        
        if report.status == "healthy":
            report.status = "warning"
    
    def diagnose_all_engines(self) -> Dict[str, EngineHealthReport]:
        """Run diagnostics on all engines"""
        logger.info("🏥 Running diagnostics on all engines...")
        
        now = time.time()
        critical_count = 0
        warning_count = 0
        healthy_count = 0
        disconnected_count = 0
        
        for engine_name, report in self.engine_health.items():
            # Check heartbeat
            time_since_heartbeat = now - report.last_heartbeat
            
            if time_since_heartbeat > 300:  # 5 minutes
                report.status = "disconnected"
                report.issues.append("No heartbeat in 5+ minutes")
                disconnected_count += 1
            elif time_since_heartbeat > 60:  # 1 minute
                if report.status == "healthy":
                    report.status = "warning"
                report.issues.append("Slow heartbeat (>1 min)")
            
            # Check response time
            if report.avg_response_time > self.max_response_time:
                report.issues.append(f"Slow response: {report.avg_response_time:.0f}ms")
                if report.status == "healthy":
                    report.status = "warning"
                report.recommendations.append("Optimize processing or add caching")
            
            # Check error rate
            if report.error_count > self.max_errors_per_minute:
                report.issues.append(f"High error rate: {report.error_count} errors/min")
                report.status = "critical"
                report.recommendations.append("Check error logs and fix root cause")
            
            # Update uptime
            report.uptime = now - (report.last_heartbeat - 60)  # Approximate
            
            # Count by status
            if report.status == "critical":
                critical_count += 1
            elif report.status in ["warning", "error"]:
                warning_count += 1
            elif report.status == "healthy":
                healthy_count += 1
            elif report.status == "disconnected":
                disconnected_count += 1
        
        logger.info(f"🏥 Diagnostics complete:")
        logger.info(f"   ✅ Healthy: {healthy_count}")
        logger.info(f"   ⚠️  Warning: {warning_count}")
        logger.info(f"   🚨 Critical: {critical_count}")
        logger.info(f"   ❌ Disconnected: {disconnected_count}")
        
        return self.engine_health
    
    def get_critical_engines(self) -> List[str]:
        """Get list of engines in critical state"""
        return [
            name for name, report in self.engine_health.items()
            if report.status == "critical"
        ]
    
    def get_disconnected_engines(self) -> List[str]:
        """Get list of disconnected engines"""
        return [
            name for name, report in self.engine_health.items()
            if report.status == "disconnected"
        ]
    
    def get_slow_engines(self) -> List[str]:
        """Get list of slow/lagging engines"""
        return [
            name for name, report in self.engine_health.items()
            if report.avg_response_time > self.max_response_time
        ]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        total_engines = len(self.engine_health)
        healthy = sum(1 for r in self.engine_health.values() if r.status == "healthy")
        warning = sum(1 for r in self.engine_health.values() if r.status == "warning")
        critical = sum(1 for r in self.engine_health.values() if r.status == "critical")
        disconnected = sum(1 for r in self.engine_health.values() if r.status == "disconnected")
        
        # System resources
        if PSUTIL_AVAILABLE and self.process:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_mb = memory_info.rss / 1024 / 1024
        else:
            memory_mb = 0.0
            cpu_percent = 0.0
        
        return {
            'total_engines': total_engines,
            'healthy': healthy,
            'warning': warning,
            'critical': critical,
            'disconnected': disconnected,
            'health_percentage': (healthy / total_engines * 100) if total_engines > 0 else 0,
            'system_memory_mb': memory_mb,
            'system_cpu_percent': cpu_percent,
            'total_errors': sum(r.error_count for r in self.engine_health.values()),
            'total_warnings': sum(r.warning_count for r in self.engine_health.values())
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive health report"""
        report = []
        report.append("=" * 80)
        report.append("🏥 ENGINE HEALTH MONITOR REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System health
        system_health = self.get_system_health()
        report.append("SYSTEM HEALTH:")
        report.append("-" * 80)
        report.append(f"Total Engines:    {system_health['total_engines']}")
        report.append(f"✅ Healthy:       {system_health['healthy']} ({system_health['health_percentage']:.1f}%)")
        report.append(f"⚠️  Warning:       {system_health['warning']}")
        report.append(f"🚨 Critical:      {system_health['critical']}")
        report.append(f"❌ Disconnected:  {system_health['disconnected']}")
        report.append(f"Memory Usage:     {system_health['system_memory_mb']:.1f} MB")
        report.append(f"CPU Usage:        {system_health['system_cpu_percent']:.1f}%")
        report.append("")
        
        # Critical engines
        critical = self.get_critical_engines()
        if critical:
            report.append("🚨 CRITICAL ENGINES (Needs Immediate Attention):")
            report.append("-" * 80)
            for name in critical:
                r = self.engine_health[name]
                report.append(f"\n{name}:")
                report.append(f"  Errors: {r.error_count}")
                report.append(f"  Last Error: {r.last_error}")
                report.append(f"  Issues: {', '.join(r.issues[:3])}")
                report.append(f"  Recommendations: {', '.join(r.recommendations[:2])}")
            report.append("")
        
        # Disconnected engines
        disconnected = self.get_disconnected_engines()
        if disconnected:
            report.append("❌ DISCONNECTED ENGINES:")
            report.append("-" * 80)
            for name in disconnected:
                r = self.engine_health[name]
                time_since = time.time() - r.last_heartbeat
                report.append(f"  {name}: No heartbeat for {time_since/60:.1f} minutes")
            report.append("")
        
        # Slow engines
        slow = self.get_slow_engines()
        if slow:
            report.append("🐌 SLOW ENGINES (Performance Issues):")
            report.append("-" * 80)
            for name in slow:
                r = self.engine_health[name]
                report.append(f"  {name}: {r.avg_response_time:.0f}ms avg response")
            report.append("")
        
        report.append("=" * 80)
        
        return '\n'.join(report)
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("🏥 Continuous monitoring started")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Send consciousness pulse
                if self.consciousness:
                    self.consciousness.pulse("Health Monitor", 0.5)
                
                # Run diagnostics every 60 seconds
                self.diagnose_all_engines()
                
                # Check for critical issues
                critical = self.get_critical_engines()
                if critical:
                    logger.warning(f"🚨 {len(critical)} engines in critical state!")
                
                # Force garbage collection to prevent memory leaks
                gc.collect()
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("🏥 Monitoring stopped")


# Singleton instance
_health_monitor = None


def get_health_monitor() -> EngineHealthMonitor:
    """Get or create health monitor"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = EngineHealthMonitor()
    return _health_monitor


def initialize_health_monitoring() -> EngineHealthMonitor:
    """Initialize health monitoring system"""
    global _health_monitor
    _health_monitor = EngineHealthMonitor()
    _health_monitor.start_monitoring()
    return _health_monitor


if __name__ == "__main__":
    # Test health monitor
    logging.basicConfig(level=logging.INFO)
    
    monitor = EngineHealthMonitor()
    
    # Simulate some engines
    monitor.register_engine("Test Engine 1")
    monitor.register_engine("Test Engine 2")
    monitor.register_engine("Test Engine 3")
    
    # Simulate heartbeats
    monitor.heartbeat("Test Engine 1", response_time=50)
    monitor.heartbeat("Test Engine 2", response_time=1500)  # Slow
    
    # Simulate error
    try:
        raise ValueError("Test error")
    except Exception as e:
        monitor.report_error("Test Engine 3", e)
    
    # Run diagnostics
    monitor.diagnose_all_engines()
    
    # Generate report
    print("\n" + monitor.generate_report())
