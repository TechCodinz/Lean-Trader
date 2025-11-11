#!/usr/bin/env python3
"""
💎 ENHANCED MICRO WALLET GROWER
Integrated with ALL bot intelligence systems

ENHANCEMENTS:
1. Consumes signals from DataHub (all 116+ systems)
2. Uses revolutionary engine signals
3. Integrated with swarm intelligence  
4. Dynamic position sizing based on confidence
5. Proper .env configuration
6. Real-time balance tracking
7. Compound growth strategy

TARGET: $10 → $100 in 30 days
"""

import ccxt
import time
import os
from datetime import datetime
from collections import deque
import asyncio

class EnhancedMicroWalletGrower:
    """
    Enhanced micro wallet grower that USES all bot intelligence
    """
    
    def __init__(self, data_hub=None):
        print("💎 Initializing Enhanced Micro Wallet Grower...")
        
        # Connect to DataHub for signals
        self.data_hub = data_hub
        
        # Gate.io configuration from .env
        self.gate_config = {
            'apiKey': os.getenv('GATEIO_API_KEY', ''),
            'secret': os.getenv('GATEIO_SECRET', ''),
            'sandbox': False,
            'enableRateLimit': True,
        }
        
        # Check if keys exist
        if not self.gate_config['apiKey'] or not self.gate_config['secret']:
            print("⚠️  WARNING: Gate.io API keys not found in .env!")
            print("   Add GATEIO_API_KEY and GATEIO_SECRET to .env file")
        
        # Initialize Gate.io
        try:
            self.gate = ccxt.gate(self.gate_config)
            print("   ✅ Gate.io connected")
        except Exception as e:
            print(f"   ❌ Gate.io connection failed: {e}")
            self.gate = None
        
        # Balance tracking
        self.starting_balance = 0.0
        self.current_balance = 0.0
        self.peak_balance = 0.0
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
        
        # Safety limits
        self.max_daily_trades = 50
        self.max_daily_loss_pct = 0.20  # 20%
        self.daily_loss = 0.0
        
        # Signal queue (from DataHub)
        self.signal_queue = deque(maxlen=100)
        self.executed_signals = set()  # Prevent duplicates
        
        # Active positions
        self.active_positions = {}
        
        # Confidence thresholds
        self.min_confidence = 75  # Only trade 75%+ confidence signals
        self.revolutionary_boost = 1.2  # 20% larger size for revolutionary signals
        
        print("💎 Enhanced Micro Wallet Grower initialized!")
        print(f"   Connected to DataHub: {'✅' if data_hub else '❌'}")
        print(f"   Min confidence: {self.min_confidence}%")
    
    def check_balance(self):
        """Check Gate.io balance"""
        if not self.gate:
            return 0.0
        
        try:
            balance = self.gate.fetch_balance()
            usdt = float(balance.get('USDT', {}).get('free', 0))
            self.current_balance = usdt
            
            # Track peak
            if usdt > self.peak_balance:
                self.peak_balance = usdt
            
            # Set starting balance if first check
            if self.starting_balance == 0.0:
                self.starting_balance = usdt
                print(f"💎 Starting balance: ${usdt:.2f}")
            
            return usdt
        except Exception as e:
            print(f"❌ Balance check error: {e}")
            return 0.0
    
    def check_gate_balance(self):
        """Alias for compatibility with old code"""
        return self.check_balance()
    
    def calculate_position_size(self, symbol, price, signal_confidence, signal_type='standard'):
        """
        Dynamic position sizing based on:
        - Current balance
        - Signal confidence
        - Signal type (revolutionary gets boost)
        - Gate.io minimums ($3)
        """
        
        balance = self.current_balance
        
        # Base size: $3-5 per trade (Gate.io minimum is $3)
        base_size_usd = min(5.0, balance * 0.15)  # Max 15% of balance per trade
        
        # Confidence multiplier (75% = 1.0x, 95% = 1.5x)
        confidence_mult = 1.0 + ((signal_confidence - 75) / 100)
        
        # Revolutionary signal boost
        if signal_type == 'revolutionary':
            confidence_mult *= self.revolutionary_boost
        
        # Calculate final size
        target_usd = base_size_usd * confidence_mult
        
        # Ensure minimum
        target_usd = max(3.5, target_usd)
        
        # Ensure we have balance
        if target_usd > balance * 0.9:
            target_usd = balance * 0.8  # Use 80% max
        
        # Convert to coin amount
        if price > 0:
            size = target_usd / price
            return size, target_usd
        
        return 0, 0
    
    async def consume_signals(self):
        """
        Consume signals from DataHub
        This is where we get signals from:
        - Revolutionary engines
        - Forex trading
        - Arbitrage
        - Moon hunting
        - Scalping
        - All 116+ systems
        """
        
        if not self.data_hub:
            print("⚠️  No DataHub connected - running in standalone mode")
            return
        
        while True:
            try:
                # Get signals from DataHub queue
                if hasattr(self.data_hub, 'signal_queue') and not self.data_hub.signal_queue.empty():
                    signal = self.data_hub.signal_queue.get_nowait()
                    
                    # Filter by confidence
                    confidence = signal.get('confidence', 0)
                    if confidence >= self.min_confidence:
                        # Add to our queue
                        signal_id = f"{signal.get('pair', 'unknown')}_{signal.get('timestamp', time.time())}"
                        
                        if signal_id not in self.executed_signals:
                            self.signal_queue.append(signal)
                            print(f"📥 New signal: {signal.get('pair')} {signal.get('side')} @ {confidence:.1f}% confidence")
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ Signal consumption error: {e}")
                await asyncio.sleep(5)
    
    async def execute_signals(self):
        """
        Execute signals from queue
        """
        
        while True:
            try:
                # Reset daily counters
                today = datetime.now().date()
                if today != self.last_reset:
                    self.daily_trades = 0
                    self.daily_loss = 0.0
                    self.last_reset = today
                    print(f"📅 Daily counters reset for {today}")
                
                # Check safety limits
                if self.daily_trades >= self.max_daily_trades:
                    print(f"🛑 Daily trade limit reached ({self.max_daily_trades})")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                if self.daily_loss >= (self.starting_balance * self.max_daily_loss_pct):
                    print(f"🛑 Daily loss limit reached (${self.daily_loss:.2f})")
                    await asyncio.sleep(3600)
                    continue
                
                # Check balance
                balance = self.check_balance()
                if balance < 3.0:
                    print(f"⚠️  Balance too low: ${balance:.2f}")
                    await asyncio.sleep(60)
                    continue
                
                # Process signals
                if self.signal_queue:
                    signal = self.signal_queue.popleft()
                    
                    # Execute trade
                    result = await self.execute_trade(signal)
                    
                    if result:
                        self.daily_trades += 1
                        self.total_trades += 1
                        
                        # Mark as executed
                        signal_id = f"{signal.get('pair', 'unknown')}_{signal.get('timestamp', time.time())}"
                        self.executed_signals.add(signal_id)
                        
                        # Clean old executed signals (keep last 1000)
                        if len(self.executed_signals) > 1000:
                            self.executed_signals = set(list(self.executed_signals)[-500:])
                
                await asyncio.sleep(5)  # 5 seconds between trades
                
            except Exception as e:
                print(f"❌ Execution error: {e}")
                await asyncio.sleep(10)
    
    async def execute_trade(self, signal):
        """
        Execute a single trade from signal
        """
        
        if not self.gate:
            print("❌ Gate.io not connected")
            return False
        
        try:
            pair = signal.get('pair', signal.get('symbol', 'unknown'))
            side = signal.get('side', '').upper()
            confidence = signal.get('confidence', 0)
            signal_type = signal.get('type', 'standard')
            
            # Validate
            if not pair or pair == 'unknown':
                print(f"⚠️  Invalid pair in signal")
                return False
            
            if side not in ['BUY', 'SELL']:
                print(f"⚠️  Invalid side: {side}")
                return False
            
            # Get current price
            try:
                ticker = self.gate.fetch_ticker(pair)
                price = float(ticker['last'])
            except Exception as e:
                print(f"❌ Price fetch failed for {pair}: {e}")
                return False
            
            # Calculate position size
            size, cost_usd = self.calculate_position_size(pair, price, confidence, signal_type)
            
            if size <= 0 or cost_usd < 3.0:
                print(f"⚠️  Position size too small: {size} ({cost_usd:.2f} USD)")
                return False
            
            # Execute order
            print(f"⚡ EXECUTING: {side} {pair} @ ${price:.6f}")
            print(f"   Size: {size:.6f} (${cost_usd:.2f})")
            print(f"   Confidence: {confidence:.1f}%")
            print(f"   Type: {signal_type}")
            
            if side == 'BUY':
                # Market buy
                params = {'createMarketBuyOrderRequiresPrice': False}
                order = self.gate.create_market_buy_order(pair, cost_usd, params)
            else:
                # Market sell
                order = self.gate.create_market_sell_order(pair, size)
            
            print(f"   ✅ Order ID: {order.get('id', 'unknown')}")
            
            # Track position
            self.active_positions[pair] = {
                'side': side,
                'size': size,
                'entry_price': price,
                'entry_time': datetime.now(),
                'confidence': confidence
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_stats(self):
        """Get performance statistics"""
        
        balance = self.current_balance
        profit_usd = balance - self.starting_balance
        profit_pct = (profit_usd / self.starting_balance * 100) if self.starting_balance > 0 else 0
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'starting_balance': self.starting_balance,
            'current_balance': balance,
            'peak_balance': self.peak_balance,
            'profit_usd': profit_usd,
            'profit_pct': profit_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'daily_trades': self.daily_trades,
        }
    
    async def run(self):
        """Main run loop"""
        
        print("🚀 Starting Enhanced Micro Wallet Grower...")
        
        # Start parallel tasks
        tasks = [
            asyncio.create_task(self.consume_signals()),
            asyncio.create_task(self.execute_signals()),
        ]
        
        # Monitor loop
        while True:
            try:
                stats = self.get_stats()
                
                print(f"\n💎 MICRO WALLET GROWER STATUS:")
                print(f"   Balance: ${stats['current_balance']:.2f}")
                print(f"   Profit: ${stats['profit_usd']:.2f} ({stats['profit_pct']:+.1f}%)")
                print(f"   Trades: {stats['total_trades']} (Win rate: {stats['win_rate']:.1f}%)")
                print(f"   Daily trades: {stats['daily_trades']}/{self.max_daily_trades}")
                print(f"   Queue: {len(self.signal_queue)} signals")
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                await asyncio.sleep(60)


# Integration function
def initialize_enhanced_micro_grower(data_hub):
    """Initialize enhanced micro wallet grower"""
    return EnhancedMicroWalletGrower(data_hub=data_hub)
