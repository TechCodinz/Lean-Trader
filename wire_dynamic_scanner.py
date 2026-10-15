#!/usr/bin/env python3
"""Wire the 2025 DYNAMIC_MARKET_SCANNER. No new logic — just boot theirs."""

import asyncio
import sys
sys.path.insert(0, '/app')

from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
import ccxt.async_support as ccxt


async def main():
    exchanges = {}
    
    # Bybit testnet (available API)
    try:
        with open('/run/secrets/bybit_testnet_api_key') as f:
            key = f.read().strip()
        with open('/run/secrets/bybit_testnet_api_secret') as f:
            secret = f.read().strip()
        ex = ccxt.bybit({'apiKey': key, 'secret': secret, 'enableRateLimit': True})
        ex.set_sandbox_mode(True)
        exchanges['bybit_testnet'] = ex
    except Exception:
        pass
    
    # Add more exchanges here as they become available — no recoding of scanner
    
    scanner = DynamicMarketScanner(exchanges=exchanges, data_hub=None)
    await scanner.run_continuous_scanning()


if __name__ == '__main__':
    asyncio.run(main())
