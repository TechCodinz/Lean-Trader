# 🖥️ VPS AUDIT COMMANDS - Run These On Your VPS

## 🚀 QUICK AUDIT (Copy-Paste This)

```bash
# Navigate to your bot directory
cd ~/bot  # or wherever your bot is installed

# Run complete audit
bash VPS_COMPLETE_AUDIT.sh

# Run sync check
python3 VPS_SYNC_CHECK.py

# Run engine diagnostic
python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py
```

---

## 📋 STEP-BY-STEP COMMANDS

### Step 1: Check If Bot Is Running

```bash
# Check for bot processes
ps aux | grep -E "python.*ORCHESTRATOR|python.*bot" | grep -v grep

# If bot is running, check what file it's using
ps aux | grep python | grep -v grep | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}'

# Check how long it's been running
ps -eo pid,etime,cmd | grep python | grep -v grep
```

**Expected Output:**
- If running: You'll see process with ORCHESTRATOR or bot
- If not running: Empty output (need to start bot)

---

### Step 2: Check Git Status & Branch

```bash
# Check current branch
git branch --show-current

# Check if up to date
git status

# Check latest commits
git log --oneline -5

# Fetch latest from remote
git fetch origin

# See if behind
git status -uno
```

**Expected Output:**
- Branch: `cursor/resume-and-optimize-trading-bot-engines-c805`
- Status: Should show if behind or up to date

---

### Step 3: Check Dependencies

```bash
# Quick check all critical dependencies
python3 << 'EOF'
import sys
deps = ['numpy', 'pandas', 'scipy', 'scikit-learn', 'ccxt', 'aiohttp', 'requests']
missing = []
for dep in deps:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - MISSING")
        missing.append(dep)

if missing:
    print(f"\nInstall missing: pip3 install {' '.join(missing)}")
else:
    print("\n✅ All dependencies installed!")
EOF
```

---

### Step 4: Check Critical Files

```bash
# Check all critical files exist
for file in \
    "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py" \
    "EXECUTION_ORCHESTRATOR.py" \
    "INTELLIGENT_EXECUTION_ENGINE.py" \
    "ULTRA_GOLDMINE_FEATURES.py" \
    "DIVINE_INTELLIGENCE_FEATURES.py" \
    "critical_features_addon.py" \
    "ALL_ENGINES_ACTIVATED.py" \
    "router.py" \
    ".env"
do
    if [ -f "$file" ]; then
        echo "✅ $file ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file - MISSING"
    fi
done
```

---

### Step 5: Check .env Configuration

```bash
# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Check if configured (don't show actual keys!)
    if grep -q "your_.*_here" .env; then
        echo "⚠️  .env has placeholder values - NEEDS CONFIGURATION"
    else
        echo "✅ .env appears configured"
    fi
    
    # Check critical keys (without showing values)
    for key in GATE_API_KEY GATE_SECRET TELEGRAM_BOT_TOKEN; do
        if grep -q "^${key}=" .env; then
            echo "✅ $key is set"
        else
            echo "❌ $key is missing"
        fi
    done
else
    echo "❌ .env file missing!"
    echo "💡 Create it: cp .env.template .env"
fi
```

---

### Step 6: Check Engine Activation

```bash
# Test engine activation module
python3 << 'EOF'
try:
    import ALL_ENGINES_ACTIVATED
    
    activated = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) 
                   if name.endswith('_AVAILABLE') 
                   and getattr(ALL_ENGINES_ACTIVATED, name))
    total = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) 
               if name.endswith('_AVAILABLE'))
    
    print(f"✅ Engine activation module loaded")
    print(f"📊 {activated}/{total} engines activated ({activated/total*100:.1f}%)")
    
    if activated >= 39:
        print(f"✅ Excellent! {activated} engines active")
    elif activated >= 30:
        print(f"✅ Good! {activated} engines active")
    else:
        print(f"⚠️  Only {activated} engines active (expected 39+)")
    
except Exception as e:
    print(f"❌ Engine activation failed: {e}")
EOF
```

---

### Step 7: Check Recent Logs

```bash
# Find log files
echo "📝 Available log files:"
ls -lh *.log 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

# Check most recent log
LOGFILE=$(ls -t *.log 2>/dev/null | head -1)

if [ -n "$LOGFILE" ]; then
    echo -e "\n📊 Recent activity in $LOGFILE:"
    
    # Last 20 lines
    tail -20 "$LOGFILE"
    
    # Count errors
    ERROR_COUNT=$(grep -i "error\|exception" "$LOGFILE" | wc -l)
    echo -e "\n⚠️  Total errors in log: $ERROR_COUNT"
    
    # Count trades
    TRADE_COUNT=$(grep -i "trade.*executed\|buy\|sell" "$LOGFILE" | wc -l)
    echo "💰 Total trades in log: $TRADE_COUNT"
else
    echo "❌ No log files found"
fi
```

---

### Step 8: Test Critical Imports

