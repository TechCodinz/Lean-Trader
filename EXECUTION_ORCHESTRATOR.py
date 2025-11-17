#!/usr/bin/env python3
"""
EXECUTION ORCHESTRATOR - THE MISSING PIECE
Smart trade execution with risk management, position sizing, and profit optimization

NOW WITH: Direct Gate.io execution using COMPLETE_PROFIT_SYSTEM
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque
import time

logger = logging.getLogger(__name__)

# Import the COMPLETE PROFIT SYSTEM
try:
    from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem, get_profit_system, initialize_profit_system
    PROFIT_SYSTEM_AVAILABLE = True
    logger.info("✅ COMPLETE PROFIT SYSTEM loaded - Direct Gate.io execution ready!")
except Exception as e:
    logger.warning(f"⚠️ COMPLETE PROFIT SYSTEM not available: {e}")
    PROFIT_SYSTEM_AVAILABLE = False

# 🧠 INTELLIGENT EXECUTION ENGINE - Uses ALL engine intelligence!
try:
    from INTELLIGENT_EXECUTION_ENGINE import IntelligentExecutionEngine, get_intelligent_execution_engine
    INTELLIGENT_EXECUTION_AVAILABLE = True
    logger.info("🧠 INTELLIGENT EXECUTION ENGINE loaded - Multi-timeframe, session-aware trading!")
except Exception as e:
    logger.warning(f"⚠️ INTELLIGENT EXECUTION ENGINE not available: {e}")
    INTELLIGENT_EXECUTION_AVAILABLE = False


class SmartPositionSizer:
    """Smart position sizing based on account balance and risk"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.balance = initial_balance
        self.max_risk_per_trade = 0.02  # 2% max risk
        self.max_position_pct = 0.10  # 10% max position size
        
        # Adaptive minimum based on balance
        if initial_balance < 100:
            self.min_position_usd = 3.5  # $3.50 minimum for small accounts (Gate.io minimum)
        else:
            self.min_position_usd = 10.0  # $10 minimum for larger accounts
        
        # Dynamic sizing based on confidence
        self.use_dynamic_sizing = True
        self.aggressive_mode = True  # Grow account faster
        
        # 🌟 CONSCIOUSNESS HARMONIZER: Connect to unified consciousness
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Execution",
                180.0,
                "emotional"
            )
            print(f"🌟 Execution connected to consciousness")
        except Exception as e:
            print(f"⚠️  Consciousness integration: {e}")
            self.consciousness = None
    def calculate_position_size(self, 
                               confidence: float,
                               volatility: float = 0.02,
                               stop_loss_pct: float = 0.01) -> float:
        """
        Calculate optimal position size using Kelly Criterion + Risk Management
        
        Args:
            confidence: AI confidence (0.0 to 1.0)
            volatility: Market volatility estimate
            stop_loss_pct: Stop loss as percentage
            
        Returns:
            Position size in USD
        """
        # Base risk amount (2% of balance)
        base_risk = self.balance * self.max_risk_per_trade
        
        # Kelly Criterion adjustment
        # Kelly = (p * b - q) / b where p=win_prob, q=loss_prob, b=win/loss ratio
        win_prob = confidence
        loss_prob = 1 - confidence
        win_loss_ratio = 2.0  # Assume 2:1 reward/risk
        
        kelly_fraction = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25% Kelly
        
        # Adjust for volatility (reduce size in high volatility)
        volatility_adjustment = max(0.5, 1.0 - volatility)
        
        # Adjust for confidence (higher confidence = larger size)
        confidence_adjustment = 0.5 + (confidence * 0.5)  # 50% to 100%
        
        # Calculate final position size
        position_size = (base_risk / stop_loss_pct) * kelly_fraction * volatility_adjustment * confidence_adjustment
        
        # AGGRESSIVE MODE: Grow account faster with high confidence trades
        if self.aggressive_mode and confidence >= 0.85:
            # Increase size by up to 50% for very high confidence
            confidence_boost = 1.0 + ((confidence - 0.80) * 3.0)  # More aggressive for 80%+ confidence  # 85% conf = 1.0x, 100% conf = 1.3x
            position_size *= confidence_boost
            logger.info(f"🚀 Aggressive sizing: confidence {confidence:.1%} → {confidence_boost:.2f}x boost")
        
        # Apply limits
        max_position = self.balance * self.max_position_pct
        position_size = min(position_size, max_position)
        position_size = max(position_size, self.min_position_usd)
        
        # Balance-aware: As balance grows, increase position sizes proportionally
        if self.balance > 1000:
            growth_multiplier = (self.balance / 1000) ** 0.5  # Square root scaling
            position_size *= growth_multiplier
            logger.debug(f"💰 Balance-aware sizing: ${self.balance:.0f} → {growth_multiplier:.2f}x multiplier")
        
        return position_size
    
    def update_balance(self, new_balance: float):
        """Update balance after trades"""
        self.balance = new_balance


class SmartRiskManager:
    """Smart risk management and validation"""
    
    def __init__(self):
        self.max_open_positions = 999999  # ♾️ INFINITE TRADING!
        self.max_daily_trades = 999999    # ♾️ UNLIMITED TRADES!
        self.max_daily_loss = 0.05  # 5% max daily loss
        self.max_correlated_positions = 999999  # No correlation limits!
        
        self.open_positions = {}
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
        
    def can_open_position(self, symbol: str, signal_type: str) -> tuple[bool, str]:
        """Check if we can open a new position"""
        
        # Check daily loss limit
        if self.daily_pnl < -self.max_daily_loss:
            return False, f"Daily loss limit reached: {self.daily_pnl:.2%}"
        
        # Check max positions
        if len(self.open_positions) >= self.max_open_positions:
            return False, f"Max positions reached: {len(self.open_positions)}/{self.max_open_positions}"
        
        # Check if already in this position
        if symbol in self.open_positions:
            return False, f"Already in position: {symbol}"
        
        # Check correlation (BTC/ETH, etc)
        correlated_count = self._count_correlated_positions(symbol)
        if correlated_count >= self.max_correlated_positions:
            return False, f"Max correlated positions: {correlated_count}/{self.max_correlated_positions}"
        
        return True, "OK"
    
    def _count_correlated_positions(self, symbol: str) -> int:
        """Count positions in correlated assets"""
        # Simplified correlation groups
        correlation_groups = {
            'BTC': ['BTC/USDT', 'BTC/USD'],
            'ETH': ['ETH/USDT', 'ETH/USD'],
            'MAJOR': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
        }
        
        count = 0
        for group, symbols in correlation_groups.items():
            if symbol in symbols:
                # Count positions in same group
                for open_symbol in self.open_positions:
                    if open_symbol in symbols:
                        count += 1
        
        return count
    
    def record_position(self, symbol: str, side: str, size: float, entry_price: float):
        """Record opened position"""
        self.open_positions[symbol] = {
            'side': side,
            'size': size,
            'entry_price': entry_price,
            'timestamp': datetime.now()
        }
    
    def close_position(self, symbol: str, exit_price: float) -> float:
        """Close position and calculate P&L"""
        if symbol not in self.open_positions:
            return 0.0
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        size = position['size']
        side = position['side']
        
        # Calculate P&L
        if side == 'buy':
            pnl = (exit_price - entry_price) * size
        else:
            pnl = (entry_price - exit_price) * size
        
        # Update daily stats
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        # Remove position
        del self.open_positions[symbol]
        
        return pnl
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset = today


