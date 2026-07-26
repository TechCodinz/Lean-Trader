
import asyncio
import ccxt
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("position_monitor_v2.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SMART_MONITOR")

# Load environment variables
load_dotenv('/root/bot/.env')

class SmartPositionMonitor:
    def __init__(self):
        # Initialize exchange with RATE LIMITING ENABLED
        self.exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
            'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
            'sandbox': True,  # TESTNET
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'pnl': True,
            }
        })
        self.min_notional = 1.0 # Approximate minimum for safety, though Bybit varies

    async def get_min_order_size(self, symbol):
        """Fetch market rules to know minimum order size"""
        try:
            markets = await self.exchange.load_markets()
            market = markets[symbol]
            return market['limits']['amount']['min'], market['limits']['cost']['min']
        except Exception as e:
            logger.error(f"Could not fetch limits for {symbol}: {e}")
            return 0.0, 0.0

    async def close_all_profitable_positions(self):
        """
        The CORE LOGIC for Infinite Compounding:
        1. Scan ALL open positions (wallet balances > 0)
        2. Check PnL against current market price
        3. If Profit > 0.1% (Scalping Mode) -> CLOSE IMMEDIATELY
        4. If Loss > 2.0% (Stop Loss) -> CLOSE IMMEDIATELY
        5. Log the win/loss for verification
        """
        try:
            # 1. Fetch complete balance
            balance = self.exchange.fetch_balance()
            
            # 2. Iterate through all assets
            for asset, data in balance.items():
                if asset == 'USDT' or not isinstance(data, dict):
                    continue
                    
                total = float(data.get('total', 0))
                free = float(data.get('free', 0)) # Use free balance to avoid locked orders
                
                if free <= 0:
                    continue
                
                symbol = f"{asset}/USDT"
                
                try:
                    # 3. Get Real-Time Price
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_price = float(ticker['last'])
                    position_value = free * current_price
                    
                    # IGNORE DUST (< $0.05) to save API calls, UNLESS we want to clean up
                    if position_value < 0.05:
                        continue

                    # Define market limits EARLY
                    market = self.exchange.market(symbol)
                    min_cost = market['limits']['cost']['min'] if market and 'limits' in market else 1.0
                    min_amt = market['limits']['amount']['min'] if market and 'limits' in market else 0.0

                    if free < min_amt:
                        continue
                    
                    # 4. Determine Entry Price & PnL
                    # We fetch recent trades to find the last BUY price
                    trades = self.exchange.fetch_my_trades(symbol, limit=5)
                    last_buy_price = 0.0
                    
                    # Find last buy
                    for trade in reversed(trades):
                        if trade['side'] == 'buy':
                            last_buy_price = float(trade['price'])
                            break
                            
                    if last_buy_price > 0:
                        # Calculate ROI
                        roi_pct = ((current_price - last_buy_price) / last_buy_price) * 100
                        logger.info(f"📊 {symbol} PnL: {roi_pct:.2f}% (Entry: {last_buy_price}, Curr: {current_price})")
                        
                        # LOGIC:
                        # 1. Take Profit: > 0.5% (Quick Scalp)
                        # 2. Stop Loss: < -2.0% (Safety)
                        # 3. Time based? (Not implemented yet)
                        
                        if roi_pct > 0.5:
                            logger.info(f">> PROFIT TARGET HIT for {symbol}: {roi_pct:.2f}%! Closing...")
                            order = self.exchange.create_market_sell_order(symbol, free)
                            logger.info(f"[OK] REALIZED PROFIT: {symbol} closed at {current_price}")
                        elif roi_pct < -2.0:
                             logger.warning(f"🛑 STOP LOSS HIT for {symbol}: {roi_pct:.2f}%. Closing to save capital.")
                             order = self.exchange.create_market_sell_order(symbol, free)
                             logger.info(f"[X] STOP LOSS EXECUTED: {symbol} closed at {current_price}")
                        else:
                            logger.info(f"⏳ HOLDING {symbol}: ROI {roi_pct:.2f}% (Target: >0.5%)")
                    
                    elif position_value > min_cost:
                        # Fallback: If we can't find a buy price (old position), we might assume it's legacy
                        # only close if significantly valuable
                        logger.info(f" No recent buy found for {symbol}. Holding until profit confirmed or manual intervention.")
                        
                    else:
                        logger.warning(f" {symbol} value ${position_value:.4f} < Min ${min_cost}. Cannot close.")
                
                except Exception as e:
                    logger.error(f"[X] Error processing {symbol}: {e}")

        except Exception as e:
            logger.error(f"CRITICAL MONITOR ERROR: {e}")

    async def run(self):
        print(">> INFINITE COMPOUNDING MONITOR STARTED")
        print("   - Scans every 5 seconds")
        print("   - Force-closes positions to release capital")
        logger.info("Starting loop...")
        
        while True:
            await self.close_all_profitable_positions()
            await asyncio.sleep(5)

if __name__ == "__main__":
    monitor = SmartPositionMonitor()
    # Asyncio loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor.run())
