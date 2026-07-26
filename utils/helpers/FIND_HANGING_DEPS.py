import sys
import subprocess

SUSPECTS = [
    "EXECUTION_SAFETY_SYSTEM",
    "CAPITAL_DEADLOCK_PREVENTION",
    "COMPOUND_LOOP_PROOF_SYSTEM",
    "EVENT_BASED_PROFIT_TRACER",
    "ADAPTIVE_ENGINE_HARDENING",
    "critical_features_addon",
    "ULTRA_GOLDMINE_FEATURES",
    "EVOLUTION_ENGINE",
    "INTELLIGENT_EXCHANGE_ROUTER"
]

def log(msg):
    print(f"[HANG_HUNTER] {msg}")

def test_module(module_name):
    # Python script to run in subprocess
    script = f"try:\n    import {module_name}\n    print('SUCCESS')\nexcept Exception as e:\n    print(f'ERROR: {{e}}')"
    
    try:
        # Run with 3 second timeout
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=3
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if "SUCCESS" in output:
            return True, "CLEAN"
        else:
            return False, f"IMPORT ERROR: {stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "HANGS (DIRTY)"
    except Exception as e:
        return False, f"EXCEPTION: {e}"

def run_hunt():
    log("Hunting for hanging dependencies...")
    
    dirty_count = 0
    
    for mod in SUSPECTS:
        log(f"Testing {mod}...")
        success, msg = test_module(mod)
        if success:
            log(f"[OK] {mod}: {msg}")
        else:
            log(f"[X] {mod}: {msg}")
            if "HANGS" in msg:
                dirty_count += 1
                
    if dirty_count == 0:
        log("No hanging dependencies found in suspects list.")
    else:
        log(f"Found {dirty_count} hanging modules.")

if __name__ == "__main__":
    run_hunt()
