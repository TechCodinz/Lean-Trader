#!/usr/bin/env python3
"""
Restore the PROFITABLE sizing configuration (8-15% aggressive)
"""

print("🔧 Restoring profitable aggressive sizing...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the sizing code we just added (2-5%)
if 'size_pct = min(0.05, max(0.02, confidence * 0.08))' in content:
    print("[OK] Found conservative sizing (2-5%)")
    print()
    print("Replacing with PROFITABLE aggressive sizing (8-15%)...")
    
    # Replace with aggressive sizing
    content = content.replace(
        'size_pct = min(0.05, max(0.02, confidence * 0.08))  # 2-5% based on confidence',
        'size_pct = min(0.15, max(0.08, confidence * 0.15))  # 8-15% based on confidence (PROFITABLE CONFIG)'
    )
    
    print("[OK] Changed: 2-5% → 8-15%")
    print()
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("=" * 70)
    print("[OK] RESTORED PROFITABLE CONFIGURATION")
    print("=" * 70)
    print()
    print("Sizing logic:")
    print("  • Base: 8-15% of balance (aggressive)")
    print("  • Scales with confidence (0.6 default)")
    print("  • High confidence = larger positions")
    print("  • Low confidence = smaller positions")
    print()
    print("With $50 balance:")
    print("  • Min position: $4 (8% at low confidence)")
    print("  • Avg position: $5.50 (11% at 0.6 confidence)")
    print("  • Max position: $7.50 (15% at high confidence)")
    print()
    print("This is the PROFITABLE config that grew $50 → $63!")
    
else:
    print("  Could not find expected sizing code")

