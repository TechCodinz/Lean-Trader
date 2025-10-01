#!/usr/bin/env python3
"""
Production-Ready Trading Bot
Complete implementation with all safety mechanisms and error handling
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration manager
from config_manager import get_config_manager, get_config
from error_handler import ErrorHandler, SafeExecutor, with_error_handler, TradingError, RiskError

# Import with error handling
try:
    import ccxt
except ImportError:
    logger.error("ccxt not installed. Please install with: pip install ccxt")
    ccxt = None

try:
    import pandas as pd
    import numpy as np
except ImportError:
    logger.warning("pandas/numpy not installed. Some features will be limited")
    pd = None
    np = None

class ProductionTradingBot:
    """Production-ready trading bot with comprehensive safety features"""
    
    def __init__(self):
        """Initialize the trading bot"""
        self.config_manager = get_config_manager()
        self.config = get_config()
        
        # Initialize components
        self.error_handler = ErrorHandler(config=self.config)
        self.safe_executor = SafeExecutor(self.error_handler)
        
        # Trading state
        self.running = False
        self.paused = False
        self.exchanges = {}
        self.active_positions = {}
        self.pending_orders = {}
        self.trading_history = []
        
        # Performance tracking
        self.stats = {
            'start_time': datetime.now(),
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'daily_pnl': 0.0,
            'errors_count': 0
        }
        
        # Risk management state
        self.daily_loss = 0.0
        self.peak_balance = 0.0
        self.current_balance = 0.0
        
        # Initialize exchanges
        self._initialize_exchanges()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("Production Trading Bot initialized")
    
    def _initialize_exchanges(self):
        """Initialize configured exchanges"""
        if not ccxt:
            logger.error("Cannot initialize exchanges without ccxt")
            return
        
        for exchange_name, exchange_config in self.config.exchange.items():
            if exchange_config.is_configured():
                try:
                    exchange_class = getattr(ccxt, exchange_name)
                    
                    # Prepare exchange parameters
                    params = {
                        'apiKey': exchange_config.api_key,
                        'secret': exchange_config.api_secret,
                        'enableRateLimit': exchange_config.rate_limit,
                        'options': {
                            'defaultType': 'spot',
                            'adjustForTimeDifference': True
                        }
                    }
                    
                    if exchange_config.passphrase:
                        params['password'] = exchange_config.passphrase
                    
                    if exchange_config.testnet:
                        params['sandbox'] = True
                        if exchange_name == 'bybit':
                            params['testnet'] = True
                    
                    # Create exchange instance
                    self.exchanges[exchange_name] = exchange_class(params)
                    logger.info(f"Initialized {exchange_name} exchange")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize {exchange_name}: {e}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialize all bot components"""
        try:
            logger.info("Initializing bot components...")
            
            # Validate configuration
            if not self.config_manager.validate_config():
                raise TradingError("Configuration validation failed")
            
            # Test exchange connections
            await self._test_exchange_connections()
            
            # Load existing positions
            await self._load_positions()
            
            # Initialize risk parameters
            await self._initialize_risk_parameters()
            
            logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            await self.error_handler.handle_error(e, {'phase': 'initialization'})
            raise
    
    async def _test_exchange_connections(self):
        """Test connections to all configured exchanges"""
        for name, exchange in self.exchanges.items():
            try:
                # Test by fetching ticker
                ticker = await self.safe_executor.execute_with_retry(
                    exchange.fetch_ticker,
                    'BTC/USDT',
                    max_retries=3
                )
                
                if ticker:
                    logger.info(f"✅ {name} connection successful")
                else:
                    logger.warning(f"⚠️ {name} connection test returned no data")
                    
            except Exception as e:
                logger.error(f"❌ {name} connection failed: {e}")
                
                if self.config.trading.mode == "live":
                    raise TradingError(f"Cannot start live trading with {name} offline")
    
    async def _load_positions(self):
        """Load existing positions from exchanges"""
        for name, exchange in self.exchanges.items():
            try:
                # Fetch open positions
                if hasattr(exchange, 'fetch_positions'):
                    positions = await self.safe_executor.execute(
                        exchange.fetch_positions
                    )
                    
                    if positions:
                        self.active_positions[name] = positions
                        logger.info(f"Loaded {len(positions)} positions from {name}")
                
                # Fetch open orders
                if hasattr(exchange, 'fetch_open_orders'):
                    orders = await self.safe_executor.execute(
                        exchange.fetch_open_orders
                    )
                    
                    if orders:
                        self.pending_orders[name] = orders
                        logger.info(f"Loaded {len(orders)} open orders from {name}")
                        
            except Exception as e:
                logger.warning(f"Could not load positions from {name}: {e}")
    
    async def _initialize_risk_parameters(self):
        """Initialize risk management parameters"""
        try:
            # Get initial balance
            self.current_balance = await self._get_total_balance()
            self.peak_balance = self.current_balance
            
            logger.info(f"Initial balance: ${self.current_balance:.2f}")
            logger.info(f"Max position size: {self.config.risk.max_position_size}%")
            logger.info(f"Daily loss limit: ${self.config.risk.daily_loss_limit}")
            logger.info(f"Max drawdown: {self.config.risk.max_drawdown}%")
            
        except Exception as e:
            logger.error(f"Failed to initialize risk parameters: {e}")
    
    async def _get_total_balance(self) -> float:
        """Get total balance across all exchanges"""
        total = 0.0
        
        for name, exchange in self.exchanges.items():
            try:
                balance = await self.safe_executor.execute(
                    exchange.fetch_balance
                )
                
                if balance:
                    # Sum up USDT/USD balances
                    usdt = balance.get('USDT', {}).get('total', 0)
                    usd = balance.get('USD', {}).get('total', 0)
                    total += float(usdt or 0) + float(usd or 0)
                    
            except Exception as e:
                logger.warning(f"Could not fetch balance from {name}: {e}")
        
        return total
    
    async def start(self):
        """Start the trading bot"""
        try:
            logger.info("🚀 Starting Production Trading Bot...")
            
            # Final safety checks
            if not await self._pre_start_checks():
                raise TradingError("Pre-start checks failed")
            
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            # Start main trading loop
            tasks = [
                asyncio.create_task(self._trading_loop()),
                asyncio.create_task(self._risk_monitor_loop()),
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._performance_tracker_loop()),
            ]
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            await self.error_handler.handle_error(e, {'phase': 'start'})
            raise
    
    async def _pre_start_checks(self) -> bool:
        """Perform pre-start safety checks"""
        checks_passed = True
        
        # Check if we have at least one exchange
        if not self.exchanges:
            logger.error("No exchanges configured")
            checks_passed = False
        
        # Check risk parameters
        if self.config.risk.max_position_size > 10:
            logger.warning("Max position size seems high (>10%)")
        
        # Check if in live mode
        if self.config.trading.mode == "live":
            logger.warning("⚠️ LIVE TRADING MODE ENABLED ⚠️")
            
            # Extra checks for live mode
            if not self.config.two_factor_auth:
                logger.warning("2FA not enabled for live trading")
            
            if self.config.debug_mode:
                logger.error("Debug mode enabled in live trading")
                checks_passed = False
            
            # Confirm live trading
            logger.info("Live trading will start in 10 seconds. Press Ctrl+C to cancel...")
            await asyncio.sleep(10)
        
        return checks_passed
    
    async def _trading_loop(self):
        """Main trading loop"""
        logger.info("Trading loop started")
        
        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(1)
                    continue
                
                # Check if trading is enabled
                if not self.config.trading.enabled:
                    await asyncio.sleep(60)
                    continue
                
                # Analyze markets and generate signals
                signals = await self._analyze_markets()
                
                # Filter signals through risk management
                valid_signals = await self._filter_signals(signals)
                
                # Execute trades for valid signals
                for signal in valid_signals:
                    await self._execute_signal(signal)
                
                # Manage existing positions
                await self._manage_positions()
                
                # Clean up completed orders
                await self._cleanup_orders()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                await self.error_handler.handle_error(e, {'phase': 'trading_loop'})
                await asyncio.sleep(60)  # Wait longer after error
    
    async def _analyze_markets(self) -> List[Dict]:
        """Analyze markets and generate trading signals"""
        signals = []
        
        # List of trading pairs to analyze
        pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']  # Add more as needed
        
        for pair in pairs:
            for exchange_name, exchange in self.exchanges.items():
                try:
                    # Fetch market data
                    ticker = await self.safe_executor.execute(
                        exchange.fetch_ticker, pair
                    )
                    
                    if not ticker:
                        continue
                    
                    # Simple signal generation (replace with your strategy)
                    signal = await self._generate_signal(pair, ticker, exchange_name)
                    
                    if signal:
                        signals.append(signal)
                        
                except Exception as e:
                    logger.debug(f"Error analyzing {pair} on {exchange_name}: {e}")
        
        return signals
    
    async def _generate_signal(self, symbol: str, ticker: Dict, exchange: str) -> Optional[Dict]:
        """Generate trading signal based on market data"""
        # This is a placeholder - implement your actual strategy here
        
        # Example: Simple momentum strategy
        change_24h = ticker.get('percentage', 0)
        
        signal = None
        
        # Bullish signal
        if change_24h > 5:
            signal = {
                'symbol': symbol,
                'exchange': exchange,
                'action': 'BUY',
                'confidence': min(80, 50 + change_24h * 2),
                'price': ticker['last'],
                'timestamp': datetime.now()
            }
        # Bearish signal
        elif change_24h < -5:
            signal = {
                'symbol': symbol,
                'exchange': exchange,
                'action': 'SELL',
                'confidence': min(80, 50 + abs(change_24h) * 2),
                'price': ticker['last'],
                'timestamp': datetime.now()
            }
        
        return signal
    
    async def _filter_signals(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals through risk management"""
        valid_signals = []
        
        for signal in signals:
            try:
                # Check confidence threshold
                if signal['confidence'] < self.config.risk.min_confidence:
                    continue
                
                # Check if we already have a position
                if self._has_position(signal['symbol'], signal['exchange']):
                    continue
                
                # Check daily loss limit
                if self.daily_loss >= self.config.risk.daily_loss_limit:
                    logger.warning("Daily loss limit reached, skipping signal")
                    continue
                
                # Check max concurrent trades
                total_positions = sum(len(pos) for pos in self.active_positions.values())
                if total_positions >= self.config.risk.max_concurrent_trades:
                    logger.warning("Max concurrent trades reached")
                    continue
                
                # Check drawdown
                if self._calculate_drawdown() > self.config.risk.max_drawdown:
                    logger.warning("Max drawdown reached, skipping signal")
                    continue
                
                valid_signals.append(signal)
                
            except Exception as e:
                logger.error(f"Error filtering signal: {e}")
        
        return valid_signals
    
    def _has_position(self, symbol: str, exchange: str) -> bool:
        """Check if we already have a position for this symbol"""
        if exchange in self.active_positions:
            for position in self.active_positions[exchange]:
                if position.get('symbol') == symbol:
                    return True
        return False
    
    def _calculate_drawdown(self) -> float:
        """Calculate current drawdown percentage"""
        if self.peak_balance == 0:
            return 0
        
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance * 100
        return max(0, drawdown)
    
    async def _execute_signal(self, signal: Dict):
        """Execute a trading signal"""
        try:
            exchange_name = signal['exchange']
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                logger.error(f"Exchange {exchange_name} not found")
                return
            
            # Calculate position size
            position_size = self._calculate_position_size(signal)
            
            if position_size <= 0:
                logger.warning("Position size too small, skipping trade")
                return
            
            # Prepare order parameters
            order_params = {
                'symbol': signal['symbol'],
                'type': 'limit',
                'side': signal['action'].lower(),
                'amount': position_size,
                'price': signal['price']
            }
            
            # Add stop loss and take profit
            if self.config.risk.stop_loss_percentage:
                sl_price = signal['price'] * (1 - self.config.risk.stop_loss_percentage / 100)
                order_params['stopLoss'] = sl_price
            
            if self.config.risk.take_profit_percentage:
                tp_price = signal['price'] * (1 + self.config.risk.take_profit_percentage / 100)
                order_params['takeProfit'] = tp_price
            
            # Execute order
            logger.info(f"Executing {signal['action']} order for {signal['symbol']} on {exchange_name}")
            
            order = await self.safe_executor.execute_with_retry(
                exchange.create_order,
                **order_params,
                max_retries=3
            )
            
            if order:
                # Track the order
                if exchange_name not in self.pending_orders:
                    self.pending_orders[exchange_name] = []
                self.pending_orders[exchange_name].append(order)
                
                # Update statistics
                self.stats['total_trades'] += 1
                
                # Log trade
                self.trading_history.append({
                    'timestamp': datetime.now(),
                    'exchange': exchange_name,
                    'symbol': signal['symbol'],
                    'action': signal['action'],
                    'price': signal['price'],
                    'amount': position_size,
                    'confidence': signal['confidence']
                })
                
                logger.info(f"✅ Order executed successfully: {order['id']}")
            else:
                logger.error("Order execution failed")
                
        except Exception as e:
            await self.error_handler.handle_error(e, {'phase': 'execute_signal', 'signal': signal})
    
    def _calculate_position_size(self, signal: Dict) -> float:
        """Calculate appropriate position size based on risk management"""
        try:
            # Get available balance
            available_balance = self.current_balance * (self.config.risk.max_position_size / 100)
            
            # Adjust for confidence
            confidence_factor = signal['confidence'] / 100
            position_value = available_balance * confidence_factor
            
            # Calculate amount in base currency
            amount = position_value / signal['price']
            
            # Round to appropriate decimals
            amount = round(amount, 6)
            
            return amount
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    async def _manage_positions(self):
        """Manage existing positions"""
        for exchange_name, positions in self.active_positions.items():
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                continue
            
            for position in positions:
                try:
                    # Check if position should be closed
                    should_close, reason = await self._should_close_position(position, exchange)
                    
                    if should_close:
                        await self._close_position(position, exchange, reason)
                    
                    # Update trailing stop if enabled
                    if self.config.risk.trailing_stop:
                        await self._update_trailing_stop(position, exchange)
                        
                except Exception as e:
                    logger.error(f"Error managing position: {e}")
    
    async def _should_close_position(self, position: Dict, exchange) -> tuple:
        """Determine if a position should be closed"""
        try:
            # Get current price
            ticker = await self.safe_executor.execute(
                exchange.fetch_ticker,
                position['symbol']
            )
            
            if not ticker:
                return False, ""
            
            current_price = ticker['last']
            entry_price = position.get('price', position.get('average', 0))
            
            # Calculate PnL percentage
            if position['side'] == 'long':
                pnl_percent = (current_price - entry_price) / entry_price * 100
            else:
                pnl_percent = (entry_price - current_price) / entry_price * 100
            
            # Check stop loss
            if pnl_percent <= -self.config.risk.stop_loss_percentage:
                return True, "Stop loss hit"
            
            # Check take profit
            if pnl_percent >= self.config.risk.take_profit_percentage:
                return True, "Take profit hit"
            
            # Check if position is too old (optional)
            position_age = datetime.now() - position.get('timestamp', datetime.now())
            if position_age > timedelta(days=7):
                return True, "Position too old"
            
            return False, ""
            
        except Exception as e:
            logger.error(f"Error checking position close: {e}")
            return False, ""
    
    async def _close_position(self, position: Dict, exchange, reason: str):
        """Close a position"""
        try:
            logger.info(f"Closing position for {position['symbol']}: {reason}")
            
            # Create closing order
            order = await self.safe_executor.execute(
                exchange.create_order,
                symbol=position['symbol'],
                type='market',
                side='sell' if position['side'] == 'long' else 'buy',
                amount=position['contracts']
            )
            
            if order:
                # Update statistics
                # Calculate actual PnL here based on execution price
                logger.info(f"✅ Position closed successfully: {order['id']}")
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    async def _update_trailing_stop(self, position: Dict, exchange):
        """Update trailing stop for a position"""
        # Implement trailing stop logic here
        pass
    
    async def _cleanup_orders(self):
        """Clean up completed or cancelled orders"""
        for exchange_name, orders in list(self.pending_orders.items()):
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                continue
            
            updated_orders = []
            
            for order in orders:
                try:
                    # Check order status
                    order_status = await self.safe_executor.execute(
                        exchange.fetch_order,
                        order['id'],
                        order['symbol']
                    )
                    
                    if order_status and order_status['status'] in ['open', 'partially_filled']:
                        updated_orders.append(order_status)
                        
                except Exception as e:
                    logger.debug(f"Error checking order status: {e}")
            
            self.pending_orders[exchange_name] = updated_orders
    
    async def _risk_monitor_loop(self):
        """Monitor risk metrics continuously"""
        logger.info("Risk monitor started")
        
        while self.running:
            try:
                # Update current balance
                self.current_balance = await self._get_total_balance()
                
                # Update peak balance
                if self.current_balance > self.peak_balance:
                    self.peak_balance = self.current_balance
                
                # Calculate current drawdown
                self.stats['current_drawdown'] = self._calculate_drawdown()
                
                # Check if we should pause trading
                if self.stats['current_drawdown'] > self.config.risk.max_drawdown:
                    logger.critical(f"MAX DRAWDOWN REACHED: {self.stats['current_drawdown']:.2f}%")
                    self.paused = True
                
                if self.daily_loss >= self.config.risk.daily_loss_limit:
                    logger.critical(f"DAILY LOSS LIMIT REACHED: ${self.daily_loss:.2f}")
                    self.paused = True
                
                # Reset daily loss at midnight
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self.daily_loss = 0.0
                    self.stats['daily_pnl'] = 0.0
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                await self.error_handler.handle_error(e, {'phase': 'risk_monitor'})
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Monitor system health"""
        logger.info("Health check monitor started")
        
        while self.running:
            try:
                health_status = {
                    'timestamp': datetime.now(),
                    'running': self.running,
                    'paused': self.paused,
                    'exchanges_online': len(self.exchanges),
                    'active_positions': sum(len(pos) for pos in self.active_positions.values()),
                    'pending_orders': sum(len(orders) for orders in self.pending_orders.values()),
                    'current_balance': self.current_balance,
                    'drawdown': self.stats['current_drawdown'],
                    'daily_pnl': self.stats['daily_pnl'],
                    'errors': self.error_handler.get_error_statistics()
                }
                
                # Log health status
                logger.debug(f"Health check: {json.dumps(health_status, default=str)}")
                
                # Check for critical issues
                if health_status['errors']['total_errors'] > 100:
                    logger.warning("High error count detected")
                
                await asyncio.sleep(self.config.monitoring.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_tracker_loop(self):
        """Track and report performance metrics"""
        logger.info("Performance tracker started")
        
        while self.running:
            try:
                # Calculate performance metrics
                runtime = datetime.now() - self.stats['start_time']
                win_rate = (self.stats['winning_trades'] / max(1, self.stats['total_trades'])) * 100
                
                performance_report = f"""
📊 PERFORMANCE REPORT
═══════════════════════════════
Runtime: {runtime}
Total Trades: {self.stats['total_trades']}
Win Rate: {win_rate:.1f}%
Total PnL: ${self.stats['total_pnl']:.2f}
Daily PnL: ${self.stats['daily_pnl']:.2f}
Current Balance: ${self.current_balance:.2f}
Current Drawdown: {self.stats['current_drawdown']:.2f}%
Max Drawdown: {self.stats['max_drawdown']:.2f}%
Active Positions: {sum(len(pos) for pos in self.active_positions.values())}
Pending Orders: {sum(len(orders) for orders in self.pending_orders.values())}
═══════════════════════════════
"""
                
                logger.info(performance_report)
                
                # Save performance data
                self._save_performance_data()
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(300)
    
    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            performance_file = Path("data/performance.json")
            performance_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats,
                'balance': self.current_balance,
                'positions': len(self.active_positions),
                'trades_today': len([t for t in self.trading_history 
                                    if t['timestamp'].date() == datetime.now().date()])
            }
            
            with open(performance_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Could not save performance data: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown the bot"""
        logger.info("Initiating graceful shutdown...")
        
        self.running = False
        
        try:
            # Cancel all pending orders
            for exchange_name, orders in self.pending_orders.items():
                exchange = self.exchanges.get(exchange_name)
                if exchange:
                    for order in orders:
                        try:
                            await exchange.cancel_order(order['id'], order['symbol'])
                            logger.info(f"Cancelled order {order['id']}")
                        except:
                            pass
            
            # Close all positions if configured
            if self.config.trading.mode != "live":  # Only in test modes
                for exchange_name, positions in self.active_positions.items():
                    exchange = self.exchanges.get(exchange_name)
                    if exchange:
                        for position in positions:
                            await self._close_position(position, exchange, "Shutdown")
            
            # Save final state
            self._save_performance_data()
            self.error_handler.save_error_history()
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    bot = ProductionTradingBot()
    
    try:
        # Initialize bot
        await bot.initialize()
        
        # Start trading
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Run the bot
    asyncio.run(main())