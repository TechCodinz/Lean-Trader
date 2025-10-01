#!/bin/bash

echo "🔧 Preparing Ultra Trading System for GitHub..."
echo "=============================================="

# Remove sensitive files
echo "🔒 Removing sensitive files..."
rm -f .env env.live env.testnet env.arbitrage env.paper 2>/dev/null
rm -f *api_key* *secret* *token* 2>/dev/null

# Clean up logs and data
echo "🧹 Cleaning up logs and data..."
rm -rf logs/*.log 2>/dev/null
rm -rf data/*.csv data/*.json 2>/dev/null
rm -rf state/* checkpoints/* models/* reports/* 2>/dev/null

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p logs data state checkpoints models reports backups

# Create placeholder files
echo "📄 Creating placeholder files..."
echo "# Logs directory" > logs/.gitkeep
echo "# Data directory" > data/.gitkeep
echo "# State directory" > state/.gitkeep
echo "# Checkpoints directory" > checkpoints/.gitkeep
echo "# Models directory" > models/.gitkeep
echo "# Reports directory" > reports/.gitkeep
echo "# Backups directory" > backups/.gitkeep

# Check file count
echo ""
echo "📊 Repository Statistics:"
echo "========================"
echo "Python files: $(find . -name "*.py" | wc -l)"
echo "Total size: $(du -sh . | cut -f1)"
echo "Main components:"
ls -lh *.py | grep -E "(ultra_|production_|multi_|universal_)" | awk '{print "  •", $9, "-", $5}'

echo ""
echo "✅ Repository is clean and ready for GitHub!"
echo ""
echo "📝 Next steps:"
echo "1. Initialize git: git init"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial commit: Ultra Trading System'"
echo "4. Add remote: git remote add origin https://github.com/yourusername/ultra-trading-system.git"
echo "5. Push: git push -u origin main"
echo ""
echo "⚠️  Remember: NEVER commit files with API keys!"