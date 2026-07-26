#!/usr/bin/env python3
"""
PROFIT_ENGINE_ANALYZER.py
Analyze event-based profit data: firing rates, calibration, bottlenecks
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfitEngineAnalyzer:
    """Analyze profit engine performance from events"""
    
    def __init__(self, reports_dir: Path = Path("/root/bot/reports")):
        self.reports_dir = reports_dir
        
        # Load data
        self.events = self.load_events()
        self.pnl_attribution = self.load_pnl_attribution()
        self.profit_engines = self.load_profit_engines()
    
    def load_events(self) -> List[Dict]:
        """Load profit events"""
        events_file = self.reports_dir / 'profit_events.jsonl'
        
        if not events_file.exists():
            logger.warning(f"Events file not found: {events_file}")
            return []
        
        events = []
        with open(events_file) as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    pass
        
        return events
    
    def load_pnl_attribution(self) -> Dict:
        """Load PnL attribution"""
        pnl_file = self.reports_dir / 'engine_pnl_attribution.json'
        
        if not pnl_file.exists():
            logger.warning(f"PnL attribution file not found: {pnl_file}")
            return {}
        
        with open(pnl_file) as f:
            return json.load(f)
    
    def load_profit_engines(self) -> List[str]:
        """Load profit engine list"""
        try:
            with open('/root/bot/PROFIT_ENGINE_VERIFICATION_REPORT.json') as f:
                report = json.load(f)
                return list(report['profit_engines'].keys())
        except:
            logger.warning("Could not load profit engine list")
            return []
    
    def compute_firing_rates(self) -> Dict:
        """Compute firing rates and calibration status"""
        engine_stats = {}
        
        engine_pnl = self.pnl_attribution.get('engine_pnl', {})
        engine_triggers = self.pnl_attribution.get('engine_triggers', {})
        engine_blocks = self.pnl_attribution.get('engine_blocks', {})
        
        for engine in self.profit_engines:
            triggers = engine_triggers.get(engine, 0)
            blocks = engine_blocks.get(engine, 0)
            pnl_data = engine_pnl.get(engine, {})
            
            trades = pnl_data.get('trades', 0)
            wins = pnl_data.get('wins', 0)
            losses = pnl_data.get('losses', 0)
            net_pnl = pnl_data.get('net', 0)
            
            # Compute metrics
            block_rate = blocks / triggers if triggers > 0 else 0
            execution_rate = trades / triggers if triggers > 0 else 0
            win_rate = wins / trades if trades > 0 else 0
            
            # Classify
            status = 'UNKNOWN'
            
            if triggers == 0:
                status = 'INERT'
            elif triggers < 10 and blocks == 0:
                status = 'OVERCALIBRATED'  # Triggers too rarely
            elif block_rate > 0.7:
                status = 'OVERCALIBRATED'  # Most signals blocked
            elif block_rate < 0.1 and win_rate < 0.3:
                status = 'UNDERCALIBRATED'  # Too many losing trades
            elif trades > 0 and net_pnl > 0:
                status = 'HEALTHY'
            elif trades > 0 and net_pnl < 0:
                status = 'NEGATIVE_PNL'
            
            engine_stats[engine] = {
                'triggers': triggers,
                'blocks': blocks,
                'trades': trades,
                'wins': wins,
                'losses': losses,
                'block_rate': round(block_rate, 3),
                'execution_rate': round(execution_rate, 3),
                'win_rate': round(win_rate, 3),
                'net_pnl': round(net_pnl, 2),
                'status': status
            }
        
        return engine_stats
    
    def find_bottlenecks(self) -> Dict:
        """Find profit flow bottlenecks"""
        bottlenecks = {
            'block_reasons': defaultdict(int),
            'slow_states': defaultdict(list),
            'top_blockers': defaultdict(int)
        }
        
        for event in self.events:
            event_type = event.get('event_type')
            
            if event_type == 'SIGNAL_BLOCKED':
                reason = event.get('block_reason', 'unknown')
                blocker = event.get('blocker_engine')
                
                bottlenecks['blockchain_reasons'][reason] += 1
                if blocker:
                    bottlenecks['top_blockers'][blocker] += 1
        
        return {
            'top_block_reasons': sorted(bottlenecks['block_reasons'].items(), key=lambda x: -x[1])[:10],
            'top_blocker_engines': sorted(bottlenecks['top_blockers'].items(), key=lambda x: -x[1])[:10]
        }
    
    def generate_scoreboard(self):
        """Generate profit engine scoreboard"""
        logger.info("Generating profit engine scoreboard...")
        
        engine_stats = self.compute_firing_rates()
        bottlenecks = self.find_bottlenecks()
        
        # Top performers by PnL
        top_by_pnl = sorted(
            [(e, s['net_pnl']) for e, s in engine_stats.items() if s['net_pnl'] != 0],
            key=lambda x: -x[1]
        )[:20]
        
        # Engines that never fired
        never_fired = [e for e, s in engine_stats.items() if s['status'] == 'INERT']
        
        # Negative PnL engines
        negative_pnl = [e for e, s in engine_stats.items() if s['status'] == 'NEGATIVE_PNL']
        
        # Overcalibrated
        overcalibrated = [e for e, s in engine_stats.items() if s['status'] == 'OVERCALIBRATED']
        
        # Generate markdown report
        scoreboard = f"""# PROFIT ENGINE SCOREBOARD

