"""
Portfolio Heat Manager

Manages correlated exposure and portfolio risk budgets.
Prevents excessive correlation clustering and heat buildup.
Hard gates trades when heat exceeds limits.

Tracks: Correlation clusters, risk budget, venue exposure.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from ..models import CorrelationCluster, HeatOutput

logger = logging.getLogger(__name__)


class PortfolioHeatManager:
    """
    Portfolio correlation and heat management
    
    Prevents correlated overexposure and manages risk budgets
    """
    
    def __init__(self,
                 max_correlated_exposure: float = 0.40,  # 40% in any cluster
                 max_portfolio_heat: float = 0.75,  # 75% heat limit
                 correlation_threshold: float = 0.6):  # 0.6+ = correlated
        """
        Initialize Portfolio Heat Manager
        
        Args:
            max_correlated_exposure: Max % in any correlation cluster
            max_portfolio_heat: Max portfolio heat before gating
            correlation_threshold: Correlation threshold for clustering
        """
        self.max_correlated_exposure = max_correlated_exposure
        self.max_portfolio_heat = max_portfolio_heat
        self.correlation_threshold = correlation_threshold
        
        # Current state (would be persisted in production)
        self.current_positions: Dict[str, Dict] = {}  # symbol -> position_data
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}
        
        logger.info("[OK] PortfolioHeatManager initialized")
        logger.info(f"   Max correlated exposure: {max_correlated_exposure:.1%}")
        logger.info(f"   Max portfolio heat: {max_portfolio_heat:.1%}")
    
    def evaluate_heat(self,
                     proposed_symbol: str,
                     proposed_size: float,
                     proposed_direction: int,  # 1 = long, -1 = short
                     portfolio_size: float,
                     bar_id: Optional[int] = None) -> HeatOutput:
        """
        Evaluate portfolio heat for proposed trade
        
        Args:
            proposed_symbol: Symbol to trade
            proposed_size: Proposed position size ($)
            proposed_direction: 1 = long, -1 = short
            portfolio_size: Total portfolio size
            bar_id: Optional bar ID
        
        Returns:
            HeatOutput with allow/deny and adjustments
        """
        try:
            # Update correlation matrix (if needed)
            self._update_correlations(proposed_symbol)
            
            # Find correlation clusters
            clusters = self._find_correlation_clusters(
                proposed_symbol, proposed_direction
            )
            
            # Calculate current heat
            current_heat = self._calc_current_heat(
                portfolio_size
            )
            
            # Calculate heat with proposed trade
            proposed_heat = self._calc_proposed_heat(
                proposed_symbol, proposed_size, proposed_direction,
                portfolio_size, clusters
            )
            
            # Calculate risk budget used
            risk_budget_used = self._calc_risk_budget_used(
                current_heat, proposed_heat
            )
            
            # Calculate venue exposure
            venue_exposure = self._calc_venue_exposure(
                proposed_symbol, proposed_size, portfolio_size
            )
            
            # Make allow/deny decision
            allow_trade, reason_codes = self._make_heat_decision(
                current_heat, proposed_heat, clusters, proposed_symbol,
                proposed_size, portfolio_size
            )
            
            # Calculate size adjustment
            adjusted_size_multiplier = self._calc_size_adjustment(
                allow_trade, proposed_heat, clusters,
                proposed_symbol, proposed_size, portfolio_size
            )
            
            components = {
                'current_heat': current_heat,
                'proposed_heat': proposed_heat,
                'heat_increase': proposed_heat - current_heat,
                'cluster_count': len(clusters),
                'largest_cluster_exposure': max([c.total_exposure / portfolio_size for c in clusters], default=0.0)
            }
            
            return HeatOutput(
                allow_trade=allow_trade,
                adjusted_size_multiplier=adjusted_size_multiplier,
                correlation_clusters=clusters,
                max_correlated_exposure=self.max_correlated_exposure,
                current_heat=current_heat,
                risk_budget_used=risk_budget_used,
                venue_exposure=venue_exposure,
                reason_codes=reason_codes,
                components=components,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"Heat evaluation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def register_position(self,
                         symbol: str,
                         size: float,
                         direction: int,
                         venue_type: str):
        """
        Register a new position for tracking
        
        Call this when a trade is executed
        """
        self.current_positions[symbol] = {
            'size': size,
            'direction': direction,
            'venue_type': venue_type,
            'timestamp': datetime.now()
        }
        
        logger.debug(f"Position registered: {symbol} ${size:.0f} {'LONG' if direction > 0 else 'SHORT'}")
    
    def remove_position(self, symbol: str):
        """
        Remove position from tracking
        
        Call this when position is closed
        """
        if symbol in self.current_positions:
            del self.current_positions[symbol]
            logger.debug(f"Position removed: {symbol}")
    
    def _update_correlations(self, new_symbol: str):
        """
        Update correlation matrix
        
        In production, this would use rolling return correlations
        For now, use heuristic clustering
        """
        # Simple heuristic: symbols starting with same letters correlate
        # In production: calculate actual return correlations
        for existing_symbol in self.current_positions.keys():
            if new_symbol == existing_symbol:
                continue
            
            # Heuristic correlation
            correlation = self._estimate_correlation(new_symbol, existing_symbol)
            self.correlation_matrix[(new_symbol, existing_symbol)] = correlation
            self.correlation_matrix[(existing_symbol, new_symbol)] = correlation
    
    def _estimate_correlation(self, symbol1: str, symbol2: str) -> float:
        """
        Estimate correlation between symbols
        
        Heuristic for now; in production use actual return correlation
        """
        # Same base currency → high correlation
        if symbol1[:3] == symbol2[:3]:  # e.g., BTC/USD, BTC/USDT
            return 0.85
        
        # Same asset class → moderate correlation
        if self._get_asset_class(symbol1) == self._get_asset_class(symbol2):
            return 0.50
        
        # Different → low correlation
        return 0.20
    
    def _get_asset_class(self, symbol: str) -> str:
        """Determine asset class from symbol"""
        if "BTC" in symbol or "ETH" in symbol:
            return "crypto_major"
        elif "/" in symbol and any(x in symbol for x in ["USD", "EUR", "GBP"]):
            return "forex"
        elif "XAU" in symbol or "XAG" in symbol:
            return "metal"
        else:
            return "other"
    
    def _find_correlation_clusters(self,
                                  proposed_symbol: str,
                                  proposed_direction: int) -> List[CorrelationCluster]:
        """
        Find correlation clusters in portfolio
        
        Groups correlated positions together
        """
        clusters = []
        clustered_symbols = set()
        
        # Create clusters of correlated positions
        for symbol1, pos1 in self.current_positions.items():
            if symbol1 in clustered_symbols:
                continue
            
            # Start new cluster
            cluster_symbols = [symbol1]
            cluster_exposure = pos1['size']
            correlations = []
            
            # Find correlated positions
            for symbol2, pos2 in self.current_positions.items():
                if symbol2 == symbol1 or symbol2 in clustered_symbols:
                    continue
                
                corr = self.correlation_matrix.get((symbol1, symbol2), 0.0)
                
                # Same direction correlation matters
                if ((pos1['direction'] > 0 and pos2['direction'] > 0) or
                    (pos1['direction'] < 0 and pos2['direction'] < 0)):
                    if corr > self.correlation_threshold:
                        cluster_symbols.append(symbol2)
                        cluster_exposure += pos2['size']
                        correlations.append(corr)
                        clustered_symbols.add(symbol2)
            
            clustered_symbols.add(symbol1)
            
            avg_corr = np.mean(correlations) if correlations else 1.0
            
            clusters.append(CorrelationCluster(
                cluster_id=f"cluster_{len(clusters)}",
                symbols=cluster_symbols,
                avg_correlation=float(avg_corr),
                total_exposure=float(cluster_exposure),
                risk_contribution=0.0  # Calculated later
            ))
        
        # Check if proposed trade fits into any cluster
        if proposed_symbol not in clustered_symbols:
            for cluster in clusters:
                for symbol in cluster.symbols:
                    corr = self.correlation_matrix.get((proposed_symbol, symbol), 0.0)
                    if corr > self.correlation_threshold:
                        # Would join this cluster
                        cluster.symbols.append(f"{proposed_symbol} (proposed)")
                        break
        
        return clusters
    
    def _calc_current_heat(self, portfolio_size: float) -> float:
        """
        Calculate current portfolio heat [0,1]
        
        Heat = sum of directional risk
        """
        if portfolio_size == 0:
            return 0.0
        
        total_long_exposure = sum(
            pos['size'] for pos in self.current_positions.values()
            if pos['direction'] > 0
        )
        
        total_short_exposure = sum(
            pos['size'] for pos in self.current_positions.values()
            if pos['direction'] < 0
        )
        
        # Heat = max directional exposure / portfolio
        heat = max(total_long_exposure, total_short_exposure) / portfolio_size
        
        return float(np.clip(heat, 0.0, 1.0))
    
    def _calc_proposed_heat(self,
                           proposed_symbol: str,
                           proposed_size: float,
                           proposed_direction: int,
                           portfolio_size: float,
                           clusters: List[CorrelationCluster]) -> float:
        """Calculate heat after adding proposed trade"""
        # Simulate adding position
        total_long = sum(
            pos['size'] for pos in self.current_positions.values()
            if pos['direction'] > 0
        )
        total_short = sum(
            pos['size'] for pos in self.current_positions.values()
            if pos['direction'] < 0
        )
        
        if proposed_direction > 0:
            total_long += proposed_size
        else:
            total_short += proposed_size
        
        proposed_heat = max(total_long, total_short) / portfolio_size
        
        return float(np.clip(proposed_heat, 0.0, 1.0))
    
    def _calc_risk_budget_used(self,
                              current_heat: float,
                              proposed_heat: float) -> float:
        """
        Calculate % of risk budget used
        
        Budget = max_portfolio_heat
        """
        used = proposed_heat / self.max_portfolio_heat
        return float(np.clip(used, 0.0, 1.0))
    
    def _calc_venue_exposure(self,
                            proposed_symbol: str,
                            proposed_size: float,
                            portfolio_size: float) -> Dict[str, float]:
        """Calculate exposure by venue"""
        venue_exposure = {}
        
        for symbol, pos in self.current_positions.items():
            venue = pos['venue_type']
            exposure_pct = pos['size'] / portfolio_size
            venue_exposure[venue] = venue_exposure.get(venue, 0.0) + exposure_pct
        
        return venue_exposure
    
    def _make_heat_decision(self,
                           current_heat: float,
                           proposed_heat: float,
                           clusters: List[CorrelationCluster],
                           proposed_symbol: str,
                           proposed_size: float,
                           portfolio_size: float) -> Tuple[bool, List[str]]:
        """
        Decide allow/deny trade based on heat
        
        Returns: (allow_trade, reason_codes)
        """
        reasons = []
        
        # Hard gate: Exceeds max heat
        if proposed_heat > self.max_portfolio_heat:
            return False, [f"Heat limit exceeded ({proposed_heat:.1%} > {self.max_portfolio_heat:.1%})"]
        
        # Check cluster exposure
        for cluster in clusters:
            cluster_pct = cluster.total_exposure / portfolio_size
            if cluster_pct > self.max_correlated_exposure:
                if f"{proposed_symbol} (proposed)" in cluster.symbols:
                    return False, [f"Cluster exposure exceeded ({cluster_pct:.1%} > {self.max_correlated_exposure:.1%})"]
        
        # Heat escalation check
        heat_increase = proposed_heat - current_heat
        if heat_increase > 0.2:  # >20% heat jump
            reasons.append(f"Significant heat increase (+{heat_increase:.1%})")
        
        # Allow trade
        return True, reasons if reasons else ["Heat check passed"]
    
    def _calc_size_adjustment(self,
                             allow_trade: bool,
                             proposed_heat: float,
                             clusters: List[CorrelationCluster],
                             proposed_symbol: str,
                             proposed_size: float,
                             portfolio_size: float) -> float:
        """
        Calculate size adjustment multiplier
        
        Reduces size as heat approaches limit
        """
        if not allow_trade:
            return 0.0  # No trade
        
        # Base: reduce size as heat increases
        heat_factor = 1.0 - (proposed_heat / self.max_portfolio_heat) ** 2
        
        # Further reduce if in concentrated cluster
        cluster_factor = 1.0
        for cluster in clusters:
            if f"{proposed_symbol} (proposed)" in cluster.symbols:
                cluster_pct = cluster.total_exposure / portfolio_size
                if cluster_pct > self.max_correlated_exposure * 0.7:  # Approaching limit
                    cluster_factor = 0.7
        
        adjustment = heat_factor * cluster_factor
        
        return float(np.clip(adjustment, 0.3, 1.0))  # Min 30%, max 100%
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> HeatOutput:
        """Return neutral output when calculation fails"""
        return HeatOutput(
            allow_trade=False,
            adjusted_size_multiplier=0.5,
            correlation_clusters=[],
            max_correlated_exposure=self.max_correlated_exposure,
            current_heat=0.5,
            risk_budget_used=0.5,
            venue_exposure={},
            reason_codes=["Heat calculation failed, defaulting to deny"],
            components={},
            timestamp=datetime.now(),
            bar_id=bar_id
        )
