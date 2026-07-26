#!/usr/bin/env python3
import re

# Read orchestrator
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Find __init__ method of CompleteUltimateOrchestrator class (around line 798)
# Add integration code after super().__init__(mode)

INTEGRATION = """
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPLETE ENGINE ACTIVATION SYSTEM - ALL 367 ENGINES
        # ═══════════════════════════════════════════════════════════════════
        try:
            from CENTRAL_ENGINE_REGISTRY import initialize_all_engines
            from ENGINE_OUTPUT_BUS import get_output_bus
            from ENGINE_EXECUTION_VERIFICATION import get_verifier
            from ENGINE_PROOF_REPORT import EngineProofReport
            
            logger.info("=" * 80)
            logger.info("INITIALIZING COMPLETE ENGINE ACTIVATION SYSTEM")
            logger.info("=" * 80)
            
            # 1. Initialize Engine Registry (ALL 367 engines)
            self.engine_registry = initialize_all_engines()
            logger.info(f"Registry: {len(self.engine_registry.engines)} engines registered")
            
            # 2. Initialize Output Bus
            self.output_bus = get_output_bus()
            
            # Register critical engines for consumption tracking
            critical_engines = [
                'AntiFragilityEngine', 'LiquidityGravityEngine', 'IntentEngine',
                'PortfolioHeatManager', 'EmotionalIntelligenceEngine', 'DivineIntelligenceCore'
            ]
            self.output_bus.register_required_consumption(critical_engines)
            
            # 3. Initialize Execution Verifier
            self.execution_verifier = get_verifier(self.engine_registry)
            
            # Verify all engines ready
            verified = self.execution_verifier.verify_startup()
            logger.info(f"Startup verification: {'PASSED' if verified else 'FAILED'}")
            
            # 4. Initialize Proof Reporter
            self.proof_reporter = EngineProofReport(self.engine_registry, self.output_bus)
            self.proof_cycle_count = 0
            self.proof_interval = 500
            
            logger.info("=" * 80)
            logger.info("ENGINE ACTIVATION SYSTEM READY")
            logger.info(f"{len(self.engine_registry.engines)} engines | Proof every {self.proof_interval} cycles")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Engine activation failed: {e}")
            import traceback
            traceback.print_exc()
            self.engine_registry = None
            self.output_bus = None
"""

# Find the line "super().__init__(mode)" in CompleteUltimateOrchestrator
pattern = r'(class CompleteUltimateOrchestrator.*?\n.*?def __init__.*?\n.*?super\(\).__init__\(mode\))'

match = re.search(pattern, content, re.DOTALL)

if match:
    # Insert integration code after super().__init__(mode)
    insert_pos = match.end()
    content = content[:insert_pos] + INTEGRATION  + content[insert_pos:]
    
    # Write modified file
    with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    
    print("SUCCESS: Integration code added to orchestrator")
else:
    print("ERROR: Could not find insertion point")
    exit(1)

