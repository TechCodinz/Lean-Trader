#!/usr/bin/env python3
"""
REAL TRADING BOT - Actual Trading with Real Money
This is NOT a simulation - it will execute real trades on exchanges
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json
import ccxt.async_support as ccxt
from decimal import Decimal
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('real_trades.log', mode='a')
    ]
)
logger = logging.getLogger('RealTrading')

class RealTradingBot:
    """REAL trading bot that executes actual trades"""
    
    def __init__(self):
        self.exchanges = {}
        self.balances = {}
        self.active_positions = {}
        self.trade_history = []
        self.min_profit_threshold = 0.002  # 0.2% minimum profit for arbitrage
        self.max_position_size = 100  # Max $100 per trade initially
        self.trading_enabled = True  # Set to False for dry run
        
    async def initialize_exchanges(self):
        """Initialize REAL exchange connections with REAL API keys"""
        
        logger.info("🔄 Initializing REAL exchange connections...")
        
        # Load real API keys
        config = {}
        with open('env.arbitrage', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip()
        
        # Initialize exchanges with REAL credentials
        exchange_configs = [
            {
                'name': 'gateio',
                'class': ccxt.gateio,
                'config': {
                    'apiKey': config.get('GATEIO_API_KEY'),
                    'secret': config.get('GATEIO_SECRET'),
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                }
            },
            {
                'name': 'binance',
                'class': ccxt.binance,
                'config': {
                    'apiKey': config.get('BINANCE_API_KEY'),
                    'secret': config.get('BINANCE_SECRET'),
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                }
            },
            {
                'name': 'okx',
                'class': ccxt.okx,
                'config': {
                    'apiKey': config.get('OKX_API_KEY'),
                    'secret': config.get('OKX_SECRET'),
                    'password': 'TradingBot123!',  # OKX requires passphrase
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                }
            }
        ]
        
        for exc_config in exchange_configs:
            try:
                exchange = exc_config['class'](exc_config['config'])
                
                # Load markets and check connection
                await exchange.load_markets()
                
                # Get REAL balance
                balance = await exchange.fetch_balance()
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                
                self.exchanges[exc_config['name']] = exchange
                self.balances[exc_config['name']] = usdt_balance
                
                logger.info(f"✅ {exc_config['name'].upper()}: Connected | Balance: ${usdt_balance:.2f} USDT")
                
            except Exception as e:
                logger.error(f"❌ {exc_config['name']}: {str(e)[:100]}")
        
        if len(self.exchanges) < 2:
            logger.error("⚠️  Need at least 2 exchanges for arbitrage!")
            return False
            
        logger.info(f"✅ {len(self.exchanges)} exchanges ready for REAL trading")
        return True
    
    async def find_real_arbitrage_opportunities(self):
        """Find REAL arbitrage opportunities across exchanges"""
        
        opportunities = []
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']
        
        for symbol in symbols:
            prices = {}
            
            # Get REAL prices from each exchange
            for name, exchange in self.exchanges.items():
                try:
                    ticker = await exchange.fetch_ticker(symbol)
                    orderbook = await exchange.fetch_order_book(symbol, limit=5)
                    
                    if orderbook['bids'] and orderbook['asks']:
                        prices[name] = {
                            'bid': orderbook['bids'][0][0],  # Best bid price
                            'ask': orderbook['asks'][0][0],  # Best ask price
                            'bid_volume': orderbook['bids'][0][1],
                            'ask_volume': orderbook['asks'][0][1],
                            'timestamp': ticker['timestamp']
                        }
                except Exception as e:
                    logger.debug(f"Error fetching {symbol} from {name}: {e}")
                    continue
            
            # Find REAL arbitrage opportunities
            if len(prices) >= 2:
                for buy_exchange in prices:
                    for sell_exchange in prices:
                        if buy_exchange != sell_exchange:
                            buy_price = prices[buy_exchange]['ask']
                            sell_price = prices[sell_exchange]['bid']
                            
                            # Calculate REAL profit
                            if sell_price > buy_price:
                                gross_profit = (sell_price - buy_price) / buy_price
                                
                                # Account for trading fees (typically 0.1% per trade)
                                fee_rate = 0.001  # 0.1% 
                                net_profit = gross_profit - (2 * fee_rate)  # Buy fee + sell fee
                                
                                if net_profit > self.min_profit_threshold:
                                    # Calculate optimal trade size
                                    max_buy_volume = prices[buy_exchange]['ask_volume']
                                    max_sell_volume = prices[sell_exchange]['bid_volume']
                                    max_volume = min(max_buy_volume, max_sell_volume)
                                    
                                    # Limit by our max position size
                                    trade_value = min(max_volume * buy_price, self.max_position_size)
                                    trade_amount = trade_value / buy_price
                                    
                                    opportunities.append({
                                        'symbol': symbol,
                                        'buy_exchange': buy_exchange,
                                        'sell_exchange': sell_exchange,
                                        'buy_price': buy_price,
                                        'sell_price': sell_price,
                                        'amount': trade_amount,
                                        'value': trade_value,
                                        'gross_profit_pct': gross_profit * 100,
                                        'net_profit_pct': net_profit * 100,
                                        'expected_profit_usd': trade_value * net_profit,
                                        'timestamp': datetime.now()
                                    })
        
        # Sort by profitability
        opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)
        return opportunities
    
    async def execute_real_arbitrage_trade(self, opportunity):
        """Execute REAL arbitrage trade on exchanges"""
        
        logger.info("=" * 60)
        logger.info("💎 EXECUTING REAL ARBITRAGE TRADE")
        logger.info(f"Symbol: {opportunity['symbol']}")
        logger.info(f"Buy on {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}")
        logger.info(f"Sell on {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}")
        logger.info(f"Amount: {opportunity['amount']:.6f}")
        logger.info(f"Value: ${opportunity['value']:.2f}")
        logger.info(f"Expected Profit: ${opportunity['expected_profit_usd']:.2f} ({opportunity['net_profit_pct']:.3f}%)")
        
        if not self.trading_enabled:
            logger.info("🔸 SIMULATION MODE - Trade not executed")
            return False
        
        try:
            # Check balances
            buy_balance = self.balances.get(opportunity['buy_exchange'], 0)
            if buy_balance < opportunity['value']:
                logger.warning(f"Insufficient balance on {opportunity['buy_exchange']}: ${buy_balance:.2f} < ${opportunity['value']:.2f}")
                return False
            
            # Execute BUY order
            buy_exchange = self.exchanges[opportunity['buy_exchange']]
            logger.info(f"📗 Placing BUY order on {opportunity['buy_exchange']}...")
            
            buy_order = await buy_exchange.create_market_buy_order(
                symbol=opportunity['symbol'],
                amount=opportunity['amount']
            )
            
            logger.info(f"✅ BUY order executed: {buy_order['id']}")
            
            # Execute SELL order immediately
            sell_exchange = self.exchanges[opportunity['sell_exchange']]
            logger.info(f"📕 Placing SELL order on {opportunity['sell_exchange']}...")
            
            sell_order = await sell_exchange.create_market_sell_order(
                symbol=opportunity['symbol'],
                amount=opportunity['amount']
            )
            
            logger.info(f"✅ SELL order executed: {sell_order['id']}")
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'symbol': opportunity['symbol'],
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'buy_price': buy_order.get('average', opportunity['buy_price']),
                'sell_price': sell_order.get('average', opportunity['sell_price']),
                'amount': opportunity['amount'],
                'profit_usd': opportunity['expected_profit_usd'],
                'buy_order_id': buy_order['id'],
                'sell_order_id': sell_order['id'],
                'status': 'completed'
            }
            
            self.trade_history.append(trade_record)
            
            # Save to file
            with open('real_trades_history.json', 'a') as f:
                f.write(json.dumps(trade_record) + '\n')
            
            # Update balances
            await self.update_balances()
            
            # Send Telegram notification
            await self.send_trade_notification(trade_record)
            
            logger.info("✅ ARBITRAGE TRADE COMPLETED SUCCESSFULLY")
            logger.info(f"💰 Profit: ${opportunity['expected_profit_usd']:.2f}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            return False
    
    async def update_balances(self):
        """Update REAL account balances"""
        
        for name, exchange in self.exchanges.items():
            try:
                balance = await exchange.fetch_balance()
                self.balances[name] = balance.get('USDT', {}).get('free', 0)
            except Exception as e:
                logger.error(f"Error updating balance for {name}: {e}")
    
    async def send_trade_notification(self, trade):
        """Send REAL trade notification to Telegram"""
        
        try:
            from telegram import Bot
            
            bot = Bot(token="8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg")
            
            message = f"""
