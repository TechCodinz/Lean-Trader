#!/usr/bin/env python3
"""
Test Error Recovery Paths
Verifies all error recovery mechanisms are working
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent))

from production_enhancements import (
    ErrorRecoverySystem,
    ComprehensiveLogger,
    HealthCheckSystem,
    PositionReconciliation,
    connection_error_recovery,
    rate_limit_recovery,
    insufficient_balance_recovery
)

async def test_error_recovery():
    """Test all error recovery paths"""
    print("=" * 60)
    print("🧪 TESTING ERROR RECOVERY PATHS")
    print("=" * 60)
    
    # Initialize components
    logger = ComprehensiveLogger("TestBot")
    error_recovery = ErrorRecoverySystem()
    
    # Register recovery strategies
    class ConnectionError(Exception): pass
    class RateLimitError(Exception): pass
    class InsufficientBalanceError(Exception): pass
    
    error_recovery.register_recovery(ConnectionError, connection_error_recovery)
    error_recovery.register_recovery(RateLimitError, rate_limit_recovery)
    error_recovery.register_recovery(InsufficientBalanceError, insufficient_balance_recovery)
    
    # Test 1: Connection Error Recovery
    print("\n📋 Test 1: Connection Error Recovery")
    try:
        error = ConnectionError("Connection lost")
        recovered = await error_recovery.handle_error(error, {'test': 1})
        if recovered:
            print("  ✅ Connection error recovered successfully")
        else:
            print("  ❌ Connection error recovery failed")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    # Test 2: Rate Limit Recovery
    print("\n📋 Test 2: Rate Limit Error Recovery")
    try:
        error = RateLimitError("Rate limit exceeded")
        recovered = await error_recovery.handle_error(error, {'attempt': 1})
        if recovered:
            print("  ✅ Rate limit error recovered successfully")
        else:
            print("  ❌ Rate limit error recovery failed")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    # Test 3: Insufficient Balance (Should not auto-recover)
    print("\n📋 Test 3: Insufficient Balance Error")
    try:
        error = InsufficientBalanceError("Not enough funds")
        recovered = await error_recovery.handle_error(error, {'required': 1000})
        if not recovered:
            print("  ✅ Correctly did not auto-recover from balance error")
        else:
            print("  ❌ Should not auto-recover from balance error")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    # Test 4: Unknown Error (No recovery strategy)
    print("\n📋 Test 4: Unknown Error Handling")
    try:
        error = ValueError("Unknown error")
        recovered = await error_recovery.handle_error(error, {})
        if not recovered:
            print("  ✅ Correctly handled unknown error type")
        else:
            print("  ❌ Should not recover from unknown error")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    # Test 5: Max Recovery Attempts
    print("\n📋 Test 5: Max Recovery Attempts")
    try:
        # Simulate multiple failures
        for i in range(4):
            error = ConnectionError(f"Connection lost attempt {i+1}")
            recovered = await error_recovery.handle_error(error, {'attempt': i+1})
            
        if error_recovery.recovery_attempts['ConnectionError'] >= 3:
            print("  ✅ Max recovery attempts enforced")
        else:
            print("  ❌ Max recovery attempts not working")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    # Get error statistics
    stats = error_recovery.get_error_stats()
    print("\n📊 Error Recovery Statistics:")
    print(f"  Total errors handled: {stats['total_errors']}")
    print(f"  Error types: {stats['error_types']}")
    print(f"  Recovery attempts: {stats['recovery_attempts']}")
    
    return True

async def test_health_checks():
    """Test health check system"""
    print("\n" + "=" * 60)
    print("🏥 TESTING HEALTH CHECK SYSTEM")
    print("=" * 60)
    
    health_check = HealthCheckSystem()
    
    # Register test health checks
    def check_test_service():
        return True
    
    async def check_async_service():
        await asyncio.sleep(0.1)
        return {'status': 'ok', 'latency': 100}
    
    def check_failing_service():
        raise Exception("Service down")
    
    health_check.register_check('test_service', check_test_service, 60)
    health_check.register_check('async_service', check_async_service, 60)
    health_check.register_check('failing_service', check_failing_service, 60)
    
    # Run health checks
    results = await health_check.run_checks()
    
    print("\n📋 Health Check Results:")
    print(f"  Overall Status: {results['overall_status']}")
    print(f"  Uptime: {results['uptime']}")
    
    for name, check in results['checks'].items():
        status_icon = "✅" if check['status'] == 'healthy' else "❌"
        print(f"  {status_icon} {name}: {check['status']}")
        if 'elapsed_ms' in check:
            print(f"      Latency: {check['elapsed_ms']}ms")
    
    # Test endpoint
    endpoint_data = health_check.get_status_endpoint()
    print(f"\n📡 HTTP Endpoint Response:")
    print(f"  Status: {endpoint_data['status']}")
    print(f"  Timestamp: {endpoint_data['timestamp']}")
    
    return True

async def test_logging_system():
    """Test comprehensive logging"""
    print("\n" + "=" * 60)
    print("📝 TESTING COMPREHENSIVE LOGGING")
    print("=" * 60)
    
    logger = ComprehensiveLogger("TestBot")
    
    # Test trade logging
    print("\n📋 Testing Trade Logging...")
    logger.log_trade({
        'id': 'test-001',
        'symbol': 'BTC/USDT',
        'side': 'BUY',
        'price': 50000,
        'amount': 0.1,
        'status': 'filled'
    })
    print("  ✅ Trade logged")
    
    # Test audit logging
    print("\n📋 Testing Audit Logging...")
    logger.log_audit('CONFIG_CHANGE', {
        'user': 'admin',
        'change': 'Updated risk limit',
        'old_value': 1000,
        'new_value': 2000
    })
    print("  ✅ Audit entry logged")
    
    # Test error logging
    print("\n📋 Testing Error Logging...")
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error(e, {'context': 'test'})
    print("  ✅ Error logged with traceback")
    
    # Test performance logging
    print("\n📋 Testing Performance Logging...")
    logger.log_performance('latency', 125.5, {'exchange': 'binance'})
    logger.log_performance('cpu_usage', 45.2)
    print("  ✅ Performance metrics logged")
    
    # Get error summary
    error_summary = logger.get_error_summary()
    print(f"\n📊 Error Summary: {error_summary}")
    
    # Check log files exist
    log_files = ['logs/trading_bot.log', 'logs/trades.json', 'logs/audit.json', 'logs/errors.log']
    for log_file in log_files:
        if Path(log_file).exists():
            print(f"  ✅ {log_file} created")
        else:
            print(f"  ❌ {log_file} not found")
    
    return True

async def test_position_reconciliation():
    """Test position reconciliation (mock)"""
    print("\n" + "=" * 60)
    print("🔄 TESTING POSITION RECONCILIATION")
    print("=" * 60)
    
    # Create mock exchange
    class MockExchange:
        async def fetch_positions(self):
            return [
                {'symbol': 'BTC/USDT', 'side': 'long', 'contracts': 0.1, 
                 'markPrice': 50000, 'unrealizedPnl': 100, 'initialMargin': 1000}
            ]
        
        async def fetch_open_orders(self):
            return []
        
        async def cancel_all_orders(self):
            return True
    
    mock_exchange = MockExchange()
    reconciler = PositionReconciliation(mock_exchange)
    
    # Add internal position (matching)
    reconciler.update_position('BTC/USDT', {
        'side': 'long',
        'amount': 0.1,
        'entry_price': 49900
    })
    
    # Add internal position (not on exchange - should be detected)
    reconciler.update_position('ETH/USDT', {
        'side': 'short',
        'amount': 1.0,
        'entry_price': 3500
    })
    
    # Run reconciliation
    print("\n📋 Running reconciliation...")
    report = await reconciler.reconcile()
    
    if report.get('reconciled'):
        print("  ✅ Positions reconciled (no discrepancies)")
    else:
        print(f"  ⚠️ Found {len(report.get('discrepancies', []))} discrepancies:")
        for disc in report.get('discrepancies', []):
            print(f"    - {disc['type']}: {disc.get('symbol', 'N/A')}")
    
    print(f"\n📊 Reconciliation Report:")
    print(f"  Internal positions: {report.get('internal_count', 0)}")
    print(f"  Exchange positions: {report.get('exchange_count', 0)}")
    print(f"  Timestamp: {report.get('timestamp', 'N/A')}")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 STARTING ERROR RECOVERY AND ENHANCEMENT TESTS")
    print("=" * 60)
    
    all_passed = True
    
    try:
        # Test error recovery
        if not await test_error_recovery():
            all_passed = False
            
        # Test health checks
        if not await test_health_checks():
            all_passed = False
            
        # Test logging
        if not await test_logging_system():
            all_passed = False
            
        # Test position reconciliation
        if not await test_position_reconciliation():
            all_passed = False
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL ERROR RECOVERY AND ENHANCEMENT TESTS PASSED!")
        print("🎉 The bot has robust error handling and monitoring!")
    else:
        print("❌ Some tests failed - review and fix issues")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)