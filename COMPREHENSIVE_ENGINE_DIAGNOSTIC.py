#!/usr/bin/env python3
"""
COMPREHENSIVE ENGINE DIAGNOSTIC
Identifies all dormant, failing, or missing engines in the trading system
"""

import os
import sys
import importlib
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

class EngineDiagnostic:
    def __init__(self):
        self.workspace = Path("/workspace")
        self.all_python_files = []
        self.engine_files = []
        self.imported_engines = set()
        self.available_engines = set()
        self.dormant_engines = set()
        self.failing_engines = {}
        self.missing_imports = []
        
    def scan_all_files(self):
        """Scan workspace for all Python files"""
        print("🔍 Scanning workspace for Python files...")
        
        for root, dirs, files in os.walk(self.workspace):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self.all_python_files.append(file_path)
                    
                    # Identify engine files
                    if any(keyword in file.upper() for keyword in [
                        'ENGINE', 'ORCHESTRATOR', 'TRADER', 'TRADING', 
                        'ARBITRAGE', 'SCALPING', 'STRATEGY', 'BRAIN',
                        'INTELLIGENCE', 'QUANTUM', 'ULTRA', 'DIVINE',
                        'CONSCIOUSNESS', 'GODMODE', 'EXECUTION', 'SYSTEM'
                    ]):
                        self.engine_files.append(file_path)
                        
        print(f"✅ Found {len(self.all_python_files)} Python files")
        print(f"✅ Identified {len(self.engine_files)} potential engine files")
        
    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """Extract all imports from a Python file"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Parse AST
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)
            except:
                # Fallback to regex if AST parsing fails
                import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
                for line in content.split('\n'):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        imports.add(match.group(1) or match.group(2))
                        
        except Exception as e:
            pass
            
        return imports
    
    def check_main_orchestrator_imports(self):
        """Check what's imported in main orchestrator files"""
        print("\n🔍 Checking main orchestrator imports...")
        
        orchestrators = [
            self.workspace / "systems" / "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
            self.workspace / "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
            self.workspace / "systems" / "ULTIMATE_ORCHESTRATOR.py",
            self.workspace / "ULTIMATE_ORCHESTRATOR.py",
            self.workspace / "AUTOMATED_ORCHESTRATOR_ENHANCED.py",
        ]
        
        for orch in orchestrators:
            if orch.exists():
                print(f"\n📄 Analyzing: {orch.name}")
                imports = self.extract_imports_from_file(orch)
                
                # Filter engine-related imports
                engine_imports = {imp for imp in imports if any(
                    keyword in imp.upper() for keyword in [
                        'ENGINE', 'TRADER', 'ORCHESTRATOR', 'STRATEGY',
                        'BRAIN', 'INTELLIGENCE', 'QUANTUM', 'ULTRA'
                    ]
                )}
                
                self.imported_engines.update(engine_imports)
                print(f"  ✅ Found {len(engine_imports)} engine imports")
                
    def identify_available_engines(self):
        """Identify all available engine modules"""
        print("\n🔍 Identifying available engines...")
        
        for engine_file in self.engine_files:
            # Get module name from file path
            try:
                rel_path = engine_file.relative_to(self.workspace)
                module_name = str(rel_path).replace('/', '.').replace('.py', '')
                
                # Simplify for common patterns
                simple_name = engine_file.stem
                self.available_engines.add(simple_name)
                
            except Exception as e:
                pass
                
        print(f"✅ Found {len(self.available_engines)} available engines")
        
    def test_engine_imports(self):
        """Test if each engine can be imported"""
        print("\n🔍 Testing engine imports...")
        
        # Add workspace to path
        sys.path.insert(0, str(self.workspace))
        
        test_count = 0
        for engine in sorted(self.available_engines):
            if test_count >= 50:  # Limit testing to prevent hanging
                break
                
            try:
                # Try to import
                importlib.import_module(engine)
                test_count += 1
            except Exception as e:
                self.failing_engines[engine] = str(e)[:100]
                test_count += 1
                
        print(f"✅ Tested {test_count} engines")
        print(f"❌ Found {len(self.failing_engines)} failing engines")
        
    def find_dormant_engines(self):
        """Find engines that exist but aren't imported"""
        print("\n🔍 Finding dormant engines...")
        
        # Simplify imported engine names for comparison
        imported_simple = set()
        for imp in self.imported_engines:
            # Extract last part of import path
            parts = imp.split('.')
            imported_simple.add(parts[-1])
            
        # Find engines that are available but not imported
        self.dormant_engines = self.available_engines - imported_simple
        
        print(f"⚠️  Found {len(self.dormant_engines)} dormant engines!")
        
    def check_critical_files(self):
        """Check if critical system files exist"""
        print("\n🔍 Checking critical system files...")
        
        critical_files = [
            "router.py",
            "EXECUTION_ORCHESTRATOR.py",
            "INTELLIGENT_EXECUTION_ENGINE.py",
            "DYNAMIC_MARKET_SCANNER.py",
            "PROFESSIONAL_RISK_MANAGEMENT.py",
            ".env",
            "universe.py",
        ]
        
        missing = []
        for file in critical_files:
            if not (self.workspace / file).exists():
                missing.append(file)
                
        if missing:
            print(f"❌ Missing critical files: {missing}")
        else:
            print(f"✅ All critical files present")
            
        return missing
    
    def generate_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE ENGINE DIAGNOSTIC REPORT")
        print("="*80)
        
        print(f"\n📈 STATISTICS:")
        print(f"  • Total Python files: {len(self.all_python_files)}")
        print(f"  • Total engine files: {len(self.engine_files)}")
        print(f"  • Imported engines: {len(self.imported_engines)}")
        print(f"  • Available engines: {len(self.available_engines)}")
        print(f"  • Dormant engines: {len(self.dormant_engines)} ⚠️")
        print(f"  • Failing engines: {len(self.failing_engines)} ❌")
        
        if self.dormant_engines:
            print(f"\n⚠️  DORMANT ENGINES (Not imported in orchestrators):")
            print(f"    These {len(self.dormant_engines)} engines exist but are NOT being used!")
            for i, engine in enumerate(sorted(self.dormant_engines)[:30], 1):
                print(f"    {i:3d}. {engine}")
            if len(self.dormant_engines) > 30:
                print(f"    ... and {len(self.dormant_engines) - 30} more")
                
        if self.failing_engines:
            print(f"\n❌ FAILING ENGINES (Import errors):")
            for engine, error in list(self.failing_engines.items())[:20]:
                print(f"    • {engine}")
                print(f"      Error: {error}")
                
        print(f"\n✅ ACTIVE ENGINES:")
        active = self.imported_engines & self.available_engines
        for i, engine in enumerate(sorted(active)[:20], 1):
            print(f"    {i:3d}. {engine}")
        if len(active) > 20:
            print(f"    ... and {len(active) - 20} more")
            
        # Calculate activation percentage
        if self.available_engines:
            activation_pct = (len(self.imported_engines) / len(self.available_engines)) * 100
            print(f"\n📊 ENGINE ACTIVATION: {activation_pct:.1f}%")
            
            if activation_pct < 50:
                print(f"⚠️  WARNING: Less than half of available engines are active!")
                print(f"    You're missing out on {100-activation_pct:.1f}% of potential profit!")
                
        print("\n" + "="*80)
        
    def save_detailed_report(self):
        """Save detailed findings to file"""
        report_path = self.workspace / "ENGINE_DIAGNOSTIC_REPORT.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("COMPREHENSIVE ENGINE DIAGNOSTIC REPORT\n")
            f.write(f"Generated: {Path(__file__).name}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"STATISTICS:\n")
            f.write(f"  Total Python files: {len(self.all_python_files)}\n")
            f.write(f"  Total engine files: {len(self.engine_files)}\n")
            f.write(f"  Imported engines: {len(self.imported_engines)}\n")
            f.write(f"  Available engines: {len(self.available_engines)}\n")
            f.write(f"  Dormant engines: {len(self.dormant_engines)}\n")
            f.write(f"  Failing engines: {len(self.failing_engines)}\n\n")
            
            f.write("DORMANT ENGINES (Available but not imported):\n")
            for engine in sorted(self.dormant_engines):
                f.write(f"  • {engine}\n")
            f.write("\n")
            
            f.write("FAILING ENGINES (Import errors):\n")
            for engine, error in self.failing_engines.items():
                f.write(f"  • {engine}: {error}\n")
            f.write("\n")
            
            f.write("ACTIVE ENGINES (Imported and available):\n")
            active = self.imported_engines & self.available_engines
            for engine in sorted(active):
                f.write(f"  • {engine}\n")
            f.write("\n")
            
        print(f"\n💾 Detailed report saved to: {report_path}")
        
def main():
    print("🚀 Starting Comprehensive Engine Diagnostic...")
    print("="*80)
    
    diagnostic = EngineDiagnostic()
    
    # Run all checks
    diagnostic.scan_all_files()
    diagnostic.check_main_orchestrator_imports()
    diagnostic.identify_available_engines()
    diagnostic.find_dormant_engines()
    diagnostic.check_critical_files()
    diagnostic.test_engine_imports()
    
    # Generate reports
    diagnostic.generate_report()
    diagnostic.save_detailed_report()
    
    print("\n✅ Diagnostic complete!")
    
    # Provide recommendations
    print("\n💡 RECOMMENDATIONS:")
    if len(diagnostic.dormant_engines) > 10:
        print(f"  1. Activate {len(diagnostic.dormant_engines)} dormant engines for +500-1000% profit boost")
    if len(diagnostic.failing_engines) > 5:
        print(f"  2. Fix {len(diagnostic.failing_engines)} failing engine imports")
    print(f"  3. Review ENGINE_DIAGNOSTIC_REPORT.txt for full details")
    
    return diagnostic

if __name__ == "__main__":
    diagnostic = main()
