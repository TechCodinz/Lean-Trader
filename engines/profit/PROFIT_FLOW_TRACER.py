#!/usr/bin/env python3
"""
PROFIT_FLOW_TRACER.py
Trace profit attribution from engines to real trades
MUST RUN ON VPS WITH LIVE/BACKTEST DATA
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfitFlowTracer:
    """Trace which engines contributed to profitable trades"""
    
    def __init__(self, reports_dir: Path = Path("/root/bot/reports")):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
        
        # Load metrics and traces
        self.metrics = self.load_metrics()
        self.decision_traces = self.load_decision_traces()
        
        # Profit attribution
        self.engine_pnl_contribution = defaultdict(lambda: {'positive': 0, 'negative': 0, 'count': 0})
        self.engine_trade_influence = defaultdict(int)
    
    def load_metrics(self) -> List[Dict]:
        """Load trading reality metrics"""
        metrics_file = self.reports_dir / 'trading_reality_metrics.jsonl'
        
        if not metrics_file.exists():
            logger.warning(f"Metrics file not found: {metrics_file}")
            return []
        
        metrics = []
        with open(metrics_file) as f:
            for line in f:
                try:
                    metrics.append(json.loads(line))
                except:
                    pass
        
        return metrics
    
    def load_decision_traces(self) -> List[Dict]:
        """Load decision traces"""
        trace_file = self.reports_dir / 'decision_traces.jsonl'
        
        if not trace_file.exists():
            logger.warning(f"Trace file not found: {trace_file}")
            return []
        
        traces = []
        with open(trace_file) as f:
            for line in f:
                try:
                    traces.append(json.loads(line))
                except:
                    pass
        
        return traces
    
    def trace_profit_flow(self):
        """Trace profit attribution"""
        logger.info("Tracing profit flow from engines to trades...")
        
        # Analyze decision traces
        for trace in self.decision_traces:
            contributing_engines = trace.get('contributing_engines', [])
            final_action = trace.get('final_action')
            
            if final_action == 'EXECUTE':
                # This trade was executed - attribute to contributing engines
                for engine in contributing_engines:
                    self.engine_trade_influence[engine] += 1
        
        logger.info(f"Analyzed {len(self.decision_traces)} decision traces")
    
    def compute_firing_rates(self) -> Dict:
        """Compute firing rate for each profitable engine"""
        logger.info("Computing engine firing rates...")
        
        # Load profit engine list
        try:
            with open('PROFIT_ENGINE_VERIFICATION_REPORT.json') as f:
                report = json.load(f)
                profit_engines = list(report['profit_engines'].keys())
        except:
            logger.warning("Could not load profit engine list, using all engines from metrics")
            profit_engines = []
        
        # From metrics, extract execution counts
        engine_execution_counts = defaultdict(int)
        
        for metric in self.metrics:
            engines_ran = metric.get('total_engines_ran', 0)
            # Note: Need per-engine execution data from StateAwareOrchestrator metrics
        
        firing_rates = {}
        
        for engine in profit_engines:
            execution_count = engine_execution_counts.get(engine, 0)
            trade_influence = self.engine_trade_influence.get(engine, 0)
            
            firing_rates[engine] = {
                'execution_count': execution_count,
                'trade_influence_count': trade_influence,
                'influence_rate': trade_influence / execution_count if execution_count > 0 else 0
            }
        
        return firing_rates
    
    def generate_profit_attribution_report(self):
        """Generate final profit attribution report"""
        logger.info("Generating profit attribution report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_metrics_analyzed': len(self.metrics),
            'total_traces_analyzed': len(self.decision_traces),
            'engine_trade_influence': dict(self.engine_trade_influence),
            'top_contributing_engines': sorted(
                self.engine_trade_influence.items(),
                key=lambda x: -x[1]
            )[:20]
        }
        
        # Save report
        report_file = self.reports_dir / 'profit_attribution_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Profit attribution report saved: {report_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("PROFIT FLOW ATTRIBUTION REPORT")
        print("=" * 80)
        
        print(f"\nMetrics Analyzed: {report['total_metrics_analyzed']}")
        print(f"Decision Traces Analyzed: {report['total_traces_analyzed']}")
        
        print(f"\nTop 20 Engines Contributing to Executed Trades:")
        for i, (engine, count) in enumerate(report['top_contributing_engines'], 1):
            print(f"  {i}. {engine}: {count} trades influenced")
        
        if not report['top_contributing_engines']:
            print("\n[X] WARNING: No engine attribution found in decision traces")
            print("   This means:")
            print("   1. Decision traces may not be capturing contributing_engines")
            print("   2. OR no trades have been executed yet")
            print("   3. OR orchestrator not writing traces correctly")
        
        print("\n" + "=" * 80)
        print("FINAL VERDICT ON PROFIT ENGINES:")
        print("=" * 80)
        
        if report['total_traces_analyzed'] == 0:
            print("""
[X] CANNOT CONFIRM PROFIT ENGINES ARE CONTRIBUTING

REASON: No decision traces found

ACTION REQUIRED:
1. Verify TRADING_REALITY_PROOF is integrated in orchestrator
2. Verify orchestrator is calling proof.record_trade_attempt()
3. Wait for more trading cycles to accumulate data
4. Check /root/bot/logs for errors in trace writing
""")
        elif not report['top_contributing_engines']:
            print("""
[X] CANNOT CONFIRM PROFIT ENGINES ARE CONTRIBUTING

REASON: Traces exist but no engine attribution

ACTION REQUIRED:
1. Modify orchestrator to pass contributing_engines in record_trade_attempt()
2. Ensure engines are setting attribution in signals
3. Verify signal blending preserves engine attribution
""")
        else:
            top_engine_count = len([c for e, c in report['top_contributing_engines'] if c > 10])
            print(f"""
✓ PARTIAL CONFIRMATION: Profit engines are influencing trades

EVIDENCE:
- {len(report['top_contributing_engines'])} engines attributed to trades
- {top_engine_count} engines with >10 trade influences
- Top engine: {report['top_contributing_engines'][0][0]} ({report['top_contributing_engines'][0][1]} trades)

STILL REQUIRED FOR FULL CONFIRMATION:
- PnL attribution per engine (need actual P&L data)
- Firing rate analysis (need per-engine execution counts)
- Calibration validation (need threshold hit rates)

NEXT STEPS:
1. Run for 500+ cycles to accumulate more data
2. Add PnL tracking to decision traces
3. Generate ENGINE_RUNTIME_PROOF with per-engine execution counts
""")
        
        return report

def main():
    tracer = ProfitFlowTracer()
    tracer.trace_profit_flow()
    firing_rates = tracer.compute_firing_rates()
    report = tracer.generate_profit_attribution_report()

if __name__ == "__main__":
    main()
