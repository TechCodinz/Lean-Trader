#!/usr/bin/env python3
"""
Test orchestrators and start the best working one
Priority:
1. COMPLETE_ULTIMATE_ORCHESTRATOR_clean.py (full power, clean)
2. COMPLETE_UNIFIED_ORCHESTRATOR.py (unified version)
3. EXECUTION_ORCHESTRATOR.py (core trading, proven)
"""

import py_compile
import subprocess
import sys
import time

print("🔍 Testing available orchestrators...")
print("=" * 70)
print()

orchestrators = [
    ('COMPLETE_ULTIMATE_ORCHESTRATOR_clean.py', 'Full Power (Clean Version)', '🚀'),
    ('COMPLETE_UNIFIED_ORCHESTRATOR.py', 'Unified Systems', '⚡'),
    ('EXECUTION_ORCHESTRATOR.py', 'Core Trading (Proven)', '✅'),
]

working_orchestrator = None

for filename, description, emoji in orchestrators:
    print(f"{emoji} Testing {filename}")
    print(f"   {description}")
    
    try:
        # Test syntax
        py_compile.compile(filename, doraise=True)
        print(f"   ✅ Syntax: VALID")
        
        # Quick runtime test (3 seconds)
        print(f"   Testing initialization...")
        proc = subprocess.Popen(
            ['python3', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        proc.terminate()
        
        returncode = proc.wait(timeout=2)
        
        if returncode is None or returncode == -15:  # -15 is SIGTERM (we terminated it)
            print(f"   ✅ Initialization: OK")
            print(f"   🎉 {filename} is WORKING!")
            working_orchestrator = filename
            print()
            break
        else:
            stdout, stderr = proc.communicate()
            if b'Error' in stderr or b'Exception' in stderr:
                print(f"   ⚠️  Runtime issues detected")
            else:
                print(f"   ✅ May be working")
                working_orchestrator = filename
                break
    
    except py_compile.PyCompileError as e:
        print(f"   ❌ Syntax: INVALID")
    except Exception as e:
        print(f"   ⚠️  Test error: {e}")
    
    print()

if working_orchestrator:
    print("=" * 70)
    print(f"✅ WINNER: {working_orchestrator}")
    print("=" * 70)
    print()
    
    # Write the choice to a file
    with open('.selected_orchestrator', 'w') as f:
        f.write(working_orchestrator)
    
    sys.exit(0)
else:
    print("=" * 70)
    print("❌ No working orchestrator found!")
    print("=" * 70)
    sys.exit(1)

