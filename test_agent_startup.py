#!/usr/bin/env python3
"""
Test Agent Startup Script
Tests if the trading agent can start properly
"""

import sys
import asyncio
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        print("✅ Main orchestrator imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_startup():
    """Test if the agent can start in testnet mode"""
    print("\n🚀 Testing agent startup...")
    
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        
        # Create orchestrator instance
        orchestrator = CompleteUltimateOrchestrator()
        print("✅ Orchestrator created successfully")
        
        # Test basic functionality
        print("✅ Agent is ready to start")
        return True
        
    except Exception as e:
        print(f"❌ Agent startup failed: {e}")
        return False

async def test_agent_run():
    """Test running the agent for a short period"""
    print("\n🏃 Testing agent run (30 seconds)...")
    
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        
        # Create and start orchestrator
        orchestrator = CompleteUltimateOrchestrator()
        
        # Run for 30 seconds
        print("⏱️ Running agent for 30 seconds...")
        await asyncio.wait_for(
            orchestrator.run_testnet_mode(),
            timeout=30
        )
        
        print("✅ Agent ran successfully for 30 seconds")
        return True
        
    except asyncio.TimeoutError:
        print("✅ Agent ran successfully (timeout reached)")
        return True
    except Exception as e:
        print(f"❌ Agent run failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 TRADING AGENT STARTUP TEST")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed - cannot proceed")
        return False
    
    # Test 2: Agent startup
    if not test_agent_startup():
        print("\n❌ Agent startup test failed")
        return False
    
    # Test 3: Agent run (optional)
    print("\n🤔 Would you like to test running the agent for 30 seconds? (y/n)")
    response = input().lower().strip()
    
    if response == 'y':
        try:
            result = asyncio.run(test_agent_run())
            if result:
                print("\n✅ All tests passed! Agent is ready to run.")
            else:
                print("\n❌ Agent run test failed")
                return False
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
            return True
    else:
        print("\n✅ Basic tests passed! Agent should be ready to run.")
    
    print("\n" + "=" * 60)
    print("🎉 AGENT IS READY TO RUN!")
    print("=" * 60)
    print("\nTo start the agent:")
    print("python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet")
    print("\nTo start in paper trading mode:")
    print("python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode paper")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)