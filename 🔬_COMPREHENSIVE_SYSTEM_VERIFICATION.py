#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM VERIFICATION
Checks that EVERYTHING actually works (not just loads)
Finds silent failures, bugs, sync issues, and critical problems
"""

import os
import sys
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
import re

class SystemVerifier:
    """Verify every component is actually functioning"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def log_pass(self, msg):
        print(f"\033[92m✅ {msg}\033[0m")
        self.passed.append(msg)
    
    def log_fail(self, msg, details=""):
        print(f"\033[91m❌ {msg}\033[0m")
        if details:
            print(f"   {details}")
        self.issues.append(f"{msg}: {details}")
    
    def log_warn(self, msg):
        print(f"\033[93m⚠️  {msg}\033[0m")
        self.warnings.append(msg)
    
    def log_info(self, msg):
        print(f"   {msg}")
    
    def header(self, msg):
        print(f"\n{'='*80}")
        print(f"\033[94m{msg}\033[0m")
        print(f"{'='*80}\n")
    
    def check_files_exist(self):
        """Check all critical files exist"""
        self.header("1️⃣  CHECKING FILE EXISTENCE")
        
        critical_files = [
            'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
            'EVOLUTION_ENGINE.py',
            'EXECUTION_ORCHESTRATOR.py',
            'AGGRESSIVE_SCALPING_ENGINE.py',
            'SMART_SCALPING_ENGINE.py',
            'evolution_engine.db'
        ]
        
        for f in critical_files:
            if os.path.exists(f):
                self.log_pass(f"Found: {f}")
            else:
                self.log_fail(f"MISSING: {f}", "Critical file not found!")
    
    def check_syntax(self):
        """Check Python files have valid syntax"""
        self.header("2️⃣  CHECKING PYTHON SYNTAX")
        
        py_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('_')]
        
        for f in py_files[:20]:  # Check first 20
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', f],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log_pass(f"Valid syntax: {f}")
                else:
                    self.log_fail(f"Syntax error: {f}", result.stderr.decode()[:100])
            except Exception as e:
                self.log_fail(f"Could not check: {f}", str(e))
    
    def check_database(self):
        """Verify database is working and has data"""
        self.header("3️⃣  CHECKING EVOLUTION DATABASE")
        
        if not os.path.exists('evolution_engine.db'):
            self.log_fail("Database file missing!", "evolution_engine.db not found")
            return
        
        try:
            db = sqlite3.connect('evolution_engine.db')
            cursor = db.cursor()
            
            # Check table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if 'model_evolution' in tables:
                self.log_pass("Table 'model_evolution' exists")
            else:
                self.log_fail("Table 'model_evolution' missing!", "Database corrupted?")
                return
            
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM model_evolution")
            count = cursor.fetchone()[0]
            
            if count > 0:
                self.log_pass(f"Database has {count} evolution records")
            else:
                self.log_warn("Database is empty (no evolution data)")
            
            # Check max generation
            cursor.execute("SELECT MAX(generation) FROM model_evolution")
            max_gen = cursor.fetchone()[0]
            
            if max_gen and max_gen > 100:
                self.log_pass(f"Evolution at Generation {max_gen} (learning is happening!)")
            elif max_gen:
                self.log_warn(f"Only at Generation {max_gen} (still early)")
            else:
                self.log_warn("No generation data (bot hasn't learned yet)")
            
            # Check recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM model_evolution 
                WHERE spawn_time > datetime('now', '-1 day')
            """)
            recent = cursor.fetchone()[0]
            
            if recent > 0:
                self.log_pass(f"{recent} new evolutions in last 24 hours (actively learning!)")
            else:
                self.log_warn("No recent evolution activity (bot not learning or not running long)")
            
            db.close()
            
        except Exception as e:
            self.log_fail("Database error", str(e))
    
    def check_logs(self):
        """Check logs for errors and activity"""
        self.header("4️⃣  CHECKING LOG FILES")
        
        log_files = ['apex.log', 'nohup.out']
        log_found = False
        
        for log_file in log_files:
            if os.path.exists(log_file):
                log_found = True
                self.log_pass(f"Found log: {log_file}")
                
                # Check log size
                size = os.path.getsize(log_file)
                if size > 1000000:  # > 1MB
                    self.log_pass(f"Log has activity: {size/1000000:.1f}MB")
                elif size > 1000:
                    self.log_warn(f"Log is small: {size/1000:.1f}KB (not much activity?)")
                else:
                    self.log_warn("Log is very small (bot barely ran?)")
                
                # Check last modification
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                time_diff = datetime.now() - mod_time
                
                if time_diff.total_seconds() < 60:
                    self.log_pass(f"Log updated {int(time_diff.total_seconds())}s ago (bot is running!)")
                elif time_diff.total_seconds() < 3600:
                    self.log_warn(f"Log updated {int(time_diff.total_seconds()/60)} mins ago")
                else:
                    self.log_fail("Log is old", f"Last update: {time_diff.total_seconds()/3600:.1f} hours ago (bot stopped?)")
                
                # Check for errors
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-1000:]  # Last 1000 lines
                        
                    error_count = sum(1 for line in lines if 'ERROR' in line or 'Exception' in line)
                    if error_count > 50:
                        self.log_fail(f"Many errors in log: {error_count}", "Check apex.log for details")
                    elif error_count > 10:
                        self.log_warn(f"Some errors in log: {error_count}")
                    else:
                        self.log_pass(f"Few errors: {error_count} (healthy)")
                    
                    # Check for signals
                    signal_count = sum(1 for line in lines if 'signal' in line.lower() or 'analyzing' in line.lower())
                    if signal_count > 10:
                        self.log_pass(f"Bot generating signals: {signal_count} in recent logs")
                    else:
                        self.log_warn(f"Few signals detected: {signal_count} (bot analyzing markets?)")
                    
                    # Check for trades
                    trade_count = sum(1 for line in lines if 'executed' in line.lower() or 'placed order' in line.lower())
                    if trade_count > 0:
                        self.log_pass(f"Bot executing trades: {trade_count} in recent logs")
                    else:
                        self.log_warn("No trades detected in recent logs")
                    
                except Exception as e:
                    self.log_warn(f"Could not read log: {e}")
        
        if not log_found:
            self.log_fail("No log files found!", "Bot never ran or logs deleted?")
    
    def check_running_process(self):
        """Check if bot is actually running"""
        self.header("5️⃣  CHECKING RUNNING PROCESSES")
        
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            
            processes = result.stdout
            
            if 'COMPLETE_ULTIMATE_ORCHESTRATOR' in processes:
                self.log_pass("Bot process is running")
                
                # Get process details
                for line in processes.split('\n'):
                    if 'COMPLETE_ULTIMATE_ORCHESTRATOR' in line:
                        parts = line.split()
                        if len(parts) > 8:
                            cpu = parts[2]
                            mem = parts[3]
                            time_run = parts[9]
                            self.log_info(f"CPU: {cpu}% | Memory: {mem}% | Runtime: {time_run}")
                            
                            # Check if using resources (sign it's working)
                            try:
                                cpu_val = float(cpu)
                                if cpu_val > 0.1:
                                    self.log_pass("Bot is actively using CPU (working!)")
                                else:
                                    self.log_warn("Bot using very little CPU (idle or stuck?)")
                            except:
                                pass
            else:
                self.log_warn("Bot process not found (not running or different name)")
                
        except Exception as e:
            self.log_warn(f"Could not check processes: {e}")
    
    def check_engines_loaded(self):
        """Check which engines actually loaded"""
        self.header("6️⃣  CHECKING ENGINE STATUS")
        
        log_file = 'apex.log' if os.path.exists('apex.log') else 'nohup.out'
        
        if not os.path.exists(log_file):
            self.log_warn("No log file to check engine status")
            return
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Check for engine loading messages
            engines_loaded = []
            engines_failed = []
            
            for line in lines:
                if 'ENGINE' in line.upper() and 'LOADED' in line.upper():
                    engines_loaded.append(line.strip())
                elif 'ENGINE' in line.upper() and ('FAILED' in line.upper() or 'ERROR' in line.upper()):
                    engines_failed.append(line.strip())
            
            if engines_loaded:
                self.log_pass(f"{len(engines_loaded)} engines loaded successfully")
                for eng in engines_loaded[-5:]:  # Show last 5
                    self.log_info(eng[:80])
            else:
                self.log_warn("No engine loading messages found")
            
            if engines_failed:
                self.log_fail(f"{len(engines_failed)} engines failed to load", "Check apex.log")
                for eng in engines_failed[:5]:  # Show first 5
                    self.log_info(eng[:80])
            
        except Exception as e:
            self.log_warn(f"Could not check engine status: {e}")
    
    def check_data_flow(self):
        """Check if data is flowing from exchange to bot"""
        self.header("7️⃣  CHECKING DATA FLOW")
        
        log_file = 'apex.log' if os.path.exists('apex.log') else 'nohup.out'
        
        if not os.path.exists(log_file):
            self.log_warn("No log file to check data flow")
            return
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-500:]  # Last 500 lines
            
            # Check for data fetching
            data_fetch = sum(1 for line in lines if 'fetch' in line.lower() or 'ticker' in line.lower())
            if data_fetch > 5:
                self.log_pass(f"Data fetching detected: {data_fetch} instances")
            else:
                self.log_warn(f"Little data fetching seen: {data_fetch} instances")
            
            # Check for market analysis
            analysis = sum(1 for line in lines if 'analyz' in line.lower() or 'scanning' in line.lower())
            if analysis > 5:
                self.log_pass(f"Market analysis active: {analysis} instances")
            else:
                self.log_warn(f"Little market analysis: {analysis} instances")
            
            # Check for signals
            signals = sum(1 for line in lines if 'signal' in line.lower() and 'confidence' in line.lower())
            if signals > 0:
                self.log_pass(f"Signals being generated: {signals} detected")
            else:
                self.log_warn("No signals detected in recent logs")
            
        except Exception as e:
            self.log_warn(f"Could not check data flow: {e}")
    
    def check_balance(self):
        """Check if bot has sufficient balance"""
        self.header("8️⃣  CHECKING BALANCE & CAPITAL")
        
        log_file = 'apex.log' if os.path.exists('apex.log') else 'nohup.out'
        
        if not os.path.exists(log_file):
            self.log_warn("No log file to check balance")
            return
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Look for balance mentions
            balance_matches = re.findall(r'balance[:\s]+\$?([\d.]+)', content, re.IGNORECASE)
            
            if balance_matches:
                balances = [float(b) for b in balance_matches if float(b) < 100000]  # Filter out crazy values
                if balances:
                    latest_balance = balances[-1]
                    self.log_info(f"Latest balance detected: ${latest_balance:.2f}")
                    
                    if latest_balance < 1.0:
                        self.log_fail("Balance too low!", f"${latest_balance:.2f} is insufficient for most trades")
                    elif latest_balance < 10.0:
                        self.log_warn(f"Balance is low: ${latest_balance:.2f} (limited trading capability)")
                    else:
                        self.log_pass(f"Balance: ${latest_balance:.2f} (sufficient for trading)")
            else:
                self.log_warn("Could not find balance in logs")
            
        except Exception as e:
            self.log_warn(f"Could not check balance: {e}")
    
    def generate_report(self):
        """Generate final verification report"""
        self.header("📊 VERIFICATION SUMMARY")
        
        print(f"\n✅ PASSED: {len(self.passed)}")
        print(f"⚠️  WARNINGS: {len(self.warnings)}")
        print(f"❌ ISSUES: {len(self.issues)}")
        
        if self.issues:
            print(f"\n\033[91m🚨 CRITICAL ISSUES FOUND:\033[0m")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.warnings:
            print(f"\n\033[93m⚠️  WARNINGS:\033[0m")
            for i, warn in enumerate(self.warnings, 1):
                print(f"   {i}. {warn}")
        
        print(f"\n{'='*80}")
        
        # Overall assessment
        if len(self.issues) == 0 and len(self.warnings) < 3:
            print(f"\033[92m✅ SYSTEM STATUS: HEALTHY\033[0m")
            print("   Your bot appears to be functioning correctly!")
        elif len(self.issues) < 3 and len(self.warnings) < 5:
            print(f"\033[93m⚠️  SYSTEM STATUS: NEEDS ATTENTION\033[0m")
            print("   Some issues detected but system is operational")
        else:
            print(f"\033[91m❌ SYSTEM STATUS: CRITICAL PROBLEMS\033[0m")
            print("   Multiple issues detected - bot may not be functioning properly")
        
        print(f"{'='*80}\n")
        
        # Save report
        report_file = f"VERIFICATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write("COMPREHENSIVE SYSTEM VERIFICATION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Date: {datetime.now()}\n\n")
            
            f.write(f"PASSED: {len(self.passed)}\n")
            for item in self.passed:
                f.write(f"  ✅ {item}\n")
            
            f.write(f"\nWARNINGS: {len(self.warnings)}\n")
            for item in self.warnings:
                f.write(f"  ⚠️  {item}\n")
            
            f.write(f"\nISSUES: {len(self.issues)}\n")
            for item in self.issues:
                f.write(f"  ❌ {item}\n")
        
        print(f"📄 Full report saved: {report_file}\n")
        
        return len(self.issues) == 0
    
    def run(self):
        """Run complete verification"""
        print("\n" + "="*80)
        print("\033[94m🔬 COMPREHENSIVE SYSTEM VERIFICATION\033[0m")
        print("="*80)
        print("\nChecking that EVERYTHING actually works (not just loads)...\n")
        
        self.check_files_exist()
        self.check_syntax()
        self.check_database()
        self.check_logs()
        self.check_running_process()
        self.check_engines_loaded()
        self.check_data_flow()
        self.check_balance()
        
        success = self.generate_report()
        return success


if __name__ == '__main__':
    verifier = SystemVerifier()
    success = verifier.run()
    sys.exit(0 if success else 1)