🎯 **REAL TRADE EXECUTED**

📊 **Pair:** {trade['symbol']}
🏦 **Buy:** {trade['buy_exchange']} @ ${trade['buy_price']:.4f}
🏦 **Sell:** {trade['sell_exchange']} @ ${trade['sell_price']:.4f}
📦 **Amount:** {trade['amount']:.6f}
💰 **Profit:** ${trade['profit_usd']:.2f}

📝 **Order IDs:**
• Buy: {trade['buy_order_id']}
• Sell: {trade['sell_order_id']}

✅ **Status:** {trade['status']}
⏰ **Time:** {trade['timestamp']}

💵 **Total Trades Today:** {len(self.trade_history)}
💰 **Total Profit:** ${sum(t['profit_usd'] for t in self.trade_history):.2f}
"""
            
            await bot.send_message(chat_id="5329503447", text=message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
    
    async def run_real_trading_loop(self):
        """Main REAL trading loop"""
        
        logger.info("🚀 Starting REAL trading loop...")
        logger.info(f"Trading Enabled: {self.trading_enabled}")
        logger.info(f"Min Profit Threshold: {self.min_profit_threshold * 100:.3f}%")
        logger.info(f"Max Position Size: ${self.max_position_size}")
        
        while True:
            try:
                # Find REAL arbitrage opportunities
                opportunities = await self.find_real_arbitrage_opportunities()
                
                if opportunities:
                    logger.info(f"Found {len(opportunities)} arbitrage opportunities")
                    
                    # Execute the best opportunity
                    best = opportunities[0]
                    
                    if best['net_profit_pct'] > (self.min_profit_threshold * 100):
                        logger.info(f"🎯 Best opportunity: {best['symbol']} - {best['net_profit_pct']:.3f}% profit")
                        
                        # Execute REAL trade
                        success = await self.execute_real_arbitrage_trade(best)
                        
                        if success:
                            # Wait a bit after successful trade
                            await asyncio.sleep(5)
                        else:
                            # Wait longer if trade failed
                            await asyncio.sleep(10)
                    else:
                        logger.debug(f"Best opportunity below threshold: {best['net_profit_pct']:.3f}%")
                else:
                    logger.debug("No arbitrage opportunities found")
                
                # Regular scan interval
                await asyncio.sleep(3)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)
        
        # Cleanup
        for exchange in self.exchanges.values():
            await exchange.close()
        
        logger.info("Trading bot stopped")

async def main():
    """Main entry point for REAL trading bot"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            💎 REAL TRADING BOT - LIVE PRODUCTION 💎                 ║
