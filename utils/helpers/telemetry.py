"""
Elite Stack Telemetry

Logging, CSV export, and metrics for elite stack.
Captures all elite context data for analysis and debugging.
"""

import pandas as pd
import logging
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime

from .models import EliteContext

logger = logging.getLogger(__name__)


class EliteTelemetry:
    """
    Telemetry system for elite stack
    
    Handles logging, CSV export, metrics
    """
    
    def __init__(self,
                 enable_csv_export: bool = True,
                 csv_base_path: str = "./data",
                 enable_metrics: bool = False,
                 metrics_endpoint: Optional[str] = None):
        """
        Initialize Elite Telemetry
        
        Args:
            enable_csv_export: Enable CSV logging
            csv_base_path: Base directory for CSV files
            enable_metrics: Enable metrics endpoint
            metrics_endpoint: Metrics endpoint URL
        """
        self.enable_csv_export = enable_csv_export
        self.csv_base_path = Path(csv_base_path)
        self.enable_metrics = enable_metrics
        self.metrics_endpoint = metrics_endpoint
        
        # Create CSV directory
        if self.enable_csv_export:
            self.csv_base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("[OK] EliteTelemetry initialized")
        logger.info(f"   CSV export: {enable_csv_export}")
        logger.info(f"   CSV path: {csv_base_path}")
    
    def log_elite_context(self,
                         context: EliteContext,
                         symbol: str,
                         venue: str,
                         final_action: Optional[str] = None,
                         execution_result: Optional[str] = None):
        """
        Log elite context to all enabled outputs
        
        Args:
            context: Elite context to log
            symbol: Symbol name
            venue: Venue type
            final_action: Final action taken (TAKE/SKIP/WAIT)
            execution_result: Execution result string
        """
        # Structured logging
        self._log_structured(context, symbol, venue, final_action)
        
        # CSV export
        if self.enable_csv_export:
            self._export_csv(context, symbol, venue, final_action, execution_result)
        
        # Metrics
        if self.enable_metrics:
            self._send_metrics(context, symbol, venue)
    
    def _log_structured(self,
                       context: EliteContext,
                       symbol: str,
                       venue: str,
                       final_action: Optional[str]):
        """
        Structured logging output
        """
        log_data = {
            'symbol': symbol,
            'venue': venue,
            'timestamp': context.timestamp,
            'wave_state': context.wave_state,
            'chaos': f"{context.chaos_score:.2f}" if context.chaos_score else "N/A",
            'pitch': f"{context.pitch_value:.2f}" if context.pitch_value else "N/A",
        }
        
        if context.intent:
            log_data['intent_bias'] = f"{context.intent.intent_bias:+.2f}"
            log_data['trap_risk'] = f"{context.intent.trap_risk:.2f}"
        
        if context.oce:
            log_data['oce_decision'] = context.oce.oce_decision
            log_data['oce_score'] = f"{context.oce.oce_score:.2f}"
        
        if context.rmf:
            log_data['rmf_action'] = context.rmf.final_action
        
        if final_action:
            log_data['final_action'] = final_action
        
        logger.info(f"Elite Context: {log_data}")
    
    def _export_csv(self,
                   context: EliteContext,
                   symbol: str,
                   venue: str,
                   final_action: Optional[str],
                   execution_result: Optional[str]):
        """
        Export to CSV file
        """
        csv_file = self.csv_base_path / f"elite_context_{symbol.replace('/', '_')}_{venue}.csv"
        
        # Build row
        row = {
            'timestamp': context.timestamp,
            'symbol': symbol,
            'venue': venue,
            'bar_id': context.bar_id,
            # Wave + Pitch
            'wave_state': context.wave_state,
            'wave_flow_score': context.wave_flow_score,
            'chaos_score': context.chaos_score,
            'pitch_value': context.pitch_value,
            'pitch_regime': context.pitch_regime,
        }
        
        # Intent
        if context.intent:
            row.update({
                'intent_bias': context.intent.intent_bias,
                'intent_strength': context.intent.intent_strength,
                'trap_risk': context.intent.trap_risk,
                'absorption_score': context.intent.absorption_score,
                'failed_impulse_score': context.intent.failed_impulse_score,
                'followthrough_score': context.intent.followthrough_score,
                'divergence_score': context.intent.divergence_score,
                'intent_confidence': context.intent.confidence
            })
        
        # Liquidity
        if context.liquidity_fields:
            row.update({
                'gravity_vector': context.liquidity_fields.gravity_vector,
                'sweep_risk': context.liquidity_fields.sweep_risk,
                'support_strength': context.liquidity_fields.support_strength,
                'resistance_strength': context.liquidity_fields.resistance_strength,
                'liquidity_confidence': context.liquidity_fields.confidence
            })
        
        # OCE
        if context.oce:
            row.update({
                'oce_decision': context.oce.oce_decision,
                'oce_score': context.oce.oce_score,
                'expected_edge': context.oce.expected_edge_score,
                'risk_cost': context.oce.risk_cost,
                'capital_lock_cost': context.oce.capital_lock_cost,
                'execution_cost': context.oce.execution_cost,
                'oce_confidence': context.oce.confidence
            })
        
        # Shadow Paths
        if context.shadow_paths:
            row.update({
                'take_expected_return': context.shadow_paths.take_expected_return,
                'take_expected_dd': context.shadow_paths.take_expected_dd,
                'skip_opp_cost': context.shadow_paths.skip_opportunity_cost,
                'regret_score': context.shadow_paths.regret_score,
                'sps_confidence': context.shadow_paths.confidence
            })
        
        # RMF
        if context.rmf:
            row.update({
                'rmf_action': context.rmf.final_action,
                'regret_take': context.rmf.regret_take,
                'regret_skip': context.rmf.regret_skip,
                'correlation_penalty': context.rmf.correlation_penalty,
                'diversification_bonus': context.rmf.diversification_bonus,
                'rmf_confidence': context.rmf.action_confidence
            })
        
        # AFE
        if context.afe:
            row.update({
                'af_guard_level': context.afe.af_guard_level,
                'size_cap_multiplier': context.afe.size_cap_multiplier,
                'entry_delay_multiplier': context.afe.entry_delay_multiplier,
                'confirmation_requirement': context.afe.confirmation_requirement,
                'afe_confidence': context.afe.confidence
            })
        
        # CRM
        if context.crm:
            row.update({
                'exposure_cap': context.crm.exposure_cap_multiplier,
                'frequency_cap': context.crm.frequency_cap_multiplier,
                'liquidity_fit': context.crm.liquidity_fit_score,
                'execution_quality': context.crm.execution_quality_score,
                'volatility_resonance': context.crm.volatility_resonance,
                'chaos_penalty': context.crm.chaos_penalty,
                'crm_confidence': context.crm.confidence
            })
        
        # Heat
        if context.heat:
            row.update({
                'heat_allow_trade': context.heat.allow_trade,
                'heat_size_multiplier': context.heat.adjusted_size_multiplier,
                'current_heat': context.heat.current_heat,
                'risk_budget_used': context.heat.risk_budget_used
            })
        
        # Final decision
        row['final_action'] = final_action
        row['execution_result'] = execution_result
        row['final_size_multiplier'] = context.get_size_multiplier()
        
        # Append to CSV
        df = pd.DataFrame([row])
        
        if csv_file.exists():
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, mode='w', header=True, index=False)
    
    def _send_metrics(self,
                     context: EliteContext,
                     symbol: str,
                     venue: str):
        """
        Send metrics to endpoint
        
        TODO: Implement Prometheus/Grafana integration
        """
        if not self.metrics_endpoint:
            return
        
        # Would send HTTP POST to metrics endpoint
        pass
