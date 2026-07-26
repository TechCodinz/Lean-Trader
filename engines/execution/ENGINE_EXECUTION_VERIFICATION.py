"""
ENGINE_EXECUTION_VERIFICATION.py
Runtime guards to ensure ALL 367 engines execute
SAFETY-CRITICAL: Halts trading if engines don't execute
"""

import logging
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Execution status for an engine"""
    NOT_EXECUTED = "not_executed"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class EngineExecutionRecord:
    """Record of engine execution in a cycle"""
    engine_name: str
    status: ExecutionStatus
    execution_time: Optional[datetime] = None
    execution_duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    output_consumed: bool = False

@dataclass
class EngineHealthMonitor:
    """
    Monitors health of ALL 367 engines
    Ensures every engine executes when expected
    """
    total_engines: int = 367
    execution_records: Dict[str, EngineExecutionRecord] = field(default_factory=dict)
    expected_executions: Set[str] = field(default_factory=set)
    cycle_count: int = 0
    failures: List[str] = field(default_factory=list)
    
    def reset_cycle(self):
        """Reset for new trading cycle"""
        self.execution_records.clear()
        self.cycle_count += 1
    
    def set_expected(self, engine_names: List[str]):
        """Set which engines are expected to execute this cycle"""
        self.expected_executions = set(engine_names)
    
    def mark_executing(self, engine_name: str):
        """Mark engine as currently executing"""
        self.execution_records[engine_name] = EngineExecutionRecord(
            engine_name=engine_name,
            status=ExecutionStatus.EXECUTING,
            execution_time=datetime.now()
        )
    
    def mark_executed(self, engine_name: str, duration_ms: float, output_consumed: bool = False):
        """Mark engine as successfully executed"""
        if engine_name in self.execution_records:
            record = self.execution_records[engine_name]
            record.status = ExecutionStatus.EXECUTED
            record.execution_duration_ms = duration_ms
            record.output_consumed = output_consumed
        else:
            self.execution_records[engine_name] = EngineExecutionRecord(
                engine_name=engine_name,
                status=ExecutionStatus.EXECUTED,
                execution_time=datetime.now(),
                execution_duration_ms=duration_ms,
                output_consumed=output_consumed
            )
    
    def mark_failed(self, engine_name: str, error: str):
        """Mark engine as failed"""
        self.execution_records[engine_name] = EngineExecutionRecord(
            engine_name=engine_name,
            status=ExecutionStatus.FAILED,
            execution_time=datetime.now(),
            error_message=error
        )
        self.failures.append(f"{engine_name}: {error}")
    
    def verify_all_executed(self) -> bool:
        """
        Verify ALL expected engines executed
        Returns False if ANY engine didn't execute
        CRITICAL: Trading should halt if this returns False
        """
        missing = self.expected_executions - set(self.execution_records.keys())
        
        if missing:
            logger.error(f"[X] CRITICAL: {len(missing)} engines did NOT execute in cycle {self.cycle_count}")
            for engine in sorted(missing):
                logger.error(f"  - {engine} (SKIPPED)")
            return False
        
        # Check for failures
        failed = [name for name, rec in self.execution_records.items() 
                 if rec.status == ExecutionStatus.FAILED]
        
        if failed:
            logger.error(f"[X] {len(failed)} engines FAILED in cycle {self.cycle_count}")
            for engine in failed:
                error = self.execution_records[engine].error_message
                logger.error(f"  - {engine}: {error}")
            return False
        
        # All good
        executed = len(self.execution_records)
        logger.info(f"[OK] ALL {executed} expected engines executed in cycle {self.cycle_count}")
        return True
    
    def get_execution_report(self) -> Dict:
        """Get detailed execution report"""
        executed = [n for n, r in self.execution_records.items() 
                   if r.status == ExecutionStatus.EXECUTED]
        failed = [n for n, r in self.execution_records.items() 
                 if r.status == ExecutionStatus.FAILED]
        missing = list(self.expected_executions - set(self.execution_records.keys()))
        
        return {
            'cycle': self.cycle_count,
            'total_expected': len(self.expected_executions),
            'executed': len(executed),
            'failed': len(failed),
            'missing': len(missing),
            'execution_rate': len(executed) / len(self.expected_executions) if self.expected_executions else 0,
            'executed_engines': executed,
            'failed_engines': failed,
            'missing_engines': missing
        }

class ExecutionVerifier:
    """
    SAFETY-CRITICAL: Verifies execution of all engines
    Enforces that NO engine is silently skipped
    """
    
    def __init__(self, registry):
        self.registry = registry
        self.health_monitor = EngineHealthMonitor()
        self.safe_mode = False
        
        logger.info("🛡️ Execution Verifier initialized")
    
    def verify_startup(self) -> bool:
        """
        Verify ALL engines registered and initialized at startup
        MUST be called before trading starts
        """
        logger.info("🔍 Verifying startup...")
        
        # Check registry
        if len(self.registry.engines) != 367:
            logger.error(f"[X] STARTUP FAILURE: Expected 367 engines, got {len(self.registry.engines)}")
            return False
        
        # Check initialization
        if not self.registry.verify_all_active():
            logger.error("[X] STARTUP FAILURE: Not all engines active")
            return False
        
        logger.info(f"[OK] STARTUP VERIFIED: All 367 engines registered and active")
        return True
    
    def begin_cycle(self, activation_point: str):
        """Begin new trading cycle"""
        self.health_monitor.reset_cycle()
        
        # Get engines for this activation point
        expected = self.registry.get_engines_by_activation_point(activation_point)
        expected_names = [e.__class__.__name__ for e in expected if e is not None]
        
        self.health_monitor.set_expected(expected_names)
        logger.debug(f"Cycle {self.health_monitor.cycle_count}: Expecting {len(expected_names)} engines")
    
    def verify_cycle(self) -> bool:
        """
        Verify all engines executed in this cycle
        CRITICAL: Returns False if ANY engine skipped
        """
        success = self.health_monitor.verify_all_executed()
        
        if not success:
            logger.error("[X] CYCLE VERIFICATION FAILED")
            self.safe_mode = True
            logger.error("🛑 ENTERING SAFE MODE - Trading halted")
        
        return success
    
    def get_report(self) -> Dict:
        """Get execution report"""
        return self.health_monitor.get_execution_report()
    
    def is_safe_to_trade(self) -> bool:
        """Check if system is safe to trade"""
        if self.safe_mode:
            logger.warning(" SAFE MODE ACTIVE - Trading blocked")
            return False
        return True

# Global verifier
_verifier = None

def get_verifier(registry=None):
    """Get global execution verifier"""
    global _verifier
    if _verifier is None and registry is not None:
        _verifier = ExecutionVerifier(registry)
    return _verifier

def verify_startup(registry) -> bool:
    """
    MUST be called at startup before trading
    Verifies ALL 367 engines are ready
    """
    verifier = get_verifier(registry)
    return verifier.verify_startup()

if __name__ == "__main__":
    # Test verification system
    logging.basicConfig(level=logging.INFO)
    
    print("\nExecution Verification System")
    print("=" * 60)
    print(f"Total engines to monitor: 367")
    print(f"Ensures ALL engines execute every cycle")
    print(f"Halts trading if ANY engine skipped")
    print("=" * 60)
