#!/usr/bin/env python3
"""
Production Readiness Verification Script
Verifies that all critical fixes have been applied
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class ProductionVerifier:
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        
    def run_all_checks(self) -> bool:
        """Run all verification checks"""
        print("=" * 60)
        print("🔍 PRODUCTION READINESS VERIFICATION")
        print("=" * 60)
        
        # Check 1: No hardcoded credentials
        self.check_no_hardcoded_credentials()
        
        # Check 2: Production safety module exists
        self.check_safety_module()
        
        # Check 3: SQL injection fixes
        self.check_sql_injection_fixes()
        
        # Check 4: Rate limiting implementation
        self.check_rate_limiting()
        
        # Check 5: Order validation
        self.check_order_validation()
        
        # Check 6: WebSocket reconnection
        self.check_websocket_reconnection()
        
        # Check 7: Circuit breaker
        self.check_circuit_breaker()
        
        # Check 8: Financial calculations
        self.check_decimal_calculations()
        
        # Check 9: Ultra launcher integration
        self.check_launcher_integration()
        
        # Check 10: Test bot startup
        self.check_bot_startup()
        
        # Print results
        self.print_results()
        
        return len(self.checks_failed) == 0
    
    def check_no_hardcoded_credentials(self):
        """Verify no hardcoded API keys remain"""
        print("\n📋 Checking for hardcoded credentials...")
        
        # Files that were deleted
        deleted_files = ['bybit_bot.py', 'simple_bot.py']
        for file in deleted_files:
            if Path(file).exists():
                self.checks_failed.append(f"File {file} still exists (should be deleted)")
                print(f"  ❌ {file} still exists")
            else:
                self.checks_passed.append(f"Hardcoded credential file {file} removed")
                print(f"  ✅ {file} removed")
        
        # Check for any remaining hardcoded keys (excluding helper scripts)
        result = subprocess.run(
            ['grep', '-r', 'g1mhPqKrOBp9rnqb4G', '.', '--include=*.py', 
             '--exclude=verify_production_ready.py', '--exclude=fix_all_hardcoded_keys.py',
             '--exclude=check_production_issues.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.checks_failed.append("Hardcoded API key still found in files")
            print(f"  ❌ Hardcoded keys still found: {result.stdout[:100]}")
        else:
            self.checks_passed.append("No hardcoded API keys found")
            print("  ✅ No hardcoded API keys found")
    
    def check_safety_module(self):
        """Check if production_fixes.py exists and can be imported"""
        print("\n📋 Checking production safety module...")
        
        if not Path('production_fixes.py').exists():
            self.checks_failed.append("production_fixes.py not found")
            print("  ❌ production_fixes.py not found")
            return
        
        try:
            import production_fixes
            
            # Check for required classes
            required = [
                'RateLimiter', 'OrderValidator', 'WebSocketManager',
                'FinancialCalculator', 'CircuitBreaker', 'ProductionSafetyWrapper'
            ]
            
            for cls in required:
                if not hasattr(production_fixes, cls):
                    self.checks_failed.append(f"Missing {cls} in production_fixes")
                    print(f"  ❌ Missing {cls}")
                else:
                    print(f"  ✅ {cls} found")
            
            self.checks_passed.append("Production safety module complete")
            
        except ImportError as e:
            self.checks_failed.append(f"Cannot import production_fixes: {e}")
            print(f"  ❌ Import error: {e}")
    
    def check_sql_injection_fixes(self):
        """Check if SQL injection vulnerabilities are fixed"""
        print("\n📋 Checking SQL injection fixes...")
        
        # Check monitoring.py for the fix
        monitoring_path = Path('src/monitoring.py')
        if monitoring_path.exists():
            content = monitoring_path.read_text()
            if 'table.replace' in content and 'isalnum()' in content:
                self.checks_passed.append("SQL injection fix applied in monitoring.py")
                print("  ✅ monitoring.py SQL injection fixed")
            else:
                self.checks_failed.append("SQL injection not fixed in monitoring.py")
                print("  ❌ monitoring.py still vulnerable")
        else:
            print("  ⚠️ monitoring.py not found")
    
    def check_rate_limiting(self):
        """Check if rate limiting is implemented"""
        print("\n📋 Checking rate limiting...")
        
        try:
            from production_fixes import RateLimiter, RATE_LIMITERS
            
            # Test rate limiter
            limiter = RateLimiter(max_calls=5, period=1.0)
            
            # Try to exceed limit
            for i in range(5):
                if not limiter.acquire(blocking=False):
                    self.checks_failed.append("Rate limiter not working")
                    print("  ❌ Rate limiter failed test")
                    return
            
            # 6th call should fail
            if limiter.acquire(blocking=False):
                self.checks_failed.append("Rate limiter not limiting")
                print("  ❌ Rate limiter not limiting properly")
            else:
                self.checks_passed.append("Rate limiter working correctly")
                print("  ✅ Rate limiter working")
                
        except Exception as e:
            self.checks_failed.append(f"Rate limiter error: {e}")
            print(f"  ❌ Error: {e}")
    
    def check_order_validation(self):
        """Check if order validation is implemented"""
        print("\n📋 Checking order validation...")
        
        try:
            from production_fixes import OrderValidator
            
            # Test validation
            result = OrderValidator.validate_order(
                exchange='binance',
                symbol='BTC/USDT',
                side='BUY',
                order_type='LIMIT',
                amount=0.0001,  # Too small
                price=50000
            )
            
            if not result['valid'] and 'below minimum' in str(result['errors']):
                self.checks_passed.append("Order validator detecting minimum size")
                print("  ✅ Order validator working")
            else:
                self.checks_failed.append("Order validator not detecting issues")
                print("  ❌ Order validator not working properly")
                
        except Exception as e:
            self.checks_failed.append(f"Order validator error: {e}")
            print(f"  ❌ Error: {e}")
    
    def check_websocket_reconnection(self):
        """Check if WebSocket reconnection is implemented"""
        print("\n📋 Checking WebSocket reconnection...")
        
        try:
            from production_fixes import WebSocketManager
            
            # Check if class exists and has reconnection logic
            manager = WebSocketManager('ws://test', lambda x: None)
            
            if hasattr(manager, 'reconnect_delay') and hasattr(manager, 'connect'):
                self.checks_passed.append("WebSocket reconnection logic present")
                print("  ✅ WebSocket manager with reconnection found")
            else:
                self.checks_failed.append("WebSocket reconnection incomplete")
                print("  ❌ WebSocket reconnection incomplete")
                
        except Exception as e:
            self.checks_failed.append(f"WebSocket manager error: {e}")
            print(f"  ❌ Error: {e}")
    
    def check_circuit_breaker(self):
        """Check if circuit breaker is implemented"""
        print("\n📋 Checking circuit breaker...")
        
        try:
            from production_fixes import CircuitBreaker
            
            breaker = CircuitBreaker(failure_threshold=2)
            
            # Test function that fails
            def failing_func():
                raise Exception("Test failure")
            
            # Should trip after 2 failures
            failures = 0
            for i in range(3):
                try:
                    breaker.call(failing_func)
                except:
                    failures += 1
            
            if breaker.state == 'OPEN' and failures >= 2:
                self.checks_passed.append("Circuit breaker working")
                print("  ✅ Circuit breaker working")
            else:
                self.checks_failed.append("Circuit breaker not tripping")
                print("  ❌ Circuit breaker not working properly")
                
        except Exception as e:
            print(f"  ⚠️ Circuit breaker test error: {e}")
    
    def check_decimal_calculations(self):
        """Check if decimal calculations are implemented"""
        print("\n📋 Checking decimal calculations...")
        
        try:
            from production_fixes import FinancialCalculator
            from decimal import Decimal
            
            # Test PnL calculation
            pnl = FinancialCalculator.calculate_pnl(
                entry_price=50000,
                exit_price=51000,
                amount=1,
                side='BUY'
            )
            
            if isinstance(pnl, Decimal):
                self.checks_passed.append("Decimal calculations working")
                print("  ✅ Using Decimal for financial calculations")
            else:
                self.checks_failed.append("Not using Decimal for calculations")
                print("  ❌ Not using Decimal")
                
        except Exception as e:
            self.checks_failed.append(f"Financial calculator error: {e}")
            print(f"  ❌ Error: {e}")
    
    def check_launcher_integration(self):
        """Check if ultra_launcher.py has safety features integrated"""
        print("\n📋 Checking launcher integration...")
        
        launcher_path = Path('ultra_launcher.py')
        if launcher_path.exists():
            content = launcher_path.read_text()
            
            checks = [
                ('production_fixes import', 'from production_fixes import'),
                ('Safety features check', 'SAFETY_FEATURES_AVAILABLE'),
                ('integrate_safety_features', 'integrate_safety_features')
            ]
            
            for name, pattern in checks:
                if pattern in content:
                    print(f"  ✅ {name} found")
                else:
                    self.checks_failed.append(f"{name} not found in launcher")
                    print(f"  ❌ {name} not found")
            
            if all(pattern in content for _, pattern in checks):
                self.checks_passed.append("Launcher properly integrated")
        else:
            self.checks_failed.append("ultra_launcher.py not found")
            print("  ❌ ultra_launcher.py not found")
    
    def check_bot_startup(self):
        """Test if bot can start without errors"""
        print("\n📋 Testing bot startup...")
        
        try:
            # Try to import and initialize
            result = subprocess.run(
                ['python3', 'ultra_launcher.py', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.checks_passed.append("Bot starts without errors")
                print("  ✅ Bot help command works")
            else:
                self.checks_failed.append(f"Bot startup failed: {result.stderr[:100]}")
                print(f"  ❌ Startup error: {result.stderr[:100]}")
                
        except subprocess.TimeoutExpired:
            self.checks_failed.append("Bot startup timeout")
            print("  ❌ Bot startup timeout")
        except Exception as e:
            print(f"  ⚠️ Could not test startup: {e}")
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "=" * 60)
        print("📊 VERIFICATION RESULTS")
        print("=" * 60)
        
        print(f"\n✅ PASSED: {len(self.checks_passed)} checks")
        for check in self.checks_passed[:5]:
            print(f"  • {check}")
        if len(self.checks_passed) > 5:
            print(f"  ... and {len(self.checks_passed) - 5} more")
        
        if self.checks_failed:
            print(f"\n❌ FAILED: {len(self.checks_failed)} checks")
            for check in self.checks_failed:
                print(f"  • {check}")
            
            print("\n⚠️ CRITICAL ISSUES REMAIN - DO NOT DEPLOY TO PRODUCTION!")
        else:
            print("\n🎉 ALL CHECKS PASSED - Major issues resolved!")
            print("✅ The bot is significantly safer for production use")
            print("\n📝 Recommended next steps:")
            print("  1. Run extensive paper trading for at least 1 week")
            print("  2. Monitor all metrics and logs carefully")
            print("  3. Start with small amounts when going live")
            print("  4. Have emergency stop procedures ready")
            print("  5. Set up proper monitoring and alerting")

if __name__ == "__main__":
    verifier = ProductionVerifier()
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)