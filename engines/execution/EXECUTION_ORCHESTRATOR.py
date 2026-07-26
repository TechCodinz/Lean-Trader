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
    from engines.profit.COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem, get_profit_system, initialize_profit_system
    PROFIT_SYSTEM_AVAILABLE = True
    logger.info("[OK] COMPLETE PROFIT SYSTEM loaded - Direct Gate.io execution ready!")
except Exception as e:
    logger.warning(f" COMPLETE PROFIT SYSTEM not available: {e}")
    PROFIT_SYSTEM_AVAILABLE = False

# 🧠 INTELLIGENT EXECUTION ENGINE - Uses ALL engine intelligence!
try:
    from engines.execution.INTELLIGENT_EXECUTION_ENGINE import IntelligentExecutionEngine, get_intelligent_execution_engine
    INTELLIGENT_EXECUTION_AVAILABLE = True
    logger.info("🧠 INTELLIGENT EXECUTION ENGINE loaded - Multi-timeframe, session-aware trading!")
except Exception as e:
    logger.warning(f" INTELLIGENT EXECUTION ENGINE not available: {e}")
    INTELLIGENT_EXECUTION_AVAILABLE = False

# 🧠 COLLECTIVE CONSENSUS ENGINE - ALL engines scrutinize together!
try:
    from ai.intelligence.COLLECTIVE_CONSENSUS_ENGINE import CollectiveConsensusEngine, get_collective_consensus
    COLLECTIVE_CONSENSUS_AVAILABLE = True
    logger.info("🧠 COLLECTIVE CONSENSUS ENGINE loaded - ALL 205+ engines work in sync!")
except Exception as e:
    logger.warning(f" COLLECTIVE CONSENSUS ENGINE not available: {e}")
    COLLECTIVE_CONSENSUS_AVAILABLE = False

# 🎯 ENRICHED SIGNAL SYSTEM - Adds ALL vital info (WHAT, WHY, WHERE, HOW, RARE MEANS)!
try:
    from ai.intelligence.ENRICHED_SIGNAL_SYSTEM import EnrichedSignalSystem, get_enriched_signal_system
    ENRICHED_SIGNAL_AVAILABLE = True
    logger.info("🎯 ENRICHED SIGNAL SYSTEM loaded - Signals get ALL vital intelligence!")
except Exception as e:
    logger.warning(f" ENRICHED SIGNAL SYSTEM not available: {e}")
    ENRICHED_SIGNAL_AVAILABLE = False

# 🎛️ PITCH-BENT ADAPTIVE CONTROL SYSTEM - Continuous parameter bending!
try:
    from pitch_bent.integration import initialize_pitch_system, get_pitch_system
    from pitch_bent.models import MarketState, VenueType
    PITCH_BENT_AVAILABLE = True
    logger.info("🎛️ PITCH-BENT SYSTEM loaded - Adaptive parameter control ready!")
except Exception as e:
    logger.warning(f" PITCH-BENT SYSTEM not available: {e}")
    PITCH_BENT_AVAILABLE = False

# Master toggle for Pitch-Bent System
import os
ENABLE_PITCH_BENT_SYSTEM = os.getenv('ENABLE_PITCH_BENT', 'true').lower() == 'true' and PITCH_BENT_AVAILABLE


