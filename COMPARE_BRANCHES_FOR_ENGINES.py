#!/usr/bin/env python3
"""
🔍 COMPARE BRANCHES TO FIND WHICH HAS ALL 205+ ENGINES
"""

import subprocess
import sys
from pathlib import Path

def run_git_command(cmd):
    """Run git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/workspace')
        return result.stdout.strip()
    except:
        return ""

def check_branch_files(branch_name):
    """Check what files exist in a branch"""
    print(f"\n{'='*80}")
    print(f"🔍 CHECKING BRANCH: {branch_name}")
    print(f"{'='*80}")
    
    # Get list of Python files in this branch
    files = run_git_command(f"git ls-tree -r {branch_name} --name-only | grep '\\.py$'")
    
    if not files:
        print(f"❌ Cannot access branch {branch_name}")
        return None
    
    file_list = files.split('\n')
    total_files = len(file_list)
    
    # Count engine files
    engine_files = [f for f in file_list if any(keyword in f.upper() for keyword in [
        'ENGINE', 'ORCHESTRATOR', 'TRADER', 'TRADING', 'BRAIN', 
        'INTELLIGENCE', 'QUANTUM', 'ULTRA', 'DIVINE', 'CONSCIOUSNESS'
    ])]
    
    # Check for critical files
    critical_files = {
        'ALL_ENGINES_ACTIVATED.py': 'ALL_ENGINES_ACTIVATED.py' in file_list,
        'ULTRA_GOLDMINE_FEATURES.py': 'ULTRA_GOLDMINE_FEATURES.py' in file_list,
        'DIVINE_INTELLIGENCE_FEATURES.py': 'DIVINE_INTELLIGENCE_FEATURES.py' in file_list,
        'COMPREHENSIVE_ENGINE_DIAGNOSTIC.py': 'COMPREHENSIVE_ENGINE_DIAGNOSTIC.py' in file_list,
        'CONSCIOUSNESS_HARMONIZER.py': 'CONSCIOUSNESS_HARMONIZER.py' in file_list,
        'SWARM_INTELLIGENCE_ENGINE.py': 'SWARM_INTELLIGENCE_ENGINE.py' in file_list,
        'VPS_COMPLETE_AUDIT.sh': 'VPS_COMPLETE_AUDIT.sh' in file_list,
        'VPS_SYNC_CHECK.py': 'VPS_SYNC_CHECK.py' in file_list,
    }
    
    # Check for orchestrators
    orchestrator_files = [f for f in file_list if 'ORCHESTRATOR' in f.upper()]
    
    print(f"\n📊 STATISTICS:")
    print(f"  Total Python files: {total_files}")
    print(f"  Engine files: {len(engine_files)}")
    print(f"  Orchestrators: {len(orchestrator_files)}")
    
    print(f"\n📁 CRITICAL FILES:")
    critical_present = sum(critical_files.values())
    for file, present in critical_files.items():
        icon = "✅" if present else "❌"
        print(f"  {icon} {file}")
    
    print(f"\n📈 SCORE: {critical_present}/{len(critical_files)} critical files")
    
    # Get last commit info
    last_commit = run_git_command(f"git log {branch_name} -1 --oneline")
    commit_date = run_git_command(f"git log {branch_name} -1 --format=%cd --date=relative")
    
    print(f"\n📅 LAST COMMIT:")
    print(f"  {last_commit}")
    print(f"  ({commit_date})")
    
    return {
        'branch': branch_name,
        'total_files': total_files,
        'engine_files': len(engine_files),
        'orchestrators': len(orchestrator_files),
        'critical_score': critical_present,
        'critical_total': len(critical_files),
        'has_all_engines': critical_files.get('ALL_ENGINES_ACTIVATED.py', False),
        'has_diagnostics': critical_files.get('COMPREHENSIVE_ENGINE_DIAGNOSTIC.py', False),
        'last_commit': last_commit,
    }

def main():
    print("="*80)
    print("🔍 BRANCH COMPARISON - FINDING BRANCH WITH ALL 205+ ENGINES")
    print("="*80)
    
    # Fetch latest
    print("\n📡 Fetching latest from remote...")
    run_git_command("git fetch origin")
    
    # Branches to check
    branches_to_check = [
        'cursor/resume-and-optimize-trading-bot-engines-c805',  # Current workspace
        'origin/continue-from-micro-fix',  # Target branch
        'origin/cursor/continue-bot-trading-improvements-4f37',  # Current VPS
        'origin/cursor/check-last-agent-stop-point-for-bot-functionality-8296',  # Previous work
    ]
    
    results = []
    
    for branch in branches_to_check:
        result = check_branch_files(branch)
        if result:
            results.append(result)
    
    # Compare results
    print("\n" + "="*80)
    print("📊 COMPARISON SUMMARY")
    print("="*80)
    
    print(f"\n{'Branch':<60} {'Files':<8} {'Engines':<10} {'Score':<8}")
    print("-"*80)
    
    for r in results:
        branch_short = r['branch'].replace('origin/', '').replace('cursor/', '')[:55]
        print(f"{branch_short:<60} {r['total_files']:<8} {r['engine_files']:<10} {r['critical_score']}/{r['critical_total']}")
    
    # Find best branch
    best_branch = max(results, key=lambda x: (x['critical_score'], x['engine_files'], x['total_files']))
    
    print("\n" + "="*80)
    print("🏆 RECOMMENDED BRANCH (Most Complete):")
    print("="*80)
    print(f"\n  Branch: {best_branch['branch']}")
    print(f"  Reason: Has {best_branch['critical_score']}/{best_branch['critical_total']} critical files")
    print(f"          Has {best_branch['engine_files']} engine files")
    print(f"          Has {best_branch['total_files']} total Python files")
    
    if best_branch['has_all_engines']:
        print(f"\n  ✅ Has ALL_ENGINES_ACTIVATED.py (39+ engines ready)")
    if best_branch['has_diagnostics']:
        print(f"  ✅ Has comprehensive diagnostics")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATION:")
    print("="*80)
    
    current_vps_branch = 'origin/cursor/continue-bot-trading-improvements-4f37'
    target_branch = 'origin/continue-from-micro-fix'
    best = best_branch['branch']
    
    if best == 'cursor/resume-and-optimize-trading-bot-engines-c805':
        print("\n  The WORKSPACE branch has the most complete code!")
        print(f"  This is where all 39 engines were just activated.")
        print(f"\n  SUGGESTED ACTION:")
        print(f"  1. Merge workspace fixes into 'continue-from-micro-fix'")
        print(f"  2. Push to 'continue-from-micro-fix'")
        print(f"  3. Switch VPS to 'continue-from-micro-fix'")
        print(f"  4. Pull on VPS")
    elif target_branch in best:
        print(f"\n  The 'continue-from-micro-fix' branch is already best!")
        print(f"  Just switch VPS to that branch and pull.")
    else:
        print(f"\n  Branch {best} has the most complete code.")
        print(f"  Consider using that as the base.")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    results = main()
