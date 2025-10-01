#!/usr/bin/env python3
"""
Production Readiness Checker for Ultra Trading Bot
Checks for common issues that could cause problems in production
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ProductionChecker:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
    def check_all(self):
        """Run all checks"""
        print("🔍 PRODUCTION READINESS CHECKER")
        print("=" * 60)
        
        self.check_hardcoded_credentials()
        self.check_infinite_loops()
        self.check_bare_excepts()
        self.check_sql_injection()
        self.check_rate_limiting()
        self.check_order_validation()
        self.check_websocket_reconnection()
        self.check_memory_leaks()
        self.check_file_handles()
        self.check_threading_issues()
        
        self.print_report()
        
    def check_hardcoded_credentials(self):
        """Check for hardcoded API keys, passwords, etc."""
        print("\n📋 Checking for hardcoded credentials...")
        
        patterns = [
            (r'api[_]?key\s*=\s*["\'][A-Za-z0-9]{10,}["\']', 'API key'),
            (r'secret\s*=\s*["\'][A-Za-z0-9]{10,}["\']', 'Secret'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Password'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{10,}["\']', 'Token')
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            if 'test' in str(py_file) or 'example' in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for pattern, cred_type in patterns:
                    if 'getenv' not in content and 'environ' not in content:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if 'example' not in match.lower() and 'your_' not in match.lower():
                                self.issues['critical'].append(
                                    f"Hardcoded {cred_type} in {py_file}: {match[:50]}..."
                                )
            except:
                pass
                
    def check_infinite_loops(self):
        """Check for while True loops without breaks"""
        print("📋 Checking for infinite loops...")
        
        count = 0
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Look for while True without break
                if 'while True:' in content or 'while 1:' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'while True:' in line or 'while 1:' in line:
                            # Check next 20 lines for break
                            has_break = False
                            for j in range(i+1, min(i+20, len(lines))):
                                if 'break' in lines[j]:
                                    has_break = True
                                    break
                            if not has_break:
                                count += 1
                                self.issues['medium'].append(
                                    f"Possible infinite loop without break in {py_file} line {i+1}"
                                )
            except:
                pass
                
        print(f"  Found {count} potential infinite loops")
        
    def check_bare_excepts(self):
        """Check for bare except clauses"""
        print("📋 Checking for bare except clauses...")
        
        count = 0
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.match(r'^\s*except:\s*$', line):
                        count += 1
                        self.issues['medium'].append(
                            f"Bare except in {py_file} line {i+1}"
                        )
            except:
                pass
                
        print(f"  Found {count} bare except clauses")
        
    def check_sql_injection(self):
        """Check for potential SQL injection vulnerabilities"""
        print("📋 Checking for SQL injection risks...")
        
        patterns = [
            r'execute\s*\(\s*["\'].*%s.*["\']',  # String formatting in SQL
            r'execute\s*\(\s*f["\']',  # f-strings in SQL
            r'execute\s*\([^,]+\+',  # String concatenation in SQL
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    if re.search(pattern, content):
                        self.issues['high'].append(
                            f"Potential SQL injection in {py_file}"
                        )
            except:
                pass
                
    def check_rate_limiting(self):
        """Check if rate limiting is implemented"""
        print("📋 Checking for rate limiting...")
        
        has_rate_limit = False
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if 'rate_limit' in content.lower() or 'ratelimit' in content.lower():
                    has_rate_limit = True
                    break
            except:
                pass
                
        if not has_rate_limit:
            self.issues['high'].append(
                "No rate limiting implementation found - risk of API bans"
            )
            
    def check_order_validation(self):
        """Check for order validation logic"""
        print("📋 Checking for order validation...")
        
        validations = {
            'min_order_size': False,
            'price_precision': False,
            'balance_check': False,
            'symbol_validation': False
        }
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if 'min_order' in content.lower() or 'minimum_order' in content.lower():
                    validations['min_order_size'] = True
                if 'precision' in content.lower() or 'decimal' in content.lower():
                    validations['price_precision'] = True
                if 'balance' in content.lower() and 'check' in content.lower():
                    validations['balance_check'] = True
                if 'symbol' in content.lower() and 'valid' in content.lower():
                    validations['symbol_validation'] = True
            except:
                pass
                
        for check, found in validations.items():
            if not found:
                self.issues['high'].append(
                    f"Missing {check} validation"
                )
                
    def check_websocket_reconnection(self):
        """Check for WebSocket reconnection logic"""
        print("📋 Checking for WebSocket reconnection...")
        
        has_websocket = False
        has_reconnect = False
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if 'websocket' in content.lower():
                    has_websocket = True
                if 'reconnect' in content.lower():
                    has_reconnect = True
            except:
                pass
                
        if has_websocket and not has_reconnect:
            self.issues['high'].append(
                "WebSocket usage found but no reconnection logic"
            )
            
    def check_memory_leaks(self):
        """Check for potential memory leaks"""
        print("📋 Checking for memory leaks...")
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Check for unbounded lists
                if '.append(' in content and 'maxlen' not in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '.append(' in line and 'while True' in content:
                            self.issues['medium'].append(
                                f"Potential memory leak (unbounded list) in {py_file}"
                            )
                            break
            except:
                pass
                
    def check_file_handles(self):
        """Check for unclosed file handles"""
        print("📋 Checking for unclosed file handles...")
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Check for open() without with statement
                if 'open(' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'open(' in line and 'with' not in line:
                            # Check if close() is called
                            has_close = False
                            for j in range(i+1, min(i+10, len(lines))):
                                if '.close()' in lines[j]:
                                    has_close = True
                                    break
                            if not has_close:
                                self.issues['medium'].append(
                                    f"Potential unclosed file handle in {py_file} line {i+1}"
                                )
            except:
                pass
                
    def check_threading_issues(self):
        """Check for threading without locks"""
        print("📋 Checking for threading issues...")
        
        for py_file in self.root_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if 'Thread' in content or 'threading' in content:
                    if 'Lock' not in content and 'lock' not in content:
                        self.issues['medium'].append(
                            f"Threading without locks in {py_file}"
                        )
            except:
                pass
                
    def print_report(self):
        """Print the final report"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS REPORT")
        print("=" * 60)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("✅ No major issues found!")
            return
            
        # Print issues by severity
        if self.issues['critical']:
            print("\n🔴 CRITICAL ISSUES (Fix immediately!):")
            for issue in self.issues['critical']:
                print(f"  ❌ {issue}")
                
        if self.issues['high']:
            print("\n🟠 HIGH PRIORITY ISSUES:")
            for issue in self.issues['high']:
                print(f"  ⚠️ {issue}")
                
        if self.issues['medium']:
            print("\n🟡 MEDIUM PRIORITY ISSUES:")
            for issue in self.issues['medium'][:5]:  # Show first 5
                print(f"  ⚠️ {issue}")
            if len(self.issues['medium']) > 5:
                print(f"  ... and {len(self.issues['medium']) - 5} more")
                
        if self.issues['low']:
            print("\n🟢 LOW PRIORITY ISSUES:")
            for issue in self.issues['low'][:3]:  # Show first 3
                print(f"  ℹ️ {issue}")
                
        # Summary
        print("\n" + "=" * 60)
        print("📈 SUMMARY:")
        print(f"  Critical: {len(self.issues['critical'])}")
        print(f"  High: {len(self.issues['high'])}")
        print(f"  Medium: {len(self.issues['medium'])}")
        print(f"  Low: {len(self.issues['low'])}")
        print(f"  Total: {total_issues}")
        
        if self.issues['critical']:
            print("\n⛔ DO NOT DEPLOY TO PRODUCTION until critical issues are fixed!")
        elif self.issues['high']:
            print("\n⚠️ Fix high priority issues before production deployment")
        else:
            print("\n✅ No critical issues, but review medium priority items")

if __name__ == "__main__":
    checker = ProductionChecker()
    checker.check_all()
    
    # Exit with error code if critical issues found
    if checker.issues['critical']:
        sys.exit(1)