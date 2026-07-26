#!/usr/bin/env python3
"""
ENGINE_UNISON_VERIFIER.py
Verify all engines operate in unison without degradation
PURE INSTRUMENTATION - NO BEHAVIOR CHANGES
"""

import json
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class EngineUnisonVerifier:
    """Verify engines operate in unison across all states"""
    
    def __init__(self, reports_dir: str = "/root/bot/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Files
        self.state_metrics_file = self.reports_dir / 'state_unison_metrics.jsonl'
        self.dependency_failures_file = self.reports_dir / 'engine_dependency_failures.jsonl'
        self.consumption_integrity_file = self.reports_dir / 'output_consumption_integrity.jsonl'
        self.stability_watch_file = self.reports_dir / 'endless_stability_watch.jsonl'
        self.unison_score_file = self.reports_dir / 'unison_score.jsonl'
        
        # State tracking
        self.cycle_count = 0
        self.state_metrics = []
        
        # Dependency tracking
        self.missing_dependencies = defaultdict(list)
        
        # Consumption tracking
        self.consumption_evidence = defaultdict(list)
        self.fake_consumption_count = 0
        
        # Stability tracking
        self.latency_history = deque(maxlen=1000)
        self.memory_history = deque(maxlen=1000)
        self.backlog_history = deque(maxlen=1000)
        self.safe_mode_history = deque(maxlen=1000)
        
        # Unison scores
        self.unison_scores = []
        
        logger.info("EngineUnisonVerifier initialized")
    
    def record_state_execution(self, state_name: str, engines_scheduled: int,
                               engines_executed: int, engines_failed: int,
                               engines_inert: int, outputs_produced: int,
                               outputs_consumed: int, duration_ms: float):
        """Record state-level unison metrics"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.cycle_count,
            'state': state_name,
            'engines_scheduled': engines_scheduled,
            'engines_executed': engines_executed,
            'engines_failed': engines_failed,
            'engines_inert': engines_inert,
            'outputs_produced': outputs_produced,
            'outputs_consumed': outputs_consumed,
            'state_duration_ms': round(duration_ms, 2)
        }
        
        # Write to file
        with open(self.state_metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        self.state_metrics.append(metrics)
    
    def verify_dependencies(self, engine_name: str, state: str,
                           required_inputs: List[str], context: Dict) -> bool:
        """Verify engine dependencies are satisfied"""
        
        missing = []
        
        for required_key in required_inputs:
            if required_key not in context:
                missing.append(required_key)
        
        if missing:
            failure = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'engine': engine_name,
                'state': state,
                'missing_keys': missing,
                'error_type': 'DEP_MISSING'
            }
            
            # Write to file
            with open(self.dependency_failures_file, 'a') as f:
                f.write(json.dumps(failure) + '\n')
            
            # Track for summary
            for key in missing:
                self.missing_dependencies[key].append({
                    'engine': engine_name,
                    'state': state,
                    'cycle': self.cycle_count
                })
            
            return False
        
        return True
    
    def record_consumption_evidence(self, output_key: str, producer_engine: str,
                                   consumer_engine: str, consumer_state: str,
                                   purpose: str):
        """Record consumption evidence"""
        
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.cycle_count,
            'output_key': output_key,
            'producer': producer_engine,
            'consumer': consumer_engine,
            'consumer_state': consumer_state,
            'purpose': purpose  # 'signal_scoring', 'risk_veto', 'sizing', 'execution', 'exit_decision'
        }
        
        # Write to file
        with open(self.consumption_integrity_file, 'a') as f:
            f.write(json.dumps(evidence) + '\n')
        
        self.consumption_evidence[output_key].append(evidence)
    
    def verify_consumption_integrity(self, output_key: str, marked_consumed: bool) -> bool:
        """Verify consumption has evidence"""
        
        if marked_consumed:
            # Check if we have evidence
            if output_key not in self.consumption_evidence or not self.consumption_evidence[output_key]:
                # FAKE CONSUMPTION
                fake = {
                    'timestamp': datetime.now().isoformat(),
                    'cycle': self.cycle_count,
                    'output_key': output_key,
                    'error_type': 'CONSUMPTION_FAKE'
                }
                
                with open(self.consumption_integrity_file, 'a') as f:
                    f.write(json.dumps(fake) + '\n')
                
                self.fake_consumption_count += 1
                return False
        
        return True
    
    def record_stability_metrics(self, cycle_latency_ms: float, output_bus_backlog: int,
                                safe_mode_active: bool):
        """Record stability metrics for trend analysis"""
        
        # Get memory usage
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
        except:
            memory_mb = 0
        
        # Record
        self.latency_history.append(cycle_latency_ms)
        self.memory_history.append(memory_mb)
        self.backlog_history.append(output_bus_backlog)
        self.safe_mode_history.append(1 if safe_mode_active else 0)
        
        # Detect degradation
        if len(self.latency_history) >= 100:
            # Compare last 100 to previous 100
            recent_latency = sum(list(self.latency_history)[-100:]) / 100
            previous_latency = sum(list(self.latency_history)[-200:-100]) / 100 if len(self.latency_history) >= 200 else recent_latency
            
            # Check trends
            degradation = []
            
            if recent_latency > previous_latency * 1.2:  # 20% increase
                degradation.append('LATENCY_INCREASE')
            
            recent_memory = sum(list(self.memory_history)[-100:]) / 100
            previous_memory = sum(list(self.memory_history)[-200:-100]) / 100 if len(self.memory_history) >= 200 else recent_memory
            
            if recent_memory > previous_memory * 1.1:  # 10% increase
                degradation.append('MEMORY_GROWTH')
            
            recent_backlog = sum(list(self.backlog_history)[-100:]) / 100
            if recent_backlog > 1000:
                degradation.append('BACKLOG_GROWTH')
            
            if degradation:
                warning = {
                    'timestamp': datetime.now().isoformat(),
                    'cycle': self.cycle_count,
                    'error_type': 'STABILITY_DEGRADATION',
                    'degradations': degradation,
                    'metrics': {
                        'latency_ms': round(recent_latency, 2),
                        'memory_mb': round(recent_memory, 2),
                        'backlog_size': round(recent_backlog, 2)
                    }
                }
                
                with open(self.stability_watch_file, 'a') as f:
                    f.write(json.dumps(warning) + '\n')
    
    def compute_unison_score(self) -> float:
        """Compute unison score from recent metrics"""
        
        if len(self.state_metrics) < 14:  # Need at least one full cycle
            return 0.0
        
        # Get last 14 states (one full cycle)
        recent = self.state_metrics[-14:]
        
        # State coverage completeness (all 14 states executed)
        states_executed = len(set(m['state'] for m in recent))
        coverage_score = states_executed / 14
        
        # Dependency satisfaction rate
        total_scheduled = sum(m['engines_scheduled'] for m in recent)
        total_executed = sum(m['engines_executed'] for m in recent)
        dependency_score = total_executed / total_scheduled if total_scheduled > 0 else 0
        
        # Valid output rate
        total_outputs = sum(m['outputs_produced'] for m in recent)
        output_score = min(total_outputs / 100, 1.0) if total_outputs > 0 else 0  # Expect ~100 outputs per cycle
        
        # Consumption rate
        total_consumed = sum(m['outputs_consumed'] for m in recent)
        consumption_score = total_consumed / total_outputs if total_outputs > 0 else 0
        
        # Stable latency rate
        if len(self.latency_history) >= 14:
            recent_latency = list(self.latency_history)[-14:]
            avg_latency = sum(recent_latency) / len(recent_latency)
            latency_score = max(1.0 - (avg_latency / 10000), 0)  # Penalty if >10s per cycle
        else:
            latency_score = 1.0
        
        # Safe mode penalty
        recent_safe_mode = list(self.safe_mode_history)[-14:] if len(self.safe_mode_history) >= 14 else []
        safe_mode_rate = sum(recent_safe_mode) / len(recent_safe_mode) if recent_safe_mode else 0
        safe_mode_score = 1.0 - safe_mode_rate
        
        # Weighted sum
        unison_score = (
            coverage_score * 0.25 +
            dependency_score * 0.20 +
            output_score * 0.15 +
            consumption_score * 0.20 +
            latency_score * 0.10 +
            safe_mode_score * 0.10
        )
        
        # Record
        score_record = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.cycle_count,
            'unison_score': round(unison_score, 4),
            'components': {
                'coverage': round(coverage_score, 3),
                'dependency': round(dependency_score, 3),
                'output': round(output_score, 3),
                'consumption': round(consumption_score, 3),
                'latency': round(latency_score, 3),
                'safe_mode': round(safe_mode_score, 3)
            }
        }
        
        with open(self.unison_score_file, 'a') as f:
            f.write(json.dumps(score_record) + '\n')
        
        self.unison_scores.append(unison_score)
        
        return unison_score
    
    def next_cycle(self):
        """Move to next cycle"""
        self.cycle_count += 1
        
        # Compute unison score every 100 cycles
        if self.cycle_count % 100 == 0:
            self.compute_unison_score()
    
    def generate_unison_proof_report(self):
        """Generate final unison proof report"""
        
        logger.info("Generating ENGINE_UNISON_PROOF_REPORT...")
        
        # Compute statistics
        if not self.unison_scores:
            min_score = 0
            avg_score = 0
            max_score = 0
        else:
            min_score = min(self.unison_scores)
            avg_score = sum(self.unison_scores) / len(self.unison_scores)
            max_score = max(self.unison_scores)
        
        # Top missing dependencies
        top_missing = sorted(
            [(k, len(v)) for k, v in self.missing_dependencies.items()],
            key=lambda x: -x[1]
        )[:20]
        
        # Check conditions for verdict
        no_critical_deps = len(self.missing_dependencies) == 0
        no_fake_consumption = self.fake_consumption_count == 0
        score_above_threshold = avg_score >= 0.92 if self.unison_scores else False
        enough_cycles = self.cycle_count >= 1000
        
        # Generate markdown report
        report = f"""# ENGINE UNISON PROOF REPORT

Generated: {datetime.now().isoformat()}
Total Cycles Analyzed: {self.cycle_count}

## Unison Score Summary

| Metric | Value |
|--------|-------|
| Minimum | {min_score:.4f} |
| Average | {avg_score:.4f} |
| Maximum | {max_score:.4f} |
| Threshold | 0.92 |
| Status | {'[OK] PASS' if score_above_threshold else '[X] BELOW THRESHOLD'} |

## Per-State Metrics Summary

"""
        
        # Group by state
        if self.state_metrics:
            state_groups = defaultdict(list)
            for metric in self.state_metrics[-1400:]:  # Last 100 cycles * 14 states
                state_groups[metric['state']].append(metric)
            
            report += "| State | Avg Engines Exec | Avg Duration (ms) | Avg Outputs |\n"
            report += "|-------|-----------------|-------------------|-------------|\n"
            
            for state, metrics in sorted(state_groups.items()):
                avg_exec = sum(m['engines_executed'] for m in metrics) / len(metrics)
                avg_duration = sum(m['state_duration_ms'] for m in metrics) / len(metrics)
                avg_outputs = sum(m['outputs_produced'] for m in metrics) / len(metrics)
                
                report += f"| {state} | {avg_exec:.1f} | {avg_duration:.2f} | {avg_outputs:.1f} |\n"
        
        report += f"""

## Top Missing Dependencies

"""
        
        if top_missing:
            for key, count in top_missing:
                report += f"- `{key}`: {count} occurrences\n"
        else:
            report += "[OK] No missing dependencies detected\n"
        
        report += f"""

## Output Consumption Integrity

- Fake Consumption Errors: {self.fake_consumption_count}
- Status: {'[OK] NO FAKE CONSUMPTION' if no_fake_consumption else '[X] FAKE CONSUMPTION DETECTED'}

## Stability Trends

"""
        
        if len(self.latency_history) >= 100:
            recent_latency = sum(list(self.latency_history)[-100:]) / 100
            recent_memory = sum(list(self.memory_history)[-100:]) / 100
            recent_backlog = sum(list(self.backlog_history)[-100:]) / 100
            
            report += f"""
| Metric | Recent Average |
|--------|---------------|
| Cycle Latency | {recent_latency:.2f} ms |
| Memory Usage | {recent_memory:.2f} MB |
| Output Bus Backlog | {recent_backlog:.1f} |
"""
        else:
            report += "Insufficient data (need 100+ cycles)\n"
        
        report += """

## FINAL VERDICT

"""
        
        # Check all conditions
        conditions_met = []
        conditions_failed = []
        
        if no_critical_deps:
            conditions_met.append("[OK] No critical dependencies missing")
        else:
            conditions_failed.append("[X] Missing dependencies detected")
        
        if no_fake_consumption:
            conditions_met.append("[OK] No fake consumption detected")
        else:
            conditions_failed.append("[X] Fake consumption detected")
        
        if score_above_threshold:
            conditions_met.append(f"[OK] Unison score above threshold ({avg_score:.4f} >= 0.92)")
        else:
            conditions_failed.append(f"[X] Unison score below threshold ({avg_score:.4f} < 0.92)")
        
        if enough_cycles:
            conditions_met.append(f"[OK] Sufficient cycles analyzed ({self.cycle_count} >= 1000)")
        else:
            conditions_failed.append(f" Need more cycles ({self.cycle_count} < 1000)")
        
        # Final statement
        verdict_pass = no_critical_deps and no_fake_consumption and score_above_threshold and enough_cycles
        
        if verdict_pass:
            report += """
**ALL ENGINES ARE OPERATING IN UNISON**

All conditions satisfied:
"""
            for condition in conditions_met:
                report += f"- {condition}\n"
        else:
            report += """
**ENGINES REQUIRE ATTENTION**

"""
            if conditions_met:
                report += "Conditions met:\n"
                for condition in conditions_met:
                    report += f"- {condition}\n"
                report += "\n"
            
            report += "Conditions not met:\n"
            for condition in conditions_failed:
                report += f"- {condition}\n"
        
        # Save report
        report_file = self.reports_dir / 'ENGINE_UNISON_PROOF_REPORT.md'
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Unison proof report saved: {report_file}")
        
        return report

# Global instance
_verifier = None

def get_unison_verifier() -> EngineUnisonVerifier:
    """Get global unison verifier"""
    global _verifier
    if _verifier is None:
       _verifier = EngineUnisonVerifier()
    return _verifier

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    verifier = get_unison_verifier()
    
    # Simulate
    for i in range(14):
        verifier.record_state_execution(
            f'STATE_{i}', 10, 9, 0, 1, 15, 12, 50.0 + i * 5
        )
    
    verifier.record_stability_metrics(150.0, 50, False)
    verifier.next_cycle()
    
    report = verifier.generate_unison_proof_report()
    print(report)
