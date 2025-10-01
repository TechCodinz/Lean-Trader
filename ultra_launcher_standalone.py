#!/usr/bin/env python3
"""
ULTRA LAUNCHER STANDALONE - Zero Dependency Trading System
Complete standalone implementation that works without external packages
"""

import sys
import os
import asyncio
import argparse
import json
import signal
import logging
import random
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from collections import deque
import math

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ASCII Art Banner
BANNER = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   ██╗   ██╗██╗  ████████╗██████╗  █████╗     ████████╗██████╗  █████╗    ║
║   ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗   ║
║   ██║   ██║██║     ██║   ██████╔╝███████║       ██║   ██████╔╝███████║   ║
║   ██║   ██║██║     ██║   ██╔══██╗██╔══██║       ██║   ██╔══██╗██╔══██║   ║
║   ╚██████╔╝███████╗██║   ██║  ██║██║  ██║       ██║   ██║  ██║██║  ██║   ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ║
║                                                                            ║
║         STANDALONE ULTRA TRADING SYSTEM - ZERO DEPENDENCIES               ║
║                                                                            ║
║                    🧠 AI-Powered 🚀 Self-Evolving 💎 Ultra-Smart         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    volume: float
    change_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime
    
@dataclass
class Signal:
    """Trading signal structure"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    timestamp: datetime
    indicators: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class Position:
    """Trading position structure"""
    symbol: str
    side: str  # LONG, SHORT
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class MarketSimulator:
    """Simulates market data when real data is not available"""
    
    def __init__(self):
        self.base_prices = {
            'BTC/USDT': 50000.0,
            'ETH/USDT': 3000.0,
            'SOL/USDT': 150.0,
            'BNB/USDT': 400.0,
            'ADA/USDT': 0.5,
            'XRP/USDT': 0.6,
            'DOT/USDT': 8.0,
            'DOGE/USDT': 0.08,
        }
        self.price_history = {symbol: deque(maxlen=100) for symbol in self.base_prices}
        self.volatility = 0.02  # 2% volatility
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Generate simulated market data"""
        if symbol not in self.base_prices:
            self.base_prices[symbol] = 100.0
            self.price_history[symbol] = deque(maxlen=100)
        
        # Get base price
        base_price = self.base_prices[symbol]
        
        # Add some randomness
        trend = math.sin(time.time() / 3600) * 0.1  # Hourly trend
        noise = random.gauss(0, self.volatility)
        price_change = trend + noise
        
        # Calculate new price
        new_price = base_price * (1 + price_change)
        
        # Update base price with momentum
        self.base_prices[symbol] = self.base_prices[symbol] * 0.99 + new_price * 0.01
        
        # Store in history
        self.price_history[symbol].append(new_price)
        
        # Calculate 24h change
        if len(self.price_history[symbol]) > 20:
            old_price = self.price_history[symbol][-20]
            change_24h = ((new_price - old_price) / old_price) * 100
        else:
            change_24h = random.uniform(-5, 5)
        
        # Generate volume
        volume = random.uniform(1000000, 10000000) * (1 + abs(change_24h) / 10)
        
        # High/Low
        recent_prices = list(self.price_history[symbol])[-24:] if self.price_history[symbol] else [new_price]
        high_24h = max(recent_prices + [new_price])
        low_24h = min(recent_prices + [new_price])
        
        return MarketData(
            symbol=symbol,
            price=new_price,
            volume=volume,
            change_24h=change_24h,
            high_24h=high_24h,
            low_24h=low_24h,
            timestamp=datetime.now()
        )

class TechnicalAnalyzer:
    """Technical analysis without external libraries"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Exponential Moving Average"""
        if not prices:
            return 0
        if len(prices) < period:
            return TechnicalAnalyzer.calculate_sma(prices, len(prices))
        
        multiplier = 2 / (period + 1)
        ema = TechnicalAnalyzer.calculate_sma(prices[:period], period)
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """MACD indicator"""
        if len(prices) < 26:
            return 0, 0, 0
        
        ema_12 = TechnicalAnalyzer.calculate_ema(prices, 12)
        ema_26 = TechnicalAnalyzer.calculate_ema(prices, 26)
        
        macd_line = ema_12 - ema_26
        signal_line = TechnicalAnalyzer.calculate_ema([macd_line], 9)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return current_price, current_price, current_price
        
        sma = TechnicalAnalyzer.calculate_sma(prices, period)
        
        # Calculate standard deviation
        variance = sum((price - sma) ** 2 for price in prices[-period:]) / period
        std = math.sqrt(variance)
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band

