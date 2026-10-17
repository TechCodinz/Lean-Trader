#!/usr/bin/env python3
"""
LeanTrader Ultra Smart AI Bot Service (2025 microservice).

2025 original: ULTRA_SMART_AI_BOT.py (2025-09-29)
Overrides dead 2025 hardcoded keys with working Bybit testnet from /run/secrets/.
"""

import logging
import sys

sys.path.insert(0, '/app')

from ULTRA_SMART_AI_BOT import ULTRA_SMART_AI_BOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ULTRA_AI_SERVICE')


def load_testnet_keys():
    """Load Bybit testnet keys from container secrets."""
    try:
        with open('/run/secrets/bybit_testnet_api_key') as f:
            key = f.read().strip()
        with open('/run/secrets/bybit_testnet_api_secret') as f:
            secret = f.read().strip()
        return key, secret
    except Exception as e:
        logger.error(f"Cannot load testnet keys: {e}")
        return None, None


def main():
    logger.info("🤖 Starting Ultra Smart AI Bot Service (2025 microservice)")
    
    bot = ULTRA_SMART_AI_BOT()
    
    # Override dead 2025 keys with working testnet
    key, secret = load_testnet_keys()
    if key and secret:
        # Replace bybit config with working testnet keys
        if 'bybit' in bot.exchange_configs:
            bot.exchange_configs['bybit']['apiKey'] = key
            bot.exchange_configs['bybit']['secret'] = secret
            bot.exchange_configs['bybit']['sandbox'] = True
            logger.info("✅ Bybit testnet keys injected (2025 dead keys replaced)")
    
    logger.info("✅ Bot initialized, starting trading loop...")
    bot.run()


if __name__ == "__main__":
    main()