Generated: {json.JSONEncoder().encode(datetime.now().isoformat())}

## Top 20 Engines by Net PnL

| Rank | Engine | Net PnL | Trades | Win Rate | Status |
|------|--------|---------|--------|----------|--------|
"""
        
        for i, (engine, pnl) in enumerate(top_by_pnl, 1):
            stats = engine_stats[engine]
            win_rate_pct = stats['win_rate'] * 100
            scoreboard += f"| {i} | {engine[:30]} | ${pnl:.2f} | {stats['trades']} | {win_rate_pct:.1f}% | {stats['status']} |\n"
        
        scoreboard += f"""

## Engines That Never Fired ({len(never_fired)})

"""
        for engine in never_fired[:20]:
            scoreboard += f"- {engine}\n"
        
        scoreboard += f"""

## Engines with Negative PnL ({len(negative_pnl)})

"""
        for engine in negative_pnl[:20]:
            stats = engine_stats[engine]
            scoreboard += f"- {engine}: ${stats['net_pnl']:.2f} ({stats['trades']} trades, {stats['win_rate']*100:.1f}% win rate)\n"
        
        scoreboard += f"""

## Overcalibrated Engines ({len(overcalibrated)})

"""
        for engine in overcalibrated[:20]:
            stats = engine_stats[engine]
            scoreboard += f"- {engine}: {stats['triggers']} triggers, {stats['block_rate']*100:.1f}% blocked\n"
        
        scoreboard += f"""

## Profit Flow Bottlenecks

### Top Block Reasons
"""
        for reason, count in bottlenecks['top_block_reasons']:
            scoreboard += f"- {reason}: {count} blocks\n"
        
        scoreboard += """

## FINAL VERDICT

"""
        
        # Conditions for verdict
        has_attribution = len(top_by_pnl) > 0
        critical_inert = any(engine_stats.get(e, {}).get('status') == 'INERT' for e in ['ScalpEngine', 'ExitEngine', 'RiskManager'])
        positive_majority = len([e for e, s in engine_stats.items() if s['net_pnl'] > 0]) > len([e for e, s in engine_stats.items() if s['net_pnl'] < 0])
        
        if has_attribution and not critical_inert and positive_majority:
            scoreboard += "[OK] **PROFIT ENGINES ARE WORKING AND CALIBRATED**\n\n"
            scoreboard += f"- Attribution exists for {len(top_by_pnl)} engines\n"
            scoreboard += f"- No critical engines are inert\n"
            scoreboard += f"- Positive PnL majority\n"
        else:
            scoreboard += "[X] **PROFIT ENGINES REQUIRE ATTENTION**\n\n"
            scoreboard += "Issues:\n"
            
            if not has_attribution:
                scoreboard += "- No PnL attribution found (zero completed trades)\n"
            if critical_inert:
                scoreboard += "- Critical engines are inert\n"
            if not positive_majority:
                scoreboard += "- Negative PnL majority\n"
            
            scoreboard += "\n**ENGINES TO RECALIBRATE:**\n"
            
            for engine in overcalibrated[:10]:
                stats = engine_stats[engine]
                scoreboard += f"\n### {engine}\n"
                scoreboard += f"- Issue: Overcalibrated ({stats['block_rate']*100:.1f}% block rate)\n"
                scoreboard += f"- Action: Reduce confidence thresholds by 10-20%\n"
                scoreboard += f"- Current triggers: {stats['triggers']}\n"
        
        # Save scoreboard
        scoreboard_file = self.reports_dir / 'PROFIT_ENGINE_SCOREBOARD.md'
        with open(scoreboard_file, 'w') as f:
            f.write(scoreboard)
        
        logger.info(f"Scoreboard saved: {scoreboard_file}")
        
        # Also save JSON version
        json_scoreboard = {
            'top_by_pnl': [{'engine': e, 'pnl': p} for e, p in top_by_pnl],
            'never_fired': never_fired,
            'negative_pnl': negative_pnl,
            'overcalibrated': overcalibrated,
            'bottlenecks': bottlenecks,
            'verdict': 'PASS' if (has_attribution and not critical_inert and positive_majority) else 'FAIL'
        }
        
        json_file = self.reports_dir / 'profit_flow_bottlenecks.json'
        with open(json_file, 'w') as f:
            json.dump(json_scoreboard, f, indent=2)
        
        print(scoreboard)

def main():
    analyzer = ProfitEngineAnalyzer()
    analyzer.generate_scoreboard()

if __name__ == "__main__":
    from datetime import datetime
    main()
