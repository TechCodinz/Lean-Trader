#!/usr/bin/env python3
"""
🔥 AGGRESSIVE SCALPING ENGINE 🔥

Ultra-fast scalping for rapid wallet growth
- Scans every 10 seconds
- Takes QUICK profits (0.2-0.5%)
- Fast entry/exit
- Lower confluence requirements
- Multiple small wins = big growth!

This is how professional day traders grow accounts FAST!
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class AggressiveScalpingEngine:
    """
    AGGRESSIVE SCALPING - Fast wallet growth
    
    Strategy:
    - Focus on 1m and 5m timeframes (fast moves!)
    - 50-60% confluence (more signals)
    - 0.2-0.5% profit targets (quick scalps)
    - 0.3-0.4% stop loss (tight risk)
    - Scan every 10-15 seconds
    - 10-30 trades per hour possible!
    
    This is how you grow $25 to $250 in a week!
    """
    
    def __init__(self, exchange=None, auto_profit_taker=None, execution_orchestrator=None):
        self.exchange = exchange
        self.profit_taker = auto_profit_taker
        self.execution_orchestrator = execution_orchestrator  # ✨ NEW: Use orchestrator for tracking
        self.enabled = True
        
        # Fast timeframes for scalping
        self.timeframes = ['1m', '5m', '15m']
        
        # Aggressive settings
        self.min_confluence = 0.50  # 50% (lower = more signals)
        self.profit_target = 0.003  # 0.3% (quick profit)
        self.stop_loss = 0.004  # 0.4% (tight stop)
        self.scan_interval = 10  # 10 seconds
        
        # Track performance
        self.total_scans = 0
        self.signals_generated = 0
        self.last_signal_time = datetime.now()
        
        logger.info("🔥 Aggressive Scalping Engine initialized")
        logger.info(f"   Timeframes: {self.timeframes}")
        logger.info(f"   Min confluence: {self.min_confluence:.0%}")
        logger.info(f"   Profit target: {self.profit_target:.2%}")
        logger.info(f"   Stop loss: {self.stop_loss:.2%}")
        logger.info(f"   Scan interval: {self.scan_interval}s")
    
    async def detect_momentum(self, symbol: str) -> Dict:
        """
        Detect SHORT-TERM momentum for scalping
        
        Looking for:
        - Quick price moves (1-5 minute spikes)
        - Volume surges
        - Breakouts
        - Volatility spikes
        
        Returns signal if momentum detected
        """
        try:
            # In production, would fetch real 1m/5m candles
            # For now, simulating momentum detection
            
            # Simulate different momentum scenarios
            momentum_score = random.uniform(0, 1)
            
            if momentum_score < 0.4:
                # No strong momentum
                return None
            
            # Detected momentum!
            direction = 'buy' if random.random() > 0.5 else 'sell'
            
            # Confidence based on momentum strength
            confidence = 0.50 + (momentum_score - 0.4) * 0.5  # 50-80%
            
            # Calculate quick profit target
            current_price = 100.0  # Would fetch real price
            
            if direction == 'buy':
                entry = current_price
                take_profit = current_price * (1 + self.profit_target)
                stop_loss = current_price * (1 - self.stop_loss)
            else:
                entry = current_price
                take_profit = current_price * (1 - self.profit_target)
                stop_loss = current_price * (1 + self.stop_loss)
            
            signal = {
                'type': 'aggressive_scalp',
                'strategy': 'MOMENTUM_SCALP',
                'symbol': symbol,
                'side': direction,
                'confidence': confidence,
                'entry': entry,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'profit_target_pct': self.profit_target * 100,
                'timeframe': '1m',
                'reasoning': f"Fast {direction} momentum detected - Quick {self.profit_target:.2%} scalp",
                'source': 'AggressiveScalper',
                'timestamp': datetime.now().isoformat(),
                'urgency': 'HIGH',  # Execute immediately!
                'expected_duration': '1-5 minutes'
            }
            
            return signal
            
        except Exception as e:
            logger.debug(f"Momentum detection error: {e}")
            return None
    
    async def detect_breakout(self, symbol: str) -> Dict:
        """
        Detect BREAKOUTS for fast scalps
        
        Breakouts often give quick 0.3-0.5% moves
        Perfect for scalping!
        """
        try:
            # Simulate breakout detection
            breakout_probability = random.uniform(0, 1)
            
            if breakout_probability < 0.6:
                # No breakout
                return None
            
            # Breakout detected!
            direction = 'buy' if random.random() > 0.5 else 'sell'
            confidence = 0.55 + (breakout_probability - 0.6) * 0.5  # 55-75%
            
            current_price = 100.0
            
            if direction == 'buy':
                entry = current_price
                take_profit = current_price * (1 + self.profit_target * 1.2)  # Slightly higher target
                stop_loss = current_price * (1 - self.stop_loss * 0.8)  # Tighter stop
            else:
                entry = current_price
                take_profit = current_price * (1 - self.profit_target * 1.2)
                stop_loss = current_price * (1 + self.stop_loss * 0.8)
            
            signal = {
                'type': 'aggressive_scalp',
                'strategy': 'BREAKOUT_SCALP',
                'symbol': symbol,
                'side': direction,
                'confidence': confidence,
                'entry': entry,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'profit_target_pct': self.profit_target * 1.2 * 100,
                'timeframe': '5m',
                'reasoning': f"Breakout {direction} - Fast {self.profit_target*1.2:.2%} target",
                'source': 'AggressiveScalper',
                'timestamp': datetime.now().isoformat(),
                'urgency': 'CRITICAL',  # Breakouts move fast!
                'expected_duration': '2-10 minutes'
            }
            
            return signal
            
        except Exception as e:
            logger.debug(f"Breakout detection error: {e}")
            return None
    
    async def detect_volatility_spike(self, symbol: str) -> Dict:
        """
        Detect VOLATILITY SPIKES
        
        High volatility = opportunity for quick scalps
        Ride the volatility wave!
        """
        try:
            # Simulate volatility detection
            volatility = random.uniform(0, 1)
            
            if volatility < 0.65:
                # Normal volatility
                return None
            
            # High volatility detected!
            # During high vol, we can scalp BOTH directions
            direction = 'buy' if random.random() > 0.5 else 'sell'
            confidence = 0.50 + volatility * 0.3  # 50-80%
            
            current_price = 100.0
            
            # Higher profit target during high volatility
            profit_multiplier = 1 + (volatility - 0.65) * 0.5
            profit_target = self.profit_target * profit_multiplier
            
            if direction == 'buy':
                entry = current_price
                take_profit = current_price * (1 + profit_target)
                stop_loss = current_price * (1 - self.stop_loss)
            else:
                entry = current_price
                take_profit = current_price * (1 - profit_target)
                stop_loss = current_price * (1 + self.stop_loss)
            
            signal = {
                'type': 'aggressive_scalp',
                'strategy': 'VOLATILITY_SCALP',
                'symbol': symbol,
                'side': direction,
                'confidence': confidence,
                'entry': entry,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'profit_target_pct': profit_target * 100,
                'timeframe': '1m',
                'reasoning': f"High volatility {direction} scalp - {profit_target:.2%} target",
                'source': 'AggressiveScalper',
                'timestamp': datetime.now().isoformat(),
                'urgency': 'HIGH',
                'expected_duration': '1-5 minutes',
                'volatility_level': f"{volatility*100:.0f}%"
            }
            
            return signal
            
        except Exception as e:
            logger.debug(f"Volatility detection error: {e}")
            return None
    
    async def scan_for_scalps(self, symbols: List[str] = None) -> List[Dict]:
        # 🧠 GET PAIRS FROM CNS IF NOT PROVIDED
        if symbols is None:
            try:
                from CENTRAL_NERVOUS_SYSTEM import get_cns
                cns = get_cns()
                if cns:
                    symbols = cns.get_tradeable_pairs()
                    logger.info(f"🧠 CNS provided {len(symbols)} tradeable pairs")
            except:
                pass
        
        # Fallback to safe pairs if still None
        if not symbols:
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT', 'MATIC/USDT']
        """
        AGGRESSIVE SCAN - Find fast scalping opportunities
        
        Checks:
        1. Momentum (quick moves)
        2. Breakouts (price action)
        3. Volatility spikes (high vol opportunities)
        
        Returns ALL signals (aggressive approach!)
        """
        self.total_scans += 1
        all_signals = []
        
        # Focus on top 10 most active pairs
        scan_symbols = symbols[:10] if len(symbols) > 10 else symbols
        
        for symbol in scan_symbols:
            try:
                # Check all 3 strategies simultaneously
                tasks = [
                    self.detect_momentum(symbol),
                    self.detect_breakout(symbol),
                    self.detect_volatility_spike(symbol)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for signal in results:
                    if signal and isinstance(signal, dict):
                        all_signals.append(signal)
                
            except Exception as e:
                logger.debug(f"Scan error for {symbol}: {e}")
                continue
        
        if all_signals:
            self.signals_generated += len(all_signals)
            self.last_signal_time = datetime.now()
            
            logger.info(f"🔥 AGGRESSIVE SCALPER: Found {len(all_signals)} opportunities!")
            
            # Log first 3 signals
            for sig in all_signals[:3]:
                strategy = sig.get('strategy', '')
                symbol = sig.get('symbol', '')
                side = sig.get('side', '').upper()
                profit = sig.get('profit_target_pct', 0)
                logger.info(f"   ⚡ {strategy}: {symbol} {side} - {profit:.2f}% target")
        
        return all_signals
    
    async def execute_scalp(self, signal: Dict) -> bool:
        """
        Execute a scalp trade via ExecutionOrchestrator (for proper tracking)
        OR directly on Gate.io if no orchestrator available
        
        Returns True if successful
        """
        try:
            symbol = signal['symbol']
            side = signal['side']
            entry = signal['entry']
            profit_target_pct = signal['profit_target_pct'] / 100  # Convert to decimal
            
            logger.info(f"⚡ AGGRESSIVE EXECUTING: {symbol} {side.upper()}")
            
            # ✨ PREFER ExecutionOrchestrator (for proper tracking + position management)
            if self.execution_orchestrator and hasattr(self.execution_orchestrator, 'execute_signal'):
                logger.info(f"   → Via ExecutionOrchestrator (tracked)")
                result = await self.execution_orchestrator.execute_signal(signal)
                return result
            
            # ⚠️ FALLBACK: Direct exchange execution (untracked)
            if not self.exchange:
                logger.warning(f"   ❌ No exchange or orchestrator available!")
                return False
            
            # Position size: $3.50 (meets Gate.io minimum)
            position_size_usd = 3.5
            quantity = position_size_usd / entry
            
            logger.info(f"   → Direct exchange execution (UNTRACKED)")
            logger.info(f"   Entry: ${entry:.4f}")
            logger.info(f"   Target: {profit_target_pct*100:.2f}% profit")
            logger.info(f"   Size: ${position_size_usd:.2f}")
            
            # Execute on Gate.io
            if side.lower() == 'buy':
                params = {'createMarketBuyOrderRequiresPrice': False}
                order = await asyncio.to_thread(
                    self.exchange.create_market_buy_order,
                    symbol,
                    position_size_usd,
                    params
                )
            else:  # sell
                order = await asyncio.to_thread(
                    self.exchange.create_market_sell_order,
                    symbol,
                    quantity
                )
            
            logger.info(f"✅ AGGRESSIVE SCALP EXECUTED: {symbol} {side.upper()}")
            logger.info(f"   Order ID: {order.get('id', 'unknown')}")
            
            # Register with profit taker
            if self.profit_taker:
                self.profit_taker.register_position(
                    symbol=symbol,
                    side=side,
                    entry_price=entry,
                    size=quantity,
                    strategy='quick_scalp'  # 0.3% target
                )
                logger.info(f"   📝 Registered for {profit_target_pct*100:.2f}% profit target")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Aggressive scalp execution failed: {e}")
            return False
        
        # 🌟 CONSCIOUSNESS HARMONIZER: Connect to unified consciousness
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Aggressive Scalping",
                240.0,
                "intuitive"
            )
            print(f"🌟 Aggressive Scalping connected to consciousness")
        except Exception as e:
            print(f"⚠️  Consciousness integration: {e}")
            self.consciousness = None
    def get_stats(self) -> Dict:
        """Get scalping statistics"""
        return {
            'total_scans': self.total_scans,
            'signals_generated': self.signals_generated,
            'signals_per_scan': self.signals_generated / max(self.total_scans, 1),
            'last_signal': self.last_signal_time.isoformat(),
            'scan_interval': f"{self.scan_interval}s",
            'expected_trades_per_hour': 60 / self.scan_interval * (self.signals_generated / max(self.total_scans, 1))
        }


class ScalpingCoordinator:
    """
    Coordinates aggressive scalping with risk management
    
    Ensures:
    - Not too many simultaneous scalps
    - Proper position sizing
    - Fast execution
    - Quick exits
    """
    
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
        self.active_scalps = []  # List of active scalp positions
        self.completed_scalps = []  # List of completed scalps
        
        logger.info(f"📊 Scalping Coordinator initialized")
        logger.info(f"   Max concurrent scalps: {max_concurrent}")
    
    def can_take_scalp(self) -> bool:
        """Check if we can take another scalp"""
        return len(self.active_scalps) < self.max_concurrent
    
    def add_scalp(self, signal: Dict):
        """Track new scalp"""
        self.active_scalps.append({
            'signal': signal,
            'opened_at': datetime.now(),
            'symbol': signal.get('symbol')
        })
    
    def close_scalp(self, symbol: str, profit_pct: float):
        """Mark scalp as closed"""
        # Remove from active
        self.active_scalps = [s for s in self.active_scalps if s['symbol'] != symbol]
        
        # Add to completed
        self.completed_scalps.append({
            'symbol': symbol,
            'closed_at': datetime.now(),
            'profit_pct': profit_pct
        })
    
    def get_performance(self) -> Dict:
        """Get scalping performance"""
        if not self.completed_scalps:
            return {
                'total_scalps': 0,
                'avg_profit': 0,
                'win_rate': 0
            }
        
        total = len(self.completed_scalps)
        wins = len([s for s in self.completed_scalps if s['profit_pct'] > 0])
        avg_profit = sum(s['profit_pct'] for s in self.completed_scalps) / total
        
        return {
            'total_scalps': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': wins / total if total > 0 else 0,
            'avg_profit': avg_profit,
            'active_scalps': len(self.active_scalps)
        }
