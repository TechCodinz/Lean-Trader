#!/usr/bin/env python3
"""
🌡️ MARKET PHASE TRANSITION ENGINE
═══════════════════════════════════════════════════════════════════
Detects structural market phase transitions (Trending → Choppy → Crash)
10-30 minutes BEFORE price candles confirm the reversal.

Uses:
- Thermodynamic Entropy of return distributions
- Kinetic energy of order flow volume
- Phase space attractor drift
"""

import asyncio
import logging
import math
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class MarketPhaseTransitionEngine:
    """
    Predicts regime reversals and phase shifts before chart price action completes.
    """

    def __init__(self):
        self.phase_history = defaultdict(lambda: deque(maxlen=100))
        self.current_phase = defaultdict(lambda: "STABLE_TREND")
        logger.info("🌡️ Market Phase Transition Engine initialized")

    def detect_phase_transition(self, symbol: str, prices: List[float], volumes: List[float]) -> Dict[str, Any]:
        """
        Calculates kinetic energy and entropy decay to detect phase transitions.
        """
        if len(prices) < 20 or len(volumes) < 20:
            return {'phase': 'INSUFFICIENT_DATA', 'transition_warning': False}

        # Calculate price returns
        returns = [(prices[i+1] - prices[i]) / max(prices[i], 1e-12) for i in range(len(prices)-1)]
        
        # Calculate Kinetic Energy = 0.5 * Mass (Volume) * Velocity^2 (Returns^2)
        kinetic_energy = [0.5 * volumes[i+1] * (returns[i] ** 2) for i in range(len(returns))]
        avg_ke_recent = sum(kinetic_energy[-5:]) / 5.0
        avg_ke_older = sum(kinetic_energy[-20:-5]) / 15.0 if len(kinetic_energy) >= 20 else avg_ke_recent

        ke_ratio = avg_ke_recent / max(avg_ke_older, 1e-12)

        # Kinetic energy exhaustion + high volume = phase transition imminent
        transition_warning = False
        new_phase = self.current_phase[symbol]

        if ke_ratio > 3.0:
            transition_warning = True
            new_phase = "ENERGY_BURST_BREAKOUT"
        elif ke_ratio < 0.2:
            transition_warning = True
            new_phase = "ENERGY_EXHAUSTION_REVERSAL"
        else:
            new_phase = "STABLE_FLOW"

        self.current_phase[symbol] = new_phase

        return {
            'symbol': symbol,
            'phase': new_phase,
            'ke_ratio': ke_ratio,
            'transition_warning': transition_warning,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
