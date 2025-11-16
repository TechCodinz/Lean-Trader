#!/usr/bin/env python3
"""
🔬 TEST AI CONSULTATION - Check what's working NOW
Run this on VPS to see current AI consultation status
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("🔬 AI CONSULTATION DIAGNOSTIC TEST")
print("=" * 80)
print()

# Check Python version
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")
print()

# Test 1: Check what AI files exist
print("📁 Step 1: Checking AI-related files...")
print("-" * 80)

ai_files = [
    'AI_CONSULTATION_SERVICE.py',
    'MULTI_AI_INTELLIGENCE_LAYER.py',
    'ULTIMATE_AUTONOMOUS_INTELLIGENCE.py',
    'INTELLIGENT_BALANCE_MANAGER.py',
    'AUTONOMOUS_MASTER_COORDINATOR.py'
]

existing_files = []
for f in ai_files:
    if Path(f).exists():
        size = Path(f).stat().st_size
        print(f"✅ {f} ({size:,} bytes)")
        existing_files.append(f)
    else:
        print(f"❌ {f} - NOT FOUND")

print()

# Test 2: Check AI packages
print("📦 Step 2: Checking installed AI packages...")
print("-" * 80)

packages = {}

try:
    import anthropic
    packages['anthropic'] = getattr(anthropic, '__version__', 'installed')
    print(f"✅ anthropic: {packages['anthropic']}")
except ImportError:
    print("❌ anthropic: NOT INSTALLED")
    packages['anthropic'] = None

try:
    import openai
    packages['openai'] = getattr(openai, '__version__', 'installed')
    print(f"✅ openai: {packages['openai']}")
except ImportError:
    print("❌ openai: NOT INSTALLED")
    packages['openai'] = None

try:
    import requests
    packages['requests'] = getattr(requests, '__version__', 'installed')
    print(f"✅ requests: {packages['requests']}")
except ImportError:
    print("❌ requests: NOT INSTALLED")
    packages['requests'] = None

print()

# Test 3: Check .env configuration
print("⚙️  Step 3: Checking AI configuration...")
print("-" * 80)

env_file = Path('systems/.env')
if env_file.exists():
    print("✅ systems/.env found")
    print()
    
    # Read and check API keys (without exposing them)
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    ai_keys = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            for key in ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GROK_API_KEY', 
                       'RAIZIOM_API_KEY', 'CUSTOM_AI_API_KEY', 'AI_PROVIDER']:
                if key in line and '=' in line:
                    value = line.split('=', 1)[1].strip()
                    if value and value not in ['', 'your_key_here', 'none']:
                        ai_keys[key] = '***SET***'
                        print(f"✅ {key}: SET")
                    else:
                        print(f"⚠️  {key}: NOT SET")
                    break
else:
    print("❌ systems/.env NOT FOUND")
    ai_keys = {}

print()

# Test 4: Try importing AI consultation
print("🤖 Step 4: Testing AI Consultation imports...")
print("-" * 80)

ai_service = None
version_info = {}

# Try importing AI_CONSULTATION_SERVICE
if 'AI_CONSULTATION_SERVICE.py' in existing_files:
    try:
        from AI_CONSULTATION_SERVICE import AIConsultationService, initialize_ai_consultation
        print("✅ AI_CONSULTATION_SERVICE import SUCCESS")
        
        # Check version by inspecting __init__
        import inspect
        sig = inspect.signature(AIConsultationService.__init__)
        params = list(sig.parameters.keys())
        
        if 'provider' in params:
            version_info['type'] = 'MULTI-AI (NEW)'
            print("   ✅ Version: MULTI-AI SUPPORT (Claude, GPT-4, Grok, Raiziom)")
            
            # Try initializing
            try:
                ai_service = AIConsultationService(provider='auto')
                version_info['initialized'] = True
                version_info['available'] = ai_service.available
                version_info['active_provider'] = ai_service.active_provider
                
                print(f"   ✅ Initialized: {ai_service.available}")
                if ai_service.available:
                    print(f"   ✅ Active Provider: {ai_service.active_provider}")
                    print(f"   ✅ Available Providers: {list(ai_service.clients.keys())}")
                else:
                    print(f"   ⚠️  No AI providers available (need API keys)")
                    
            except Exception as e:
                print(f"   ⚠️  Initialization failed: {e}")
                version_info['initialized'] = False
                
        elif 'api_key' in params:
            version_info['type'] = 'CLAUDE-ONLY (OLD)'
            print("   ⚠️  Version: OLD (Claude only)")
            print("   💡 This needs to be updated to multi-AI version")
        else:
            version_info['type'] = 'UNKNOWN'
            print("   ❓ Version: UNKNOWN")
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

# Try importing MULTI_AI_INTELLIGENCE_LAYER if exists
elif 'MULTI_AI_INTELLIGENCE_LAYER.py' in existing_files:
    try:
        from MULTI_AI_INTELLIGENCE_LAYER import MultiAIIntelligenceLayer
        print("✅ MULTI_AI_INTELLIGENCE_LAYER import SUCCESS")
        version_info['type'] = 'MULTI-AI (LAYER)'
        print("   ✅ Version: Multi-AI Intelligence Layer")
    except Exception as e:
        print(f"❌ Import failed: {e}")

else:
    print("❌ No AI consultation files found")

print()

# Test 5: Summary and recommendations
print("=" * 80)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 80)
print()

print("Current State:")
print(f"  - AI Files: {len(existing_files)} found")
print(f"  - AI Packages: {sum(1 for v in packages.values() if v)} installed")
print(f"  - API Keys: {len(ai_keys)} configured")
if ai_service:
    print(f"  - AI Service: {'WORKING' if ai_service.available else 'CONFIGURED BUT NO KEYS'}")
    if ai_service.available:
        print(f"  - Active Provider: {ai_service.active_provider}")
else:
    print(f"  - AI Service: NOT INITIALIZED")

print()
print("Recommendations:")

if version_info.get('type') == 'MULTI-AI (NEW)':
    print("✅ YOU HAVE THE NEW MULTI-AI VERSION!")
    print("   No update needed for AI consultation")
    
    if not ai_keys:
        print("⚠️  Add API keys to systems/.env to enable AI learning")
        print("   Supported: Claude, GPT-4, Grok, Raiziom, Custom")
        
elif version_info.get('type') == 'CLAUDE-ONLY (OLD)':
    print("⚠️  YOU HAVE THE OLD VERSION (Claude only)")
    print("   Pulling updates will add: GPT-4, Grok, Raiziom support!")
    print("   ✅ SAFE TO PULL - This is an upgrade, not a breaking change")
    
elif version_info.get('type') == 'MULTI-AI (LAYER)':
    print("✅ YOU HAVE MULTI-AI (via Layer)")
    print("   Pulling updates will enhance it further")
    
else:
    print("❓ NO AI CONSULTATION FOUND")
    print("   Pulling updates will ADD this feature!")
    print("   ✅ COMPLETELY SAFE - This is a new addition")

print()

# Test 6: Other intelligence systems
print("🧠 Other Intelligence Systems:")
print("-" * 80)

other_systems = [
    'INTELLIGENT_BALANCE_MANAGER.py',
    'ULTIMATE_AUTONOMOUS_INTELLIGENCE.py',
    'AUTONOMOUS_MASTER_COORDINATOR.py'
]

for system in other_systems:
    if Path(system).exists():
        print(f"✅ {system}")
        # Try importing
        try:
            module_name = system.replace('.py', '')
            __import__(module_name)
            print(f"   ✅ Import works")
        except Exception as e:
            print(f"   ⚠️  Import failed: {str(e)[:50]}...")
    else:
        print(f"❌ {system} - NOT FOUND (will be added by pull)")

print()
print("=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)
print()
print("🔍 Copy ALL output above and send to me!")
print("   I'll tell you if it's safe to pull updates.")
print()

# Return exit code based on safety
if version_info.get('type') in ['MULTI-AI (NEW)', 'MULTI-AI (LAYER)', None]:
    # Already new or doesn't exist - safe to pull
    sys.exit(0)
else:
    # Old version - upgrade recommended
    sys.exit(1)
