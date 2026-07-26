#!/usr/bin/env python3
"""
PHASE2_STATE_MODEL_DEFINITION.py
Define WHEN each engine should execute - state assignments
"""

import json
from typing import Dict, List, Set
from dataclasses import dataclass, asdict

# Define all valid system states
VALID_STATES = [
    'DATA_INGESTION',         # Raw market data arrives
    'PRE_ANALYSIS',           # Initial data processing
    'MARKET_ANALYSIS',        # Technical/fundamental analysis
    'WAVE_FLOW',              # Wave/Flow/Pitch evaluation
    'PITCH_EVALUATION',       # Pitch-specific logic
    'SIGNAL_GENERATION',      # Trade signal creation
    'INTENT_DETECTION',       # Market intent analysis
    'STRATEGY_BLENDING',      # Combine multiple strategies
    'RISK_EVALUATION',        # Risk assessment
    'EXECUTION_PREP',         # Pre-execution checks
    'EXECUTION',              # Trade execution
    'POST_EXECUTION',         # After trade placed
    'LEARNING_UPDATE',        # Update models/memory
    'OPTIMIZATION',           # Parameter tuning
    'HEALTH_MONITORING'       # System health checks
]

@dataclass
class StateAssignment:
    """State assignment for one engine"""
    engine_name: str
    valid_states: List[str]
    invalid_states: List[str]
    primary_state: str
    state_justification: str

class StateModelDefiner:
    """Phase 2: Define when each engine should execute"""
    
    def __init__(self, profiles_path: str):
        # Load functional profiles
        with open(profiles_path) as f:
            data = json.load(f)
            self.profiles = data['profiles']
        
        self.state_assignments = {}
    
    def assign_states(self, engine_name: str, profile: Dict) -> StateAssignment:
        """Assign valid/invalid states for one engine"""
        
        category = profile['category']
        intent = profile['functional_intent'].lower()
        required_states = profile['required_state']
        exec_freq = profile['execution_frequency']
        
        # Determine valid states based on functional profile
        valid_states = set()
        
        # Category-based state assignment
        if category == 'detection':
            valid_states.update(['PRE_ANALYSIS', 'MARKET_ANALYSIS', 'INTENT_DETECTION'])
        elif category == 'analysis':
            valid_states.update(['MARKET_ANALYSIS', 'PRE_ANALYSIS'])
        elif category == 'signal_generation':
            valid_states.update(['SIGNAL_GENERATION', 'STRATEGY_BLENDING'])
        elif category == 'execution':
            valid_states.update(['EXECUTION_PREP', 'EXECUTION', 'POST_EXECUTION'])
        elif category == 'learning':
            valid_states.update(['LEARNING_UPDATE', 'POST_EXECUTION'])
        elif category == 'prediction':
            valid_states.update(['MARKET_ANALYSIS', 'SIGNAL_GENERATION'])
        elif category == 'optimization':
            valid_states.update(['OPTIMIZATION'])
        
        # Intent-based refinement
        if 'wave' in intent or 'flow' in intent:
            valid_states.add('WAVE_FLOW')
        if 'pitch' in intent:
            valid_states.add('PITCH_EVALUATION')
        if 'data' in intent or 'ingest' in intent:
            valid_states.add('DATA_INGESTION')
        if 'risk' in intent:
            valid_states.add('RISK_EVALUATION')
        if 'intent' in intent:
            valid_states.add('INTENT_DETECTION')
        if 'health' in intent or 'monitor' in intent:
            valid_states.add('HEALTH_MONITORING')
        if 'blend' in intent or 'strategy' in intent:
            valid_states.add('STRATEGY_BLENDING')
        
        # Add from required_state field
        valid_states.update(required_states)
        
        # If no states assigned, default based on execution frequency
        if not valid_states:
            if exec_freq == 'per_tick':
                valid_states.add('DATA_INGESTION')
            elif exec_freq == 'per_bar':
                valid_states.add('MARKET_ANALYSIS')
            elif exec_freq == 'per_trade':
                valid_states.add('POST_EXECUTION')
            else:
                valid_states.add('MARKET_ANALYSIS')  # Safe default
        
        valid_states_list = sorted(list(valid_states))
        primary_state = valid_states_list[0]
        
        # Determine invalid states (all others)
        invalid_states = [s for s in VALID_STATES if s not in valid_states]
        
        # Justification
        justification = f"{category.upper()} engine; runs in {', '.join(valid_states_list[:3])}"
        
        return StateAssignment(
            engine_name=engine_name,
            valid_states=valid_states_list,
            invalid_states=invalid_states,
            primary_state=primary_state,
            state_justification=justification
        )
    
    def assign_all_states(self):
        """Assign states for all engines"""
        print(f"Assigning states for {len(self.profiles)} engines...")
        
        for i, (engine_name, profile) in enumerate(self.profiles.items(), 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(self.profiles)}")
            
            assignment = self.assign_states(engine_name, profile)
            self.state_assignments[engine_name] = assignment
        
        print(f"[OK] Assigned states for {len(self.state_assignments)} engines")
    
    def generate_state_stats(self) -> Dict:
        """Generate statistics about state assignments"""
        stats = {state: 0 for state in VALID_STATES}
        
        for assignment in self.state_assignments.values():
            for state in assignment.valid_states:
                stats[state] += 1
        
        return stats
    
    def save_state_model(self, filename: str = "ENGINE_STATE_MODEL.json"):
        """Save state model to JSON"""
        data = {
            'valid_states': VALID_STATES,
            'total_engines': len(self.state_assignments),
            'state_statistics': self.generate_state_stats(),
            'assignments': {name: asdict(assignment) for name, assignment in self.state_assignments.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[OK] Saved state model: {filename}")
        
        # Print summary
        print("\nState Assignment Summary:")
        stats = data['state_statistics']
        for state, count in sorted(stats.items(), key=lambda x: -x[1])[:10]:
            print(f"  {state}: {count} engines")

def main():
    definer = StateModelDefiner('ENGINE_FUNCTIONAL_PROFILES.json')
    definer.assign_all_states()
    definer.save_state_model()
    
    print("\n[OK] PHASE 2 COMPLETE: State Model Definition")
    print(f"   All {len(definer.state_assignments)} engines assigned to states")
    print("\nProceed to Phase 3: Execution Contracts")

if __name__ == "__main__":
    main()