class MLPredictor:
    """Simple ML predictor without sklearn"""
    
    def __init__(self):
        self.weights = {}
        self.learning_rate = 0.01
        self.momentum = 0.9
        self.prev_gradients = {}
    
    def predict(self, features: Dict[str, float]) -> float:
        """Make a prediction based on features"""
        # Initialize weights if needed
        for feature in features:
            if feature not in self.weights:
                self.weights[feature] = random.gauss(0, 0.1)
        
        # Calculate weighted sum with sigmoid activation
        weighted_sum = sum(self.weights.get(f, 0) * v for f, v in features.items())
        
        # Sigmoid activation
        prediction = 1 / (1 + math.exp(-weighted_sum))
        
        return prediction
    
    def update(self, features: Dict[str, float], actual: float):
        """Update weights based on actual outcome"""
        prediction = self.predict(features)
        error = actual - prediction
        
        # Gradient descent with momentum
        for feature, value in features.items():
            gradient = error * value * self.learning_rate
            
            if feature in self.prev_gradients:
                gradient += self.momentum * self.prev_gradients[feature]
            
            self.weights[feature] += gradient
            self.prev_gradients[feature] = gradient

class QuantumInspiredOptimizer:
    """Quantum-inspired optimization without qiskit"""
    
    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.superposition_states = 2 ** num_qubits
    
    def optimize(self, objective_function, iterations: int = 100) -> float:
        """Quantum-inspired optimization"""
        best_solution = None
        best_value = float('-inf')
        
        for _ in range(iterations):
            # Create superposition of states
            states = []
            for i in range(self.superposition_states):
                # Convert to binary representation
                state = format(i, f'0{self.num_qubits}b')
                states.append(state)
            
            # Evaluate each state
            for state in states:
                # Convert binary state to continuous value
                value = sum(int(bit) * (2 ** idx) for idx, bit in enumerate(state))
                value = value / (2 ** self.num_qubits)  # Normalize to [0, 1]
                
                # Evaluate objective function
                result = objective_function(value)
                
                if result > best_value:
                    best_value = result
                    best_solution = value
        
        return best_solution

