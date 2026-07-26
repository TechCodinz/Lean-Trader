#!/usr/bin/env python3
"""
SIGNAL_COALESCENCE_ENGINE.py

Phase 7.4: Multi-Engine Signal Coalescence
Merges compatible signals to reduce execution overhead while preserving attribution
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class CoalescedSignal:
    """Merged signal from multiple engines"""
    symbol: str
    direction: str  # 'LONG' or 'SHORT'
    merged_at: float
    source_signals: List[Dict] = field(default_factory=list)
    source_engines: List[str] = field(default_factory=list)
    
    # Merged properties
    combined_confidence: float = 0.0
    combined_size: float = 0.0
    entry_price: float = 0.0
    
    # Attribution
    attribution: Dict[str, float] = field(default_factory=dict)  # {engine: size}
    
    def to_dict(self):
        """Convert to dict for execution"""
        return {
            'symbol': self.symbol,
            'direction': self.direction,
            'side': self.direction,
            'confidence': self.combined_confidence,
            'size': self.combined_size,
            'entry': self.entry_price,
            'price': self.entry_price,
            'coalesced': True,
            'source_engines': self.source_engines,
            'attribution': self.attribution,
            'timestamp': self.merged_at
        }

class SignalCoalescenceEngine:
    """
    Phase 7.4: Intelligent Signal Coalescence
    
    Merges compatible signals to reduce execution overhead:
    - Same symbol + direction + close timestamps → ONE execution
    - Preserves per-engine attribution for PnL
    - NO signal suppression - all engines remain active
    """
    
    def __init__(self, coalescence_window_ms=500):
        self.window_ms = coalescence_window_ms
        self.merged_log = []
        
    def can_coalesce(self, sig1: Dict, sig2: Dict) -> bool:
        """Check if two signals are compatible for merging"""
        # Same symbol
        sym1 = sig1.get('symbol') or sig1.get('pair')
        sym2 = sig2.get('symbol') or sig2.get('pair')
        if sym1 != sym2:
            return False
        
        # Same direction
        dir1 = str(sig1.get('direction', sig1.get('side', ''))).upper()
        dir2 = str(sig2.get('direction', sig2.get('side', ''))).upper()
        
        # Normalize BUY/SELL to LONG/SHORT
        if 'BUY' in dir1:
            dir1 = 'LONG'
        elif 'SELL' in dir1:
            dir1 = 'SHORT'
        if 'BUY' in dir2:
            dir2 = 'LONG'
        elif 'SELL' in dir2:
            dir2 = 'SHORT'
            
        if dir1 != dir2:
            return False
        
        # Close timestamps (within coalescence window)
        time1 = sig1.get('timestamp', sig1.get('time', datetime.now().timestamp()))
        time2 = sig2.get('timestamp', sig2.get('time', datetime.now().timestamp()))
        if abs(time1 - time2) > self.window_ms / 1000:
            return False
        
        return True
    
    def merge_signals(self, signals: List[Dict]) -> CoalescedSignal:
        """Merge compatible signals into one"""
        if not signals:
            return None
        
        base = signals[0]
        symbol = base.get('symbol') or base.get('pair', 'UNKNOWN')
        direction = str(base.get('direction', base.get('side', 'LONG'))).upper()
        
        # Normalize direction
        if 'BUY' in direction:
            direction = 'LONG'
        elif 'SELL' in direction:
            direction = 'SHORT'
        
        coalesced = CoalescedSignal(
            symbol=symbol,
            direction=direction,
            merged_at=datetime.now().timestamp(),
            source_signals=signals,
            source_engines=[s.get('strategy', s.get('engine', 'unknown')) for s in signals]
        )
        
        # Merge confidence (weighted average)
        confidences = [s.get('confidence', 0.5) for s in signals]
        coalesced.combined_confidence = sum(confidences) / len(confidences)
        
        # Merge sizing (sum - each engine contributes)
        sizes = [s.get('size', 5.0) for s in signals]
        coalesced.combined_size = sum(sizes)
        
        # Entry price (average of all)
        prices = [s.get('entry', s.get('price', 0)) for s in signals]
        prices = [p for p in prices if p and p > 0]
        coalesced.entry_price = sum(prices) / len(prices) if prices else 0
        
        # Attribution tracking
        for sig in signals:
            engine = sig.get('strategy', sig.get('engine', 'unknown'))
            size = sig.get('size', 5.0)
            coalesced.attribution[engine] = coalesced.attribution.get(engine, 0) + size
        
        # Log merge
        merge_record = {
            'timestamp': coalesced.merged_at,
            'symbol': coalesced.symbol,
            'direction': coalesced.direction,
            'engines': coalesced.source_engines,
            'original_count': len(signals),
            'combined_confidence': coalesced.combined_confidence,
            'combined_size': coalesced.combined_size
        }
        self.merged_log.append(merge_record)
        
        logger.info(f"   🔗 COALESCED: {len(signals)} signals for {symbol} {direction} → 1 execution")
        
        return coalesced
    
    def coalesce_batch(self, signals: List[Dict]) -> List[CoalescedSignal]:
        """
        Coalesce a batch of signals
        
        Returns: List of coalesced signals (some may be single-engine)
        """
        if not signals:
            return []
        
        # Group compatible signals
        groups = []
        processed = set()
        
        for i, sig1 in enumerate(signals):
            if i in processed:
                continue
            
            group = [sig1]
            processed.add(i)
            
            # Find all compatible signals
            for j in range(i+1, len(signals)):
                if j in processed:
                    continue
                
                sig2 = signals[j]
                if self.can_coalesce(sig1, sig2):
                    group.append(sig2)
                    processed.add(j)
            
            groups.append(group)
        
        # Merge each group
        coalesced = []
        for group in groups:
            merged = self.merge_signals(group)
            if merged:
                coalesced.append(merged)
        
        if len(coalesced) < len(signals):
            logger.info(f"   🔗 COALESCENCE: {len(signals)} signals → {len(coalesced)} merged ({len(signals)-len(coalesced)} reduced)")
        
        return coalesced
    
    def get_merged_log(self):
        """Get coalescence log for reporting"""
        return self.merged_log
    
    def save_merged_log(self, filepath='/root/bot/logs/merged_signals.json'):
        """Save coalescence log to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.merged_log, f, indent=2)
            logger.info(f"   📊 Saved {len(self.merged_log)} merge records to {filepath}")
        except Exception as e:
            logger.warning(f"Could not save merged log: {e}")