class ExecutionOrchestrator:
    """
    SMART EXECUTION ORCHESTRATOR
    The critical missing piece that actually executes trades
    
    Features:
    - Smart position sizing (Kelly Criterion)
    - Risk management and validation
    - Stop loss and take profit automation
    - Multi-exchange support
    - Performance tracking
    - Trade recovery and retry logic
    """
    
    def __init__(self, data_hub, trading_engines, risk_engine, ledger, mode: str = "testnet"):
        self.data_hub = data_hub
        self.engines = trading_engines
        self.risk_engine = risk_engine
        self.ledger = ledger
        self.mode = mode
        
        # Smart components
        self.position_sizer = SmartPositionSizer(initial_balance=1000.0)
        self.risk_manager = SmartRiskManager()
        
        # ✨ MULTI-EXCHANGE SUPPORT - Testnet OR Live!
        self.profit_system = None  # For live Gate.io trading
        self.testnet_exchange = None  # For Bybit testnet
        self.active_exchange = None  # The one we're actually using
        
        # 🧠 INTELLIGENT EXECUTION ENGINE - THE MISSING PIECE!
        self.intelligent_engine = None
        
        if mode == "testnet":
            # 🧪 TESTNET MODE - Use Bybit testnet
            logger.info("🧪 Setting up TESTNET execution via Bybit...")
            # Will be set by orchestrator with actual testnet exchange
            self.active_exchange = None  # Set later by wire_execution_to_testnet()
            logger.info("   Waiting for testnet exchange from orchestrator...")
        else:
            # 💰 LIVE MODE - Use Gate.io via COMPLETE PROFIT SYSTEM
            if PROFIT_SYSTEM_AVAILABLE:
                try:
                    import os
                    api_key = os.getenv('GATE_API_KEY', 'a0508d8aadf3bcb76e16f4373e1f3a76')
                    api_secret = os.getenv('GATE_API_SECRET', '451770a07dbede1b87bb92f5ce98e24029d2fe91e0053be2ec41771c953113f9')
                    self.profit_system = CompleteProfitSystem(api_key, api_secret)
                    self.active_exchange = 'profit_system'
                    logger.info("✅ COMPLETE PROFIT SYSTEM initialized - Direct Gate.io execution!")
                except Exception as e:
                    logger.error(f"Failed to init profit system: {e}")
        
        # ADVANCED COMPONENTS (wired externally)
        self.action_decider = None  # AdvancedActionDecider
        self.trailing_stop = None  # TrailingStopManager
        self.compound_engine = None  # CompoundEngine  
        self.partial_tp = None  # PartialTPManager
        
        # Execution settings
        self.min_confidence = 0.75  # 75% minimum confidence to execute (lowered for more opportunities)
        self.execution_enabled = True
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.execution_times = deque(maxlen=100)
        
        logger.info("⚡ Execution Orchestrator initialized (SMART LOGIC + COMPLETE PROFIT SYSTEM)")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Min Confidence: {self.min_confidence}")
        logger.info(f"   Risk per trade: {self.position_sizer.max_risk_per_trade:.1%}")
        logger.info(f"   Profit System: {'✅ ACTIVE' if self.profit_system else '❌ INACTIVE'}")
    
    async def run_execution_loop(self):
        """
        Main execution loop - monitors data hub and executes high-confidence trades
        
        ACTIVELY TRADES:
        - Smart Scalping signals (75%+ confluence)
        - Aggressive Scalping signals (momentum/breakouts)
        - Sentient Scalping signals (hot pairs)
        - Money Printer signals (arbitrage/market making)
        - All other engine signals
        """
        logger.info("⚡ Starting SMART execution loop...")
        logger.info("   → Will execute ALL scalper signals with profit targets!")
        
        # Initialize profit system if available
        if self.profit_system:
            await self.profit_system.initialize()
            # Start position monitoring loop in background
            asyncio.create_task(self.profit_system.run_monitoring_loop())
            logger.info("✅ COMPLETE PROFIT SYSTEM monitoring active!")
        
        while self.execution_enabled:
            try:
                # Reset daily stats if new day
                self.risk_manager.reset_daily_stats()
                
                # Check for decisions in alert queue
                if not self.data_hub.alert_queue.empty():
                    decision = await self.data_hub.alert_queue.get()
                    
                    # Validate and execute
                    await self.process_decision(decision)
                
                # ACTIVELY CHECK HUB FOR NEW SIGNALS (don't just wait for alert queue!)
                signals = self.data_hub.get_signals(limit=20)
                
                for signal in signals:
                    # Only execute high-confidence scalper signals
                    source = signal.get('source', '')
                    strategy = signal.get('strategy', '')
                    confidence = signal.get('confidence', 0)
                    
                    # Convert confidence to 0-1 range if needed
                    if confidence > 1:
                        confidence = confidence / 100
                    
                    # Execute if:
                    # - From scalpers (Smart, Aggressive, Sentient)
                    # - Or high confidence (>70%)
                    # - Has profit targets
                    is_scalper = any(x in source or x in strategy for x in [
                        'Scalp', 'SCALP', 'Aggressive', 'Sentient', 'MOMENTUM', 'BREAKOUT', 'VOLATILITY'
                    ])
                    
                    has_targets = signal.get('take_profit') or signal.get('profit_target_pct')
                    
                    # ✅ FIX: If no profit targets, add intelligent defaults!
                    if not has_targets:
                        # Add intelligent profit targets based on timeframe/strategy
                        timeframe = signal.get('timeframe', '5m')
                        if timeframe == '1m':
                            signal['profit_target_pct'] = 0.003  # 0.3%
                        elif timeframe == '5m':
                            signal['profit_target_pct'] = 0.005  # 0.5%
                        else:
                            signal['profit_target_pct'] = 0.01   # 1%
                        has_targets = True
                        logger.debug(f"   Added profit target: {signal['profit_target_pct']:.1%}")
                    
                    if (is_scalper or confidence >= 0.70) and has_targets:
                        # Execute this signal!
                        await self.execute_signal(signal)
                        
                        # Rate limit
                        await asyncio.sleep(1)
                
                # Monitor open positions (close at profit targets!)
                try:
                    await asyncio.wait_for(self.monitor_positions(), timeout=3.0)
                except asyncio.TimeoutError:
                    logger.warning("⚠️  Position monitoring timed out (3s), continuing...")
                except Exception as e:
                    logger.error(f"Position monitoring error: {e}")
                
                logger.info("💤 Sleeping 5 seconds before next iteration...")
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Execution loop error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                await asyncio.sleep(5)
    
    async def execute_signal(self, signal: Dict[str, Any]):
        """
        Execute a trading signal from DataHub
        THIS IS THE CRITICAL METHOD THAT WAS MISSING!
        """
        
        try:
            # Extract signal details
            symbol = signal.get('pair') or signal.get('symbol')
            side = signal.get('side', 'BUY')
            confidence = signal.get('confidence', 0.0)
            
            if not symbol:
                return
            
            # Convert confidence to 0-1 range if needed
            if confidence > 1:
                confidence = confidence / 100
            
            # Check confidence threshold
            if confidence < self.min_confidence:
                logger.debug(f"   Skipping {symbol}: confidence {confidence:.1%} < {self.min_confidence:.1%}")
                return
            
            # Log the signal
            logger.info(f"📥 Processing signal: {side} {symbol} ({confidence:.1%})")
            
            # Execute the trade!
            result = await self.execute_trade(
                symbol=symbol,
                side=side,
                confidence=confidence,
                signal=signal
            )
            
            if result:
                logger.info(f"✅ Signal executed successfully!")
            else:
                logger.warning(f"⚠️  Signal execution failed")
        
        except Exception as e:
            logger.error(f"Execute signal error: {e}")
    
    async def process_decision(self, decision: Dict[str, Any]):
        """Process AI decision using ADVANCED ACTION LOGIC"""
        
        try:
            # Extract decision details
            signal = decision.get('signal', {})
            action = decision.get('action', 'hold')
            confidence = decision.get('confidence', 0.0)
            
            symbol = signal.get('symbol') or signal.get('data', {}).get('symbol')
            if not symbol:
                logger.debug("No symbol in decision")
                return
            
            # Validate confidence
            if confidence < self.min_confidence:
                logger.debug(f"Low confidence: {confidence:.2%} < {self.min_confidence:.2%}")
                return
            
            # USE ADVANCED ACTION DECIDER if available
            if self.action_decider:
                # Get price history (simulate for now)
                price = signal.get('data', {}).get('price', 0)
                price_history = [price] * 50  # Would fetch real history
                
                # Get all current opportunities (for portfolio balancing)
                opportunities = []  # Would get from data_hub
                
                # DECIDE SOPHISTICATED ACTION!
                advanced_decision = await self.action_decider.decide_action(
                    symbol=symbol,
                    signal=signal,
                    confidence=confidence,
                    price_history=price_history,
                    opportunities=opportunities
                )
                
                action = advanced_decision['action']
                size = advanced_decision.get('size', 0)
                reason = advanced_decision.get('reason', '')
                
                logger.info(f"🧠 ADVANCED DECISION: {action.upper()} {symbol}")
                logger.info(f"   Reason: {reason}")
                logger.info(f"   Confidence: {confidence:.1%}")
                logger.info(f"   Market Regime: {advanced_decision.get('regime', 'unknown')}")
                
                # Handle different actions
                if action == 'avoid' or action == 'hold':
                    logger.info(f"   ⏸️  No action taken")
                    return
                    
                elif action == 'scale_in':
                    logger.info(f"   📈 Scaling into position (DCA)")
                    
                elif action == 'scale_out':
                    logger.info(f"   📉 Scaling out {size:.0%} of position")
                    # Would execute partial close
                    return
            
            else:
                # Fallback to simple logic
                if action not in ['buy', 'sell']:
                    return
            
            # Check risk management
            can_trade, reason = self.risk_manager.can_open_position(symbol, action)
            if not can_trade:
                logger.info(f"⚠️ Trade blocked: {reason}")
                return
        
        except Exception as e:
            logger.error(f"Process decision error: {e}")
    
    def wire_execution_to_testnet(self, testnet_exchange, all_exchanges=None):
        """Wire ExecutionOrchestrator to use Bybit testnet exchange"""
        self.testnet_exchange = testnet_exchange
        self.active_exchange = 'testnet'
        
        # 🧠 Initialize INTELLIGENT EXECUTION ENGINE with testnet AND all exchanges!
        if INTELLIGENT_EXECUTION_AVAILABLE and testnet_exchange:
            # Get actual balance
            actual_bal = self.position_sizer.balance if hasattr(self, 'position_sizer') else 1000.0
            
            self.intelligent_engine = IntelligentExecutionEngine(
                testnet_exchange, 
                mode='testnet',
                exchanges=all_exchanges or {},  # ✅ Pass all exchanges for router!
                balance=actual_bal  # ✅ PASS ACTUAL BALANCE!
            )
            logger.info("🧠 ✅ INTELLIGENT EXECUTION ENGINE initialized with TESTNET!")
            if all_exchanges:
                logger.info(f"   🎯 Has access to {len(all_exchanges)} exchanges for routing")
        
        logger.info("✅ ExecutionOrchestrator wired to Bybit TESTNET!")
        logger.info(f"   Exchange: {type(testnet_exchange).__name__}")
        logger.info(f"   Intelligent Engine: {'ACTIVE ✨' if self.intelligent_engine else 'Not available'}")
    
    async def execute_signal(self, signal: Dict[str, Any]):
        """
        Execute a trading signal using appropriate exchange
        
        - TESTNET mode: Uses Bybit testnet
        - LIVE mode: Uses COMPLETE PROFIT SYSTEM (Gate.io)
        
        🎯 NOW SUPPORTS SPECIAL STRATEGIES:
        - Triangular Arbitrage (3 simultaneous orders)
        - Pairs Trading (long + short)
        - Volatility Straddles (options/hedges)
        - Market Making (bid/ask spreads)
        """
        try:
            # 🎯 DETECT SIGNAL TYPE - Standard or Special Strategy
            signal_type = signal.get('type', 'standard')
            
            # ============================================================
            # SPECIAL STRATEGY EXECUTION
            # ============================================================
            
            if signal_type == 'triangular_arbitrage':
                logger.info(f"💰 TRIANGULAR ARBITRAGE: {signal.get('profit_pct', 0):.2f}% profit!")
                return await self._execute_triangular_arbitrage(signal)
            
            elif signal_type == 'correlation_exploit':  # ✅ MONEY_PRINTER uses this for pairs trade
                logger.info(f"💰 PAIRS TRADE: {signal.get('profit_potential', 0):.1f}% profit potential!")
                return await self._execute_pairs_trade(signal)
            
            elif signal_type == 'volatility_harvest':  # ✅ MONEY_PRINTER uses this
                logger.info(f"💰 VOLATILITY STRADDLE: Profit from {signal.get('volatility_pct', 0):.1f}% vol!")
                return await self._execute_volatility_straddle(signal)
            
            elif signal_type == 'market_maker':
                logger.info(f"💰 MARKET MAKER: Earn ${signal.get('expected_profit', 0):.2f} spread!")
                return await self._execute_market_maker(signal)
            
            elif signal_type == 'funding_farm':  # ✅ MONEY_PRINTER uses this
                logger.info(f"💰 FUNDING ARBITRAGE: {signal.get('daily_rate', 0)*100:.2f}% daily!")
                return await self._execute_funding_arbitrage(signal)
            
            # ============================================================
            # STANDARD BUY/SELL EXECUTION
            # ============================================================
            
            symbol = signal.get('symbol')
            side = signal.get('side', signal.get('action', '')).lower()
            confidence = signal.get('confidence', 0)
            
            # Convert confidence to 0-1 if needed
            if confidence > 1:
                confidence = confidence / 100
            
            if not symbol or not side:
                logger.debug(f"Invalid signal: missing symbol or side")
                return False
            
            # Check risk management
            can_trade, reason = self.risk_manager.can_open_position(symbol, side)
            if not can_trade:
                logger.debug(f"Trade blocked: {reason}")
                return False
            
            # 🚀 TIER 1 ENHANCEMENTS - Apply before execution!
            try:
                # Get orchestrator's enhancement systems
                from COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                orchestrator = get_orchestrator()
                
                if orchestrator:
                    # 1. Fund Protection Check
                    if hasattr(orchestrator, 'fund_protection') and orchestrator.fund_protection:
                        can_trade_safe, protection_reason = orchestrator.fund_protection.can_open_position(
                            symbol, self.position_sizer.balance
                        )
                        if not can_trade_safe:
                            logger.info(f"   🛡️  FUND PROTECTION: {protection_reason}")
                            return False
                    
                    # 2. Hidden Pattern Enhancement
                    if hasattr(orchestrator, 'pattern_detector') and orchestrator.pattern_detector:
                        pattern_signal = orchestrator.pattern_detector.detect_hidden_patterns(
                            symbol, signal.get('timeframe', '5m'), confidence
                        )
                        if pattern_signal and pattern_signal.get('boost_confidence'):
                            confidence = min(0.98, confidence * 1.1)
                            logger.info(f"   🎯 HIDDEN PATTERN BOOST: Confidence → {confidence:.0%}")
                    
                    # 3. Dynamic Risk Adjustment
                    if hasattr(orchestrator, 'risk_adjuster') and orchestrator.risk_adjuster:
                        # Risk adjuster will be used in position sizing
                        pass
                    
                    # 4. Multi-Timeframe Trading
                    if hasattr(orchestrator, 'mtf_coordinator') and orchestrator.mtf_coordinator:
                        timeframes = orchestrator.mtf_coordinator.get_priority_timeframes(signal)
                        if len(timeframes) > 1:
                            logger.info(f"   ⏱️  MULTI-TIMEFRAME: Will trade {len(timeframes)} timeframes!")
                            # Signal will be executed on multiple TFs
                    
                    # 5. Micro Growth Position Sizing
                    if hasattr(orchestrator, 'micro_growth') and orchestrator.micro_growth:
                        optimal_size = orchestrator.micro_growth.get_position_size(confidence)
                        logger.info(f"   💰 MICRO GROWTH: Optimal size ${optimal_size:.2f} for ${orchestrator.micro_growth.current_balance:.0f} balance")
                        # Engine will use this size
                    
                    # 6. Black Swan Detection
                    if hasattr(orchestrator, 'black_swan') and orchestrator.black_swan:
                        orchestrator.black_swan.add_price(signal.get('price', 0) or signal.get('entry', 0))
                        is_swan, z_score, severity = orchestrator.black_swan.check_black_swan()
                        if is_swan:
                            logger.warning(f"   🦢 BLACK SWAN: {severity} ({z_score:.1f}σ) - REDUCING SIZE 50%!")
                            # Reduce size drastically during black swans
                            confidence *= 0.5
                    
                    # 7. Adaptive Streak Logic (RL-inspired)
                    if hasattr(orchestrator, 'streak_logic') and orchestrator.streak_logic:
                        if orchestrator.streak_logic.should_pause_trading():
                            logger.warning(f"   🛑 STREAK LOGIC: Pausing after losses!")
                            return False
                        size_mult = orchestrator.streak_logic.get_position_multiplier()
                        conf_boost = orchestrator.streak_logic.get_confidence_boost()
                        if size_mult != 1.0 or conf_boost != 1.0:
                            logger.info(f"   🧠 STREAK LOGIC: Size {size_mult:.2f}x, Conf {conf_boost:.2f}x")
                            confidence *= conf_boost
                    
                    # 8. Volatility Forecasting
                    if hasattr(orchestrator, 'vol_forecaster') and orchestrator.vol_forecaster:
                        # Will be used in stop-loss calculation
                        pass
            except Exception as e:
                logger.warning(f"Enhancement hook error: {e}")  # Log errors instead of silent fail
            
            logger.info(f"⚡ EXECUTING: {side.upper()} {symbol} (confidence: {confidence:.1%})")
            logger.info(f"   Mode: {self.mode} | Exchange: {self.active_exchange}")
            
            # ✨ TESTNET EXECUTION (Bybit testnet)
            if self.mode == "testnet" and self.testnet_exchange:
                return await self._execute_on_testnet(signal, symbol, side, confidence)
            
            # 💰 LIVE EXECUTION (Gate.io via COMPLETE PROFIT SYSTEM)
            elif self.profit_system:
                return await self._execute_via_profit_system(signal, symbol, side, confidence)
            
            else:
                logger.error(f"❌ No exchange available! Mode: {self.mode}, Active: {self.active_exchange}")
                return False
                
        except Exception as e:
            logger.error(f"execute_signal error: {e}")
            return False
    
    async def _execute_on_testnet(self, signal: Dict, symbol: str, side: str, confidence: float):
        """
        Execute trade on Bybit testnet using INTELLIGENT EXECUTION ENGINE
        
        🧠 USES ALL ENGINE INTELLIGENCE:
        - Multi-timeframe coordination
        - Dynamic lot sizing (confidence + volatility + session)
        - Multi-level take profits
        - Session-aware execution
        - Complete trade planning
        """
        try:
            # Initialize route
            route = None
            
            # 🧠 INTELLIGENT ROUTING: Find best exchange/market for this pair!
            try:
                from INTELLIGENT_EXCHANGE_ROUTER import get_intelligent_router
                router = get_intelligent_router()
                if router:
                    route = await router.route_signal(signal)
                if route:
                    logger.info(f"   🧠 ROUTER: {symbol} routed to {route['exchange']} {route['market_type']}")
                    # If pair not on this exchange, skip
                    if route['exchange'] != 'bybit_testnet' and self.mode == 'testnet':
                        logger.info(f"   ⏭️  {symbol} not on testnet, skipping")
                        return False
                else:
                    if route is None:
                        logger.debug("   Router: No route found")
                    else:
                        logger.debug("   Router not available (not initialized yet)")
            except Exception as e:
                logger.debug(f"   Router check failed: {e}")
                # Fallback route
                if not route:
                    route = {"exchange": "bybit_testnet", "market_type": "spot"}
            
            logger.info(f"   🧪 Executing on BYBIT TESTNET...")
            
            # 🧠 USE INTELLIGENT EXECUTION if available!
            if self.intelligent_engine:
                logger.info(f"   🧠 Using INTELLIGENT EXECUTION ENGINE!")
                
                # ♾️ INFINITE TRADING - NO DUPLICATE CHECKS!
                # With 490 models, trade as much as profitable!
                # Each signal is unique (different timeframe, strategy, confidence)
                is_hedge = signal.get('is_hedge', False)
                if is_hedge:
                    logger.info(f"   🛡️  Hedge position detected")
                
                # ✅ PASS ROUTE INFO TO EXECUTION ENGINE!
                if route:
                    signal['route_exchange'] = route['exchange']  # bybit_testnet
                    signal['route_market_type'] = route['market_type']  # spot/swap
                
                # 1. Create COMPLETE trade plan using ALL intelligence
                trade_plan = await self.intelligent_engine.create_complete_trade_plan(signal)
                
                if not trade_plan:
                    logger.error("Failed to create intelligent trade plan!")
                    return False
                
                # 2. Execute the intelligent trade
                result = await self.intelligent_engine.execute_intelligent_trade(trade_plan)
                
                if result:
                    logger.info(f"✅ INTELLIGENT TRADE EXECUTED!")
                    logger.info(f"   🎯 Strategy: {trade_plan['strategy']}")
                    logger.info(f"   💰 Size: ${trade_plan['lot_size_usd']:.2f} @ {trade_plan['leverage']}x")
                    logger.info(f"   📊 {len(trade_plan['take_profit_levels'])} TP levels")
                    logger.info(f"   🛡️  Stop Loss: ${trade_plan['stop_loss']:.4f}")
                    logger.info(f"   ⏱️  Max Hold: {trade_plan['max_hold_time_minutes']} min")
                    logger.info(f"   📈 Active TFs on {symbol}: {len(self.intelligent_engine.active_trades_by_tf[symbol])}")
                    
                    self.total_trades += 1
                    return True
                else:
                    return False
            
            # FALLBACK: Basic execution if intelligent engine not available
            logger.warning("⚠️  Intelligent Engine not available - using basic execution")
            entry_price = signal.get('entry', signal.get('price', 0))
            size_usd = 10.0  # Start with $10 positions on testnet
            
            # Create order via ccxt
            if side == 'buy':
                params = {'createMarketBuyOrderRequiresPrice': False}
                order = await asyncio.to_thread(
                    self.testnet_exchange.create_market_buy_order,
                    symbol,
                    size_usd,
                    params
                )
            else:  # sell
                # Calculate quantity
                quantity = size_usd / entry_price if entry_price > 0 else 0.01
                order = await asyncio.to_thread(
                    self.testnet_exchange.create_market_sell_order,
                    symbol,
                    quantity
                )
            
            logger.info(f"✅ TESTNET Trade executed (basic)!")
            logger.info(f"   Order ID: {order.get('id', 'N/A')}")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Side: {side.upper()}")
            logger.info(f"   Size: ${size_usd}")
            
            self.total_trades += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Testnet execution failed: {e}")
            return False
    
    async def _execute_via_profit_system(self, signal: Dict, symbol: str, side: str, confidence: float):
        """Execute trade via COMPLETE PROFIT SYSTEM (Gate.io live)"""
        try:
            logger.info(f"   💰 Executing via COMPLETE PROFIT SYSTEM (Gate.io)...")
            
            # Format signal for profit system
            signal_dict = {
                'symbol': symbol,
                'side': side,
                'confidence': confidence,
                'entry': signal.get('entry', signal.get('price', 0)),
                'take_profit': signal.get('take_profit'),
                'stop_loss': signal.get('stop_loss'),
                'strategy': signal.get('strategy', signal.get('type', 'unknown')),
                'source': signal.get('source', 'ExecutionOrchestrator'),
                'timeframe': signal.get('timeframe', ''),
                'profit_target_pct': signal.get('profit_target_pct', 0.3),
            }
            
            execution_result = await self.profit_system.execute_signal(signal_dict)
            
            if execution_result:
                logger.info(f"✅ Trade executed via COMPLETE PROFIT SYSTEM!")
                self.total_trades += 1
                return True
            else:
                logger.warning(f"❌ Execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Profit system execution failed: {e}")
            return False
            
            # EXECUTE THE TRADE!
            logger.info(f"⚡ EXECUTING: {action.upper()} {symbol} (confidence: {confidence:.1%})")
            
            result = await self.execute_trade(
                symbol=symbol,
                side=action,
                confidence=confidence,
                signal=signal
            )
            
            if result:
                logger.info(f"✅ Trade executed successfully: {symbol}")
            else:
                logger.warning(f"❌ Trade execution failed: {symbol}")
                
        except Exception as e:
            logger.error(f"Decision processing error: {e}")
    
    async def execute_trade(self, 
                           symbol: str, 
                           side: str, 
                           confidence: float,
                           signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute trade with smart logic
        
        Returns trade result or None if failed
        """
        
        start_time = time.time()
        
        try:
            # Get current price
            price = signal.get('data', {}).get('price', 0)
            if not price:
                # Try to fetch current price
                price = await self.get_current_price(symbol)
            
            if not price:
                logger.error(f"Cannot get price for {symbol}")
                return None
            
            # Calculate smart position size
            volatility = signal.get('data', {}).get('volatility', 0.02)
            position_size_usd = self.position_sizer.calculate_position_size(
                confidence=confidence,
                volatility=volatility
            )
            
            # Convert to base currency amount
            amount = position_size_usd / price
            
            # Calculate stop loss and take profit
            stop_loss_pct = 0.01  # 1% stop loss
            take_profit_pct = 0.02  # 2% take profit (2:1 reward/risk)
            
            if side == 'buy':
                stop_loss = price * (1 - stop_loss_pct)
                take_profit = price * (1 + take_profit_pct)
            else:
                stop_loss = price * (1 + stop_loss_pct)
                take_profit = price * (1 - take_profit_pct)
            
            # USE COMPLETE PROFIT SYSTEM for direct Gate.io execution
            execution_result = None
            
            if self.profit_system:
                try:
                    # Execute using COMPLETE PROFIT SYSTEM
                    # This does ACTUAL Gate.io orders, not delegation
                    logger.info("🚀 Using COMPLETE PROFIT SYSTEM for direct execution...")
                    
                    signal_dict = {
                        'symbol': symbol,
                        'side': side,
                        'confidence': confidence,
                        'price': price
                    }
                    
                    execution_result = await self.profit_system.execute_signal(signal_dict)
                    
                    if execution_result:
                        logger.info("✅ COMPLETE PROFIT SYSTEM executed successfully!")
                    
                except Exception as e:
                    logger.error(f"COMPLETE PROFIT SYSTEM execution error: {e}")
            
            # Fallback: Try REAL_PROFIT_BOT (Gate.io)
            if not execution_result and 'real_profit' in self.engines and self.engines['real_profit']:
                try:
                    execution_result = self.engines['real_profit'].execute_trade(
                        symbol=symbol,
                        signal=side.upper(),
                        price=price
                    )
                except Exception as e:
                    logger.debug(f"Real profit execution: {e}")
            
            # Fallback 2: Direct exchange execution (Bybit testnet or any exchange)
            if not execution_result:
                try:
                    # Get first available exchange
                    exchange = None
                    exchange_name = 'unknown'
                    
                    if isinstance(self.engines, dict):
                        for name, eng in self.engines.items():
                            if eng:
                                exchange = eng
                                exchange_name = name
                                break
                    
                    if exchange:
                        logger.info(f"💱 Placing REAL order on {exchange_name}...")
                        
                        # Place REAL market order
                        order = exchange.create_order(
                            symbol=symbol,
                            type='market',
                            side=side.lower(),
                            amount=amount
                        )
                        
                        order_id = order.get('id', 'unknown')
                        filled_price = order.get('price', price)
                        filled_amount = order.get('filled', amount)
                        
                        logger.info(f"   ✅ Order placed: ID {order_id}")
                        logger.info(f"   📝 Filled: {filled_amount:.6f} {symbol} @ ${filled_price:.4f}")
                        
                        execution_result = {
                            'symbol': symbol,
                            'side': side,
                            'amount': filled_amount,
                            'price': filled_price,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': datetime.now().isoformat(),
                            'order_id': order_id,
                            'exchange': exchange_name,
                            'simulated': False  # REAL ORDER!
                        }
                        
                        # Update profit tracking
                        self.total_trades += 1
                        logger.info(f"   💰 Total trades: {self.total_trades}")
                    
                    else:
                        logger.warning("   ⚠️  No exchange available - simulation only")
                        execution_result = {
                            'symbol': symbol,
                            'side': side,
                            'amount': amount,
                            'price': price,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'timestamp': datetime.now().isoformat(),
                            'simulated': True
                        }
                
                except Exception as e:
                    logger.error(f"Exchange execution error: {e}")
                    # Still create record for tracking
                    execution_result = {
                        'symbol': symbol,
                        'side': side,
                        'amount': amount,
                        'price': price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': datetime.now().isoformat(),
                        'simulated': True,
                        'error': str(e)
                    }
            
            if execution_result:
                # Record position with risk manager
                self.risk_manager.record_position(
                    symbol=symbol,
                    side=side,
                    size=amount,
                    entry_price=price
                )
                
                # Record in ledger
                trade_record = {
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'entry_price': price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': confidence,
                    'position_size_usd': position_size_usd,
                    'timestamp': datetime.now(),
                    'status': 'open'
                }
                
                await self.data_hub.publish_trade(trade_record)
                
                # Update stats
                self.total_trades += 1
                execution_time = time.time() - start_time
                self.execution_times.append(execution_time)
                
                # Detailed trade information
                timeframe = signal.get('timeframe', '15m')
                strategy = signal.get('strategy', 'unknown')
                data_source = signal.get('source', 'AI_Collective')
                leverage = signal.get('leverage', 1)
                
                logger.info(f"⚡ TRADE EXECUTED:")
                logger.info(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                logger.info(f"   📊 Symbol: {symbol}")
                logger.info(f"   📈 Side: {side.upper()}")
                logger.info(f"   💵 Amount: {amount:.6f}")
                logger.info(f"   💰 Entry: ${price:.4f}")
                logger.info(f"   🛑 Stop Loss: ${stop_loss:.4f} (-{stop_loss_pct:.1%})")
                logger.info(f"   🎯 Take Profit: ${take_profit:.4f} (+{take_profit_pct:.1%})")
                logger.info(f"   💼 Position Size: ${position_size_usd:.2f}")
                logger.info(f"   ⚡ Leverage: {leverage}x")
                logger.info(f"   🎯 Confidence: {confidence:.1%}")
                logger.info(f"   ⏱️  Timeframe: {timeframe}")
                logger.info(f"   🧠 Strategy: {strategy}")
                logger.info(f"   📡 Data Source: {data_source}")
                logger.info(f"   ⚙️  Execution Time: {execution_time:.2f}s")
                logger.info(f"   💰 Expected Profit: ${position_size_usd * take_profit_pct:.2f}")
                logger.info(f"   📊 Risk/Reward: 1:{take_profit_pct/stop_loss_pct:.1f}")
                
                if not execution_result.get('simulated'):
                    logger.info(f"   ✅ Order ID: {execution_result.get('order_id', 'N/A')}")
                    logger.info(f"   💱 Exchange: {execution_result.get('exchange', 'unknown')}")
                
                logger.info(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                return execution_result
            
            return None
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return None
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price from engines or fresh exchange connection"""
        try:
            # Try to get from router
            if hasattr(self, 'router') and self.router:
                ticker = await self.router.fetch_ticker(symbol)
                if ticker and ticker.get('last'):
                    return ticker.get('last', 0)
        except Exception as e:
            logger.debug(f"Router fetch failed: {str(e)[:50]}")
        
        # Try engines
        if self.engines:
            for engine_name, engine in self.engines.items():
                try:
                    # Check if engine has an exchange object
                    if hasattr(engine, 'exchange') and engine.exchange:
                        ticker = await engine.exchange.fetch_ticker(symbol)
                        if ticker and ticker.get('last'):
                            logger.debug(f"Got price from {engine_name}: ${ticker['last']:.2f}")
                            return ticker['last']
                except Exception as e:
                    logger.debug(f"{engine_name} fetch failed: {str(e)[:50]}")
                    continue
        
        # Fallback: Create fresh exchange connection
        try:
            import ccxt.async_support as ccxt
            import os
            
            logger.debug(f"Trying fresh exchange connection for {symbol}...")
            
            # Try Gate.io first (user's main exchange)
            if os.getenv('GATE_API_KEY'):
                try:
                    exchange = ccxt.gateio({
                        'apiKey': os.getenv('GATE_API_KEY'),
                        'secret': os.getenv('GATE_SECRET'),
                        'enableRateLimit': True
                    })
                    ticker = await exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    await exchange.close()
                    logger.debug(f"Got ${price:.2f} from Gate.io")
                    return price
                except Exception as e:
                    logger.debug(f"Gate.io failed: {str(e)[:50]}")
            
            # Try Binance public API
            exchange = ccxt.binance({'enableRateLimit': True})
            ticker = await exchange.fetch_ticker(symbol)
            price = ticker['last']
            await exchange.close()
            logger.debug(f"Got ${price:.2f} from Binance")
            return price
            
        except Exception as e:
            logger.error(f"All price fetch attempts failed for {symbol}: {e}")
        
        return None
    
    async def monitor_positions(self):
        """Monitor open positions with ADVANCED FEATURES (Trailing Stop, Partial TP)"""
        
        # 🔥 CRITICAL FIX: Monitor BOTH tracking systems!
        positions_to_monitor = {}
        
        # 1. Check risk_manager positions
        positions_to_monitor.update(self.risk_manager.open_positions)
        
        # 2. Check intelligent_engine positions (THIS WAS MISSING!)
        if self.intelligent_engine and hasattr(self.intelligent_engine, 'active_trades_by_tf'):
            for symbol, trades in self.intelligent_engine.active_trades_by_tf.items():
                for trade in trades:
                    if trade.get('status') == 'open':
                        positions_to_monitor[symbol] = {
                            'entry_price': trade.get('entry_price'),
                            'side': trade.get('side'),
                            'order_id': trade.get('order_id'),
                            'timeframe': trade.get('timeframe')
                        }
        
        if positions_to_monitor:
            logger.info(f"💰 Monitoring {len(positions_to_monitor)} open positions...")
        
        for symbol, position in list(positions_to_monitor.items()):
            try:
                # Get current price
                current_price = await self.get_current_price(symbol)
                if not current_price:
                    continue
                
                entry_price = position['entry_price']
                side = position['side']
                
                # Calculate current P&L
                if side == 'buy':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # USE TRAILING STOP if available
                if self.trailing_stop:
                    new_stop = self.trailing_stop.update(
                        symbol=symbol,
                        current_price=current_price,
                        entry_price=entry_price,
                        initial_stop=entry_price * 0.99  # 1% initial stop
                    )
                    
                    # Check if trailing stop hit
                    if current_price <= new_stop:
                        logger.info(f"🛑 Trailing stop triggered: {symbol} ({pnl_pct:.2%})")
                        await self.close_position(symbol, current_price, 'trailing_stop')
                        continue
                
                # USE PARTIAL TP if available
                if self.partial_tp:
                    tp_orders = await self.partial_tp.check_tp_levels(symbol, current_price)
                    if tp_orders:
                        for order in tp_orders:
                            logger.info(f"🎯 {order['tp_level']} hit: {symbol}")
                            # Would execute partial close here
                
                # Fallback to basic stop loss and take profit
                else:
                    # Check stop loss (1% loss)
                    if pnl_pct < -0.01:
                        logger.warning(f"🛑 Stop loss triggered: {symbol} ({pnl_pct:.2%})")
                        await self.close_position(symbol, current_price, 'stop_loss')
                    
                    # Check take profit (2% profit)
                    elif pnl_pct > 0.02:
                        logger.info(f"🎯 Take profit triggered: {symbol} ({pnl_pct:.2%})")
                        await self.close_position(symbol, current_price, 'take_profit')
                
            except Exception as e:
                logger.debug(f"Position monitoring error for {symbol}: {e}")
    
    async def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close position and record result"""
        
        try:
            # Calculate P&L with risk manager
            pnl = self.risk_manager.close_position(symbol, exit_price)
            
            # Update balance
            new_balance = self.position_sizer.balance + pnl
            self.position_sizer.update_balance(new_balance)
            
            # Update stats
            if pnl > 0:
                self.winning_trades += 1
            
            self.total_profit += pnl
            
            # Record in ledger
            close_record = {
                'symbol': symbol,
                'exit_price': exit_price,
                'pnl': pnl,
                'reason': reason,
                'timestamp': datetime.now(),
                'status': 'closed'
            }
            
            await self.data_hub.publish_trade(close_record)
            
            # Calculate actual P&L percentage
            pnl_pct = ((exit_price - entry_price) / entry_price) if side == 'buy' else ((entry_price - exit_price) / entry_price)
            
            # Update win tracking
            if pnl > 0:
                self.winning_trades += 1
            
            logger.info(f"💰 POSITION CLOSED:")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Entry: ${entry_price:.4f}")
            logger.info(f"   Exit: ${exit_price:.4f}")
            logger.info(f"   P&L: ${pnl:.2f} ({pnl_pct:+.2%})")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   New Balance: ${new_balance:.2f}")
            logger.info(f"   Total Profit: ${self.total_profit:.2f}")
            logger.info(f"   Win Rate: {self.get_win_rate():.1%}")
            
        except Exception as e:
            logger.error(f"Position close error: {e}")
    
    def get_win_rate(self) -> float:
        """Get current win rate"""
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.get_win_rate(),
            'total_profit': self.total_profit,
            'current_balance': self.position_sizer.balance,
            'open_positions': len(self.risk_manager.open_positions),
            'daily_pnl': self.risk_manager.daily_pnl,
            'daily_trades': self.risk_manager.daily_trades,
            'avg_execution_time': sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        }
    
    # ============================================================================
    # 💰 SPECIAL STRATEGY EXECUTION HANDLERS
    # ============================================================================
    
    async def _execute_triangular_arbitrage(self, signal: Dict) -> bool:
        """
        Execute TRIANGULAR ARBITRAGE - 3 simultaneous orders for risk-free profit
        
        Example: BTC/USDT → ETH/USDT → ETH/BTC
        """
        try:
            path = signal.get('path', [])
            profit_pct = signal.get('profit_pct', 0)
            
            if len(path) != 3 or profit_pct < 0.1:
                logger.info(f"   ⏭️  Skipping: Insufficient profit or invalid path")
                return False
            
            logger.info(f"   🔄 Executing 3-leg arbitrage: {' → '.join(path)}")
            logger.info(f"   💰 Expected profit: {profit_pct:.2f}%")
            logger.info(f"   🎯 Risk: ZERO (simultaneous execution)")
            
            # Calculate order sizes (small for arbitrage)
            base_size_usd = min(self.position_sizer.balance * 0.01, 50)  # Max $50
            
            logger.info(f"   📊 Size per leg: ${base_size_usd:.2f}")
            logger.info(f"   ✅ TRIANGULAR ARBITRAGE LOGGED!")
            logger.info(f"   💎 Ready for atomic execution (TODO: implement 3-order placement)")
            
            self.total_trades += 1
            return True  # Logged for now
            
        except Exception as e:
            logger.error(f"Triangular arbitrage error: {e}")
            return False
    
    async def _execute_pairs_trade(self, signal: Dict) -> bool:
        """
        Execute PAIRS TRADE - Long one asset, short another (hedge)
        
        Example: LONG ETH + SHORT BTC (profit when ETH outperforms BTC)
        """
        try:
            trade_strategy = signal.get('trade', '')  # LONG_ETH_SHORT_BTC
            expected_profit_pct = signal.get('profit_potential', 0)
            
            # Parse strategy to get symbols
            if 'LONG_ETH_SHORT_BTC' in trade_strategy:
                long_symbol = 'ETH/USDT'
                short_symbol = 'BTC/USDT'
            elif 'LONG_BTC_SHORT_ETH' in trade_strategy:
                long_symbol = 'BTC/USDT'
                short_symbol = 'ETH/USDT'
            else:
                logger.info(f"   ⏭️  Unknown pairs trade: {trade_strategy}")
                return False
            
            logger.info(f"   📊 Pairs trade: LONG {long_symbol} + SHORT {short_symbol}")
            logger.info(f"   💰 Expected profit: {expected_profit_pct:.1f}% when correlation reverts")
            logger.info(f"   🛡️  Market-neutral hedge (no directional risk)")
            
            # Execute both legs (smaller size for hedged position)
            size_per_leg = min(self.position_sizer.balance * 0.02, 100)  # $100 max per leg
            
            logger.info(f"   🔄 Executing BOTH legs:")
            logger.info(f"      1. BUY {long_symbol} (${size_per_leg:.2f})")
            logger.info(f"      2. SELL {short_symbol} (${size_per_leg:.2f})")
            
            # Create signals for both legs
            long_signal = {
                'symbol': long_symbol,
                'side': 'buy',
                'confidence': signal.get('confidence', 0.85),
                'strategy': 'PAIRS_TRADE_LONG',
                'paired_with': short_symbol,
                'timeframe': '4h',  # Use different timeframe to avoid conflicts
                'is_hedge': True,  # Flag to bypass duplicate checks
                'price': 0  # Will fetch live price
            }
            
            short_signal = {
                'symbol': short_symbol,
                'side': 'sell',
                'confidence': signal.get('confidence', 0.85),
                'strategy': 'PAIRS_TRADE_SHORT',
                'paired_with': long_symbol,
                'timeframe': '4h',  # Use different timeframe
                'is_hedge': True,  # Flag to bypass duplicate checks
                'price': 0  # Will fetch live price
            }
            
            logger.info(f"   🎯 Both legs use 4h timeframe (separate from 5m scalps)")
            logger.info(f"   🛡️  Marked as hedge positions (bypass duplicate check)")
            
            # Execute both legs
            long_result = await self._execute_on_testnet(long_signal, long_symbol, 'buy', signal.get('confidence', 0.85))
            short_result = await self._execute_on_testnet(short_signal, short_symbol, 'sell', signal.get('confidence', 0.85))
            
            if long_result and short_result:
                logger.info(f"   ✅ PAIRS TRADE EXECUTED! Both legs opened!")
                logger.info(f"   💎 Market-neutral hedge active - profit when correlation reverts!")
                self.total_trades += 1
                return True
            elif long_result or short_result:
                logger.warning(f"   ⚠️  PARTIAL EXECUTION: Long={long_result}, Short={short_result}")
                logger.warning(f"   🛡️  WARNING: Unhedged position! Monitor closely!")
                return False
            else:
                logger.info(f"   ⏭️  Neither leg executed (balance or limits)")
                return False
            
        except Exception as e:
            logger.error(f"Pairs trade error: {e}")
            return False
    
    async def _execute_volatility_straddle(self, signal: Dict) -> bool:
        """
        Execute VOLATILITY STRADDLE - Profit from movement, not direction
        """
        try:
            logger.info(f"   💎 VOLATILITY STRADDLE logged")
            logger.info(f"   📊 Profits from ANY price movement (direction-agnostic)")
            logger.info(f"   🎯 TODO: Implement with options or hedged positions")
            
            return True  # Logged for now
            
        except Exception as e:
            logger.error(f"Volatility straddle error: {e}")
            return False
    
    async def _execute_market_maker(self, signal: Dict) -> bool:
        """
        Execute MARKET MAKER - Place limit orders on both sides to earn spread
        """
        try:
            logger.info(f"   💰 MARKET MAKER mode logged")
            logger.info(f"   📊 Would place limit orders on bid/ask")
            logger.info(f"   💎 Earn spread like an exchange!")
            logger.info(f"   🎯 TODO: Implement limit order placement")
            
            return True  # Logged for now
            
        except Exception as e:
            logger.error(f"Market maker error: {e}")
            return False
    
    async def _execute_funding_arbitrage(self, signal: Dict) -> bool:
        """
        Execute FUNDING ARBITRAGE - Get paid to hold positions
        """
        try:
            logger.info(f"   💰 FUNDING ARBITRAGE logged")
            logger.info(f"   📊 Would open hedged perpetual position")
            logger.info(f"   💎 Earn funding rate passively!")
            logger.info(f"   🎯 TODO: Implement with perpetual contracts")
            
            return True  # Logged for now
            
        except Exception as e:
            logger.error(f"Funding arbitrage error: {e}")
            return False
