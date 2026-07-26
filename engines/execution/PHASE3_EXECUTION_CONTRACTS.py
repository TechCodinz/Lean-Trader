#!/usr/bin/env python3
"""
PHASE3_EXECUTION_CONTRACTS.py
Create contracts that MUST be met for each engine execution
"""

import json
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class ExecutionContract:
    """Contract that must be met for engine execution"""
    engine_name: str
    must_run_in_states: List[str]
    must_not_run_in_states: List[str]
    required_inputs_present: bool
    required_input_fields: List[str]
    expected_output_type: str
    expected_output_not_null: bool
    max_skip_tolerance: int
    contract_description: str

class ContractGenerator:
    """Phase 3: Generate execution contracts"""
    
    def __init__(self, profiles_path: str, states_path: str):
        # Load functional profiles
        with open(profiles_path) as f:
            data = json.load(f)
            self.profiles = data['profiles']
        
        # Load state assignments
        with open(states_path) as f:
            data = json.load(f)
            self.state_assignments = data['assignments']
        
        self.contracts = {}
    
    def create_contract(self, engine_name: str) -> ExecutionContract:
        """Create execution contract for one engine"""
        
        profile = self.profiles[engine_name]
        state_assignment = self.state_assignments[engine_name]
        
        # Must run in these states
        must_run_in = state_assignment['valid_states']
        
        # Must NOT run in these states
        must_not_run = state_assignment['invalid_states']
        
        # Required inputs
        critical_inputs = profile['critical_inputs']
        required_inputs_present = len(critical_inputs) > 0
        
        # Expected output
        expected_outputs = profile['expected_outputs']
        if expected_outputs:
            output_type = expected_outputs[0] if expected_outputs else "Dict"
        else:
            output_type = "Dict"  # Default
        
        # Skip tolerance (0 for critical engines)
        category = profile['category']
        if category in ['execution', 'signal_generation', 'detection']:
            max_skip = 0  # MUST execute every time
        elif category in ['learning', 'optimization']:
            max_skip = 10  # Can skip a few cycles
        else:
            max_skip = 5  # Moderate tolerance
        
        # Contract description
        description = f"{engine_name} must execute in {', '.join(must_run_in[:2])} states"
        if required_inputs_present:
            description += f" with inputs: {', '.join(critical_inputs[:3])}"
        description += f". Output: {output_type}. Max skip: {max_skip}"
        
        return ExecutionContract(
            engine_name=engine_name,
            must_run_in_states=must_run_in,
            must_not_run_in_states=must_not_run,
            required_inputs_present=required_inputs_present,
            required_input_fields=critical_inputs,
            expected_output_type=output_type,
            expected_output_not_null=True,  # All outputs must be non-null
            max_skip_tolerance=max_skip,
            contract_description=description
        )
    
    def generate_all_contracts(self):
        """Generate contracts for all engines"""
        print(f"Generating execution contracts for {len(self.profiles)} engines...")
        
        for i, engine_name in enumerate(self.profiles.keys(), 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(self.profiles)}")
            
            contract = self.create_contract(engine_name)
            self.contracts[engine_name] = contract
        
        print(f"[OK] Generated {len(self.contracts)} execution contracts")
    
    def get_contract_stats(self) -> Dict:
        """Get statistics about contracts"""
        stats = {
            'zero_skip_tolerance': 0,
            'requires_inputs': 0,
            'multi_state_engines': 0
        }
        
        for contract in self.contracts.values():
            if contract.max_skip_tolerance == 0:
                stats['zero_skip_tolerance'] += 1
            if contract.required_inputs_present:
                stats['requires_inputs'] += 1
            if len(contract.must_run_in_states) > 1:
                stats['multi_state_engines'] += 1
        
        return stats
    
    def save_contracts(self, filename: str = "ENGINE_EXECUTION_CONTRACTS.json"):
        """Save contracts to JSON"""
        data = {
            'total_contracts': len(self.contracts),
            'contract_stats': self.get_contract_stats(),
            'contracts': {name: asdict(contract) for name, contract in self.contracts.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[OK] Saved execution contracts: {filename}")
        
        # Print summary
        stats = data['contract_stats']
        print("\nContract Statistics:")
        print(f"  Zero skip tolerance (must execute): {stats['zero_skip_tolerance']}")
        print(f"  Require inputs: {stats['requires_inputs']}")
        print(f"  Multi-state engines: {stats['multi_state_engines']}")

def main():
    generator = ContractGenerator(
        'ENGINE_FUNCTIONAL_PROFILES.json',
        'ENGINE_STATE_MODEL.json'
    )
    generator.generate_all_contracts()
    generator.save_contracts()
    
    print("\n[OK] PHASE 3 COMPLETE: Execution Contracts")
    print(f"   All {len(generator.contracts)} contracts defined")
    print("\nProceed to Phase 4: State-Aware Orchestrator")

if __name__ == "__main__":
    main()