class TradingStrategy:
    """Advanced trading strategy"""
    
    def __init__(self):
        self.ml_predictor = MLPredictor()
        self.quantum_optimizer = QuantumInspiredOptimizer()
        self.technical_analyzer = TechnicalAnalyzer()
    
    def analyze(self, market_data: MarketData, price_history: List[float]) -> Signal:
        """Analyze market and generate signal"""
        
        # Technical indicators
        indicators = {}
        
        if len(price_history) > 0:
            indicators['sma_20'] = self.technical_analyzer.calculate_sma(price_history, 20)
            indicators['ema_12'] = self.technical_analyzer.calculate_ema(price_history, 12)
            indicators['rsi'] = self.technical_analyzer.calculate_rsi(price_history)
            
            macd, signal, histogram = self.technical_analyzer.calculate_macd(price_history)
            indicators['macd'] = macd
            indicators['macd_signal'] = signal
            indicators['macd_histogram'] = histogram
            
            upper, middle, lower = self.technical_analyzer.calculate_bollinger_bands(price_history)
            indicators['bb_upper'] = upper
            indicators['bb_middle'] = middle
            indicators['bb_lower'] = lower
        
        # ML features
        features = {
            'price_normalized': market_data.price / 100000,
            'volume_normalized': market_data.volume / 10000000,
            'change_24h': market_data.change_24h / 100,
            'rsi': indicators.get('rsi', 50) / 100,
            'price_to_sma': market_data.price / indicators.get('sma_20', market_data.price) if indicators.get('sma_20') else 1,
        }
        
        # Get ML prediction
        ml_confidence = self.ml_predictor.predict(features)
        
        # Quantum-inspired optimization for entry timing
        def objective(x):
            return ml_confidence * (1 + x) - abs(market_data.change_24h) * x
        
        quantum_factor = self.quantum_optimizer.optimize(objective, iterations=10)
        
        # Generate signal
        action = 'HOLD'
        confidence = 50.0
        
        # RSI-based signals
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            action = 'BUY'
            confidence = 70 + (30 - rsi)
        elif rsi > 70:
            action = 'SELL'
            confidence = 70 + (rsi - 70)
        
        # MACD crossover
        if indicators.get('macd_histogram', 0) > 0 and action != 'SELL':
            action = 'BUY'
            confidence = max(confidence, 65 + abs(indicators['macd_histogram']) * 10)
        elif indicators.get('macd_histogram', 0) < 0 and action != 'BUY':
            action = 'SELL'
            confidence = max(confidence, 65 + abs(indicators['macd_histogram']) * 10)
        
        # Bollinger Bands
        if market_data.price < indicators.get('bb_lower', market_data.price):
            action = 'BUY'
            confidence = max(confidence, 75)
        elif market_data.price > indicators.get('bb_upper', market_data.price):
            action = 'SELL'
            confidence = max(confidence, 75)
        
        # Apply ML and quantum factors
        confidence = confidence * ml_confidence * (1 + quantum_factor * 0.1)
        confidence = min(95, confidence)  # Cap at 95%
        
        return Signal(
            symbol=market_data.symbol,
            action=action,
            confidence=confidence,
            price=market_data.price,
            timestamp=datetime.now(),
            indicators=indicators
        )

