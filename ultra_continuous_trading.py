from dataclasses import dataclass
"""
Ultra Continuous Trading Orchestrator - 24/7 Trading System
Designed for rapid $48 → $3000-5000 growth by November

Features:
- 24/7 continuous trading across all timeframes
- Simultaneous position management
- Rapid profit taking and reinvestment
- Micro-account optimization
- Compound growth acceleration
- Multi-strategy coordination
"""
from typing import Dict, List, Optional, Any

import asyncio
import time
import logging
import numpy as np

# Core imports
from ultra_core import UltraCore
from risk_engine import RiskEngine
from ultra_scalping_engine import UltraScalpingEngine
from ultra_arbitrage_engine import UltraArbitrageEngine

@dataclass
class TradingSession:
    """Trading session data structure"""

    session_id: str
    start_time: float
    end_time: float
    strategy: str
    timeframe: str
    symbol: str
    initial_balance: float
    final_balance: float
    profit: float
    trades_count: int
    win_rate: float
    status: str
    entry_price: float = 0.0
    qty: float = 0.0

@dataclass
class ContinuousTradingConfig:
    """Continuous trading configuration"""

    # Timeframe configuration
    timeframes: List[str] = None
    timeframe_weights: Dict[str, float] = None

    # Strategy configuration
    strategies: List[str] = None
    strategy_weights: Dict[str, float] = None

    # Risk configuration
    max_positions_per_timeframe: int = 3
    max_total_positions: int = 15
    daily_loss_limit: float = 100.0
    daily_profit_target: float = 500.0

    # Execution configuration
    execution_delay: float = 0.1
    position_timeout: float = 300.0
    profit_taking_threshold: float = 0.02

    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']

        if self.timeframe_weights is None:
            self.timeframe_weights = {
                'M1': 0.25,  # 25% - Scalping
                'M5': 0.20,  # 20% - Short-term
                'M15': 0.15,  # 15% - Intraday
                'M30': 0.15,  # 15% - Session
                'H1': 0.10,  # 10% - Daily bias
                'H4': 0.10,  # 10% - Swing
                'D1': 0.05,  # 5% - Long-term
            }

        if self.strategies is None:
            self.strategies = [
                'scalping',
                'arbitrage',
                'momentum',
                'mean_reversion',
                'breakout',
                'trend_following',
                'news_trading',
            ]

        if self.strategy_weights is None:
            self.strategy_weights = {
                'scalping': 0.30,  # 30% - High frequency
                'arbitrage': 0.25,  # 25% - Risk-free
                'momentum': 0.15,  # 15% - Trend following
                'mean_reversion': 0.10,  # 10% - Counter-trend
                'breakout': 0.10,  # 10% - Breakout trading
                'trend_following': 0.05,  # 5% - Long-term trends
                'news_trading': 0.05,  # 5% - News events
            }

