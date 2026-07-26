#!/usr/bin/env python3
"""
AB_COMPARE_ORCHESTRATION.py
Compare BASELINE vs STATEAWARE orchestration modes
Run backtest with both and output performance comparison
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestrationComparer:
    """Compare BASELINE vs STATEAWARE orchestration performance"""
    
    def __init__(self, reports_dir: str = "/root/bot/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def load_metrics(self, mode: str) -> List[Dict]:
        """Load metrics from JSONL file"""
        metrics_file = self.reports_dir / 'trading_reality_metrics.jsonl'
        
        if not metrics_file.exists():
            logger.warning(f"Metrics file not found: {metrics_file}")
            return []
        
        metrics = []
        with open(metrics_file) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('mode') == mode:
                        metrics.append(data)
                except:
                    pass
        
        return metrics
    
    def analyze_metrics(self, metrics: List[Dict]) -> Dict:
        """Analyze metrics and compute performance stats"""
        if not metrics:
            return {}
        
        total_signals = sum(m.get('signals_generated_count', 0) for m in metrics)
        total_attempted = sum(m.get('trades_attempted_count', 0) for m in metrics)
        total_executed = sum(m.get('trades_executed_count', 0) for m in metrics)
        total_blocked_risk = sum(m.get('trades_blocked_by_risk_count', 0) for m in metrics)
        total_blocked_safe = sum(m.get('trades_blocked_by_safe_mode_count', 0) for m in metrics)
        
        avg_cycle_ms = sum(m.get('cycle_duration_ms', 0) for m in metrics) / len(metrics)
        avg_engines = sum(m.get('total_engines_ran', 0) for m in metrics) / len(metrics)
        
        safe_mode_cycles = sum(1 for m in metrics if m.get('safe_mode_active', False))
        
        return {
            'cycles': len(metrics),
            'total_signals': total_signals,
            'total_trades_attempted': total_attempted,
            'total_trades_executed': total_executed,
            'execution_rate_pct': round(total_executed / total_attempted * 100, 2) if total_attempted > 0 else 0,
            'blocked_by_risk': total_blocked_risk,
            'blocked_by_safe_mode': total_blocked_safe,
            'risk_block_rate_pct': round(total_blocked_risk / total_attempted * 100, 2) if total_attempted > 0 else 0,
            'safe_mode_block_rate_pct': round(total_blocked_safe / total_attempted * 100, 2) if total_attempted > 0 else 0,
            'avg_cycle_duration_ms': round(avg_cycle_ms, 2),
            'avg_engines_per_cycle': round(avg_engines, 2),
            'safe_mode_cycles': safe_mode_cycles,
            'safe_mode_rate_pct': round(safe_mode_cycles / len(metrics) * 100, 2)
        }
    
    def compare_modes(self):
        """Compare BASELINE vs STATEAWARE"""
        logger.info("Loading metrics for both modes...")
        
        baseline_metrics = self.load_metrics('BASELINE')
        stateaware_metrics = self.load_metrics('STATEAWARE')
        
        logger.info(f"BASELINE: {len(baseline_metrics)} cycles")
        logger.info(f"STATEAWARE: {len(stateaware_metrics)} cycles")
        
        baseline_stats = self.analyze_metrics(baseline_metrics)
        stateaware_stats = self.analyze_metrics(stateaware_metrics)
        
        # Comparison
        comparison = {
            'baseline': baseline_stats,
            'stateaware': stateaware_stats,
            'delta': {}
        }
        
        # Calculate deltas
        if baseline_stats and stateaware_stats:
            for key in baseline_stats:
                if isinstance(baseline_stats[key], (int, float)):
                    baseline_val = baseline_stats[key]
                    stateaware_val = stateaware_stats[key]
                    delta = stateaware_val - baseline_val
                    delta_pct = (delta / baseline_val * 100) if baseline_val != 0 else 0
                    comparison['delta'][key] = {
                        'absolute': round(delta, 2),
                        'percent': round(delta_pct, 2)
                    }
        
        # Save results
        results_file = self.reports_dir / 'ab_comparison_results.json'
        with open(results_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"Comparison saved: {results_file}")
        
        # Create CSV summary
        self.create_csv_summary(comparison)
        
        # Check profitability guards
        self.check_profitability_guards(comparison)
        
        return comparison
    
    def create_csv_summary(self, comparison: Dict):
        """Create CSV summary table"""
        rows = []
        
        baseline = comparison.get('baseline', {})
        stateaware = comparison.get('stateaware', {})
        delta = comparison.get('delta', {})
        
        for key in baseline:
            rows.append({
                'Metric': key,
                'BASELINE': baseline[key],
                'STATEAWARE': stateaware[key],
                'Delta': delta.get(key, {}).get('absolute', 'N/A'),
                'Delta %': delta.get(key, {}).get('percent', 'N/A')
            })
        
        df = pd.DataFrame(rows)
        csv_file = self.reports_dir / 'ab_comparison_summary.csv'
        df.to_csv(csv_file, index=False)
        
        logger.info(f"CSV summary saved: {csv_file}")
        print("\nA/B COMPARISON SUMMARY:")
        print(df.to_string(index=False))
    
    def check_profitability_guards(self, comparison: Dict):
        """Check if STATEAWARE reduces profitability"""
        delta = comparison.get('delta', {})
        
        warnings = []
        recommendations = []
        
        # Check trades reduction
        trades_delta_pct = delta.get('total_trades_executed', {}).get('percent', 0)
        if trades_delta_pct < -40:
            warnings.append(f" TRADES REDUCED BY {abs(trades_delta_pct):.1f}%")
            recommendations.append("Reduce MARKET_ANALYSIS engine frequency (per-bar, not per-tick)")
            recommendations.append("Introduce engine tiers (critical every cycle, others every N cycles)")
        
        # Check safe mode blocking
        safe_mode_block_pct = comparison['stateaware'].get('safe_mode_block_rate_pct', 0)
        if safe_mode_block_pct > 10:
            warnings.append(f" SAFE MODE BLOCKING {safe_mode_block_pct:.1f}% OF TRADES")
            recommendations.append("Relax over-strict effect verification for non-critical engines")
            recommendations.append("Ensure safe-mode doesn't trigger for non-trading-critical engines")
        
        # Check latency increase
        latency_delta_pct = delta.get('avg_cycle_duration_ms', {}).get('percent', 0)
        if latency_delta_pct > 50:
            warnings.append(f" LATENCY INCREASED BY {latency_delta_pct:.1f}%")
            recommendations.append("Optimize slowest engines")
            recommendations.append("Run non-critical engines less frequently")
        
        # Save guard report
        guard_report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'warnings': warnings,
            'recommendations': recommendations,
            'requires_mitigation': len(warnings) > 0
        }
        
        guard_file = self.reports_dir / 'profitability_guards.json'
        with open(guard_file, 'w') as f:
            json.dump(guard_report, f, indent=2)
        
        if warnings:
            print("\n" + "="*80)
            print("PROFITABILITY GUARDS TRIGGERED")
            print("="*80)
            for warning in warnings:
                print(warning)
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
            print("="*80)
        else:
            print("\n[OK] All profitability guards passed - no performance degradation detected")

def main():
    comparer = OrchestrationComparer()
    comparison = comparer.compare_modes()

if __name__ == "__main__":
    main()
