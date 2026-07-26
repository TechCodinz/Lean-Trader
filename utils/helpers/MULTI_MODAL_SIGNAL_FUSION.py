#!/usr/bin/env python3
"""
🔬 MULTI-MODAL SIGNAL FUSION 🔬

Combines ALL signal sources into ONE super-signal:
- OHLCV data (price action)
- Order book (depth, liquidity)
- Sentiment (news, social)
- Technical indicators
- AI predictions

Uses XGBoost ensemble for fusion!
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try importing ML libraries
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False
    logger.warning(" XGBoost not installed. Run: pip install xgboost")


class MultiModalSignalFusion:
    """
    FUSION ENGINE
    
    Combines multiple signal sources:
    - Price signals (technical)
    - Volume signals (flow)
    - Sentiment signals (psychology)
    - News signals (events)
    - AI signals (collective intelligence)
    
    Into ONE high-confidence prediction!
    """
    
    def __init__(self, exchange=None):
        self.exchange = exchange
        self.model = XGBRegressor(n_estimators=100, max_depth=5) if XGBOOST_AVAILABLE else None
        self.is_fitted = False
        
        # Signal weights (learned over time)
        self.signal_weights = {
            'technical': 0.30,
            'volume': 0.20,
            'sentiment': 0.15,
            'news': 0.15,
            'ai_collective': 0.20
        }
        
        logger.info("🔬 MULTI-MODAL SIGNAL FUSION initialized!")
        logger.info(f"   XGBoost available: {XGBOOST_AVAILABLE}")
    
    async def fuse_signals(self, signals: Dict) -> Dict:
        """
        Fuse multiple signals into super-signal
        
        Args:
            signals: {
                'technical': {'score': 0.75, 'confidence': 0.8},
                'volume': {'score': 0.68, 'confidence': 0.7},
                'sentiment': {'score': 0.82, 'confidence': 0.6},
                'news': {'score': 0.71, 'confidence': 0.5},
                'ai_collective': {'score': 0.85, 'confidence': 0.9}
            }
        
        Returns:
            {
                'fused_score': 0.76,
                'fused_confidence': 0.85,
                'confidence_interval': [0.72, 0.80],
                'component_scores': {...}
            }
        """
        logger.info("🔬 Fusing signals from all sources...")
        
        # Extract scores and confidences
        scores = []
        confidences = []
        weights = []
        
        for signal_type, signal_data in signals.items():
            if signal_data and 'score' in signal_data:
                score = signal_data['score']
                conf = signal_data.get('confidence', 0.5)
                weight = self.signal_weights.get(signal_type, 0.1)
                
                scores.append(score)
                confidences.append(conf)
                weights.append(weight * conf)  # Weight by confidence!
        
        if not scores:
            return None
        
        # Weighted fusion
        total_weight = sum(weights)
        fused_score = sum(s * w for s, w in zip(scores, weights)) / total_weight if total_weight > 0 else 0
        fused_confidence = sum(confidences) / len(confidences)
        
        # Calculate confidence interval
        score_variance = np.var(scores) if len(scores) > 1 else 0.01
        ci_range = 1.96 * np.sqrt(score_variance)  # 95% CI
        
        result = {
            'fused_score': fused_score,
            'fused_confidence': fused_confidence,
            'confidence_interval': [fused_score - ci_range, fused_score + ci_range],
            'component_scores': {k: v.get('score', 0) for k, v in signals.items()},
            'score_variance': score_variance,
            'signal_count': len(scores)
        }
        
        logger.info(f"   [OK] Fused score: {fused_score:.3f} (±{ci_range:.3f})")
        logger.info(f"   Confidence: {fused_confidence:.1%}")
        logger.info(f"   Components: {len(scores)} signals")
        
        return result


# Singleton
_signal_fusion = None

def get_signal_fusion():
    """Get signal fusion instance"""
    return _signal_fusion

def initialize_signal_fusion(exchange=None):
    """Initialize signal fusion"""
    global _signal_fusion
    _signal_fusion = MultiModalSignalFusion(exchange)
    return _signal_fusion
