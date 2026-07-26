
import os
import re

DIRS_TO_PATCH = [
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\core\orchestrators",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\engines\routing",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\utils\helpers",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\engines\execution",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\engines\profit",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\ai\intelligence",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\ultra_rare\goldmine",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\features\critical",
    r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\engines\scanners"
]

def patch_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Fix Imports (Global)
        content = re.sub(r'from router import', r'from engines.routing.router import', content)
        content = re.sub(r'from market_router import', r'from engines.routing.market_router import', content)
        content = re.sub(r'from dex_router import', r'from engines.routing.dex_router import', content)
        content = re.sub(r'from paper_broker import', r'from utils.helpers.paper_broker import', content)
        content = re.sub(r'import paper_broker', r'import utils.helpers.paper_broker as paper_broker', content)
        content = re.sub(r'from risk_engine import', r'from safety.risk.risk_engine import', content)
        content = re.sub(r'import risk_engine', r'import safety.risk.risk_engine as risk_engine', content)
        content = re.sub(r'from DIVINE_INTELLIGENCE_FEATURES import', r'from ai.intelligence.DIVINE_INTELLIGENCE_FEATURES import', content)
        content = re.sub(r'from brain import', r'from utils.helpers.brain import', content)
        content = re.sub(r'import brain', r'import utils.helpers.brain as brain', content)
        content = re.sub(r'from hivemind import', r'from utils.helpers.hivemind import', content)
        content = re.sub(r'import hivemind', r'import utils.helpers.hivemind as hivemind', content)
        content = re.sub(r'from ANTI_CLOCKWISE_TRADING_ENGINE import', r'from utils.helpers.ANTI_CLOCKWISE_TRADING_ENGINE import', content)
        content = re.sub(r'import ANTI_CLOCKWISE_TRADING_ENGINE', r'import utils.helpers.ANTI_CLOCKWISE_TRADING_ENGINE as ANTI_CLOCKWISE_TRADING_ENGINE', content)
        content = re.sub(r'from pattern_memory import', r'from utils.helpers.pattern_memory import', content)
        content = re.sub(r'import pattern_memory', r'import utils.helpers.pattern_memory as pattern_memory', content)
        content = re.sub(r'from alpha_engines import', r'from utils.helpers.alpha_engines import', content)
        content = re.sub(r'import alpha_engines', r'import utils.helpers.alpha_engines as alpha_engines', content)
        content = re.sub(r'from FRACTAL_RECURSION_ENGINE import', r'from utils.helpers.FRACTAL_RECURSION_ENGINE import', content)
        content = re.sub(r'import FRACTAL_RECURSION_ENGINE', r'import utils.helpers.FRACTAL_RECURSION_ENGINE as FRACTAL_RECURSION_ENGINE', content)
        content = re.sub(r'from ledger import', r'from utils.helpers.ledger import', content)
        content = re.sub(r'import ledger', r'import utils.helpers.ledger as ledger', content)
        content = re.sub(r'from news_adapter import', r'from utils.helpers.news_adapter import', content)
        content = re.sub(r'import news_adapter', r'import utils.helpers.news_adapter as news_adapter', content)
        content = re.sub(r'from DIMENSIONAL_TRADING_ENGINE import', r'from utils.helpers.DIMENSIONAL_TRADING_ENGINE import', content)
        content = re.sub(r'import DIMENSIONAL_TRADING_ENGINE', r'import utils.helpers.DIMENSIONAL_TRADING_ENGINE as DIMENSIONAL_TRADING_ENGINE', content)
        content = re.sub(r'from ultra_core import', r'from utils.helpers.ultra_core import', content)
        content = re.sub(r'import ultra_core', r'import utils.helpers.ultra_core as ultra_core', content)
        content = re.sub(r'from ultra_scout import', r'from ultra_rare.goldmine.ultra_scout import', content)
        content = re.sub(r'import ultra_scout', r'import ultra_rare.goldmine.ultra_scout as ultra_scout', content)
        content = re.sub(r'from critical_features_addon import', r'from features.critical.critical_features_addon import', content)
        content = re.sub(r'import critical_features_addon', r'import features.critical.critical_features_addon as critical_features_addon', content)
        content = re.sub(r'from awareness import', r'from utils.helpers.awareness import', content)
        content = re.sub(r'import awareness', r'import utils.helpers.awareness as awareness', content)
        content = re.sub(r'from gloaware import', r'from utils.helpers.gloaware import', content)
        content = re.sub(r'import gloaware', r'import utils.helpers.gloaware as gloaware', content)
        content = re.sub(r'from ultra_arbitrage_engine import', r'from utils.helpers.ultra_arbitrage_engine import', content)
        content = re.sub(r'import ultra_arbitrage_engine', r'import utils.helpers.ultra_arbitrage_engine as ultra_arbitrage_engine', content)
        content = re.sub(r'from scanners import', r'from engines.scanners import', content)
        content = re.sub(r'import scanners', r'import engines.scanners as scanners', content)
        content = re.sub(r'from ultra_scalping_engine import', r'from utils.helpers.ultra_scalping_engine import', content)
        content = re.sub(r'import ultra_scalping_engine', r'import utils.helpers.ultra_scalping_engine as ultra_scalping_engine', content)
        content = re.sub(r'from ultra_moon_spotter import', r'from ultra_rare.goldmine.ultra_moon_spotter import', content)
        content = re.sub(r'import ultra_moon_spotter', r'import ultra_rare.goldmine.ultra_moon_spotter as ultra_moon_spotter', content)
        content = re.sub(r'from REAL_PROFIT_BOT import', r'from engines.profit.REAL_PROFIT_BOT import', content)
        # Use negative lookbehind to ensure we don't match "from ... import REAL_PROFIT_BOT"
        content = re.sub(r'(?<!from )import REAL_PROFIT_BOT', r'import engines.profit.REAL_PROFIT_BOT as REAL_PROFIT_BOT', content)
        content = re.sub(r'from enhanced_trading_bot import', r'from utils.helpers.enhanced_trading_bot import', content)
        content = re.sub(r'import enhanced_trading_bot', r'import utils.helpers.enhanced_trading_bot as enhanced_trading_bot', content)
        
        # 2. Fix Emojis
        replacements = {
            "\u26a0\ufe0f": "",
            "🚀": ">>",
            "❌": "[X]",
            "✅": "[OK]",
            "⚠️": "",
            "🔌": "",
            "\U0001f3d7\ufe0f": "",
            "\u274c": "[X]",
            "\U0001f300": ""
        }
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
            
        if content != original_content:
            try:
                print(f"Patching {os.path.basename(filepath)}...")
            except:
                pass
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            
    except Exception:
        pass

def main():
    print("Starting Global Patch...")
    for directory in DIRS_TO_PATCH:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    patch_file(os.path.join(root, file))
                    
    print("Global Patch Complete.")

if __name__ == "__main__":
    main()
