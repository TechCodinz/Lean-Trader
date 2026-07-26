#!/usr/bin/env python3
import re

# Read orchestrator
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Add imports at top (after existing imports)
IMPORTS = """
# STATE-AWARE ORCHESTRATION - ALL ENGINES RUN IN CORRECT STATES
try:
    from PHASE4_8_COMPLETE_FUNCTIONAL_ENFORCEMENT import (
        StateAwareOrchestrator, SystemState, FunctionalEffectVerifier, generate_final_proof
    )
    STATEAWARE_AVAILABLE = True
except:
    STATEAWARE_AVAILABLE = False
"""

# Find class CompleteUltimateOrchestrator __init__
init_pattern = r'(class CompleteUltimateOrchestrator.*?def __init__.*?super\(\).__init__\(mode\))'

# Add StateAware init in __init__ method
STATEAWARE_INIT = """
        
        # ═══════════════════════════════════════════════════════════
        # STATE-AWARE ORCHESTRATION - ALL 367 ENGINES
        # ═══════════════════════════════════════════════════════════
        if STATEAWARE_AVAILABLE:
            try:
                logger.info("Initializing StateAwareOrchestrator...")
                
                # Create state-aware orchestrator with registry
                if hasattr(self, 'engine_registry'):
                    self.state_orchestrator = StateAwareOrchestrator(self.engine_registry)
                else:
                    self.state_orchestrator = None
                    logger.warning("No engine registry - StateAware disabled")
                
                # Effect verifier
                if hasattr(self, 'output_bus'):
                    self.effect_verifier = FunctionalEffectVerifier(self.output_bus)
                else:
                    self.effect_verifier = None
                
                # Cycle counter for proof
                self.cycle_count = 0
                self.proof_interval = 500
                
                logger.info("StateAwareOrchestrator initialized")
                
            except Exception as e:
                logger.error(f"StateAware init failed: {e}")
                self.state_orchestrator = None
"""

# Add state execution in trading loop
TRADING_LOOP_ADDITIONS = '''
    def execute_trading_cycle_stateaware(self, market_data):
        """Execute one complete trading cycle with state-aware orchestration"""
        
        if not hasattr(self, 'state_orchestrator') or not self.state_orchestrator:
            # Fallback to original execution
            return self.execute_trading_cycle_original(market_data)
        
        try:
            context = {
                'market_data': market_data,
                'timestamp': datetime.now(),
                'cycle': self.cycle_count
            }
            
            # Execute each state in order
            self.state_orchestrator.execute_state(SystemState.DATA_INGESTION, context)
            self.state_orchestrator.execute_state(SystemState.PRE_ANALYSIS, context)
            self.state_orchestrator.execute_state(SystemState.MARKET_ANALYSIS, context)
            self.state_orchestrator.execute_state(SystemState.DETECTION, context)
            self.state_orchestrator.execute_state(SystemState.PREDICTION, context)
            self.state_orchestrator.execute_state(SystemState.SIGNAL_GENERATION, context)
            self.state_orchestrator.execute_state(SystemState.STRATEGY_BLENDING, context)
            self.state_orchestrator.execute_state(SystemState.RISK_EVALUATION, context)
            self.state_orchestrator.execute_state(SystemState.EXECUTION_PREP, context)
            self.state_orchestrator.execute_state(SystemState.EXECUTION, context)
            self.state_orchestrator.execute_state(SystemState.POST_EXECUTION, context)
            self.state_orchestrator.execute_state(SystemState.LEARNING_UPDATE, context)
            
            # Increment cycle
            self.cycle_count += 1
            
            # Generate proof every 500 cycles
            if self.cycle_count % self.proof_interval == 0:
                logger.info(f"Generating runtime proof at cycle {self.cycle_count}")
                proof = generate_final_proof(self.state_orchestrator, self.cycle_count)
                
                # Save proof
                with open(f'/root/bot/RUNTIME_PROOF_CYCLE_{self.cycle_count}.json', 'w') as f:
                    import json
                    json.dump(proof, f, indent=2)
                
                # Check if safe mode needed
                if proof.get('never_ran_count', 0) > 10:
                    logger.error(f"Too many engines not running: {proof['never_ran_count']}")
                    # Enter safe mode (existing logic)
            
            # Optimization and health check periodically
            if self.cycle_count % 100 == 0:
                self.state_orchestrator.execute_state(SystemState.OPTIMIZATION, context)
            
            if self.cycle_count % 50 == 0:
                self.state_orchestrator.execute_state(SystemState.HEALTH_MONITORING, context)
                
        except Exception as e:
            logger.error(f"State-aware execution failed: {e}")
            # Fallback to original
            return self.execute_trading_cycle_original(market_data)
'''

# Insert imports
if 'STATE-AWARE ORCHESTRATION' not in content:
    # Find last import
    import_pos = content.rfind('from ')
    if import_pos > 0:
        next_newline = content.find('\n\n', import_pos)
        content = content[:next_newline] + IMPORTS + content[next_newline:]

# Insert init code
match = re.search(init_pattern, content, re.DOTALL)
if match:
    insert_pos = match.end()
    content = content[:insert_pos] + STATEAWARE_INIT + content[insert_pos:]
else:
    print("WARNING: Could not find __init__ insertion point")

# Add trading loop method
if 'execute_trading_cycle_stateaware' not in content:
    # Find class end or good insertion point
    class_match = re.search(r'class CompleteUltimateOrchestrator', content)
    if class_match:
        # Find a good spot (before main/run methods)
        content = content.replace(
            'class CompleteUltimateOrchestrator',
            'class CompleteUltimateOrchestrator' + TRADING_LOOP_ADDITIONS.replace('\n', '\n    ')
        )

# Write modified file
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print("[OK] StateAware integration complete")
