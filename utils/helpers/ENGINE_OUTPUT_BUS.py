#!/usr/bin/env python3
"""
ENGINE_OUTPUT_BUS.py
Central bus for ALL engine outputs - enforces consumption
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class EngineOutput:
    """Single engine output"""
    engine_name: str
    bar_id: Optional[int]
    timestamp: datetime
    output_data: Any
    output_type: str
    consumed: bool = False
    consumed_by: List[str] = field(default_factory=list)

class EngineOutputBus:
    """
    CENTRAL BUS FOR ALL ENGINE OUTPUTS
    Stores outputs and enforces consumption rules
    """
    
    def __init__(self):
        self.outputs: Dict[str, List[EngineOutput]] = defaultdict(list)
        self.consumption_required = set()  # Engines that MUST be consumed
        self.current_bar_id = 0
        
        logger.info("🚌 EngineOutputBus initialized")
    
    def register_required_consumption(self, engine_names: List[str]):
        """Register engines whose outputs MUST be consumed"""
        self.consumption_required.update(engine_names)
        logger.info(f"Registered {len(engine_names)} engines requiring output consumption")
    
    def publish(self, engine_name: str, output_data: Any, output_type: str = "general"):
        """Publish engine output to bus"""
        output = EngineOutput(
            engine_name=engine_name,
            bar_id=self.current_bar_id,
            timestamp=datetime.now(),
            output_data=output_data,
            output_type=output_type
        )
        
        self.outputs[engine_name].append(output)
        
        # Keep only last 100 outputs per engine
        if len(self.outputs[engine_name]) > 100:
            self.outputs[engine_name] = self.outputs[engine_name][-100:]
        
        logger.debug(f"Published: {engine_name} → {output_type}")
    
    def consume(self, engine_name: str, consumer_name: str, bar_id: Optional[int] = None) -> Optional[Any]:
        """Consume output from specific engine"""
        if engine_name not in self.outputs or not self.outputs[engine_name]:
            return None
        
        # Get output for specific bar or latest
        if bar_id is not None:
            for output in reversed(self.outputs[engine_name]):
                if output.bar_id == bar_id:
                    output.consumed = True
                    output.consumed_by.append(consumer_name)
                    return output.output_data
        else:
            # Get latest
            output = self.outputs[engine_name][-1]
            output.consumed = True
            output.consumed_by.append(consumer_name)
            return output.output_data
        
        return None
    
    def get_latest(self, engine_name: str) -> Optional[Any]:
        """Get latest output without marking as consumed"""
        if engine_name not in self.outputs or not self.outputs[engine_name]:
            return None
        return self.outputs[engine_name][-1].output_data
    
    def verify_consumption(self) -> Dict[str, bool]:
        """Verify all required outputs were consumed"""
        results = {}
        
        for engine_name in self.consumption_required:
            if engine_name not in self.outputs or not self.outputs[engine_name]:
                results[engine_name] = False  # No output produced
                continue
            
            # Check if latest output was consumed
            latest = self.outputs[engine_name][-1]
            results[engine_name] = latest.consumed
        
        return results
    
    def get_unconsumed_count(self) -> int:
        """Get count of required outputs not consumed"""
        verification = self.verify_consumption()
        return sum(1 for consumed in verification.values() if not consumed)
    
    def next_bar(self):
        """Move to next bar/cycle"""
        self.current_bar_id += 1

# Global bus
_bus = None

def get_output_bus() -> EngineOutputBus:
    """Get global output bus"""
    global _bus
    if _bus is None:
        _bus = EngineOutputBus()
    return _bus

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    bus = get_output_bus()
    bus.register_required_consumption(['engine1', 'engine2'])
    
    bus.publish('engine1', {'signal': 'BUY'}, 'signal')
    bus.publish('engine2', {'risk': 0.02}, 'risk')
    
    # Consume
    signal = bus.consume('engine1', 'strategy_blender')
    risk = bus.consume('engine2', 'execution_engine')
    
    print(f"Consumed signal: {signal}")
    print(f"Consumed risk: {risk}")
    print(f"Verification: {bus.verify_consumption()}")
    print(f"Unconsumed: {bus.get_unconsumed_count()}")