class RiskManager:
    """Risk management system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_position_size = config.get('max_position_size', 0.02)
        self.max_positions = config.get('max_positions', 5)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.05)
        self.max_drawdown = config.get('max_drawdown_pct', 0.20)
        self.daily_loss_limit = config.get('max_daily_loss', 100)
        self.current_positions = {}
        self.daily_pnl = 0
        self.peak_balance = 0
    
    def can_trade(self, signal: Signal, balance: float) -> bool:
        """Check if trade is allowed"""
        # Check position limit
        if len(self.current_positions) >= self.max_positions:
            return False
        
        # Check daily loss
        if self.daily_pnl < -self.daily_loss_limit:
            return False
        
        # Check drawdown
        if self.peak_balance > 0:
            drawdown = (self.peak_balance - balance) / self.peak_balance
            if drawdown > self.max_drawdown:
                return False
        
        # Check confidence threshold
        if signal.confidence < self.config.get('confidence_threshold', 65):
            return False
        
        return True
    
    def calculate_position_size(self, signal: Signal, balance: float) -> float:
        """Calculate appropriate position size"""
        # Risk-based sizing
        risk_amount = balance * self.max_position_size
        
        # Adjust for confidence
        confidence_factor = signal.confidence / 100
        position_value = risk_amount * confidence_factor
        
        # Calculate shares/units
        position_size = position_value / signal.price
        
        return round(position_size, 6)
    
    def get_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == 'LONG':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def get_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        if side == 'LONG':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

class DatabaseManager:
    """Simple database manager using SQLite"""
    
    def __init__(self, db_path: str = "ultra_trading.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize()
    
    def initialize(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                size REAL NOT NULL,
                price REAL NOT NULL,
                confidence REAL,
                pnl REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_pnl REAL,
                win_rate REAL,
                max_drawdown REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_trade(self, trade: Dict[str, Any]):
        """Save trade to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, action, size, price, confidence, pnl)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            trade['symbol'],
            trade['action'],
            trade['size'],
            trade['price'],
            trade.get('confidence', 0),
            trade.get('pnl', 0)
        ))
        self.conn.commit()
    
    def save_performance(self, performance: Dict[str, Any]):
        """Save performance metrics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO performance (total_trades, winning_trades, losing_trades, total_pnl, win_rate, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            performance['total_trades'],
            performance['winning_trades'],
            performance['losing_trades'],
            performance['total_pnl'],
            performance['win_rate'],
            performance['max_drawdown']
        ))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class UltraTrader:
    """Main trading engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        
        # Initialize components
        self.market_simulator = MarketSimulator()
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManager(config)
        self.db_manager = DatabaseManager()
        
        # Trading state
        self.positions = {}
        self.balance = config.get('initial_capital', 10000)
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0
        }
        
        # Price history for technical analysis
        self.price_history = {symbol: [] for symbol in config.get('symbols', [])}
    
    async def run(self):
        """Main trading loop"""
        self.running = True
        logger.info("🚀 Trading engine started")
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # Process each symbol
                for symbol in self.config.get('symbols', []):
                    # Get market data
                    market_data = self.market_simulator.get_market_data(symbol)
                    
                    # Update price history
                    if symbol not in self.price_history:
                        self.price_history[symbol] = []
                    self.price_history[symbol].append(market_data.price)
                    
                    # Keep only last 100 prices
                    if len(self.price_history[symbol]) > 100:
                        self.price_history[symbol] = self.price_history[symbol][-100:]
                    
                    # Generate signal
                    signal = self.strategy.analyze(market_data, self.price_history[symbol])
                    
                    # Check if we should trade
                    if signal.action != 'HOLD' and self.risk_manager.can_trade(signal, self.balance):
                        await self.execute_trade(signal)
                
                # Manage existing positions
                await self.manage_positions()
                
                # Display status every 10 iterations
                if iteration % 10 == 0:
                    self.display_status()
                
                # Save performance periodically
                if iteration % 50 == 0:
                    self.db_manager.save_performance(self.performance)
                
                # Sleep before next iteration
                await asyncio.sleep(self.config.get('update_interval', 5))
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(10)
    
    async def execute_trade(self, signal: Signal):
        """Execute a trade"""
        try:
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(signal, self.balance)
            
            if position_size <= 0:
                return
            
            # Determine side
            side = 'LONG' if signal.action == 'BUY' else 'SHORT'
            
            # Create position
            position = Position(
                symbol=signal.symbol,
                side=side,
                size=position_size,
                entry_price=signal.price,
                current_price=signal.price,
                unrealized_pnl=0,
                timestamp=datetime.now(),
                stop_loss=self.risk_manager.get_stop_loss(signal.price, side),
                take_profit=self.risk_manager.get_take_profit(signal.price, side)
            )
            
            # Store position
            self.positions[signal.symbol] = position
            self.risk_manager.current_positions[signal.symbol] = position
            
            # Update balance (deduct position value for simulation)
            position_value = position_size * signal.price
            self.balance -= position_value * 0.001  # 0.1% fee
            
            # Log trade
            trade = {
                'symbol': signal.symbol,
                'action': signal.action,
                'size': position_size,
                'price': signal.price,
                'confidence': signal.confidence
            }
            self.db_manager.save_trade(trade)
            
            self.performance['total_trades'] += 1
            
            logger.info(f"📈 Trade executed: {signal.action} {position_size:.4f} {signal.symbol} @ ${signal.price:.2f} (Confidence: {signal.confidence:.1f}%)")
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
    
    async def manage_positions(self):
        """Manage open positions"""
        for symbol, position in list(self.positions.items()):
            try:
                # Get current market data
                market_data = self.market_simulator.get_market_data(symbol)
                current_price = market_data.price
                
                # Update position
                position.current_price = current_price
                
                # Calculate PnL
                if position.side == 'LONG':
                    pnl_pct = (current_price - position.entry_price) / position.entry_price
                else:
                    pnl_pct = (position.entry_price - current_price) / position.entry_price
                
                position.unrealized_pnl = position.size * position.entry_price * pnl_pct
                
                # Check exit conditions
                should_close = False
                reason = ""
                
                if position.side == 'LONG':
                    if current_price <= position.stop_loss:
                        should_close = True
                        reason = "Stop Loss"
                    elif current_price >= position.take_profit:
                        should_close = True
                        reason = "Take Profit"
                else:
                    if current_price >= position.stop_loss:
                        should_close = True
                        reason = "Stop Loss"
                    elif current_price <= position.take_profit:
                        should_close = True
                        reason = "Take Profit"
                
                if should_close:
                    # Close position
                    self.balance += position.size * current_price * (1 - 0.001)  # 0.1% fee
                    
                    # Update performance
                    if position.unrealized_pnl > 0:
                        self.performance['winning_trades'] += 1
                    else:
                        self.performance['losing_trades'] += 1
                    
                    self.performance['total_pnl'] += position.unrealized_pnl
                    self.risk_manager.daily_pnl += position.unrealized_pnl
                    
                    # Calculate win rate
                    total = self.performance['winning_trades'] + self.performance['losing_trades']
                    if total > 0:
                        self.performance['win_rate'] = self.performance['winning_trades'] / total
                    
                    # Update max drawdown
                    if self.balance > self.risk_manager.peak_balance:
                        self.risk_manager.peak_balance = self.balance
                    
                    if self.risk_manager.peak_balance > 0:
                        drawdown = (self.risk_manager.peak_balance - self.balance) / self.risk_manager.peak_balance
                        self.performance['max_drawdown'] = max(self.performance['max_drawdown'], drawdown)
                    
                    logger.info(f"📊 Position closed: {symbol} - {reason} - PnL: {pnl_pct:.2%} (${position.unrealized_pnl:.2f})")
                    
                    # Remove position
                    del self.positions[symbol]
                    del self.risk_manager.current_positions[symbol]
                    
            except Exception as e:
                logger.error(f"Position management error for {symbol}: {e}")
    
    def display_status(self):
        """Display current status"""
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 TRADING STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        logger.info(f"💰 Balance: ${self.balance:.2f}")
        logger.info(f"📈 Total Trades: {self.performance['total_trades']}")
        logger.info(f"✅ Win Rate: {self.performance['win_rate']:.1%}")
        logger.info(f"💵 Total PnL: ${self.performance['total_pnl']:.2f}")
        logger.info(f"📉 Max Drawdown: {self.performance['max_drawdown']:.1%}")
        logger.info(f"🔄 Active Positions: {len(self.positions)}")
        
        if self.positions:
            logger.info("\n📋 Open Positions:")
            for symbol, pos in self.positions.items():
                pnl_pct = pos.unrealized_pnl / (pos.size * pos.entry_price) * 100 if pos.size > 0 else 0
                logger.info(f"  • {symbol}: {pos.side} - PnL: {pnl_pct:+.2f}% (${pos.unrealized_pnl:+.2f})")
        
        logger.info("=" * 60)
    
    def stop(self):
        """Stop trading"""
        self.running = False
        self.db_manager.close()
        logger.info("🛑 Trading engine stopped")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Ultra Trading System - Standalone Zero Dependency Version'
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
        help='Trading symbols'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        default=10000,
        help='Initial capital (default: $10000)'
    )
    
    parser.add_argument(
        '--risk',
        type=float,
        default=0.02,
        help='Risk per trade (default: 0.02 = 2%%)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=65,
        help='Minimum confidence threshold (default: 65%%)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Update interval in seconds (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print(BANNER)
    
    # Configuration
    config = {
        'symbols': args.symbols,
        'initial_capital': args.capital,
        'max_position_size': args.risk,
        'confidence_threshold': args.confidence,
        'update_interval': args.interval,
        'max_positions': 5,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.05,
        'max_drawdown_pct': 0.20,
        'max_daily_loss': args.capital * 0.05
    }
    
    logger.info("🚀 Starting Ultra Trading System (Standalone Version)")
    logger.info(f"📊 Symbols: {', '.join(config['symbols'])}")
    logger.info(f"💰 Initial Capital: ${config['initial_capital']:.2f}")
    logger.info(f"⚠️ Risk per Trade: {config['max_position_size']:.1%}")
    logger.info(f"🎯 Confidence Threshold: {config['confidence_threshold']:.0f}%")
    logger.info(f"⏱️ Update Interval: {config['update_interval']}s")
    logger.info("=" * 60)
    
    # Create and run trader
    trader = UltraTrader(config)
    
    # Handle shutdown
    def signal_handler(signum, frame):
        logger.info("\n🛑 Shutdown signal received")
        trader.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await trader.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        trader.stop()

if __name__ == "__main__":
    asyncio.run(main())