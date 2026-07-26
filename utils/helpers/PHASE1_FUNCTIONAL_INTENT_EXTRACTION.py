#!/usr/bin/env python3
"""
PHASE1_FUNCTIONAL_INTENT_EXTRACTION.py
Extract functional intent from ALL 367 engines by analyzing code
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class FunctionalProfile:
    """Complete functional profile for one engine"""
    engine_name: str
    file_path: str
    category: str
    functional_intent: str
    required_state: List[str]
    execution_frequency: str
    critical_inputs: List[str]
    expected_outputs: List[str]
    side_effects: List[str]
    method_purposes: Dict[str, str]

class FunctionalIntentExtractor:
    """Phase 1: Extract what each engine ACTUALLY does"""
    
    def __init__(self, inventory_path: str, base_dir: str):
        self.base_dir = Path(base_dir)
        
        # Load inventory
        with open(inventory_path) as f:
            data = json.load(f)
            self.engines = data['engines']
        
        self.profiles = {}
    
    def extract_intent_from_code(self, engine_name: str, file_path: str) -> FunctionalProfile:
        """Extract functional intent by analyzing code"""
        full_path = self.base_dir / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find the class
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == engine_name:
                    class_node = node
                    break
            
            if not class_node:
                return self._create_default_profile(engine_name, file_path)
            
            # Extract docstring
            docstring = ast.get_docstring(class_node) or ""
            
            # Extract methods and their purposes
            method_purposes = {}
            for item in class_node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = ast.get_docstring(item) or ""
                    method_purposes[item.name] = method_doc[:200] if method_doc else f"Method: {item.name}"
            
            # Infer functional intent from docstring and method names
            intent = self._infer_intent(engine_name, docstring, list(method_purposes.keys()))
            
            # Infer required state
            required_state = self._infer_required_state(engine_name, method_purposes)
            
            # Infer execution frequency
            exec_freq = self._infer_execution_frequency(engine_name, method_purposes)
            
            # Infer inputs/outputs from method signatures
            inputs, outputs = self._infer_io(class_node)
            
            # Infer side effects
            side_effects = self._infer_side_effects(engine_name, method_purposes)
            
            return FunctionalProfile(
                engine_name=engine_name,
                file_path=file_path,
                category=self.engines[engine_name].get('category', 'general'),
                functional_intent=intent,
                required_state=required_state,
                execution_frequency=exec_freq,
                critical_inputs=inputs,
                expected_outputs=outputs,
                side_effects=side_effects,
                method_purposes=method_purposes
            )
            
        except Exception as e:
            print(f"Error extracting {engine_name}: {e}")
            return self._create_default_profile(engine_name, file_path)
    
    def _infer_intent(self, name: str, docstring: str, methods: List[str]) -> str:
        """Infer what the engine does"""
        # Use docstring first
        if docstring and len(docstring) > 20:
            return docstring.split('\n')[0][:200]
        
        # Infer from name and methods
        if 'Detector' in name:
            return f"Detects patterns/anomalies in market data"
        elif 'Analyzer' in name:
            return f"Analyzes market conditions and generates insights"
        elif 'Predictor' in name:
            return f"Predicts future market movements"
        elif 'Engine' in name and 'execute' in methods:
            return f"Executes trading logic and generates signals"
        elif 'Manager' in name:
            return f"Manages system resources or state"
        elif 'Optimizer' in name:
            return f"Optimizes parameters or strategies"
        else:
            return f"Provides {name} functionality"
    
    def _infer_required_state(self, name: str, methods: Dict[str, str]) -> List[str]:
        """Infer when engine should run"""
        states = []
        
        # Analysis engines
        if 'Analyz' in name or 'analyze' in str(methods):
            states.append('MARKET_ANALYSIS')
        
        # Detection engines
        if 'Detect' in name or 'detect' in str(methods):
            states.append('PRE_ANALYSIS')
            states.append('MARKET_ANALYSIS')
        
        # Signal generation
        if 'signal' in str(methods).lower() or 'Signal' in name:
            states.append('SIGNAL_GENERATION')
        
        # Execution
        if 'execut' in str(methods).lower() or 'Execute' in name:
            states.append('EXECUTION')
        
        # Learning
        if 'learn' in str(methods).lower() or 'Learn' in name:
            states.append('LEARNING_UPDATE')
        
        # Optimization
        if 'optim' in str(methods).lower() or 'Optim' in name:
            states.append('OPTIMIZATION')
        
        # Default to analysis if unclear
        if not states:
            states.append('MARKET_ANALYSIS')
        
        return states
    
    def _infer_execution_frequency(self, name: str, methods: Dict[str, str]) -> str:
        """Infer how often engine should run"""
        if 'Monitor' in name or 'Health' in name:
            return 'per_session'
        elif 'Scalp' in name or 'Micro' in name:
            return 'per_tick'
        elif 'Signal' in name or 'Strategy' in name:
            return 'per_bar'
        elif 'Learn' in name or 'Optim' in name:
            return 'per_trade'
        else:
            return 'per_bar'  # Default
    
    def _infer_io(self, class_node) -> tuple:
        """Infer inputs and outputs from methods"""
        inputs = set()
        outputs = set()
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                # Check parameters
                for arg in item.args.args:
                    if arg.arg not in ['self', 'cls']:
                        inputs.add(arg.arg)
                
                # Check return type hints
                if item.returns:
                    outputs.add(str(item.returns))
        
        return list(inputs)[:10], list(outputs)[:10]
    
    def _infer_side_effects(self, name: str, methods: Dict[str, str]) -> List[str]:
        """Infer what state changes engine makes"""
        effects = []
        
        if 'update' in str(methods).lower():
            effects.append('Updates internal state')
        if 'save' in str(methods).lower() or 'store' in str(methods).lower():
            effects.append('Persists data')
        if 'publish' in str(methods).lower():
            effects.append('Publishes signals/events')
        if 'learn' in str(methods).lower():
            effects.append('Updates learning models')
        
        return effects if effects else ['Functional computation']
    
    def _create_default_profile(self, engine_name: str, file_path: str) -> FunctionalProfile:
        """Create default profile if extraction fails"""
        return FunctionalProfile(
            engine_name=engine_name,
            file_path=file_path,
            category='general',
            functional_intent=f"{engine_name} - intent extraction failed",
            required_state=['MARKET_ANALYSIS'],
            execution_frequency='per_bar',
            critical_inputs=[],
            expected_outputs=[],
            side_effects=[],
            method_purposes={}
        )
    
    def extract_all(self):
        """Extract profiles for all engines"""
        print(f"Extracting functional profiles for {len(self.engines)} engines...")
        
        for i, (engine_name, metadata) in enumerate(self.engines.items(), 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(self.engines)}")
            
            profile = self.extract_intent_from_code(engine_name, metadata['file_path'])
            self.profiles[engine_name] = profile
        
        print(f"[OK] Extracted {len(self.profiles)} functional profiles")
    
    def save_profiles(self, filename: str = "ENGINE_FUNCTIONAL_PROFILES.json"):
        """Save profiles to JSON"""
        data = {
            'total_engines': len(self.profiles),
            'profiles': {name: asdict(profile) for name, profile in self.profiles.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[OK] Saved profiles: {filename}")

def main():
    base_dir = r"c:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\Lean-Trader-continue-from-micro-fix"
    
    extractor = FunctionalIntentExtractor('COMPLETE_ENGINE_INVENTORY.json', base_dir)
    extractor.extract_all()
    extractor.save_profiles()
    
    print("\n[OK] PHASE 1 COMPLETE: Functional Intent Extraction")
    print(f"   {len(extractor.profiles)} engine profiles created")
    print("\nProceed to Phase 2: State Model Definition")

if __name__ == "__main__":
    main()