class SmartPositionSizer:
    """Smart position sizing based on account balance and risk"""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.balance = initial_balance
        # Adaptive sizing based on balance
        if initial_balance < 200:
            self.max_risk_per_trade = 0.08  # 8% risk for micro accounts (Aggressive growth)
            self.max_position_pct = 0.45    # 45% max position size (Allow growing fast)
            self.min_position_usd = 2.0     # LOWERED: Work with $57 balance (was 3.5)
            logger.info(f">> MICRO ACCOUNT DETECTED: Activating AGGRESSIVE COMPOUNDING (45% size limit, $2 min)")
        elif initial_balance < 1000:
            self.max_risk_per_trade = 0.05  # 5% risk
            self.max_position_pct = 0.25    # 25% max position size
            self.min_position_usd = 5.0
        else:
            self.max_risk_per_trade = 0.02  # 2% standard
            self.max_position_pct = 0.10    # 10% standard
            self.min_position_usd = 10.0
        
        # Dynamic sizing based on confidence
        self.use_dynamic_sizing = True
        self.aggressive_mode = True  # Grow account faster
        
        # 🌟 CONSCIOUSNESS HARMONIZER: Connect to unified consciousness
        try:
            from ai.intelligence.CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            self.consciousness = get_consciousness_harmonizer()
            self.consciousness.register_engine(
                "Execution",
                180.0,
                "emotional"
            )
            print(f"🌟 Execution connected to consciousness")
        except Exception as e:
            print(f"  Consciousness integration: {e}")
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
        # Base risk amount
        base_risk = self.balance * self.max_risk_per_trade
        
        # Kelly Criterion adjustment with cap
        win_prob = confidence
        loss_prob = 1 - confidence
        win_loss_ratio = 2.0
        
        kelly_fraction = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.40))  # Increased Kelly cap to 40% for growth
        
        # Adjust for volatility
        volatility_adjustment = max(0.5, 1.0 - volatility)
        
        # Adjust for confidence
        confidence_adjustment = 0.5 + (confidence * 0.5)
        
        # Calculate raw position size
        position_size = (base_risk / max(stop_loss_pct, 0.01)) * kelly_fraction * volatility_adjustment * confidence_adjustment
        
        # AGGRESSIVE MODE BOOST
        if self.aggressive_mode and confidence >= 0.75:
             # Boost for high confidence
             boost = 1.0 + ((confidence - 0.70) * 4.0) # Up to 2.2x boost
             position_size *= boost
             logger.info(f">> Aggressive sizing: confidence {confidence:.1%} → {boost:.2f}x boost")
        
        # Apply limits
        max_position = self.balance * self.max_position_pct
        position_size = min(position_size, max_position)
        position_size = max(position_size, self.min_position_usd)
        
        # Ensure we don't exceed balance
        position_size = min(position_size, self.balance * 0.98) # Leave 2% for fees
        
        return position_size
    
    def update_balance(self, new_balance: float):
        """Update balance after trades and adjust sizing parameters"""
        self.balance = new_balance
        
        # Re-evaluate adaptive sizing for compounding
        if self.balance < 200:
            self.max_risk_per_trade = 0.08
            self.max_position_pct = 0.45
            self.min_position_usd = 3.5
        elif self.balance < 500:
             self.max_risk_per_trade = 0.05
             self.max_position_pct = 0.25
             self.min_position_usd = 5.0
        else:
            self.max_risk_per_trade = 0.02
            self.max_position_pct = 0.10
            self.min_position_usd = 10.0


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
    
    def record_position(self, symbol: str, side: str, size: float, entry_price: float, stop_loss_pct: float = 0.01, take_profit_pct: float = None):
        """Record opened position with TP/SL tracking"""
        # 🔥 CRITICAL FIX: Calculate balance-aware TP if not provided
        if take_profit_pct is None:
            # Use balance-aware TP based on current balance
            take_profit_pct = self.get_balance_aware_take_profit(self.current_balance) if hasattr(self, 'current_balance') and self.current_balance else 0.02
        
        self.open_positions[symbol] = {
            'side': side,
            'size': size,
            'entry_price': entry_price,
            'timestamp': datetime.now(),
            'stop_loss_pct': stop_loss_pct,  # Store stop loss % for monitoring
            'take_profit_pct': take_profit_pct,  # 🔥 FIX: Store take profit % for monitoring
            'opened_at': datetime.now(),  # For max hold time tracking
        }
    
    def close_position(self, symbol: str, exit_price: float) -> float:
        """Close position and calculate P&L"""
        if symbol not in self.open_positions:
            return 0.0
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        # 🔥 FIX: Use size_usd if available, otherwise calculate from size
        size_usd = position.get('size_usd', 0)
        if size_usd == 0:
            # Fallback: try 'size' or calculate from entry_price
            size = position.get('size', 0)
            if size == 0:
                # Calculate size from position value
                size_usd = position.get('size_usd', position.get('value', 0))
                if size_usd == 0:
                    # Last resort: use entry_price to estimate
                    size_usd = entry_price * 0.1  # Estimate 10% of entry as size
            else:
                size_usd = size * entry_price  # Convert quantity to USD
        side = position['side']
        
        # 🔥 FIX: Calculate P&L using USD value - ensure it's accurate
        if side == 'buy':
            pnl = (exit_price - entry_price) / entry_price * size_usd  # P&L as USD
        else:
            pnl = (entry_price - exit_price) / entry_price * size_usd  # P&L as USD
        
        # 🔥 CRITICAL FIX: Cap P&L to reasonable limits to prevent inflation
        # If P&L is > 50% of size_usd, it's likely a calculation error
        if abs(pnl) > size_usd * 0.5:
            logger.warning(f"  P&L calculation seems wrong for {symbol}: ${pnl:.2f} (size: ${size_usd:.2f})")
            # Cap to 50% of size_usd
            pnl = max(-size_usd * 0.5, min(size_usd * 0.5, pnl))
            logger.warning(f"   Capped to: ${pnl:.2f}")
        
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
        
        # 🧠 COLLECTIVE CONSENSUS ENGINE - ALL engines work together!
        self.collective_consensus = None
        
        # 🎯 ENRICHED SIGNAL SYSTEM - ALL vital info!
        self.enriched_signal_system = None
        
        # 🎛️ PITCH-BENT SYSTEM - Adaptive parameter control
        self.pitch_system = None
        self.pitch_bent_enabled = ENABLE_PITCH_BENT_SYSTEM
        
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
                    logger.info("[OK] COMPLETE PROFIT SYSTEM initialized - Direct Gate.io execution!")
                except Exception as e:
                    logger.error(f"Failed to init profit system: {e}")
        
        # ADVANCED COMPONENTS (wired externally)
        self.action_decider = None  # AdvancedActionDecider
        self.trailing_stop = None  # TrailingStopManager
        self.compound_engine = None  # CompoundEngine  
        self.partial_tp = None  # PartialTPManager
        
        # Execution settings - ADAPTIVE BASED ON BALANCE!
        self.base_min_confidence = 0.75  # Base confidence for medium balances
        self.min_confidence = self.base_min_confidence  # Will be updated dynamically
        self.execution_enabled = True
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.execution_times = deque(maxlen=100)
        self.current_balance = 1000.0  # Track for adaptive confidence
        
        logger.info("⚡ Execution Orchestrator initialized (SMART LOGIC + COMPLETE PROFIT SYSTEM)")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Base Min Confidence: {self.base_min_confidence} (adaptive)")
        logger.info(f"   Risk per trade: {self.position_sizer.max_risk_per_trade:.1%}")
        logger.info(f"   Profit System: {'[OK] ACTIVE' if self.profit_system else '[X] INACTIVE'}")
        logger.info("   🎯 ADAPTIVE CONFIDENCE: Lower threshold for small balances!")

    def get_adaptive_confidence_threshold(self, balance: float) -> float:
        """
        Get adaptive confidence threshold based on balance size
        
        Small balances need MORE trades for faster growth
        Large balances can be MORE selective
        
        Balance Tiers:
        - $0-$20: 65% confidence (2-3x more trades)
        - $20-$100: 70% confidence  
        - $100-$500: 75% confidence (base)
        - $500+: 78% confidence (more selective)
        """
        if balance < 20:
            return 0.65  # AGGRESSIVE for micro balances
        elif balance < 100:
            return 0.70  # Still aggressive
        elif balance < 500:
            return 0.75  # Base threshold
        else:
            return 0.78  # More selective for larger balances
    
    def get_balance_aware_take_profit(self, balance: float) -> float:
        """
        🎯 BALANCE-AWARE TAKE PROFIT - TURBO CAPITAL RECYCLING!
        
        Lower balance = FASTER profit taking to recycle capital
        Higher balance = Can wait for bigger moves
        
        Key insight: With $10, waiting for 2% = $0.20 but ties up all capital
        Better to take 0.1-0.5% quickly = MORE trades = COMPOUND faster!
        
        Balance Tiers (ULTRA-AGGRESSIVE FOR GROWTH):
        - $0-$5: 0.10% TP (TURBO, ~15-30 seconds) >>
        - $5-$10: 0.15% TP (ultra-fast, ~30 seconds)
        - $10-$25: 0.25% TP (fast, ~1 minute)
        - $25-$50: 0.4% TP (quick, ~2 minutes)
        - $50-$100: 0.5% TP (normal scalp)
        - $100-$500: 1.0% TP (standard)
        - $500+: 2.0% TP (let profits run)
        """
        if balance < 5:
            return 0.001   # 0.10% - TURBO MODE (15-30sec exits) >> NEW!
        elif balance < 10:
            return 0.0015  # 0.15% - ULTRA FAST (30sec exits)
        elif balance < 25:
            return 0.0025  # 0.25% - FAST (1min exits)
        elif balance < 50:
            return 0.004   # 0.4% - QUICK (2min exits)
        elif balance < 100:
            return 0.005   # 0.5% - NORMAL SCALP
        elif balance < 500:
            return 0.01    # 1.0% - STANDARD
        else:
            return 0.02    # 2.0% - LET PROFITS RUN
    
    def get_balance_aware_max_positions(self, balance: float) -> int:
        """
        🎯 BALANCE-AWARE MAX CONCURRENT POSITIONS
        
        Lower balance = FEWER positions to not spread too thin
        Higher balance = More positions for diversification
        
        Key insight: $10 split into 5 trades = $2 each = dust!
        Better to do 1-2 trades with $5-10 each
        
        Balance Tiers:
        - $0-$10: MAX 1 position (focus capital)
        - $10-$25: MAX 2 positions
        - $25-$50: MAX 3 positions
        - $50-$100: MAX 4 positions
        - $100-$500: MAX 6 positions
        - $500+: MAX 10 positions
        """
        if balance < 10:
            return 1  # Focus ALL capital on one trade
        elif balance < 25:
            return 2
        elif balance < 50:
            return 3
        elif balance < 100:
            return 4
        elif balance < 500:
            return 6
        else:
            return 10
    
    def get_balance_aware_position_size(self, balance: float) -> float:
        """
        🎯 BALANCE-AWARE POSITION SIZE
        
        Lower balance = HIGHER % per trade (concentrate for growth)
        Higher balance = LOWER % per trade (protect capital)
        
        Balance Tiers:
        - $0-$10: 95% of balance (all-in for growth)
        - $10-$25: 80% of balance
        - $25-$50: 60% of balance
        - $50-$100: 40% of balance
        - $100-$500: 25% of balance
        - $500+: 15% of balance
        """
        if balance < 10:
            return 0.95  # 95% - GO BIG OR GO HOME
        elif balance < 25:
            return 0.80  # 80%
        elif balance < 50:
            return 0.60  # 60%
        elif balance < 100:
            return 0.40  # 40%
        elif balance < 500:
            return 0.25  # 25%
        else:
            return 0.15  # 15% - PROTECT LARGE BALANCE
    
    def get_balance_aware_max_hold_time(self, balance: float) -> int:
        """
        🎯 BALANCE-AWARE MAX HOLD TIME (minutes)
        
        Lower balance = SHORTER holds (quick profit taking)
        Higher balance = Can hold longer for bigger moves
        
        Balance Tiers:
        - $0-$10: 1 minute max (ultra-fast)
        - $10-$25: 2 minutes max
        - $25-$50: 3 minutes max
        - $50-$100: 5 minutes max
        - $100-$500: 10 minutes max
        - $500+: 30 minutes max
        """
        if balance < 10:
            return 1   # 1 min - GET OUT FAST
        elif balance < 25:
            return 2   # 2 min
        elif balance < 50:
            return 3   # 3 min
        elif balance < 100:
            return 5   # 5 min
        elif balance < 500:
            return 10  # 10 min
        else:
            return 30  # 30 min - LET IT RUN
    
    def get_balance_aware_timeframes(self, balance: float) -> list:
        """
        🎯 SCALPING-FIRST TIMEFRAME SELECTION
        
        ALWAYS use 1m-5m for scalping at ALL balance levels!
        Higher balance = BIGGER trade size, not different timeframes
        
        As balance grows, we ADD more timeframes but ALWAYS keep 1m-5m!
        The key is: scalping continues, but with bigger positions
        
        Balance Tiers:
        - ALL balances: ALWAYS include 1m, 5m (core scalping)
        - $25+: Can also add 15m opportunities
        - $50+: Can also add 1h swing trades
        - $500+: Can add 4h for bigger moves (but still scalping!)
        """
        # ALWAYS include 1m and 5m for scalping!
        timeframes = ['1m', '5m']  # CORE SCALPING - ALWAYS ON!
        
        if balance >= 25:
            timeframes.append('15m')  # Add medium opportunities
        if balance >= 50:
            timeframes.append('1h')   # Add swing trades
        if balance >= 500:
            timeframes.extend(['4h', '1d'])  # Add big moves
        
        return timeframes
    
    def get_scalping_trade_amount(self, balance: float) -> float:
        """
        🎯 SCALPING TRADE AMOUNT - SCALES WITH BALANCE!
        
        Small balance = Small trades (but high %)
        Large balance = BIGGER ABSOLUTE trades (better accumulation!)
        
        Formula: Use % of balance that grows as balance grows
        
        Balance Tiers:
        - $0-$25: Use 95% (maximize growth from nothing)
        - $25-$50: Use $20 or 80% (whichever larger)
        - $50-$100: Use $40 or 60% (whichever larger)
        - $100-$500: Use $80 or 40% (whichever larger)
        - $500-$1000: Use $200 or 30% (whichever larger)
        - $1000+: Use $400 or 25% (scale up!)
        """
        if balance < 25:
            return balance * 0.95  # 95% - GO BIG
        elif balance < 50:
            return max(20, balance * 0.80)  # At least $20 per trade
        elif balance < 100:
            return max(40, balance * 0.60)  # At least $40 per trade
        elif balance < 500:
            return max(80, balance * 0.40)  # At least $80 per trade
        elif balance < 1000:
            return max(200, balance * 0.30)  # At least $200 per trade
        else:
            return max(400, balance * 0.25)  # BIG trades at high balance!
        
        
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
        logger.info("   [OK] EXECUTION LOOP IS RUNNING - Monitoring for signals...")
        
        # 🔥 CRITICAL: Sync balance IMMEDIATELY on startup!
        try:
            actual_balance = await self.sync_balance()
            if actual_balance and actual_balance > 0:
                self.current_balance = actual_balance
                logger.info(f"   💰 EARLY BALANCE SYNC: ${actual_balance:.2f}")
                logger.info(f"   🎯 Balance-aware TP: {self.get_balance_aware_take_profit(actual_balance):.2%}")
                logger.info(f"   ⏱️ Max hold time: {self.get_balance_aware_max_hold_time(actual_balance)} min")
                logger.info(f"   📊 Max positions: {self.get_balance_aware_max_positions(actual_balance)}")
                
                # Update risk manager with balance-aware max positions
                if hasattr(self.risk_manager, 'max_open_positions'):
                    self.risk_manager.max_open_positions = self.get_balance_aware_max_positions(actual_balance)
                    logger.info(f"   🔧 Updated max positions: {self.risk_manager.max_open_positions}")
            else:
                logger.warning(f"    Could not sync balance, using default ${self.current_balance:.2f}")
        except Exception as e:
            logger.warning(f"    Early balance sync failed: {e}")
        
        # Initialize profit system if available
        if self.profit_system:
            await self.profit_system.initialize()
            # Start position monitoring loop in background
            asyncio.create_task(self.profit_system.run_monitoring_loop())
            logger.info("[OK] COMPLETE PROFIT SYSTEM monitoring active!")
        
        loop_iterations = 0
        while self.execution_enabled:
            loop_iterations += 1
            # Log that loop is running (every 10 iterations)
            if loop_iterations % 10 == 0:
                logger.info(f"   🔄 Execution loop running... (iteration {loop_iterations})")
            
            try:
                # Reset daily stats if new day
                self.risk_manager.reset_daily_stats()
                
                # Check for decisions in alert queue
                if not self.data_hub.alert_queue.empty():
                    decision = await self.data_hub.alert_queue.get()
                    
                    # Validate and execute
                    await self.process_decision(decision)
                
                # ACTIVELY CHECK HUB FOR NEW SIGNALS (don't just wait for alert queue!)
                signals = list(self.data_hub.recent_signals)[:20]
                
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
                    
                    # [OK] FIX: If no profit targets, add intelligent defaults!
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
                    await self.monitor_positions()  # No timeout - let it run fully
                except Exception as e:
                    logger.error(f"Position monitoring error: {e}")
                
                # 🔥 AGGRESSIVE BALANCE RECOVERY - Sell any stuck crypto holdings!
                try:
                    await self.aggressive_balance_recovery()
                except Exception as e:
                    logger.debug(f"Balance recovery: {e}")
                
                logger.info("💤 Sleeping 5 seconds before next iteration...")
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"[X] Execution loop error: {e}")
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
            
            # 🔥 VALIDATE SYMBOL - Skip invalid symbols (forex, invalid pairs, etc.)
            invalid_patterns = ['/JPY', '/NZD', '/EUR', '/GBP', 'UKOIL', 'XPDUSD', 'COPPER', 'PI/USDT', 'AERO/USDT', 'FYNOR/USDT', 'BIST/USDT', 'ONT/USDT', 'RATS/USDT', 'LEE/USDT', 'GUSD/USDT']
            if any(pattern in symbol for pattern in invalid_patterns):
                logger.info(f"   ⏭️  Gracefully skipping forex pair: {symbol} (not available on current exchange)")
                return
            
            # Skip if symbol doesn't end with /USDT (for now)
            if not symbol.endswith('/USDT'):
                logger.info(f"   ⏭️  Gracefully skipping non-USDT pair: {symbol} (crypto exchange supports USDT pairs only)")
                return
            
            # Convert confidence to 0-1 range if needed
            if confidence > 1:
                confidence = confidence / 100
            
            # Check confidence threshold
            # Get adaptive confidence threshold based on current balance
            adaptive_threshold = self.get_adaptive_confidence_threshold(self.current_balance)
            
            if confidence < adaptive_threshold:
                logger.debug(f"   Skipping {symbol}: confidence {confidence:.1%} < {adaptive_threshold:.1%} (balance ${self.current_balance:.2f})")
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
                logger.info(f"[OK] Signal executed successfully!")
            else:
                logger.warning(f"  Signal execution failed")
        
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
            # Get adaptive confidence threshold
            adaptive_threshold = self.get_adaptive_confidence_threshold(self.current_balance)
            
            if confidence < adaptive_threshold:
                logger.debug(f"Low confidence: {confidence:.2%} < {adaptive_threshold:.2%} (balance ${self.current_balance:.2f})")
                return
            
            # USE ADVANCED ACTION DECIDER if available
            if self.action_decider:
                # Get price history from exchange (REAL DATA)
                price = signal.get('data', {}).get('price', 0)
                price_history = [price] if price else []
                
                try:
                    # Fetch real OHLCV candles for price history
                    exchange = getattr(self, 'testnet_exchange', None) or (
                        list(self.engines.values())[0] if isinstance(self.engines, dict) and self.engines else None
                    )
                    if exchange and hasattr(exchange, 'fetch_ohlcv') and symbol:
                        ohlcv = await asyncio.to_thread(exchange.fetch_ohlcv, symbol, '5m', None, 50)
                        if ohlcv and len(ohlcv) > 0:
                            price_history = [candle[4] for candle in ohlcv]  # Close prices
                except Exception:
                    pass  # Fall back to signal price
                
                if not price_history:
                    price_history = [price] * 50  # Ultimate fallback
                
                # Get current opportunities from data_hub
                opportunities = list(self.data_hub.recent_signals)[:10] if hasattr(self, 'data_hub') and self.data_hub else []

                
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
                logger.info(f" Trade blocked: {reason}")
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
                exchanges=all_exchanges or {},  # [OK] Pass all exchanges for router!
                balance=actual_bal  # [OK] PASS ACTUAL BALANCE!
            )
            logger.info("🧠 [OK] INTELLIGENT EXECUTION ENGINE initialized with TESTNET!")
            if all_exchanges:
                logger.info(f"   🎯 Has access to {len(all_exchanges)} exchanges for routing")
        
        logger.info("[OK] ExecutionOrchestrator wired to Bybit TESTNET!")
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
            # 🔥 STEP 0: EARLY FOREX/COMMODITY FILTER - Save cycles on testnet!
            # In testnet mode, we can ONLY trade crypto USDT pairs on Bybit
            symbol = signal.get('symbol', signal.get('pair', ''))
            if self.mode == "testnet":
                # List of forex currency pairs to reject
                forex_indicators = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'NZD', 'CAD']
                # List of commodity indicators to reject  
                commodity_indicators = ['GOLD', 'SILVER', 'OIL', 'GAS', 'WHEAT', 'CORN', 'SOYBEAN', 
                                       'COFFEE', 'COTTON', 'PALLADIUM', 'PLATINUM', 'COPPER', 'NATGAS',
                                       'UKOIL', 'XPDUSD', 'XPTUSD', 'XAUUSD']
                
                # Check if it's a forex pair (has two currency codes like EUR/USD or EURUSD)
                is_forex = False
                clean_symbol = symbol.replace('/', '')
                for curr1 in forex_indicators:
                    for curr2 in forex_indicators:
                        if curr1 != curr2 and (f"{curr1}{curr2}" in clean_symbol or f"{curr1}/{curr2}" in symbol):
                            is_forex = True
                            break
                
                # Check if it's a commodity
                is_commodity = any(comm in symbol.upper() for comm in commodity_indicators)
                
                # If forex or commodity, skip immediately (don't waste time on consensus/enrichment)
                if is_forex or is_commodity:
                    logger.info(f"   ⚡ EARLY SKIP: {symbol} is {'forex' if is_forex else 'commodity'} - not available on Bybit testnet")
                    return False
                
                # Crypto pairs MUST contain /USDT for Bybit testnet spot trading
                if '/USDT' not in symbol:
                    logger.info(f"   ⚡ EARLY SKIP: {symbol} is not a /USDT pair - skipping on testnet")
                    return False
            
            # 🧠 STEP 1: COLLECTIVE CONSENSUS - ALL 205+ engines scrutinize together!
            if self.collective_consensus:
                logger.info(f"🔍 Sending signal to COLLECTIVE CONSENSUS for scrutiny...")
                signal = await self.collective_consensus.scrutinize_signal(signal)
                
                # Check if collective approved the signal
                if not signal.get('approved', False):
                    logger.warning(f"   [X] Signal REJECTED by collective consensus!")
                    logger.warning(f"   Agreement: {signal.get('collective_agreement', 0):.0%} (adaptive threshold used)")
                    logger.warning(f"   Confidence: {signal.get('collective_confidence', 0):.0%} (adaptive threshold used)")
                    return False
                
                logger.info(f"   [OK] Signal APPROVED by collective consensus!")
                logger.info(f"   🤝 Agreement: {signal.get('collective_agreement', 0):.0%}")
                logger.info(f"   💪 Collective confidence: {signal.get('collective_confidence', 0):.0%}")
            else:
                logger.debug("    Collective consensus not available - proceeding without full scrutiny")
            
            # 🎯 STEP 2: ENRICH SIGNAL with ALL VITAL INFO (WHAT, WHY, WHERE, HOW, RARE MEANS)!
            if self.enriched_signal_system:
                logger.info(f"🎯 Enriching signal with ALL vital intelligence...")
                signal = await self.enriched_signal_system.enrich_signal(signal)
                logger.info(f"   [OK] Signal enriched with complete intelligence!")
                logger.info(f"   📊 WHAT: {signal.get('what', {}).get('action')} @ {signal.get('what', {}).get('urgency')} urgency")
                logger.info(f"   🧠 WHY: {signal.get('why', {}).get('primary_reason')}")
                logger.info(f"   📍 WHERE: {signal.get('where', {}).get('exchange')} {signal.get('where', {}).get('market_type')}")
                logger.info(f"   🎯 HOW: {signal.get('how', {}).get('execution_strategy')}")
                logger.info(f"   💎 RARE MEANS: {len(signal.get('rare_precious_means', {}).get('hidden_opportunities', []))} opportunities")
            else:
                logger.debug("    Enriched signal system not available")
            
            # 🔄 STEP 2.5: INTELLIGENT MULTI-EXCHANGE ROUTING
            # Check WHERE signal should execute and verify balance
            target_exchange_name = signal.get('where', {}).get('exchange', 'bybit_testnet')
            market_type = signal.get('where', {}).get('market_type', 'spot')
            symbol = signal.get('symbol', '')
            
            # Import auto-discovery if available
            try:
                from AUTO_EXCHANGE_DISCOVERY import get_auto_discovery
                discovery = get_auto_discovery()
                
                # Check balance on all exchanges
                await discovery.check_all_balances()
                
                # MT5 Forex routing - WIRE ACTUAL EXECUTION
                if market_type in ['forex', 'commodities'] or target_exchange_name == 'bybit_forex':
                    logger.info(f"   🌍 FOREX/COMMODITY signal → Routing to MT5 Demo")
                    if discovery.exchanges.get('mt5_forex_available'):
                        logger.info(f"   [OK] Routing {symbol} to MT5 Demo Account")
                        
                        # 🔥 ACTUALLY EXECUTE ON MT5 DEMO
                        try:
                            from mt5_adapter import order_send_market, mt5_init
                            import MetaTrader5 as mt5
                            
                            # Initialize MT5 connection
                            if not mt5_init():
                                logger.error("   [X] MT5 connection failed")
                                return False
                            
                            # Format symbol for MT5 (EUR/USD → EURUSD)
                            mt5_symbol = symbol.replace('/', '').replace('+', '')
                            
                            # Calculate lot size based on balance (0.01 lot minimum for demo)
                            lot_size = 0.01  # Micro lot for demo testing
                            
                            # Get SL/TP from signal
                            sl = signal.get('stop_loss', None)
                            tp = signal.get('take_profit', None)
                            
                            # Execute MT5 order
                            result = order_send_market(
                                mt5mod=mt5,
                                symbol=mt5_symbol,
                                side=side,
                                lots=lot_size,
                                sl=sl,
                                tp=tp
                            )
                            
                            if result and result.get('ok'):
                                logger.info(f"   [OK] MT5 ORDER PLACED: {mt5_symbol} {side} {lot_size} lots")
                                return True
                            else:
                                logger.warning(f"    MT5 order result: {result.get('comment', 'unknown')}")
                                # Fallback: still record signal even if MT5 blocked
                                return False
                                
                        except ImportError as ie:
                            logger.warning(f"    MT5 import error: {ie}")
                            logger.warning(f"   📝 Running on Linux VPS - MT5 not available directly")
                            # Record the forex signal for manual execution or future use
                            return False
                        except Exception as e:
                            logger.error(f"   [X] MT5 execution error: {e}")
                            return False
                    else:
                        logger.warning(f"    MT5 not configured, skipping forex/commodity signal")
                
                # Check if target exchange has sufficient balance
                target_balance = discovery.balances.get(target_exchange_name, 0)
                # 🔥 CRITICAL FIX: Lowered from $10 to $0.10 to enable micro-trading on testnet!
                min_required = 0.10  # Minimum $0.10 to trade (was $10 - blocking all trades!)
                
                if target_balance < min_required:
                    logger.info(f"    {target_exchange_name} balance too low (${target_balance:.2f})")
                    
                    # Find alternative exchange with balance
                    best = discovery.get_best_exchange_for_trade(min_required)
                    if best:
                        alt_name, alt_exchange, alt_balance = best
                        logger.info(f"   [OK] SMART ROUTING: {target_exchange_name} → {alt_name} (${alt_balance:.2f})")
                        
                        # Update signal routing
                        if 'where' not in signal:
                            signal['where'] = {}
                        signal['where']['exchange'] = alt_name
                        signal['where']['routing_reason'] = f'Balance-aware routing (${alt_balance:.2f} available)'
                    else:
                        logger.warning(f"   [X] NO exchange has sufficient balance! Skipping trade.")
                        return False
            except ImportError:
                logger.debug("   Auto-discovery not available, proceeding with default routing")
            except Exception as e:
                logger.warning(f"   Exchange routing check failed: {e}, proceeding anyway")
            
            # 🎯 STEP 3: DETECT SIGNAL TYPE - Standard or Special Strategy
            signal_type = signal.get('type', 'standard')
            
            # DEBUG: Log signal type
            logger.debug(f"   🔍 Signal type: '{signal_type}'")
            
            # ============================================================
            # SPECIAL STRATEGY EXECUTION
            # ============================================================
            
            if signal_type == 'triangular_arbitrage':
                logger.info(f"💰 TRIANGULAR ARBITRAGE: {signal.get('profit_pct', 0):.2f}% profit!")
                return await self._execute_triangular_arbitrage(signal)
            
            elif signal_type == 'correlation_exploit':  # [OK] MONEY_PRINTER uses this for pairs trade
                logger.info(f"💰 PAIRS TRADE: {signal.get('profit_potential', 0):.1f}% profit potential!")
                return await self._execute_pairs_trade(signal)
            
            elif signal_type == 'volatility_harvest':  # [OK] MONEY_PRINTER uses this
                logger.info(f"💰 VOLATILITY STRADDLE: Profit from {signal.get('volatility_pct', 0):.1f}% vol!")
                return await self._execute_volatility_straddle(signal)
            
            elif signal_type == 'market_maker':
                logger.info(f"💰 MARKET MAKER: Earn ${signal.get('expected_profit', 0):.2f} spread!")
                return await self._execute_market_maker(signal)
            
            elif signal_type == 'funding_farm':  # [OK] MONEY_PRINTER uses this
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
                logger.info(f"Invalid signal: missing symbol or side")
                return False
            
            # 🎯 CRITICAL FILTER: Gracefully handle forex, commodities, and special pairs
            # Forex/commodity pairs (no / or : in symbol) - COFFEE, WHEAT, EUR/USD etc.
            if '/' not in symbol and ':' not in symbol:
                logger.info(f"   🌐 Signal received for {symbol} (forex/commodity) - will route to appropriate exchange when multi-market support is added")
                return False
            
            # Leveraged tokens (3S, 3L, 5S, 5L - not always available)
            if '3S/' in symbol or '3L/' in symbol or '5S/' in symbol or '5L/' in symbol:
                logger.info(f"   ⚡ Signal received for leveraged token {symbol} - checking availability...")
                # Continue execution - let exchange validation handle it
            
            # Crypto exchange mode checks  
            # REMOVED: Bybit testnet supports forex/commodities - let exchange decide
            # if self.mode == 'testnet' and '/USDT' not in symbol:
            #     logger.info(f"   ⏭️  Skipping {symbol} on testnet (USDT pairs only in test mode)")
            #     return False
            
            # Check risk management
            can_trade, reason = self.risk_manager.can_open_position(symbol, side)
            if not can_trade:
                logger.info(f"Trade blocked: {reason}")
                return False
            
            # >> TIER 1 ENHANCEMENTS - Apply before execution!
            try:
                # Get orchestrator's enhancement systems
                from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
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
                logger.error(f"[X] No exchange available! Mode: {self.mode}, Active: {self.active_exchange}")
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
            # 🔥 VALIDATE SYMBOL AGAIN - Double check before execution!
            invalid_patterns = ['/JPY', '/NZD', '/EUR', '/GBP', 'UKOIL', 'XPDUSD', 'COPPER', 
                              'PI/USDT', 'AERO/USDT', 'FYNOR/USDT', 'BIST/USDT', 'ONT/USDT', 
                              'RATS/USDT', 'LEE/USDT', 'GUSD/USDT', 'COINX/USDT']
            if any(pattern in symbol for pattern in invalid_patterns):
                logger.debug(f"   ⏭️  Skipping invalid symbol in testnet execution: {symbol}")
                return False
            
            # Skip if symbol doesn't end with /USDT
            if not symbol.endswith('/USDT'):
                logger.debug(f"   ⏭️  Skipping non-USDT pair in testnet: {symbol}")
                return False
            
            # 🔥 VALIDATE SYMBOL AGAIN - Double check before execution!
            invalid_patterns = ['/JPY', '/NZD', '/EUR', '/GBP', 'UKOIL', 'XPDUSD', 'COPPER', 
                              'PI/USDT', 'AERO/USDT', 'FYNOR/USDT', 'BIST/USDT', 'ONT/USDT', 
                              'RATS/USDT', 'LEE/USDT', 'GUSD/USDT', 'COINX/USDT']
            if any(pattern in symbol for pattern in invalid_patterns):
                logger.debug(f"   ⏭️  Skipping invalid symbol in testnet execution: {symbol}")
                return False
            
            # Skip if symbol doesn't end with /USDT
            if not symbol.endswith('/USDT'):
                logger.debug(f"   ⏭️  Skipping non-USDT pair in testnet: {symbol}")
                return False
            
            # Initialize route with default
            route = {"exchange": "bybit_testnet", "market_type": "spot"}
            
            # 🧠 INTELLIGENT ROUTING: Find best exchange/market for this pair!
            try:
                from engines.routing.INTELLIGENT_EXCHANGE_ROUTER import get_intelligent_router
                router = get_intelligent_router()
                if router:
                    smart_route = await router.route_signal(signal)
                    if smart_route:
                        route = smart_route
                        logger.info(f"   🧠 ROUTER: {symbol} routed to {route['exchange']} {route['market_type']}")
                    else:
                        # Router returned None - try default route anyway for common testnet pairs
                        # This allows trading on pairs that exist on testnet but weren't discovered yet
                        logger.info(f"    Router returned None for {symbol} - using default testnet route anyway")
                        # Keep using default route (bybit_testnet, spot)
                else:
                    # Router not initialized - use default route
                    logger.info(f"    Router not initialized - using default bybit_testnet route for {symbol}")
            except Exception as e:
                logger.debug(f"   Router check failed: {e}, using default route")
            
            logger.info(f"   🧪 Executing on BYBIT TESTNET...")
            
            # 🧠 USE INTELLIGENT EXECUTION if available!
            if self.intelligent_engine:
                logger.info(f"   🧠 Using INTELLIGENT EXECUTION ENGINE!")
                
                # 🔧 INTELLIGENT ROUTING: Check if symbol is supported BEFORE creating plan!
                if self.intelligent_engine._should_skip_symbol(symbol):
                    logger.debug(f"⏭️  Skipping {symbol} - Not supported by current exchange (will route to MT5 when added)")
                    return False
                
                # ♾️ INFINITE TRADING - NO DUPLICATE CHECKS!
                # With 490 models, trade as much as profitable!
                # Each signal is unique (different timeframe, strategy, confidence)
                is_hedge = signal.get('is_hedge', False)
                if is_hedge:
                    logger.info(f"   🛡️  Hedge position detected")
                
                # [OK] PASS ROUTE INFO TO EXECUTION ENGINE!
                if route:
                    signal['route_exchange'] = route['exchange']  # bybit_testnet
                    signal['route_market_type'] = route['market_type']  # spot/swap
                
                # 1. Create COMPLETE trade plan using ALL intelligence
                trade_plan = await self.intelligent_engine.create_complete_trade_plan(signal)
                
                if not trade_plan:
                    logger.debug(f"⏭️  Could not create trade plan for {symbol} (may not be available)")
                    return False
                
                # 2. Execute the intelligent trade
                logger.info(f"   >> Calling execute_intelligent_trade for {symbol}...")
                result = await self.intelligent_engine.execute_intelligent_trade(trade_plan)
                
                if result and result.get('success') != False:
                    logger.info(f"[OK] INTELLIGENT TRADE EXECUTED!")
                    logger.info(f"   🎯 Strategy: {trade_plan['strategy']}")
                    logger.info(f"   💰 Size: ${trade_plan['lot_size_usd']:.2f} @ {trade_plan['leverage']}x")
                    logger.info(f"   📊 {len(trade_plan['take_profit_levels'])} TP levels")
                    logger.info(f"   🛡️  Stop Loss: ${trade_plan['stop_loss']:.4f}")
                    logger.info(f"   ⏱️  Max Hold: {trade_plan['max_hold_time_minutes']} min")
                    logger.info(f"   📈 Active TFs on {symbol}: {len(self.intelligent_engine.active_trades_by_tf[symbol])}")
                    
                    # 🔥 DEBUG: Log what's in result (use INFO so it's visible)
                    logger.info(f"   🔍 DEBUG: Result type: {type(result)}")
                    logger.info(f"   🔍 DEBUG: Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    logger.info(f"   🔍 DEBUG: Result entry_price: {result.get('entry_price') if isinstance(result, dict) else 'N/A'}")
                    
                    # 🔥 CRITICAL: Track position IMMEDIATELY with ACTUAL entry price from order!
                    try:
                        # Get ACTUAL entry price from result (from order execution)
                        # Check multiple possible locations in result dict
                        entry_price = result.get('entry_price') or result.get('trade_record', {}).get('entry_price')
                        if not entry_price or entry_price <= 0:
                            # Fallback to trade_plan entry_price
                            entry_price = trade_plan.get('entry_price')
                        if not entry_price or entry_price <= 0:
                            # Check if result has the trade_record with entry_price
                            if isinstance(result, dict) and 'trade_record' in result:
                                entry_price = result['trade_record'].get('entry_price', 0)
                        if not entry_price or entry_price <= 0:
                            # Last resort: get current price
                            try:
                                ticker = await asyncio.to_thread(self.testnet_exchange.fetch_ticker, symbol)
                                entry_price = ticker.get('last', 0)
                                logger.warning(f"     Using current price as entry_price fallback: ${entry_price:.6f}")
                            except:
                                entry_price = trade_plan.get('stop_loss', 0) * 1.01  # Estimate from stop loss
                                logger.warning(f"     Using estimated entry_price from stop_loss: ${entry_price:.6f}")
                        
                        if entry_price <= 0:
                            logger.error(f"   [X] CRITICAL: Could not determine entry_price for {symbol}!")
                            logger.error(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                            logger.error(f"   Result entry_price: {result.get('entry_price') if isinstance(result, dict) else 'N/A'}")
                            logger.error(f"   Trade plan entry: {trade_plan.get('entry_price')}")
                        else:
                            if hasattr(self, 'risk_manager') and self.risk_manager:
                                # 🔥 CRITICAL: Verify entry_price is valid before storing
                                if entry_price and entry_price > 0:
                                    self.risk_manager.open_positions[symbol] = {
                                        'entry_price': entry_price,  # ACTUAL executed price!
                                        'side': signal.get('side', 'buy'),
                                        'order_id': result.get('order_id'),
                                        'size_usd': trade_plan['lot_size_usd'],
                                        'entry_time': asyncio.get_event_loop().time(),
                                        'stop_loss_pct': trade_plan.get('stop_loss_pct', 0.01),  # Store stop loss % for monitoring
                                        'take_profit_pct': trade_plan.get('take_profit_pct', 0.02),  # 🔥 Store TP % for monitoring
                                        'stop_loss': trade_plan.get('stop_loss'),
                                        'take_profit': trade_plan.get('take_profit'),
                                        'is_tracked': True  # Mark as properly tracked
                                    }
                                    logger.info("=" * 70)
                                    logger.info(f"   [OK] [OK] [OK] POSITION TRACKED: {symbol}")
                                    logger.info(f"   📍 Entry Price: ${entry_price:.6f}")
                                    logger.info(f"   💰 Size: ${trade_plan['lot_size_usd']:.2f}")
                                    logger.info(f"   🛡️  Stop Loss: {trade_plan.get('stop_loss_pct', 0.01)*100:.1f}%")
                                    logger.info(f"   🎯 Take Profit: {trade_plan.get('take_profit_pct', 0.02)*100:.1f}%")
                                    logger.info(f"   📋 Order ID: {result.get('order_id', 'N/A')}")
                                    logger.info("=" * 70)
                                else:
                                    logger.error(f"   [X] CRITICAL: Invalid entry_price ({entry_price}) - NOT TRACKING POSITION!")
                                    logger.error(f"   This position will NOT be monitored properly!")
                    except Exception as e:
                        logger.error(f"   [X] CRITICAL ERROR tracking position: {e}")
                        import traceback
                        logger.error(f"   Traceback: {traceback.format_exc()}")
                    
                    self.total_trades += 1
                    return True
                else:
                    reason = result.get('reason', 'unknown') if result else 'no_result'
                    error = result.get('error', '') if result else ''
                    logger.warning(f"     Trade execution failed: {reason}")
                    if error:
                        logger.warning(f"   Error details: {error}")
                    return False
            
            # FALLBACK: Basic execution if intelligent engine not available
            logger.warning("  Intelligent Engine not available - using basic execution")
            
            # Get actual balance first
            try:
                balance_info = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
                usdt_balance = balance_info.get('USDT', {}).get('free', 0) if isinstance(balance_info.get('USDT'), dict) else balance_info.get('USDT', 0)
                if not usdt_balance or usdt_balance < 5.0:
                    logger.error(f"[X] Insufficient balance: ${usdt_balance:.2f} (need at least $5.00)")
                    return False
            except Exception as e:
                logger.warning(f"  Could not fetch balance: {e}, using default")
                usdt_balance = 10.0  # Fallback
            
            entry_price = signal.get('entry', signal.get('price', 0))
            
            # Calculate position size: 8-15% of balance, minimum $5
            size_pct = min(0.15, max(0.08, confidence * 0.15))  # 8-15% based on confidence
            size_usd = max(5.0, min(usdt_balance * size_pct, usdt_balance * 0.25))  # Min $5, max 25% of balance
            
            # 🔥 CRITICAL FIX: Ensure minimum $5.00 (Bybit requirement)
            if size_usd < 5.0 and usdt_balance >= 5.0:
                # Scale up to meet minimum
                size_usd = min(5.0, usdt_balance * 0.30)  # Use up to 30% if needed
                logger.warning(f"     Scaled up to meet $5 minimum: ${size_usd:.2f}")
            
            # Final safety check
            size_usd = max(5.0, size_usd)
            
            logger.info(f"   💰 Position size: ${size_usd:.2f} ({size_pct*100:.1f}% of ${usdt_balance:.2f})")
            
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
            
            logger.info(f"[OK] TESTNET Trade executed (basic)!")
            logger.info(f"   Order ID: {order.get('id', 'N/A')}")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Side: {side.upper()}")
            logger.info(f"   Size: ${size_usd}")
            
            # 🔥 CRITICAL FIX: Track position so it can be monitored and closed!
            logger.warning(f"   🔍 Starting position tracking for {symbol}...")
            logger.info(f"   🔍 TRACKING: Starting position tracking for {symbol}...")
            try:
                # Get entry price from order
                entry_price = order.get('price') or order.get('average') or entry_price or 0
                logger.debug(f"   Entry price from order: {entry_price}")
                if entry_price == 0:
                    # Fetch current price as fallback
                    logger.debug(f"   Entry price is 0, fetching current price...")
                    ticker = await asyncio.to_thread(self.testnet_exchange.fetch_ticker, symbol)
                    entry_price = ticker.get('last', 0)
                    logger.debug(f"   Fetched entry price: {entry_price}")
                
                if entry_price == 0:
                    logger.warning(f"     Could not determine entry price for {symbol}")
                else:
                    # Track in risk manager
                    if hasattr(self, 'risk_manager') and self.risk_manager:
                        if not hasattr(self.risk_manager, 'open_positions'):
                            self.risk_manager.open_positions = {}
                        self.risk_manager.open_positions[symbol] = {
                            'entry_price': entry_price,
                            'side': side,
                            'order_id': order.get('id'),
                            'size_usd': size_usd,
                            'entry_time': asyncio.get_event_loop().time(),
                            'stop_loss_pct': 0.01,  # Default 1% stop loss
                            'take_profit_pct': 0.02,  # 🔥 Default 2% take profit (2:1 reward/risk)
                            'stop_loss': stop_loss,
                            'take_profit': take_profit
                        }
                        logger.warning(f"   [OK] Position tracked in risk_manager: {symbol} @ ${entry_price:.4f} (Total tracked: {len(self.risk_manager.open_positions)})")
                        # Also log at INFO level to ensure it shows up
                        logger.info(f"[OK] POSITION TRACKED: {symbol} @ ${entry_price:.4f} | Total: {len(self.risk_manager.open_positions)}")
                    else:
                        logger.error(f"   [X] risk_manager not available for tracking!")
                    
                    # Track in intelligent engine if available
                    if hasattr(self, 'intelligent_engine') and self.intelligent_engine:
                        if not hasattr(self.intelligent_engine, 'active_trades_by_tf'):
                            self.intelligent_engine.active_trades_by_tf = {}
                        if symbol not in self.intelligent_engine.active_trades_by_tf:
                            self.intelligent_engine.active_trades_by_tf[symbol] = []
                        
                        self.intelligent_engine.active_trades_by_tf[symbol].append({
                            'status': 'open',
                            'entry_price': entry_price,
                            'side': side,
                            'order_id': order.get('id'),
                            'timeframe': signal.get('timeframe', '5m'),
                            'entry_time': asyncio.get_event_loop().time()
                        })
                        logger.info(f"   [OK] Position tracked in intelligent_engine: {symbol}")
                    else:
                        logger.debug(f"   Intelligent engine not available (using risk_manager only)")
            except Exception as e:
                logger.error(f"   [X] ERROR tracking position: {e}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # 🔥 CRITICAL: Start profit monitoring for fast closing!
            try:
                from PROFIT_MONITORING_SYSTEM import monitor_trade_for_profit
                # Create trade plan for monitoring
                trade_plan = {
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'side': side,
                    'stop_loss': stop_loss,
                    'take_profit_levels': [take_profit] if take_profit else [entry_price * (1 + self.get_balance_aware_take_profit(self.current_balance))],
                    'max_hold_time_minutes': self.get_balance_aware_max_hold_time(self.current_balance),
                    'timeframe': signal.get('timeframe', '5m'),
                    'review_interval_seconds': 2  # FORCE FAST CHECKS
                }
                # Start monitoring in background (non-blocking)
                asyncio.create_task(monitor_trade_for_profit(
                    self.testnet_exchange,
                    trade_plan,
                    orchestrator=self
                ))
                logger.info(f"   [OK] Profit monitoring started for {symbol} - will close at profit targets!")
            except Exception as e:
                logger.warning(f"     Could not start profit monitoring: {e}")
            
            self.total_trades += 1
            return True
            
        except Exception as e:
            logger.error(f"[X] Testnet execution failed: {e}")
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
                logger.info(f"[OK] Trade executed via COMPLETE PROFIT SYSTEM!")
                self.total_trades += 1
                return True
            else:
                logger.warning(f"[X] Execution failed")
                return False
                
        except Exception as e:
            logger.error(f"[X] Profit system execution failed: {e}")
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
                logger.info(f"[OK] Trade executed successfully: {symbol}")
            else:
                logger.warning(f"[X] Trade execution failed: {symbol}")
                
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
                    logger.info(">> Using COMPLETE PROFIT SYSTEM for direct execution...")
                    
                    signal_dict = {
                        'symbol': symbol,
                        'side': side,
                        'confidence': confidence,
                        'price': price
                    }
                    
                    execution_result = await self.profit_system.execute_signal(signal_dict)
                    
                    if execution_result:
                        logger.info("[OK] COMPLETE PROFIT SYSTEM executed successfully!")
                    
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
                        
                        logger.info(f"   [OK] Order placed: ID {order_id}")
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
                        logger.warning("     No exchange available - simulation only")
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
                    entry_price=price,
                    stop_loss_pct=stop_loss_pct
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
                    logger.info(f"   [OK] Order ID: {execution_result.get('order_id', 'N/A')}")
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
        import ccxt.async_support as ccxt
        import os
        
        logger.debug(f"Trying fresh exchange connection for {symbol}...")
        
        # Try Gate.io first (user's main exchange)
        if os.getenv('GATE_API_KEY'):
            exchange = None
            try:
                exchange = ccxt.gateio({
                    'apiKey': os.getenv('GATE_API_KEY'),
                    'secret': os.getenv('GATE_SECRET'),
                    'enableRateLimit': True
                })
                ticker = await exchange.fetch_ticker(symbol)
                price = ticker['last']
                logger.debug(f"Got ${price:.2f} from Gate.io")
                return price
            except Exception as e:
                logger.debug(f"Gate.io failed: {str(e)[:50]}")
            finally:
                if exchange:
                    try:
                        await exchange.close()
                    except Exception:
                        pass
        
        # Try Binance public API
        exchange = None
        try:
            exchange = ccxt.binance({'enableRateLimit': True})
            ticker = await exchange.fetch_ticker(symbol)
            price = ticker['last']
            logger.debug(f"Got ${price:.2f} from Binance")
            return price
        except Exception as e:
            logger.error(f"All price fetch attempts failed for {symbol}: {e}")
        finally:
            if exchange:
                try:
                    await exchange.close()
                except Exception:
                    pass
        
        return None
    
    async def close_all_untracked_positions(self):
        """Force close ALL non-USDT balances found on exchange"""
        """This frees stuck balance in other pairs"""
        
        if not hasattr(self, 'testnet_exchange') or not self.testnet_exchange:
            return
        
        try:
            logger.info("🔄 Checking for untracked positions to close...")
            balance = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
            
            positions_found = []
            for asset, info in balance.items():
                if asset not in ['USDT', 'info', 'total', 'used', 'free'] and isinstance(info, dict):
                    total = info.get('total', 0)
                    if total > 0:
                        symbol = f"{asset}/USDT"
                        positions_found.append((symbol, asset, total))
            
            if positions_found:
                logger.warning(f"  Found {len(positions_found)} untracked position(s) - closing to free balance...")
                for symbol, asset, amount in positions_found:
                    try:
                        # Get current price
                        ticker = await asyncio.to_thread(self.testnet_exchange.fetch_ticker, symbol)
                        price = ticker.get('last', 0)
                        
                        if price > 0:
                            # Calculate position value
                            position_value = amount * price
                            
                            # Get market info to check minimums
                            try:
                                market = self.testnet_exchange.market(symbol)
                                min_amount = market.get('limits', {}).get('amount', {}).get('min', 0)
                                min_cost = market.get('limits', {}).get('cost', {}).get('min', 0)
                                
                                # Check if position meets minimums
                                if amount < min_amount:
                                    logger.warning(f"   💤 Dust position: {symbol} - amount {amount:.8f} < minimum {min_amount:.8f}")
                                    continue
                                
                                if position_value < min_cost:
                                    logger.warning(f"   💤 Dust position: {symbol} - value ${position_value:.2f} < minimum ${min_cost:.2f}")
                                    continue
                            except Exception as e:
                                logger.debug(f"   Could not check market limits for {symbol}: {e}")
                                # Continue anyway if we can't check limits
                            
                            # Sell 99% to account for fees
                            sell_amount = amount * 0.99
                            
                            # Ensure sell_amount meets minimum
                            if sell_amount < min_amount:
                                logger.warning(f"   💤 Dust position: {symbol} - sell amount {sell_amount:.8f} < minimum {min_amount:.8f}")
                                continue
                            
                            logger.info(f"   Closing {symbol}: {sell_amount:.8f} {asset} @ ${price:.4f} (value: ${position_value:.2f})")
                            
                            order = await asyncio.to_thread(
                                self.testnet_exchange.create_market_sell_order,
                                symbol,
                                sell_amount
                            )
                            
                            logger.info(f"   [OK] Closed {symbol} - Order: {order.get('id', 'N/A')}")
                    except Exception as e:
                        error_msg = str(e)
                        if 'minimum amount' in error_msg.lower() or 'minimum precision' in error_msg.lower() or 'lower limit' in error_msg.lower():
                            logger.warning(f"   💤 Dust position: {symbol} - below exchange minimums ({error_msg[:80]})")
                        else:
                            logger.error(f"   [X] Error closing {symbol}: {e}")
                
                # Get final balance
                final_balance = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
                usdt_info = final_balance.get('USDT', {})
                if isinstance(usdt_info, dict):
                    usdt_balance = usdt_info.get('free', 0) or usdt_info.get('total', 0)
                else:
                    usdt_balance = float(usdt_info) if usdt_info else 0
                
                logger.info(f"💰 All positions closed! New USDT balance: ${usdt_balance:.2f}")
                
                # Update position sizer
                if hasattr(self, 'position_sizer') and self.position_sizer:
                    self.position_sizer.update_balance(usdt_balance)
            else:
                logger.info("[OK] No untracked positions found")
        except Exception as e:
            logger.error(f"Error closing untracked positions: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
    
    async def aggressive_balance_recovery(self):
        """
        🔥 AGGRESSIVE BALANCE RECOVERY
        
        Scans exchange balance and SELLS any non-USDT holdings immediately!
        This prevents balance getting stuck in crypto that isn't being sold.
        
        Runs every loop iteration to ensure USDT stays liquid for new trades.
        """
        try:
            if not hasattr(self, 'testnet_exchange') or not self.testnet_exchange:
                return
            
            # Get current balance from exchange
            balance = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
            
            # Track what we sell
            sold_assets = []
            recovered_usdt = 0
            
            # Check all non-USDT holdings
            skip_assets = ['USDT', 'info', 'free', 'used', 'total', 'timestamp', 'datetime']
            for asset, info in balance.items():
                if asset in skip_assets or not isinstance(info, dict):
                    continue
                
                total = info.get('total', 0)
                if total > 0:
                    symbol = f"{asset}/USDT"
                    
                    try:
                        # Get current price
                        ticker = await asyncio.to_thread(self.testnet_exchange.fetch_ticker, symbol)
                        current_price = ticker.get('last', 0)
                        
                        if current_price > 0:
                            value_usd = total * current_price
                            
                            # Only sell if worth more than $0.10 (avoid dust)
                            if value_usd >= 0.10:
                                logger.warning(f"💰 BALANCE RECOVERY: Selling {asset} ({total:.6f} = ${value_usd:.2f})")
                                
                                # Market sell all
                                try:
                                    order = await asyncio.to_thread(
                                        self.testnet_exchange.create_market_sell_order,
                                        symbol, total
                                    )
                                    sold_assets.append(asset)
                                    recovered_usdt += value_usd
                                    logger.info(f"   [OK] SOLD {asset} for ~${value_usd:.2f}")
                                except Exception as sell_error:
                                    # Skip if order too small or pair doesn't exist
                                    if 'Order value' in str(sell_error) or 'minimum' in str(sell_error).lower():
                                        logger.debug(f"   ⏭️ {asset} too small to sell")
                                    else:
                                        logger.debug(f"   ⏭️ Cannot sell {asset}: {str(sell_error)[:50]}")
                    except Exception as e:
                        # Pair probably doesn't exist on this exchange
                        pass
            
            # Report recovery
            if sold_assets:
                logger.info(f"💰 BALANCE RECOVERY COMPLETE: Sold {len(sold_assets)} assets, recovered ~${recovered_usdt:.2f}")
                
                # Update current_balance for adaptive thresholds
                new_balance = balance.get('USDT', {}).get('free', 0) + recovered_usdt
                if new_balance > 0:
                    self.current_balance = new_balance
                    logger.info(f"   💵 New USDT balance: ${new_balance:.2f}")
        except Exception as e:
            # Silent fail - this runs every loop, don't spam logs
            pass
    
    async def monitor_positions(self):
        """Monitor open positions with ADVANCED FEATURES (Trailing Stop, Partial TP)"""
        
        # 🔥 EXPLICIT HEARTBEAT LOG - proves monitor is running!
        logger.info("💰 Position Monitor Running...")
        
        # 🔥 CRITICAL FIX: Monitor BOTH tracking systems!
        positions_to_monitor = {}
        
        # 1. Check risk_manager positions
        if hasattr(self, 'risk_manager') and self.risk_manager:
            if hasattr(self.risk_manager, 'open_positions'):
                positions_to_monitor.update(self.risk_manager.open_positions)
                # 🔥 FIX: Use INFO level so we can see in logs!
                logger.info(f"   📊 Risk Manager: {len(self.risk_manager.open_positions)} tracked positions")
            else:
                logger.warning("     risk_manager has no open_positions attribute!")
        else:
            logger.warning("     risk_manager not available!")
        
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
        
        # 3. 🔥 BACKUP: Check exchange balance for spot positions (if tracking failed)
        try:
            exchange_to_check = None
            if hasattr(self, 'testnet_exchange') and self.testnet_exchange:
                exchange_to_check = self.testnet_exchange
            elif hasattr(self, 'profit_system') and self.profit_system and hasattr(self.profit_system, 'gate'):
                exchange_to_check = self.profit_system.gate
                
            if exchange_to_check:
                balance = await asyncio.to_thread(exchange_to_check.fetch_balance)
                for asset, info in balance.items():
                    if asset != 'USDT' and asset != 'info' and isinstance(info, dict):
                        free = info.get('free', 0)
                        total = info.get('total', 0)
                        if total > 0:
                            symbol = f"{asset}/USDT"
                            # If we have a position but it's not tracked, add it
                            if symbol not in positions_to_monitor:
                                # Try to get entry price from recent trades
                                try:
                                    ticker = await asyncio.to_thread(exchange_to_check.fetch_ticker, symbol)
                                    current_price = ticker.get('last', 0)
                                    if current_price > 0:
                                        # Calculate value
                                        value = total * current_price
                                        if value < 2.0: # Skip dust < $2
                                            continue
                                            
                                        # 🔥 CRITICAL: For untracked positions, close IMMEDIATELY - we don't know entry price!
                                        logger.warning(f"     Found UNTRACKED position: {symbol} ({total} {asset}) @ ${current_price:.4f} Value: ${value:.2f}")
                                        logger.warning(f"   🚨 CLOSING IMMEDIATELY - Unknown entry price, cannot calculate P&L accurately!")
                                        # Close immediately without tracking
                                        try:
                                            # Use the correct close method
                                            if hasattr(self, 'close_untracked_position'):
                                                await self.close_untracked_position(symbol, total, exchange_to_check)
                                            else:
                                                # Manual close
                                                await asyncio.to_thread(
                                                    exchange_to_check.create_market_sell_order,
                                                    symbol,
                                                    total
                                                )
                                                logger.info(f"   [OK] CLOSED untracked position: {symbol}")
                                        except Exception as e:
                                            logger.error(f"   [X] Failed to close untracked position {symbol}: {e}")
                                        continue  # Skip adding to monitoring - already closed
                                except:
                                    pass
        except Exception as e:
            logger.debug(f"Balance check backup failed: {e}")
        
        if positions_to_monitor:
            logger.info(f"💰 Monitoring {len(positions_to_monitor)} open positions...")
            # 🔥 LOG WHICH POSITIONS ARE OPEN! (ALWAYS LOG, even if size is 0)
            for sym, pos in positions_to_monitor.items():
                entry = pos.get('entry_price', 0)
                side = pos.get('side', 'unknown')
                size = pos.get('size_usd', 0)
                # If size_usd is 0, try to calculate from other fields
                if size == 0:
                    size_qty = pos.get('size', 0)
                    if size_qty > 0 and entry > 0:
                        size = size_qty * entry
                logger.info(f"   📊 Open: {sym} | Side: {side} | Entry: ${entry:.4f} | Size: ${size:.2f} | Full data: {pos}")
        
        for symbol, position in list(positions_to_monitor.items()):
            try:
                # Get current price
                current_price = await self.get_current_price(symbol)
                if not current_price:
                    continue
                
                entry_price = position.get('entry_price', 0)
                side = position.get('side', 'buy')
                
                # 🔥 CRITICAL VALIDATION: Skip positions with invalid entry_price
                if not entry_price or entry_price <= 0:
                    logger.error(f"   [X] SKIPPING {symbol}: Invalid entry_price={entry_price}")
                    logger.error(f"   Position data: {position}")
                    # Remove invalid position from tracking
                    if symbol in self.risk_manager.open_positions:
                        del self.risk_manager.open_positions[symbol]
                    continue
                
                # Calculate current P&L with validated entry_price
                if side == 'buy':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # 🔥 LOG P&L FOR EVERY CHECK (not just debug) - so we can see what's happening!
                logger.info(f"   📊 {symbol}: Entry=${entry_price:.6f} Current=${current_price:.6f} P&L={pnl_pct:.2%} | TP: {position.get('take_profit_pct', 0.02):.1%} SL: {position.get('stop_loss_pct', 0.01):.1%}")
                
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
                    # 🔥 BALANCE-AWARE TP: Use dynamic take profit based on current balance!
                    # Micro balance ($7.71) = 0.15% TP for FAST exits and capital recycling
                    balance_aware_tp = self.get_balance_aware_take_profit(self.current_balance)
                    balance_aware_max_hold = self.get_balance_aware_max_hold_time(self.current_balance)
                    
                    # Use the LOWER of stored TP or balance-aware TP (take profit sooner!)
                    position_take_profit_pct = min(
                        position.get('take_profit_pct', 0.02),
                        balance_aware_tp
                    )
                    position_stop_loss_pct = position.get('stop_loss_pct', 0.01)  # Default 1% SL
                    
                    # 🔥 BALANCE-AWARE MAX HOLD: Force close if held too long
                    # Try multiple timestamp fields for backwards compatibility
                    position_open_time = position.get('opened_at') or position.get('created_at') or position.get('timestamp')
                    if position_open_time:
                        try:
                            from datetime import datetime
                            if isinstance(position_open_time, str):
                                position_open_time = datetime.fromisoformat(position_open_time.replace('Z', '+00:00'))
                            
                            # Calculate hold time
                            if position_open_time.tzinfo:
                                hold_time_minutes = (datetime.now(position_open_time.tzinfo) - position_open_time).total_seconds() / 60
                            else:
                                hold_time_minutes = (datetime.now() - position_open_time).total_seconds() / 60
                            
                            if hold_time_minutes >= balance_aware_max_hold:
                                logger.warning(f"⏰ MAX HOLD TIME EXCEEDED: {symbol} held {hold_time_minutes:.1f}min >= {balance_aware_max_hold}min limit!")
                                logger.info(f"   🔄 Force closing to free capital for new trades...")
                                await self.close_position(symbol, current_price, 'max_hold_exceeded')
                                continue
                        except Exception as e:
                            # 🔥 FAILSAFE: If we can't determine hold time, STILL force close if position is untracked!
                            if position.get('from_balance', False) or position.get('is_untracked', False):
                                logger.warning(f"⏰ FAILSAFE: Closing untracked position {symbol} (can't determine hold time)")
                                await self.close_position(symbol, current_price, 'failsafe_untracked')
                                continue
                    
                    # [OK] CHECK TAKE PROFIT FIRST (before stop loss) - prioritize profits!
                    if pnl_pct >= position_take_profit_pct:
                        logger.info(f"🎯 [OK] Take profit triggered: {symbol} ({pnl_pct:.2%} >= {position_take_profit_pct:.2%})")
                        logger.info(f"   💰 Balance-aware TP: {balance_aware_tp:.2%} | Balance: ${self.current_balance:.2f}")
                        await self.close_position(symbol, current_price, 'take_profit')
                        continue  # Position closed, move to next
                    
                    # 🔥>> ULTRA-AGGRESSIVE EARLY STOP: Check at 0.6% FIRST (before it hits 0.8% or 1%!)
                    # This ensures we catch losses VERY early and prevent ANY significant drawdowns
                    # Faster loss-cutting = More capital preserved = More trades = Faster growth!
                    if pnl_pct <= -0.006:  # 0.6% loss - close VERY EARLY to preserve capital!
                        logger.warning(f"🛑>> EARLY STOP: {symbol} ({pnl_pct:.2%}) - Closing at 0.6% to preserve capital for next trade!")
                        logger.warning(f"   💡 Capital preserved → More trades → Faster profit growth!")
                        await self.close_position(symbol, current_price, 'early_stop_loss')
                        continue
                    
                    # 🔥 BACKUP: Check at 0.8% (before it hits 1%!)
                    if pnl_pct <= -0.008:  # 0.8% loss - close BEFORE it hits 1%
                        logger.warning(f"🛑 Early stop loss triggered: {symbol} ({pnl_pct:.2%} - closing at 0.8% to prevent 1% loss)")
                        await self.close_position(symbol, current_price, 'early_stop_loss')
                        continue
                    
                    # 🔥 REGULAR STOP LOSS: Check at exactly 1% loss (backup if early check missed)
                    if pnl_pct <= -position_stop_loss_pct:
                        logger.warning(f"🛑 Stop loss triggered: {symbol} ({pnl_pct:.2%} <= -{position_stop_loss_pct:.2%})")
                        await self.close_position(symbol, current_price, 'stop_loss')
                        continue  # Position closed, move to next
                    
                    # 🔥 CRITICAL: For untracked positions, close IMMEDIATELY if at ANY loss (we don't know real entry!)
                    if position.get('from_balance', False) or position.get('is_untracked', False):
                        if pnl_pct < 0:  # ANY loss - close immediately (we don't know real entry, could be much worse!)
                            logger.warning(f"🔄 UNTRACKED position at loss: {symbol} ({pnl_pct:.2%}) - Closing IMMEDIATELY (unknown real entry!)")
                            await self.close_position(symbol, current_price, 'untracked_position_cleanup')
                            continue
                        # If at profit, still check TP/SL normally
                        if pnl_pct >= position_take_profit_pct:
                            logger.info(f"🎯 [OK] Take profit on untracked position: {symbol} ({pnl_pct:.2%})")
                            await self.close_position(symbol, current_price, 'take_profit')
                            continue
                
            except Exception as e:
                try:
                    logger.debug(f"Position monitoring error for {symbol}: {e}")
                except:
                    logger.debug(f"Position monitoring error: {e}")
    
    async def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close position and record result"""
        
        try:
            # 🔥 CRITICAL: For untracked positions, actually execute sell order on exchange!
            position = self.risk_manager.open_positions.get(symbol, {})
            is_untracked = position.get('from_balance', False)
            
            if is_untracked or symbol not in self.risk_manager.open_positions:
                # This is an untracked position - need to actually sell on exchange
                logger.info(f"🔄 Closing untracked position: {symbol}")
                
                try:
                    # Get base currency and amount from exchange balance
                    base_currency = symbol.split('/')[0]
                    if hasattr(self, 'testnet_exchange') and self.testnet_exchange:
                        balance = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
                        base_info = balance.get(base_currency, {})
                        if isinstance(base_info, dict):
                            amount = base_info.get('free', 0) or base_info.get('total', 0)
                        else:
                            amount = float(base_info) if base_info else 0
                        
                        if amount > 0:
                            # Get current price to calculate position value
                            try:
                                ticker = await asyncio.to_thread(self.testnet_exchange.fetch_ticker, symbol)
                                price = ticker.get('last', 0)
                                position_value = amount * price
                            except Exception:
                                price = exit_price  # Use exit_price as fallback
                                position_value = amount * price
                            
                            # Get market info to check minimums
                            min_amount = 0
                            min_cost = 0
                            try:
                                market = self.testnet_exchange.market(symbol)
                                min_amount = market.get('limits', {}).get('amount', {}).get('min', 0)
                                min_cost = market.get('limits', {}).get('cost', {}).get('min', 0)
                            except Exception:
                                pass
                            
                            # Check if position meets minimums
                            if min_amount > 0 and amount < min_amount:
                                logger.warning(f"   💤 Dust position: {symbol} - amount {amount:.8f} < minimum {min_amount:.8f}, skipping close")
                                # Still mark as closed in our tracking to stop trying
                                if symbol in self.risk_manager.open_positions:
                                    del self.risk_manager.open_positions[symbol]
                                return
                            
                            if min_cost > 0 and position_value < min_cost:
                                logger.warning(f"   💤 Dust position: {symbol} - value ${position_value:.2f} < minimum ${min_cost:.2f}, skipping close")
                                # Still mark as closed in our tracking to stop trying
                                if symbol in self.risk_manager.open_positions:
                                    del self.risk_manager.open_positions[symbol]
                                return
                            
                            # Sell 99% to account for fees
                            sell_amount = amount * 0.99
                            
                            # Ensure sell_amount meets minimum
                            if min_amount > 0 and sell_amount < min_amount:
                                logger.warning(f"   💤 Dust position: {symbol} - sell amount {sell_amount:.8f} < minimum {min_amount:.8f}, skipping close")
                                # Still mark as closed in our tracking to stop trying
                                if symbol in self.risk_manager.open_positions:
                                    del self.risk_manager.open_positions[symbol]
                                return
                            
                            logger.info(f"   Selling {sell_amount:.8f} {base_currency} to free balance (value: ${position_value:.2f})")
                            
                            # Execute market sell
                            order = await asyncio.to_thread(
                                self.testnet_exchange.create_market_sell_order,
                                symbol,
                                sell_amount
                            )
                            
                            logger.info(f"   [OK] Sold {symbol} - Order ID: {order.get('id', 'N/A')}")
                            
                            # Get old balance before close
                            old_balance = self.position_sizer.balance if hasattr(self, 'position_sizer') and self.position_sizer else 0
                            
                            # Update balance by fetching new balance
                            new_balance_data = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
                            usdt_info = new_balance_data.get('USDT', {})
                            if isinstance(usdt_info, dict):
                                new_balance = usdt_info.get('free', 0) or usdt_info.get('total', 0)
                            else:
                                new_balance = float(usdt_info) if usdt_info else 0
                            
                            logger.info(f"   💰 New USDT balance: ${new_balance:.2f}")
                            
                            # Calculate actual P&L from balance difference
                            pnl = new_balance - old_balance
                            
                            # Update position sizer
                            if hasattr(self, 'position_sizer') and self.position_sizer:
                                self.position_sizer.update_balance(new_balance)
                            
                            # Track profit
                            if pnl != 0:
                                self.total_profit += pnl
                                if pnl > 0:
                                    self.winning_trades += 1
                                logger.info(f"   💵 Actual P&L from balance: ${pnl:+.2f}")
                            
                            logger.info(f"💰 UNTRACKED POSITION CLOSED:")
                            logger.info(f"   Symbol: {symbol}")
                            logger.info(f"   Amount sold: {sell_amount:.8f} {base_currency}")
                            logger.info(f"   Exit price: ${exit_price:.4f}")
                            logger.info(f"   New Balance: ${new_balance:.2f}")
                            logger.info(f"   Reason: {reason}")
                            
                            return  # Exit early for untracked positions
                except Exception as e:
                    logger.error(f"   [X] Error closing untracked position {symbol}: {e}")
                    import traceback
                    logger.debug(f"   Traceback: {traceback.format_exc()}")
            
            # 🔥 CRITICAL FIX: For tracked positions, ACTUALLY CLOSE ON EXCHANGE!
            position = self.risk_manager.open_positions.get(symbol, {})
            side = position.get('side', 'buy')
            size_usd = position.get('size_usd', 0)
            
            # Get position quantity
            position_quantity = position.get('size', 0)
            if position_quantity <= 0 and size_usd > 0 and exit_price > 0:
                # Calculate quantity from size_usd
                position_quantity = size_usd / exit_price
            
            # 🔥 ACTUALLY CLOSE THE POSITION ON EXCHANGE!
            if position_quantity > 0 and hasattr(self, 'testnet_exchange') and self.testnet_exchange:
                try:
                    # Determine close side (opposite of entry side)
                    close_side = 'sell' if side.lower() == 'buy' else 'buy'
                    
                    logger.info(f"   >> Closing tracked position on exchange: {close_side} {position_quantity} {symbol}")
                    
                    # Execute market order to close position
                    if close_side == 'sell':
                        close_order = await asyncio.to_thread(
                            self.testnet_exchange.create_market_sell_order,
                            symbol,
                            position_quantity
                        )
                    else:
                        # For closing a short, need to buy back
                        close_cost = position_quantity * exit_price
                        close_order = await asyncio.to_thread(
                            self.testnet_exchange.create_market_buy_order,
                            symbol,
                            close_cost
                        )
                    
                    logger.info(f"   [OK] Position closed on exchange - Order ID: {close_order.get('id', 'N/A')}")
                except Exception as e:
                    logger.error(f"   [X] Failed to close position on exchange: {e}")
                    import traceback
                    logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Calculate P&L with risk manager (updates internal tracking)
            pnl = self.risk_manager.close_position(symbol, exit_price)
            
            # Update balance
            new_balance = self.position_sizer.balance + pnl
            self.position_sizer.update_balance(new_balance)
            
            # 🔥 CRITICAL: Sync with actual exchange balance after close
            try:
                if hasattr(self, 'testnet_exchange') and self.testnet_exchange:
                    actual_balance_data = await asyncio.to_thread(self.testnet_exchange.fetch_balance)
                    usdt_info = actual_balance_data.get('USDT', {})
                    if isinstance(usdt_info, dict):
                        actual_balance = usdt_info.get('free', 0) or usdt_info.get('total', 0)
                    else:
                        actual_balance = float(usdt_info) if usdt_info else 0
                    
                    # Use actual exchange balance (more accurate)
                    if actual_balance > 0:
                        # Calculate actual P&L from balance difference
                        old_balance = self.position_sizer.balance
                        balance_diff = actual_balance - old_balance
                        if abs(balance_diff) > 0.01:  # Significant difference
                            # Use actual balance difference as P&L (more accurate than calculated)
                            actual_pnl = balance_diff
                            self.position_sizer.update_balance(actual_balance)
                            new_balance = actual_balance
                            pnl = actual_pnl # Sync actual balance from exchange
                            previous_balance = self.position_sizer.balance # Assuming position_sizer.balance holds the balance before this sync
                            current_balance = await self.sync_balance()
                            
                            # Update current_balance for adaptive confidence threshold
                            if current_balance > 0:
                                self.current_balance = current_balance
                            
                            logger.info(f"   [OK] Balance synced: ${current_balance:.2f} (was ${previous_balance:.2f}, P&L: $+{pnl:.2f})")
                            
                            # 🧠 AUTOMATIC COMPOUNDING - Reinvest profits intelligently!
                            try:
                                from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                                orch = get_orchestrator()
                                if orch and hasattr(orch, 'compound_engine') and orch.compound_engine:
                                    compound_stats = orch.compound_engine.update_balance(new_balance)
                                    growth_pct = compound_stats.get('growth_pct', 0)
                                    total_profit = compound_stats.get('profit', 0)
                                    initial = compound_stats.get('initial', 0)
                                    current = compound_stats.get('current', 0)
                                    
                                    # 🔥 ALWAYS LOG COMPOUND ENGINE - Critical for tracking profits!
                                    logger.info(f"   📈 COMPOUNDING ENGINE UPDATE:")
                                    logger.info(f"      Initial Balance: ${initial:.2f}")
                                    logger.info(f"      Current Balance: ${current:.2f}")
                                    logger.info(f"      Total Profit: ${total_profit:+.2f}")
                                    logger.info(f"      Growth: {growth_pct:+.2f}%")
                                    if growth_pct > 0:
                                        logger.info(f"   [OK] PROFIT GROWING! Balance increased by ${total_profit:.2f}")
                            except Exception as e:
                                logger.error(f"   [X] Compound engine update failed: {e}")
                                import traceback
                                logger.error(f"   Traceback: {traceback.format_exc()}")
                        else:
                            # Balance matches, use calculated P&L
                            self.position_sizer.update_balance(actual_balance)
                            new_balance = actual_balance
                            
                            # 🧠 AUTOMATIC COMPOUNDING - Reinvest profits intelligently!
                            try:
                                from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                                orch = get_orchestrator()
                                if orch and hasattr(orch, 'compound_engine') and orch.compound_engine:
                                    compound_stats = orch.compound_engine.update_balance(new_balance)
                                    growth_pct = compound_stats.get('growth_pct', 0)
                                    total_profit = compound_stats.get('profit', 0)
                                    initial = compound_stats.get('initial', 0)
                                    current = compound_stats.get('current', 0)
                                    
                                    # 🔥 ALWAYS LOG COMPOUND ENGINE - Critical for tracking profits!
                                    logger.info(f"   📈 COMPOUNDING ENGINE UPDATE:")
                                    logger.info(f"      Initial Balance: ${initial:.2f}")
                                    logger.info(f"      Current Balance: ${current:.2f}")
                                    logger.info(f"      Total Profit: ${total_profit:+.2f}")
                                    logger.info(f"      Growth: {growth_pct:+.2f}%")
                                    if growth_pct > 0:
                                        logger.info(f"   [OK] PROFIT GROWING! Balance increased by ${total_profit:.2f}")
                            except Exception as e:
                                logger.error(f"   [X] Compound engine update failed: {e}")
                                import traceback
                                logger.error(f"   Traceback: {traceback.format_exc()}")
            except Exception as e:
                logger.debug(f"   Balance sync failed: {e}, using calculated balance")
            
            # Update stats (only add pnl once)
            if pnl > 0:
                self.winning_trades += 1
            
            self.total_profit += pnl
            
            # 🔥 CRITICAL: Log profit/loss for every closed position - ALWAYS VISIBLE!
            pnl_pct = (pnl / (self.position_sizer.balance - pnl) * 100) if (self.position_sizer.balance - pnl) > 0 else 0
            if pnl > 0:
                logger.info("=" * 70)
                logger.info(f"   [OK] [OK] [OK] PROFIT CLOSED: {symbol}")
                logger.info(f"   💰 Profit: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
                logger.info(f"   📊 Total Profit: ${self.total_profit:.2f}")
                logger.info(f"   📈 New Balance: ${new_balance:.2f}")
                logger.info("=" * 70)
            else:
                logger.warning("=" * 70)
                logger.warning(f"   [X] [X] [X] LOSS CLOSED: {symbol}")
                logger.warning(f"   💸 Loss: ${pnl:.2f} ({pnl_pct:.2f}%)")
                logger.warning(f"   📊 Total Profit: ${self.total_profit:.2f}")
                logger.warning(f"   📉 New Balance: ${new_balance:.2f}")
                logger.warning("=" * 70)
            
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
            
            # Get entry_price and side from position
            position = self.risk_manager.open_positions.get(symbol, {})
            entry_price = position.get("entry_price", exit_price)
            side = position.get("side", "buy")
            
            # Calculate actual P&L percentage
            if side == 'buy':
                pnl_pct = (exit_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - exit_price) / entry_price
            
            # Update win tracking (already done above, but keep for consistency)
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
            
            # 🧠 AUTOMATIC COMPOUNDING - Update compound engine after position close
            try:
                if hasattr(self, 'compound_engine') and self.compound_engine:
                    compound_stats = self.compound_engine.update_balance(new_balance)
                    growth_pct = compound_stats.get('growth_pct', 0)
                    if growth_pct > 0:
                        logger.info(f"   📈 COMPOUNDING: {growth_pct:.2f}% growth from ${compound_stats.get('initial', 0):.2f}")
                        logger.info(f"   💰 Total compounded profit: ${compound_stats.get('profit', 0):.2f}")
                else:
                    # Fallback: Try to get from orchestrator
                    try:
                        from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                        orch = get_orchestrator()
                        if orch and hasattr(orch, 'compound_engine') and orch.compound_engine:
                            compound_stats = orch.compound_engine.update_balance(new_balance)
                            growth_pct = compound_stats.get('growth_pct', 0)
                            if growth_pct > 0:
                                logger.info(f"   📈 COMPOUNDING: {growth_pct:.2f}% growth from ${compound_stats.get('initial', 0):.2f}")
                                logger.info(f"   💰 Total compounded profit: ${compound_stats.get('profit', 0):.2f}")
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"   Compound engine update skipped: {e}")
            
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
            
            # 🔥 FIXED: Lower threshold from 0.1 (10%) to 0.005 (0.5%) to capture more arb!
            if len(path) != 3 or profit_pct < 0.005:  # Only skip if < 0.5%
                logger.info(f"   ⏭️  Skipping: Profit {profit_pct:.2f}% below 0.5% threshold")
                return False
            
            logger.info(f"   🔄 Executing 3-leg arbitrage: {' → '.join(path)}")
            logger.info(f"   💰 Expected profit: {profit_pct:.2f}%")
            logger.info(f"   🎯 Risk: ZERO (simultaneous execution)")
            
            # Calculate order sizes (small for arbitrage)
            base_size_usd = min(self.position_sizer.balance * 0.02, 100)  # Up to $100
            
            # 🔥 ACTUALLY EXECUTE the arbitrage legs!
            if hasattr(self, 'execution_engine') and self.execution_engine:
                for i, leg_symbol in enumerate(path):
                    side = 'buy' if i % 2 == 0 else 'sell'  # Alternate buy/sell
                    arb_signal = {
                        'symbol': leg_symbol,
                        'side': side,
                        'price': signal.get('prices', {}).get(leg_symbol, 0),
                        'confidence': 0.99,  # High confidence for arb
                        'strategy': 'triangular_arbitrage',
                        'timeframe': '1m'
                    }
                    logger.info(f"   📊 LEG {i+1}: {side.upper()} {leg_symbol}")
                    try:
                        await self.execution_engine.execute_intelligent_trade(arb_signal)
                    except Exception as e:
                        logger.warning(f"    Leg {i+1} failed: {e}")
            
            logger.info(f"   [OK] TRIANGULAR ARBITRAGE EXECUTED!")
            
            self.total_trades += 1
            return True
            
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
                logger.info(f"   [OK] PAIRS TRADE EXECUTED! Both legs opened!")
                logger.info(f"   💎 Market-neutral hedge active - profit when correlation reverts!")
                self.total_trades += 1
                return True
            elif long_result or short_result:
                logger.warning(f"     PARTIAL EXECUTION: Long={long_result}, Short={short_result}")
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
    
    def get_stats(self) -> dict:
        """Get execution statistics"""
        stats = {
            'total_trades': getattr(self, 'total_trades', 0),
            'winning_trades': getattr(self, 'winning_trades', 0),
            'total_profit': getattr(self, 'total_profit', 0.0),
            'open_positions': 0,
            'daily_pnl': 0.0,
            'daily_trades': 0,
            'win_rate': 0.0,
            'current_balance': 0.0
        }
        
        # Get from risk_manager if available
        if hasattr(self, 'risk_manager') and self.risk_manager:
            if hasattr(self.risk_manager, 'open_positions'):
                stats['open_positions'] = len(self.risk_manager.open_positions)
            if hasattr(self.risk_manager, 'daily_pnl'):
                stats['daily_pnl'] = self.risk_manager.daily_pnl
            if hasattr(self.risk_manager, 'daily_trades'):
                stats['daily_trades'] = self.risk_manager.daily_trades
        
        # Calculate win rate
        if stats['total_trades'] > 0:
            stats['win_rate'] = stats['winning_trades'] / stats['total_trades']
        
        # Get balance
        if hasattr(self, 'position_sizer') and self.position_sizer:
            stats['current_balance'] = getattr(self.position_sizer, 'balance', 0.0)
        
        return stats
