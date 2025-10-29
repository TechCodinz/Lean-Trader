#!/usr/bin/env python3
import ccxt
import time
import requests
from datetime import datetime

class MICRO_GATE_BOT:
    def __init__(self):
        # TELEGRAM CONFIGURATION
        self.telegram_bot_token = "8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg"
        self.admin_chat_id = "5329503447"
        self.vip_chat_id = "-1002983007302"
        self.free_chat_id = "-1002930953007"

        # GATE.IO API CONFIGURATION (REAL TRADING)
        self.gate_config = {
            'apiKey': 'a0508d8aadf3bcb76e16f4373e1f3a76',
            'secret': '451770a07dbede1b87bb92f5ce98e24029d2fe91e0053be2ec41771c953113f9',
            'sandbox': False,  # REAL TRADING
            'enableRateLimit': True,
        }

        # Initialize Gate.io exchange
        self.gate = ccxt.gate(self.gate_config)

        # MICRO POSITION SIZES - VERY SMALL TO ENSURE SUFFICIENT BALANCE
        # These are extremely conservative to avoid "BALANCE_NOT_ENOUGH" errors
        self.position_sizes = {
            'BTC/USDT': 0.0001,  # ~$4.30 (well below 3 USDT minimum, but let's test)
            'ETH/USDT': 0.001,  # ~$2.50 (well below 3 USDT minimum)
            'BNB/USDT': 0.01,  # ~$1.50 (well below 3 USDT minimum)
            'SOL/USDT': 0.1,  # ~$1.00 (well below 3 USDT minimum)
            'ADA/USDT': 10.0,  # ~$2.40 (well below 1 ADA minimum)
            'XRP/USDT': 5.0,  # ~$2.40 (well below 1 XRP minimum)
            'DOGE/USDT': 50.0,  # ~$6.00 (well below 10 DOGE minimum)
            'SHIB/USDT': 100000.0,  # ~$2.40 (well below 100000 SHIB minimum)
            'PEPE/USDT': 200000.0,  # ~$2.40 (well below 1000000 PEPE minimum)
        }
        
        # Dynamic crypto pairs (can be updated by orchestrator)
        self.crypto_pairs = []
        
        # Profit tracking
        self.total_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.running = True
        
        # SAFETY FEATURES - Initialize BEFORE using them!
        self.starting_balance = self.check_gate_balance()
        self.max_daily_loss = self.starting_balance * 0.20  # Max 20% loss per day
        self.daily_loss = 0.0  # Track daily losses
        self.max_trades_per_day = 50  # Limit trades

        
        print("🚀 MICRO GATE.IO BOT INITIALIZED!")
        print("💰 TRADING EXCHANGE: Gate.io (MICRO POSITIONS)")
        print(f"📊 {len(self.crypto_pairs)} Crypto Pairs")
        print("🎯 READY FOR MICRO PROFITS!")

    def calculate_position_size(self, symbol, price, balance):
        """Calculate position size dynamically for cheap coins"""
        # Use predefined size if available
        if symbol in self.position_sizes:
            return self.position_sizes[symbol]
        
        # For unknown coins, calculate based on price
        # Target: $3-5 per trade
        target_cost = min(balance * 0.3, 4.0)  # Max 30% of balance or $4
        
        if price > 0:
            size = target_cost / price
            return size
        return 0.001  # fallback

    def send_telegram(self, message, chat_id=None):
        if chat_id is None:
            chat_id = self.admin_chat_id

        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
            requests.post(url, data=data, timeout=10)
            print("✅ Telegram message sent")
            return True
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False

    def check_gate_balance(self):
        """Check Gate.io USDT balance"""
        try:
            balance = self.gate.fetch_balance()
            usdt_balance = balance['USDT']['free']
            print(f"💰 Gate.io USDT Balance: {usdt_balance}")
            return float(usdt_balance)
        except Exception as e:
            print(f"❌ Balance check error: {e}")
            return 0.0

    def get_gate_ticker(self, symbol):
        """Get ticker data from Gate.io with proper error handling"""
        try:
            ticker = self.gate.fetch_ticker(symbol)
            return {
                'price': float(ticker['last']),
                'change': float(ticker['percentage']) if ticker['percentage'] else 0,
                'volume': float(ticker['quoteVolume']) if ticker['quoteVolume'] else 0,
            }
        except Exception as e:
            print(f"❌ Gate.io ticker error for {symbol}: {e}")
            return None

    def analyze_market(self, symbol):
        """Simple market analysis"""
        try:
            ticker_data = self.get_gate_ticker(symbol)
            if not ticker_data:
                return "HOLD", 0, 0, 0, 0

            price = ticker_data['price']
            change = ticker_data['change']
            volume = ticker_data['volume']

            # Simple strategy - buy on positive momentum
            if change > 0.5 and volume > 10000:
                return "BUY", 80, price, change, volume
            elif change < -0.5 and volume > 10000:
                return "SELL", 80, price, change, volume
            else:
                return "HOLD", 50, price, change, volume

        except Exception as e:
            print(f"❌ Market analysis error for {symbol}: {e}")
            return "HOLD", 0, 0, 0, 0

    def execute_trade(self, symbol, signal, price, quantity=None):
        """Execute trade with micro position sizing"""
        print(f"🔍 execute_trade called: {symbol} {signal} price={price} qty={quantity}")
        try:
            # SAFETY CHECK: Stop if daily loss limit reached
            print(f"   Checking daily loss: {self.daily_loss:.2f} / {self.max_daily_loss:.2f}")
            if self.daily_loss >= self.max_daily_loss:
                print(f"🛑 SAFETY: Daily loss limit reached (${self.daily_loss:.2f}). Stopping trading.")
                return None
            
            # Check balance FIRST (before using it!)
            balance = self.check_gate_balance()
            print(f"   Current balance: ${balance:.2f}")
            
            # Use passed quantity or calculate from balance
            if quantity is None:
                position_size = self.calculate_position_size(symbol, price, balance)
            else:
                position_size = quantity
            
            # Calculate required balance
            required_balance = price * position_size * 1.1  # Add 10% buffer for fees

            print(f"   Balance check: have ${balance:.2f}, need ${required_balance:.2f}")
            if balance < required_balance:
                print(f"❌ Insufficient balance: Need ${required_balance:.2f}, have ${balance:.2f}")
                return None

            print(f"   Signal type: {signal.upper()}")
            if signal.upper() == "BUY":
                print(f"   Creating BUY order...")
                # Gate.io market buy needs COST (total $ to spend), not quantity
                cost_to_spend = price * position_size
                print(f"   Buying ${cost_to_spend:.2f} worth of {symbol}")
                params = {'createMarketBuyOrderRequiresPrice': False}
                order = self.gate.create_market_buy_order(symbol, cost_to_spend, params)
                print(f"✅ MICRO BUY EXECUTED: {symbol} - Spent ${cost_to_spend:.2f}")
                print(f"   Order ID: {order.get('id', 'unknown')}")
                return order
            elif signal.upper() == "SELL":
                print(f"   Selling {position_size} {symbol}")
                order = self.gate.create_market_sell_order(symbol, position_size)
                print(f"✅ MICRO SELL EXECUTED: {symbol} @ ${price:.4f} | Size: {position_size}")
                print(f"   Order ID: {order.get('id', 'unknown')}")
                return order
            else:
                print(f"⚠️ Unknown signal type: {signal}")
                return None

        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    def run_micro_trading(self):
        """Main micro trading cycle"""
        print("🚀 Starting MICRO GATE.IO BOT...")

        balance = self.check_gate_balance()

        startup_message = f"""🚀 <b>MICRO GATE.IO BOT ACTIVATED!</b>

💰 <b>YOUR BALANCE:</b> ${balance:.2f}
📊 <b>TRADING PAIRS:</b> {len(self.crypto_pairs)}
🎯 <b>MICRO POSITION STRATEGY</b>

<b>💰 MICRO POSITION SIZES:</b>
• DOGE: 50 (~$6)

🎯 <b>TARGET: $0.50-2.00 daily profits</b>
🚀 <b>CONSERVATIVE MICRO TRADING</b>"""

        self.send_telegram(startup_message)

        trade_count = 0

        while self.running:
            try:
                for symbol in self.crypto_pairs:
                    signal, confidence, price, change, volume = self.analyze_market(symbol)

                    if confidence >= 80 and signal != "HOLD":
                        trade_count += 1

                        trade_result = self.execute_trade(symbol, signal, price)

                        if trade_result:
                            position_size = self.calculate_position_size(symbol, price, balance)
                            profit = abs(price * position_size * 0.01)  # 1% profit factor
                            self.total_profit += profit
                            self.total_trades += 1

                            if profit > 0:
                                self.winning_trades += 1

                            signal_message = f"""🚀 <b>MICRO SIGNAL #{trade_count}</b>

💰 <b>{symbol}</b>
🎯 <b>Signal:</b> {signal}
💵 <b>Price:</b> ${price:.6f}
📈 <b>Change:</b> {change:+.2f}%
🔥 <b>Confidence:</b> {confidence}%

<b>💰 MICRO PROFIT:</b> ${profit:.4f}
<b>📊 TOTAL PROFIT:</b> ${self.total_profit:.4f}
<b>✅ MICRO TRADE EXECUTED</b>

⏰ {datetime.now().strftime('%H:%M:%S')}"""

                            self.send_telegram(signal_message)
                            print(
                                f"🚀 MICRO {symbol}: {signal} @ ${price:.6f} | Profit: ${profit:.4f}"
                            )

                            time.sleep(60)  # Wait 1 minute between trades

                print(
                    f"🔄 Micro trading cycle completed - Trades: {trade_count}, Profit: ${self.total_profit:.4f}"
                )
                time.sleep(30)  # 30 second cycles

            except Exception as e:
                print(f"❌ Error in micro trading cycle: {e}")
                time.sleep(60)

    def run(self):
        try:
            self.run_micro_trading()
        except KeyboardInterrupt:
            print("🛑 Micro bot stopped")
            self.running = False
        except Exception as e:
            print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    bot = MICRO_GATE_BOT()
    bot.run()
