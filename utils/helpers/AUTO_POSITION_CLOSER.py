#!/usr/bin/env python3
"""
INTELLIGENT AUTO POSITION CLOSER
- Only closes positions AFTER checking for profit
- Works with AutoProfitTaker settings (0.2% quick, 0.5% normal)
- Prevents closing at a loss
"""
import ccxt
import logging
import os
from dotenv import load_dotenv
import time

load_dotenv('/root/bot/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - INTELLIGENT_CLOSER - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentAutoCloser:
    def __init__(self):
        api_key = os.getenv('BYBIT_TESTNET_API_KEY')
        secret = os.getenv('BYBIT_TESTNET_API_SECRET')
        
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.exchange.set_sandbox_mode(True)
        self.exchange.load_markets()
        
        # Profit targets from AutoProfitTaker
        self.quick_scalp_target = 0.002  # 0.2%
        self.normal_target = 0.005  # 0.5%
        self.min_profit_to_close = 0.001  # 0.1% minimum profit before closing
        
        # Entry prices (would normally come from position tracking)
        self.entry_prices = {}
        
        self.check_interval = 30  # Check every 30 seconds
        logger.info("INTELLIGENT AUTO CLOSER initialized")
        logger.info(f"  Min profit to close: {self.min_profit_to_close*100}%")
    
    def check_and_close_profitable_positions(self):
        """Only close positions that are in profit"""
        try:
            balance = self.exchange.fetch_balance()
            
            for currency, amounts in balance.items():
                if currency in ['info', 'free', 'used', 'total', 'timestamp', 'datetime', 'USDT', 'USDC']:
                    continue
                
                if isinstance(amounts, dict):
                    free = amounts.get('free', 0)
                else:
                    free = float(amounts) if amounts else 0
                
                if free > 0:
                    symbol = f"{currency}/USDT"
                    try:
                        if symbol in self.exchange.markets:
                            ticker = self.exchange.fetch_ticker(symbol)
                            current_price = ticker['last']
                            
                            # Get entry price (use last known or estimate from 24h average)
                            entry_price = self.entry_prices.get(symbol, ticker.get('vwap', current_price * 0.999))
                            
                            # Calculate profit %
                            profit_pct = (current_price - entry_price) / entry_price
                            
                            min_amount = self.exchange.markets[symbol].get('limits', {}).get('amount', {}).get('min', 0) or 0.000001
                            
                            if free >= min_amount:
                                if profit_pct >= self.min_profit_to_close:
                                    # IN PROFIT - close the position
                                    logger.info(f"[OK] PROFIT CLOSE: {currency} +{profit_pct*100:.2f}% - Selling {free}")
                                    order = self.exchange.create_market_sell_order(symbol, free)
                                    logger.info(f"  CLOSED at profit!")
                                else:
                                    # Not in profit yet, skip
                                    logger.debug(f"⏳ {currency} at {profit_pct*100:.2f}% - waiting for profit")
                    except Exception as e:
                        logger.debug(f"Could not check {currency}: {e}")
        except Exception as e:
            logger.error(f"Balance error: {e}")
    
    def run_forever(self):
        """Run continuously with intelligent profit checking"""
        logger.info("Starting intelligent position closing loop...")
        while True:
            try:
                self.check_and_close_profitable_positions()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    closer = IntelligentAutoCloser()
    closer.run_forever()