║                                                                      ║
║  ⚠️  WARNING: This bot executes REAL trades with REAL money!       ║
║                                                                      ║
║  Features:                                                          ║
║  • Real-time arbitrage detection                                    ║
║  • Automatic trade execution                                        ║
║  • Multi-exchange support                                           ║
║  • Risk management                                                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Confirm with user
    print("⚠️  This bot will execute REAL trades with your money!")
    print("Type 'YES' to enable real trading, or press Enter for simulation mode:")
    
    confirmation = input().strip()
    
    bot = RealTradingBot()
    
    if confirmation == 'YES':
        bot.trading_enabled = True
        logger.info("🔴 REAL TRADING ENABLED - Bot will execute real trades!")
    else:
        bot.trading_enabled = False
        logger.info("🔸 SIMULATION MODE - No real trades will be executed")
    
    # Initialize exchanges
    if not await bot.initialize_exchanges():
        logger.error("Failed to initialize exchanges")
        return
    
    # Show current balances
    logger.info("\n💰 Current Balances:")
    total_balance = 0
    for exchange, balance in bot.balances.items():
        logger.info(f"  {exchange}: ${balance:.2f} USDT")
        total_balance += balance
    logger.info(f"  TOTAL: ${total_balance:.2f} USDT")
    
    if total_balance < 10:
        logger.warning("⚠️  Low balance detected. Add funds to exchanges for trading.")
    
    # Start trading
    await bot.run_real_trading_loop()

if __name__ == "__main__":
    asyncio.run(main())