class UltraContinuousTradingOrchestrator:
    """
    Ultra Continuous Trading Orchestrator for 24/7 trading

    Designed to generate consistent profits through:
    - 24/7 continuous trading across all timeframes
    - Simultaneous position management
    - Rapid profit taking and reinvestment
    - Micro-account optimization
    - Compound growth acceleration
    """

    def __init__(
        self,
        ultra_core: UltraCore,
        risk_engine: RiskEngine,
        config: Optional[ContinuousTradingConfig] = None,
    ):
        self.ultra_core = ultra_core
        self.risk_engine = risk_engine
        self.config = config or ContinuousTradingConfig()

        # Initialize trading engines
        self.scalping_engine = UltraScalpingEngine(ultra_core, risk_engine)
        self.arbitrage_engine = UltraArbitrageEngine(ultra_core, risk_engine)

        # Trading state
        self.active_sessions: Dict[str, TradingSession] = {}
        self.completed_sessions: List[TradingSession] = []
        self.daily_balance = 48.0  # Starting with $48
        # Live balance (fallback to 48.0)
        try:
            import ccxt
            _ex = ccxt.bybit({'enableRateLimit': True})
            _ex.set_sandbox_mode(True)
            _bal = _ex.fetch_balance()
            self.total_balance = float(_bal.get('total', {}).get('USDT', 48.0) or 48.0)
        except Exception:
            self.total_balance = 48.0
        self.daily_profit = 0.0
        self.total_profit = 0.0

        # Performance tracking
        self.daily_trades = 0
        self.total_trades = 0
        self.daily_wins = 0
        self.total_wins = 0
        self.win_rate = 0.0
        self.avg_profit_per_trade = 0.0

        # Compound growth tracking
        self.compound_growth_rate = 0.0
        self.daily_growth_rate = 0.0
        self.target_balance = 3000.0  # November target

        self.executor = None  # injected by hosting service: real execution
        self.logger = logging.getLogger(__name__)

    async def start_continuous_trading(self) -> None:
        """Start 24/7 continuous trading system"""
        self.logger.info("🚀 Starting Ultra Continuous Trading Orchestrator...")
        self.logger.info(f"💰 Starting Balance: ${self.daily_balance:.2f}")
        self.logger.info(f"🎯 November Target: ${self.target_balance:.2f}")

        # Start all trading engines
        tasks = []

        # Start scalping engine
        tasks.append(asyncio.create_task(self.scalping_engine.start_scalping()))

        # Start arbitrage engine
        tasks.append(asyncio.create_task(self.arbitrage_engine.start_arbitrage_scanning()))

        # Start continuous trading tasks
        tasks.append(asyncio.create_task(self._continuous_trading_loop()))
        tasks.append(asyncio.create_task(self._monitor_all_positions()))
        tasks.append(asyncio.create_task(self._manage_compound_growth()))
        tasks.append(asyncio.create_task(self._track_performance()))
        tasks.append(asyncio.create_task(self._daily_reset()))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    async def _continuous_trading_loop(self) -> None:
        """Main continuous trading loop"""
        while True:
            try:
                # Check if we can trade
                if not await self._can_trade():
                    await asyncio.sleep(10)
                    continue

                # Get trading opportunities across all timeframes
                opportunities = await self._scan_all_opportunities()
                self.logger.info(
                    f'CONT SCAN: {len(opportunities)} opportunities '
                    f'(balance ${self.daily_balance:.2f}, '
                    f'active {len(self.active_sessions)})')

                # Execute opportunities based on priority
                for opportunity in opportunities:
                    if await self._can_open_position():
                        await self._execute_opportunity(opportunity)

                # Wait before next scan
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in continuous trading loop: {e}")
                await asyncio.sleep(5)

    async def _scan_all_opportunities(self) -> List[Dict[str, Any]]:
        """Scan for trading opportunities across all timeframes and strategies"""
        opportunities = []

        try:
            # Get opportunities from each timeframe
            for timeframe in self.config.timeframes:
                weight = self.config.timeframe_weights.get(timeframe, 0.1)

                # Get opportunities for this timeframe
                tf_opportunities = await self._scan_timeframe_opportunities(timeframe, weight)
                opportunities.extend(tf_opportunities)

        except Exception as e:
            self.logger.error(f"Error scanning all opportunities: {e}")

        return opportunities

    async def _scan_timeframe_opportunities(
        self, timeframe: str, weight: float
    ) -> List[Dict[str, Any]]:
        """Scan for opportunities in specific timeframe"""
        opportunities = []

        try:
            # Get symbols for this timeframe
            symbols = await self._get_symbols_for_timeframe(timeframe)

            for symbol in symbols:
                # Get market data
                market_data = await self.ultra_core.get_market_data(symbol, timeframe)

                if not market_data:
                    continue

                # Analyze for opportunities
                symbol_opportunities = await self._analyze_symbol_opportunities(
                    symbol, timeframe, market_data, weight
                )

                opportunities.extend(symbol_opportunities)

        except Exception as e:
            self.logger.error(f"Error scanning timeframe opportunities: {e}")

        return opportunities

    async def _get_symbols_for_timeframe(self, timeframe: str) -> List[str]:
        """Symbols from the fleet's REAL scored universe (2026-10-20
        fix #2: discover_symbols ranks by volume metadata that is 0
        for most markets here, so its reverse sort degenerated into
        reverse-ALPHABETICAL - the grower was scanning Z-tokens that
        are not even listed on testnet, and the executor silently
        refused every one). Primary source: discovery_service's
        scored pairs (live exchange list, testnet-aware); secondary:
        the scanner's trending fast movers; majors as last resort."""
        import time as _t
        cache = getattr(self, '_sym_cache', None)
        if cache and _t.time() - cache[0] < 600:
            return cache[1]
        top = 8 if timeframe in ('M1', 'M5') else (
            10 if timeframe in ('M15', 'M30') else 12)
        def _extract(data):
            out = []
            items = data.get('pairs', data) if isinstance(data, dict) else data
            for x in items or []:
                if isinstance(x, dict) and x.get('symbol'):
                    out.append(x['symbol'])
                elif isinstance(x, str):
                    # discovery stores perp form 'ABC/USDT:USDT'
                    v = x.replace(':USDT', '')
                    out.append(v if '/' in v else v + '/USDT')
            return out
        syms = []
        try:
            import json as _j
            with open('/tmp/discovered_pairs.json') as f:
                syms = _extract(_j.load(f))
        except Exception:
            syms = []
        if len(syms) < 4:
            try:
                import json as _j
                with open('/tmp/trending_pairs.json') as f:
                    syms = _extract(_j.load(f))
            except Exception:
                pass
        if not syms:
            syms = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT',
                    'SOL/USDT']
        syms = syms[:top]
        # Venue truth (2026-10-21, the sniper's #143 pattern): the
        # scored universe carries names not listed on testnet at all
        # (WLD) - the grower wedged for hours retrying a dead contract
        # (110074) plus a zero-position close (110017) at ~1Hz, 4.7M
        # log lines, zero production. Intersect with the on-disk
        # testnet instrument table before scanning.
        try:
            import json as _jv
            with open('/app/runtime/venue_instruments.json') as _vf:
                _venue = _jv.load(_vf)
            _kept = [x for x in syms
                     if x.replace('/USDT', 'USDT').replace('/', '') in _venue]
            if _kept:
                syms = _kept
        except Exception:
            pass
        self._sym_cache = (_t.time(), syms)
        self.logger.info(f'CONT UNIVERSE ({timeframe}): {syms}')
        return syms
    async def _analyze_symbol_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Analyze symbol for trading opportunities"""
        opportunities = []

        try:
            # Get opportunities from each strategy
            for strategy in self.config.strategies:
                strategy_weight = self.config.strategy_weights.get(strategy, 0.1)
                combined_weight = weight * strategy_weight

                # Analyze strategy-specific opportunities
                strategy_opportunities = await self._analyze_strategy_opportunities(
                    symbol, timeframe, market_data, strategy, combined_weight
                )

                opportunities.extend(strategy_opportunities)

        except Exception as e:
            self.logger.error(f"Error analyzing symbol opportunities: {e}")

        return opportunities

    async def _analyze_strategy_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], strategy: str, weight: float
    ) -> List[Dict[str, Any]]:
        """Analyze strategy-specific opportunities"""
        opportunities = []

        try:
            if strategy == 'scalping':
                # Scalping opportunities
                scalp_opportunities = await self._detect_scalping_opportunities(
                    symbol, timeframe, market_data, weight
                )
                opportunities.extend(scalp_opportunities)

            elif strategy == 'arbitrage':
                # Arbitrage opportunities
                arb_opportunities = await self._detect_arbitrage_opportunities(
                    symbol, timeframe, market_data, weight
                )
                opportunities.extend(arb_opportunities)

            elif strategy == 'momentum':
                # Momentum opportunities
                momentum_opportunities = await self._detect_momentum_opportunities(
                    symbol, timeframe, market_data, weight
                )
                opportunities.extend(momentum_opportunities)

            elif strategy == 'mean_reversion':
                # Mean reversion opportunities
                mr_opportunities = await self._detect_mean_reversion_opportunities(
                    symbol, timeframe, market_data, weight
                )
                opportunities.extend(mr_opportunities)

            elif strategy == 'breakout':
                # Breakout opportunities
                breakout_opportunities = await self._detect_breakout_opportunities(
                    symbol, timeframe, market_data, weight
                )
                opportunities.extend(breakout_opportunities)

        except Exception as e:
            self.logger.error(f"Error analyzing strategy opportunities: {e}")

        return opportunities

    async def _detect_scalping_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Detect scalping opportunities"""
        opportunities = []

        try:
            # Only for M1 and M5 timeframes
            if timeframe not in ['M1', 'M5']:
                return opportunities

            current_price = market_data.get('close', 0)
            if current_price <= 0:
                return opportunities

            # Check for micro-momentum
            prices = market_data.get('prices', [])
            if len(prices) >= 5:
                recent_prices = prices[-5:]
                momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

                if abs(momentum) > 0.0001:  # 0.01% minimum momentum
                    confidence = min(0.95, abs(momentum) * 1000)

                    if confidence >= 0.75:
                        opportunities.append(
                            {
                                'symbol': symbol,
                                'timeframe': timeframe,
                                'strategy': 'scalping',
                                'entry_price': current_price,
                                'confidence': confidence,
                                'weight': weight,
                                'profit_target': 0.5,  # 0.5 pip target
                                'stop_loss': 1.0,  # 1 pip stop
                                'timestamp': time.time(),
                            }
                        )

        except Exception as e:
            self.logger.error(f"Error detecting scalping opportunities: {e}")

        return opportunities

    async def _detect_arbitrage_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Detect arbitrage opportunities"""
        opportunities = []

        try:
            # Check for cross-exchange arbitrage
            # This would integrate with the arbitrage engine
            # For now, return empty list
            pass

        except Exception as e:
            self.logger.error(f"Error detecting arbitrage opportunities: {e}")

        return opportunities

    async def _detect_momentum_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Detect momentum opportunities"""
        opportunities = []

        try:
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return opportunities

            # Calculate momentum indicators
            recent_prices = prices[-20:]
            sma_short = np.mean(recent_prices[-5:])
            sma_long = np.mean(recent_prices[-20:])

            momentum = (sma_short - sma_long) / sma_long

            if abs(momentum) > 0.005:  # 0.5% minimum momentum
                confidence = min(0.90, abs(momentum) * 100)

                if confidence >= 0.70:
                    opportunities.append(
                        {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'strategy': 'momentum',
                            'entry_price': recent_prices[-1],
                            'confidence': confidence,
                            'weight': weight,
                            'profit_target': 2.0,  # 2 pip target
                            'stop_loss': 1.5,  # 1.5 pip stop
                            'timestamp': time.time(),
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error detecting momentum opportunities: {e}")

        return opportunities

    async def _detect_mean_reversion_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Detect mean reversion opportunities"""
        opportunities = []

        try:
            prices = market_data.get('prices', [])
            if len(prices) < 50:
                return opportunities

            # Calculate mean reversion indicators
            recent_prices = prices[-50:]
            sma = np.mean(recent_prices)
            current_price = recent_prices[-1]

            deviation = (current_price - sma) / sma

            # Look for overbought/oversold conditions
            if abs(deviation) > 0.02:  # 2% deviation from mean
                confidence = min(0.85, abs(deviation) * 20)

                if confidence >= 0.65:
                    opportunities.append(
                        {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'strategy': 'mean_reversion',
                            'entry_price': current_price,
                            'confidence': confidence,
                            'weight': weight,
                            'profit_target': 1.5,  # 1.5 pip target
                            'stop_loss': 2.0,  # 2 pip stop
                            'timestamp': time.time(),
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error detecting mean reversion opportunities: {e}")

        return opportunities

    async def _detect_breakout_opportunities(
        self, symbol: str, timeframe: str, market_data: Dict[str, Any], weight: float
    ) -> List[Dict[str, Any]]:
        """Detect breakout opportunities"""
        opportunities = []

        try:
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return opportunities

            # Calculate breakout indicators
            recent_prices = prices[-20:]
            high = max(recent_prices)
            # low = min(recent_prices)  # Unused variable
            current_price = recent_prices[-1]

            # Check for breakout above resistance or below support
            if current_price > high * 0.999:  # Near high
                confidence = min(0.80, (current_price - high) / high * 1000)

                if confidence >= 0.60:
                    opportunities.append(
                        {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'strategy': 'breakout',
                            'entry_price': current_price,
                            'confidence': confidence,
                            'weight': weight,
                            'profit_target': 3.0,  # 3 pip target
                            'stop_loss': 2.0,  # 2 pip stop
                            'timestamp': time.time(),
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error detecting breakout opportunities: {e}")

        return opportunities

    async def _can_trade(self) -> bool:
        """Check if we can trade"""
        try:
            # Check daily loss limit
            if self.daily_profit < -self.config.daily_loss_limit:
                return False

            # Check if we have enough balance
            if self.daily_balance < 5.0:  # Minimum $5 balance
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if can trade: {e}")
            return False

    async def _can_open_position(self) -> bool:
        """Check if we can open a new position"""
        try:
            # Check total position limit
            if len(self.active_sessions) >= self.config.max_total_positions:
                return False

            # Check if we have enough balance
            if self.daily_balance < 5.0:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if can open position: {e}")
            return False

    def _persist_sessions(self):
        """Persist REAL active sessions (session persistence,
        2026-10-20): a service restart used to orphan the grower's
        open positions - exchange-safe but exit-blind (the monitor
        only watches current-run sessions). Sessions now survive
        restarts: written on every open/close, rehydrated and
        exchange-verified by the service at boot."""
        try:
            import json as _j
            import os as _o
            data = {}
            for sid, ssn in self.active_sessions.items():
                if getattr(ssn, 'entry_price', 0) and ssn.entry_price > 0:
                    data[sid] = {
                        'session_id': ssn.session_id,
                        'start_time': ssn.start_time,
                        'strategy': ssn.strategy,
                        'timeframe': ssn.timeframe,
                        'symbol': ssn.symbol,
                        'initial_balance': ssn.initial_balance,
                        'entry_price': ssn.entry_price,
                        'qty': ssn.qty}
            path = '/app/runtime/continuous_sessions.json'
            tmp = path + '.tmp'
            with open(tmp, 'w') as f:
                _j.dump(data, f)
            _o.replace(tmp, path)
        except Exception:
            pass

    async def _execute_opportunity(self, opportunity: Dict[str, Any]) -> None:
        """Execute trading opportunity"""
        try:
            # Create trading session
            session_id = f"{opportunity['symbol']}_{opportunity['timeframe']}_{int(opportunity['timestamp'])}"

            session = TradingSession(
                session_id=session_id,
                start_time=time.time(),
                end_time=0,
                strategy=opportunity['strategy'],
                timeframe=opportunity['timeframe'],
                symbol=opportunity['symbol'],
                initial_balance=self.daily_balance,
                final_balance=0,
                profit=0,
                trades_count=0,
                win_rate=0,
                status='active',
            )

            # Store active session
            self.active_sessions[session_id] = session

            # Real execution hook: an injected executor turns the session
            # into a real position and fills entry_price/qty on it.
            if getattr(self, 'executor', None) is not None:
                try:
                    _ok = await self.executor.open_position(session, opportunity)
                except Exception as _e:
                    self.logger.error(f"executor open failed: {_e}")
                    _ok = False
                if not _ok:
                    del self.active_sessions[session_id]
                    return

            self._persist_sessions()
            self.logger.info(
                f"🎯 Opened Position: {opportunity['symbol']} "
                f"{opportunity['timeframe']} {opportunity['strategy']} "
                f"@ {opportunity['entry_price']:.6f} "
                f"(confidence: {opportunity['confidence']:.2f})"
            )

        except Exception as e:
            self.logger.error(f"Error executing opportunity: {e}")

    async def _monitor_all_positions(self) -> None:
        """Monitor all active positions"""
        while True:
            try:
                # current_time = time.time()  # Unused variable

                for session_id, session in list(self.active_sessions.items()):
                    # Check if position should be closed
                    if await self._should_close_position(session):
                        await self._close_position(session_id, session)

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Error monitoring positions: {e}")
                await asyncio.sleep(5)

    async def _should_close_position(self, session: TradingSession) -> bool:
        """Check if position should be closed (real P&L when an executor is attached)"""
        try:
            if time.time() - session.start_time > self.config.position_timeout:
                return True
            if getattr(self, 'executor', None) is not None and session.entry_price > 0:
                try:
                    md = await self.ultra_core.get_market_data(session.symbol)
                    cur = (md or {}).get('close') or 0
                    if cur:
                        pct = (cur - session.entry_price) / session.entry_price
                        if pct >= self.config.profit_taking_threshold or pct <= -0.015:
                            return True
                except Exception:
                    pass
                return False
            if time.time() - session.start_time > 60:
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking if should close position: {e}")
            return True

    async def _close_position(self, session_id: str, session: TradingSession) -> None:
        """Close trading position"""
        try:
            # Real exit: the executor places the closing order and returns
            # the exit price; P&L is computed from actual entry/exit.
            if getattr(self, 'executor', None) is not None and session.entry_price > 0 and session.qty > 0:
                _exit = await self.executor.close_position(session)
                profit = (_exit - session.entry_price) * session.qty
            else:
                # No real fill prices this close (executor absent or
                # the session never filled): book ZERO, loudly. This
                # branch used to draw random.uniform profit into the
                # balances feeding growth sizing - a fabrication on
                # a money path (external audit MP-02, cross-checked
                # 2026-10-20). Zero is the only honest number here.
                self.logger.error(
                    f'CONT CLOSE UNPRICED {session.symbol}: no executor '
                    f'fill - booking 0.0 (never fabricated)')
                profit = 0.0

            # Update session
            session.end_time = time.time()
            session.final_balance = session.initial_balance + profit
            session.profit = profit
            session.trades_count = 1
            session.win_rate = 1.0 if profit > 0 else 0.0
            session.status = 'completed'

            # Update balances
            self.daily_balance += profit
            self.total_balance += profit
            self.daily_profit += profit
            self.total_profit += profit

            # Update trade counts
            self.daily_trades += 1
            self.total_trades += 1
            if profit > 0:
                self.daily_wins += 1
                self.total_wins += 1

            # Move to completed sessions
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            self._persist_sessions()

            # Capacity ledger: real closes only (executor-attached)
            if getattr(self, 'executor', None) is not None and session.entry_price > 0 and session.qty > 0:
                try:
                    import being_ledger as _ledger
                    _ledger.record_close('continuous', session.symbol, profit, real=True)
                except Exception:
                    pass

            # Log result
            status = "✅ WIN" if profit > 0 else "❌ LOSS"
            self.logger.info(
                f"{status} Position: {session.symbol} {session.timeframe} "
                f"Profit: ${profit:.4f} Balance: ${self.daily_balance:.2f}"
            )

        except Exception as e:
            self.logger.error(f"Error closing position: {e}")

    async def _manage_compound_growth(self) -> None:
        """Manage compound growth acceleration"""
        while True:
            try:
                # Calculate growth rates
                if self.total_balance > 48.0:
                    self.compound_growth_rate = (self.total_balance / 48.0 - 1) * 100

                # Calculate daily growth rate
                if len(self.completed_sessions) > 0:
                    recent_sessions = [
                        s for s in self.completed_sessions if time.time() - s.end_time < 86400
                    ]
                    if recent_sessions:
                        daily_profit = sum(s.profit for s in recent_sessions)
                        self.daily_growth_rate = (daily_profit / self.daily_balance) * 100

                # Check if we've reached target
                if self.total_balance >= self.target_balance:
                    self.logger.info(f"🎉 TARGET REACHED! Balance: ${self.total_balance:.2f}")

                # Log growth status
                self.logger.info(
                    f"📈 Growth Status: "
                    f"Balance: ${self.total_balance:.2f} "
                    f"Compound: {self.compound_growth_rate:.1f}% "
                    f"Daily: {self.daily_growth_rate:.1f}% "
                    f"Target: ${self.target_balance:.2f}"
                )

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error managing compound growth: {e}")
                await asyncio.sleep(300)

    async def _track_performance(self) -> None:
        """Track overall performance"""
        while True:
            try:
                # Calculate win rate
                if self.total_trades > 0:
                    self.win_rate = self.total_wins / self.total_trades

                # Calculate average profit per trade
                if self.total_trades > 0:
                    self.avg_profit_per_trade = self.total_profit / self.total_trades

                # Log performance
                self.logger.info(
                    f"📊 Performance: "
                    f"Active: {len(self.active_sessions)}, "
                    f"Trades: {self.total_trades}, "
                    f"Win Rate: {self.win_rate:.1%}, "
                    f"Avg Profit: ${self.avg_profit_per_trade:.4f}, "
                    f"Balance: ${self.total_balance:.2f}"
                )

                await asyncio.sleep(60)  # Log every minute

            except Exception as e:
                self.logger.error(f"Error tracking performance: {e}")
                await asyncio.sleep(60)

    async def _daily_reset(self) -> None:
        """Daily reset and optimization"""
        while True:
            try:
                # Wait until next day
                await asyncio.sleep(86400)  # 24 hours

                # Reset daily metrics
                self.daily_balance = self.total_balance
                self.daily_profit = 0.0
                self.daily_trades = 0
                self.daily_wins = 0

                # Log daily reset
                self.logger.info(f"🔄 Daily Reset: New Balance: ${self.daily_balance:.2f}")

            except Exception as e:
                self.logger.error(f"Error in daily reset: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'total_balance': self.total_balance,
            'daily_balance': self.daily_balance,
            'total_profit': self.total_profit,
            'daily_profit': self.daily_profit,
            'total_trades': self.total_trades,
            'daily_trades': self.daily_trades,
            'win_rate': self.win_rate,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'compound_growth_rate': self.compound_growth_rate,
            'daily_growth_rate': self.daily_growth_rate,
            'target_balance': self.target_balance,
            'active_sessions': len(self.active_sessions),
            'completed_sessions': len(self.completed_sessions),
        }

# Integration function
def integrate_ultra_continuous_trading(
    ultra_core: UltraCore, risk_engine: RiskEngine, config: Optional[ContinuousTradingConfig] = None
) -> UltraContinuousTradingOrchestrator:
    """Integrate Ultra Continuous Trading Orchestrator with core system"""
    return UltraContinuousTradingOrchestrator(ultra_core, risk_engine, config)