```bash
# Test if engines can be imported
python3 << 'EOF'
import sys

print("Testing critical imports:")
imports = [
    ('ULTRA_GOLDMINE_FEATURES', 'GammaSqueezeDetector'),
    ('DIVINE_INTELLIGENCE_FEATURES', 'DivineIntelligenceManager'),
    ('critical_features_addon', 'TrailingStopManager'),
    ('EXECUTION_ORCHESTRATOR', 'ExecutionOrchestrator'),
    ('INTELLIGENT_EXECUTION_ENGINE', 'IntelligentExecutionEngine'),
]

working = 0
for module_name, class_name in imports:
    try:
        module = __import__(module_name)
        if hasattr(module, class_name):
            print(f"  ✅ {module_name}.{class_name}")
            working += 1
        else:
            print(f"  ⚠️  {module_name}.{class_name} - class not found")
    except Exception as e:
        print(f"  ❌ {module_name} - {str(e)[:50]}")

print(f"\n📊 {working}/{len(imports)} imports working")

if working == len(imports):
    print("✅ All critical imports working!")
else:
    print(f"⚠️  {len(imports) - working} imports failed")
EOF
```

---

### Step 9: Check System Resources

```bash
# CPU and Memory
echo "🖥️  System Resources:"
echo "  CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "  Memory: $(free -h | awk 'NR==2 {print $3 "/" $2 " used"}')"
echo "  Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"

# Top Python processes
echo -e "\n🐍 Python Processes:"
ps aux | grep python | grep -v grep | head -5 | awk '{printf "  CPU: %s%% | MEM: %s%% | %s\n", $3, $4, $11}'
```

---

### Step 10: Network Connectivity

```bash
# Test exchange connections
echo "🌐 Testing Exchange Connectivity:"
for host in api.gate.io api.bybit.com api.binance.com; do
    if ping -c 1 -W 2 $host &>/dev/null; then
        echo "  ✅ $host"
    else
        echo "  ❌ $host - unreachable"
    fi
done
```

---

## 🔧 AUTOMATED AUDIT SCRIPTS

### Option 1: Full Audit (Most Comprehensive)

```bash
# Run the complete audit script
bash VPS_COMPLETE_AUDIT.sh > vps_audit_$(date +%Y%m%d_%H%M%S).txt

# View the results
cat vps_audit_*.txt | tail -100
```

### Option 2: Sync Check (Compare with Expected)

```bash
# Run sync verification
python3 VPS_SYNC_CHECK.py

# Check the JSON report
cat VPS_SYNC_REPORT.json
```

### Option 3: Engine Diagnostic (Detailed Engine Analysis)

```bash
# Run comprehensive engine diagnostic
python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py > engine_diagnostic_$(date +%Y%m%d_%H%M%S).txt

# View dormant engines
grep "DORMANT" engine_diagnostic_*.txt -A 50
```

---

## 📊 WHAT TO LOOK FOR

### ✅ GOOD SIGNS:
- Bot process running
- 39+ engines activated
- All dependencies installed
- .env configured
- Recent log activity
- Trades executing
- No errors in logs

### ⚠️ WARNING SIGNS:
- Bot not running
- Less than 30 engines active
- Missing dependencies
- .env has placeholders
- No recent log activity
- No trades executing
- Errors in logs

### ❌ CRITICAL ISSUES:
- Git branch mismatch
- Missing critical files
- Import failures
- Syntax errors
- Network connectivity issues
- Out of memory/disk space

---

## 🚑 QUICK FIXES

### If Bot Not Running:
```bash
# Start the bot
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py &

# Or with nohup
nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
```

### If Missing Dependencies:
```bash
pip3 install numpy pandas scipy scikit-learn ccxt aiohttp requests
```

### If .env Missing:
```bash
cp .env.template .env
nano .env  # Add your API keys
```

### If Behind Remote:
```bash
git pull origin cursor/resume-and-optimize-trading-bot-engines-c805
```

### If Engines Not Loading:
```bash
# Test engine activation
python3 -c "import ALL_ENGINES_ACTIVATED; print('OK')"

# Re-run system check
python3 COMPREHENSIVE_SYSTEM_CHECK.py
```

---

## 📋 COMPLETE ONE-LINER AUDIT

Copy-paste this single command for full audit:

```bash
cd ~/bot && echo "🔍 Starting VPS Audit..." && \
git branch --show-current && \
git status -uno && \
python3 -c "import numpy, pandas, ccxt; print('✅ Dependencies OK')" 2>&1 && \
python3 -c "import ALL_ENGINES_ACTIVATED; print(f'✅ {sum(1 for n in dir(ALL_ENGINES_ACTIVATED) if n.endswith(\"_AVAILABLE\") and getattr(ALL_ENGINES_ACTIVATED, n))} engines active')" 2>&1 && \
ls -lh systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py ALL_ENGINES_ACTIVATED.py .env 2>&1 && \
ps aux | grep python | grep -v grep && \
echo "✅ Audit complete! Review output above."
```

---

## 📞 NEED MORE HELP?

If audit shows issues, run:

```bash
# Auto-fix common problems
bash AUTO_FIX_ALL_ISSUES.sh

# Full system check
python3 COMPREHENSIVE_SYSTEM_CHECK.py

# Read documentation
cat FINAL_SYSTEM_STATUS_REPORT.md
cat QUICK_START_GUIDE.md
```

---

**All scripts are in `/workspace/` on both local and VPS after git pull!**
