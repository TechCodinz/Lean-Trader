#!/usr/bin/env python3
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ProperPositionCloser:
    def __init__(self, exchange):
        self.exchange = exchange
        self.running = True
        self.check_interval = 5
        logger.info("PROPER POSITION CLOSER initialized")
    
    async def start_continuous_closure(self):
        logger.info("Starting continuous position closure loop...")
        while self.running:
            try:
                await self.close_all_non_usdt_positions()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Position closure error: {e}")
                await asyncio.sleep(1)
    
    async def close_all_non_usdt_positions(self):
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            
            for currency, amounts in balance.items():
                if currency in ['info', 'free', 'used', 'total', 'timestamp', 'datetime', 'USDT', 'USDC']:
                    continue
                
                if isinstance(amounts, dict):
                    total = amounts.get('total', 0)
                    free = amounts.get('free', 0)
                else:
                    total = float(amounts) if amounts else 0
                    free = total
                
                if total > 0 and free > 0:
                    symbol = f"{currency}/USDT"
                    try:
                        if symbol in self.exchange.markets:
                            min_amount = self.exchange.markets[symbol].get('limits', {}).get('amount', {}).get('min', 0) or 0
                            if free >= min_amount:
                                logger.info(f"CLOSING: Selling {free} {currency} to USDT")
                                order = await asyncio.to_thread(
                                    self.exchange.create_market_sell_order,
                                    symbol,
                                    free
                                )
                                logger.info(f"CLOSED: {currency} -> USDT")
                    except Exception as e:
                        logger.debug(f"Could not sell {currency}: {e}")
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")

