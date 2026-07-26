#!/usr/bin/env python3
"""Fix CNS import error in COMPLETE_ULTIMATE_ORCHESTRATOR"""

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

changes = []

# Fix 1: CNS import - wrap in try/except
if "from CENTRAL_NERVOUS_SYSTEM import initialize_cns" in content:
    old = "from CENTRAL_NERVOUS_SYSTEM import initialize_cns"
    new = """try:
    from CENTRAL_NERVOUS_SYSTEM import initialize_cns
except ImportError:
    def initialize_cns():
        return None  # CNS optional, use fallback"""
    
    content = content.replace(old, new)
    changes.append("CNS import wrapped in try/except")

# Fix 2: CNS initialization - make optional
if "initialize_cns()" in content and "CNS initialization failed" not in content:
    old = "self.cns = initialize_cns()"
    new = """try:
            self.cns = initialize_cns()
            if self.cns:
                logger.info("[OK] CNS initialized")
        except Exception as e:
            logger.warning(f"  CNS unavailable: {e}")
            self.cns = None"""
    
    if old in content:
        content = content.replace(old, new)
        changes.append("CNS initialization made optional")

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

for change in changes:
    print(f"[OK] {change}")

if not changes:
    print("ℹ️  CNS already handled or not found")
