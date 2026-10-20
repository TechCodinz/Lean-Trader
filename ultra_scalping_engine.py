import numpy as np
"""
Ultra Scalping Engine - Micro-Profit Accumulation System
Designed for rapid $48 → $3000-5000 growth by November

Features:
- Continuous M1/M5 scalping across all timeframes
- Micro-pip profit targeting (0.5-2 pips)
- Rapid execution (sub-second)
- Risk-free scalping with tight stops
- Compound growth optimization
- Multi-asset simultaneous scalping
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Core imports
from ultra_core import UltraCore
from risk_engine import RiskEngine
from pattern_memory import PatternMemory
from brain import Brain

@dataclass
class ScalpSignal:
    """Scalping signal data structure"""

    symbol: str
    timeframe: str
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    profit_pips: float
    risk_reward: float
    timestamp: float
    strategy: str

@dataclass
class ScalpResult:
    """Scalping result data structure"""

    symbol: str
    entry_price: float
    exit_price: float
    profit: float
    profit_pips: float
    duration: float
    success: bool
    timestamp: float

class UltraScalpingEngine:
    """
    Ultra Scalping Engine for micro-profit accumulation

    Designed to generate consistent micro-profits through:
    - High-frequency scalping (M1, M5 timeframes)
    - Micro-pip profit targeting
    - Risk-free position management
    - Compound growth acceleration
    """

    def __init__(self, ultra_core: UltraCore, risk_engine: RiskEngine):
        self.ultra_core = ultra_core
        self.risk_engine = risk_engine
        self.pattern_memory = PatternMemory()
        self.brain = Brain()

        # Scalping configuration
        self.MICRO_PIP_TARGET = 0.5  # 0.5 pip minimum target
        self.MAX_PIP_TARGET = 2.0  # 2 pip maximum target
        self.TIGHT_STOP_LOSS = 1.0  # 1 pip stop loss
        self.MIN_CONFIDENCE = 0.75  # 75% minimum confidence
        self.MAX_POSITIONS = 10  # Maximum simultaneous positions

        # Performance tracking
        self.active_positions: Dict[str, ScalpSignal] = {}
        self.completed_trades: List[ScalpResult] = []
        self.daily_profit = 0.0
        self.total_profit = 0.0
        self.win_rate = 0.0
        self.avg_profit_per_trade = 0.0

        # Timeframe weights for scalping
        self.TIMEFRAME_WEIGHTS = {
            'M1': 0.4,  # 40% weight - primary scalping
            'M5': 0.3,  # 30% weight - secondary scalping
            'M15': 0.2,  # 20% weight - momentum scalping
            'M30': 0.1,  # 10% weight - trend scalping
        }

        # Scalping strategies
        self.SCALPING_STRATEGIES = [
            'micro_momentum',
            'spread_capture',
            'volatility_scalp',
            'news_scalp',
            'correlation_scalp',
            'arbitrage_scalp',
        ]

        self.logger = logging.getLogger(__name__)

    async def start_scalping(self) -> None:
        """Start continuous scalping across all timeframes"""
        self.logger.info("🚀 Starting Ultra Scalping Engine...")

        # Start scalping tasks for each timeframe
        tasks = []
        for timeframe, weight in self.TIMEFRAME_WEIGHTS.items():
            task = asyncio.create_task(self._scalp_timeframe(timeframe, weight))
            tasks.append(task)

        # Start monitoring and management tasks
        tasks.append(asyncio.create_task(self._monitor_positions()))
        tasks.append(asyncio.create_task(self._manage_risk()))
        tasks.append(asyncio.create_task(self._track_performance()))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    async def _scalp_timeframe(self, timeframe: str, weight: float) -> None:
        """Scalp specific timeframe with given weight"""
        self.logger.info(f"📊 Starting {timeframe} scalping (weight: {weight})")

        while True:
            try:
                # Get scalping opportunities for this timeframe
                opportunities = await self._scan_scalp_opportunities(timeframe)

                for opportunity in opportunities:
                    if len(self.active_positions) < self.MAX_POSITIONS:
                        await self._execute_scalp_trade(opportunity)

                # Wait before next scan (faster for lower timeframes)
                wait_time = 1 if timeframe == 'M1' else 5 if timeframe == 'M5' else 15
                await asyncio.sleep(wait_time)

            except Exception as e:
                self.logger.error(f"Error in {timeframe} scalping: {e}")
                await asyncio.sleep(5)

    async def _scan_scalp_opportunities(self, timeframe: str) -> List[ScalpSignal]:
        """Scan for scalping opportunities in specific timeframe"""
        opportunities = []

        try:
            # Get market data for all symbols
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']

            for symbol in symbols:
                # Get price data
                price_data = await self.ultra_core.get_market_data(symbol, timeframe)

                if not price_data:
                    continue

                # Analyze for scalping opportunities
                scalp_signals = await self._analyze_scalp_opportunities(
                    symbol, timeframe, price_data
                )

                opportunities.extend(scalp_signals)

        except Exception as e:
            self.logger.error(f"Error scanning scalp opportunities: {e}")

        return opportunities

    async def _analyze_scalp_opportunities(
        self, symbol: str, timeframe: str, price_data: Dict[str, Any]
    ) -> List[ScalpSignal]:
        """Analyze price data for scalping opportunities"""
        signals = []

        try:
            current_price = price_data.get('close', 0)
            if current_price <= 0:
                return signals

            # Micro momentum scalping
            momentum_signal = await self._detect_micro_momentum(symbol, timeframe, price_data)
            if momentum_signal:
                signals.append(momentum_signal)

            # Spread capture scalping
            spread_signal = await self._detect_spread_capture(symbol, timeframe, price_data)
            if spread_signal:
                signals.append(spread_signal)

            # Volatility scalping
            volatility_signal = await self._detect_volatility_scalp(symbol, timeframe, price_data)
            if volatility_signal:
                signals.append(volatility_signal)

        except Exception as e:
            self.logger.error(f"Error analyzing scalp opportunities: {e}")

        return signals

    async def _detect_micro_momentum(
        self, symbol: str, timeframe: str, price_data: Dict[str, Any]
    ) -> Optional[ScalpSignal]:
        """Detect micro momentum for scalping"""
        try:
            # Calculate micro momentum indicators
            prices = price_data.get('prices', [])
            if len(prices) < 10:
                return None

            # Simple momentum calculation
            recent_prices = prices[-10:]
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

            # Check if momentum is strong enough for scalping
            if abs(momentum) > 0.0001:  # 0.01% minimum momentum
                current_price = recent_prices[-1]

                # Determine direction
                if momentum > 0:
                    # Bullish momentum - buy scalp
                    target_price = current_price * (1 + self.MICRO_PIP_TARGET / 10000)
                    stop_loss = current_price * (1 - self.TIGHT_STOP_LOSS / 10000)
                    confidence = min(0.95, abs(momentum) * 1000)
                else:
                    # Bearish momentum - sell scalp
                    target_price = current_price * (1 - self.MICRO_PIP_TARGET / 10000)
                    stop_loss = current_price * (1 + self.TIGHT_STOP_LOSS / 10000)
                    confidence = min(0.95, abs(momentum) * 1000)

                if confidence >= self.MIN_CONFIDENCE:
                    return ScalpSignal(
                        symbol=symbol,
                        timeframe=timeframe,
                        entry_price=current_price,
                        target_price=target_price,
                        stop_loss=stop_loss,
                        confidence=confidence,
                        profit_pips=self.MICRO_PIP_TARGET,
                        risk_reward=self.MICRO_PIP_TARGET / self.TIGHT_STOP_LOSS,
                        timestamp=time.time(),
                        strategy='micro_momentum',
                    )

        except Exception as e:
            self.logger.error(f"Error detecting micro momentum: {e}")

        return None

    async def _detect_spread_capture(
        self, symbol: str, timeframe: str, price_data: Dict[str, Any]
    ) -> Optional[ScalpSignal]:
        """Detect spread capture opportunities"""
        try:
            # Get bid/ask spread
            bid = price_data.get('bid', 0)
            ask = price_data.get('ask', 0)

            if bid <= 0 or ask <= 0:
                return None

            spread = ask - bid
            spread_pips = (spread / bid) * 10000

            # Check if spread is tight enough for scalping
            if spread_pips <= 2.0:  # 2 pip maximum spread
                current_price = (bid + ask) / 2

                # Create scalp signal for spread capture
                target_price = current_price * (1 + self.MICRO_PIP_TARGET / 10000)
                stop_loss = current_price * (1 - self.TIGHT_STOP_LOSS / 10000)

                return ScalpSignal(
                    symbol=symbol,
                    timeframe=timeframe,
                    entry_price=current_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    confidence=0.85,  # High confidence for spread capture
                    profit_pips=self.MICRO_PIP_TARGET,
                    risk_reward=self.MICRO_PIP_TARGET / self.TIGHT_STOP_LOSS,
                    timestamp=time.time(),
                    strategy='spread_capture',
                )

        except Exception as e:
            self.logger.error(f"Error detecting spread capture: {e}")

        return None

    async def _detect_volatility_scalp(
        self, symbol: str, timeframe: str, price_data: Dict[str, Any]
    ) -> Optional[ScalpSignal]:
        """Detect volatility scalping opportunities"""
        try:
            prices = price_data.get('prices', [])
            if len(prices) < 20:
                return None

            # Calculate volatility
            recent_prices = prices[-20:]
            returns = [
                recent_prices[i] / recent_prices[i - 1] - 1 for i in range(1, len(recent_prices))
            ]
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility

            # Check if volatility is suitable for scalping
            if 0.1 < volatility < 0.5:  # 10-50% volatility range
                current_price = recent_prices[-1]

                # Determine direction based on recent trend
                short_trend = (recent_prices[-1] - recent_prices[-5]) / recent_prices[-5]

                if abs(short_trend) > 0.0005:  # 0.05% minimum trend
                    if short_trend > 0:
                        # Bullish trend - buy scalp
                        target_price = current_price * (1 + self.MICRO_PIP_TARGET / 10000)
                        stop_loss = current_price * (1 - self.TIGHT_STOP_LOSS / 10000)
                    else:
                        # Bearish trend - sell scalp
                        target_price = current_price * (1 - self.MICRO_PIP_TARGET / 10000)
                        stop_loss = current_price * (1 + self.TIGHT_STOP_LOSS / 10000)

                    confidence = min(0.90, abs(short_trend) * 200)

                    if confidence >= self.MIN_CONFIDENCE:
                        return ScalpSignal(
                            symbol=symbol,
                            timeframe=timeframe,
                            entry_price=current_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            confidence=confidence,
                            profit_pips=self.MICRO_PIP_TARGET,
                            risk_reward=self.MICRO_PIP_TARGET / self.TIGHT_STOP_LOSS,
                            timestamp=time.time(),
                            strategy='volatility_scalp',
                        )

        except Exception as e:
            self.logger.error(f"Error detecting volatility scalp: {e}")

        return None

    async def _execute_scalp_trade(self, signal: ScalpSignal) -> None:
        """Execute scalping trade"""
        try:
            # Check risk limits
            if not await self.risk_engine.check_scalp_risk(signal):
                return

            # Execute trade
            position_id = f"{signal.symbol}_{signal.timeframe}_{int(signal.timestamp)}"

            # Store active position
            self.active_positions[position_id] = signal

            self.logger.info(
                f"🎯 Executed scalp trade: {signal.symbol} {signal.timeframe} "
                f"@ {signal.entry_price:.6f} → {signal.target_price:.6f} "
                f"(confidence: {signal.confidence:.2f})"
            )

            # Real testnet execution on the relay (guarded, capped)
            try:
                self._real_open(signal)
            except Exception as e:
                self.logger.warning(f"real open {signal.symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error executing scalp trade: {e}")

    async def _monitor_positions(self) -> None:
        """Monitor active scalping positions"""
        while True:
            try:
                current_time = time.time()

                for position_id, signal in list(self.active_positions.items()):
                    # Check if target or stop loss hit
                    current_price = await self._get_current_price(signal.symbol)

                    if current_price <= 0:
                        continue

                    # Check target hit
                    if signal.target_price > signal.entry_price:  # Long position
                        if current_price >= signal.target_price:
                            await self._close_scalp_position(
                                position_id, signal, current_price, True
                            )
                        elif current_price <= signal.stop_loss:
                            await self._close_scalp_position(
                                position_id, signal, current_price, False
                            )
                    else:  # Short position
                        if current_price <= signal.target_price:
                            await self._close_scalp_position(
                                position_id, signal, current_price, True
                            )
                        elif current_price >= signal.stop_loss:
                            await self._close_scalp_position(
                                position_id, signal, current_price, False
                            )

                    # Check timeout (max 5 minutes for scalping)
                    if current_time - signal.timestamp > 300:  # 5 minutes
                        await self._close_scalp_position(position_id, signal, current_price, False)

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Error monitoring positions: {e}")
                await asyncio.sleep(5)

    async def _close_scalp_position(
        self, position_id: str, signal: ScalpSignal, exit_price: float, success: bool
    ) -> None:
        """Close scalping position and record result"""
        try:
            # Real testnet close first (if this position is real)
            try:
                self._real_close(signal, exit_price)
            except Exception as e:
                self.logger.error(f"real close hook: {e}")
            # Calculate profit
            if signal.target_price > signal.entry_price:  # Long position
                profit = exit_price - signal.entry_price
            else:  # Short position
                profit = signal.entry_price - exit_price

            profit_pips = (profit / signal.entry_price) * 10000
            duration = time.time() - signal.timestamp

            # Create result
            result = ScalpResult(
                symbol=signal.symbol,
                entry_price=signal.entry_price,
                exit_price=exit_price,
                profit=profit,
                profit_pips=profit_pips,
                duration=duration,
                success=success,
                timestamp=time.time(),
            )

            # Store result
            self.completed_trades.append(result)

            # Capacity evidence: paper closes belong in the ledger
            # too - until now the sniper's internal results vanished
            # and the governor had nothing to measure it by (0 rows).
            if not getattr(signal, 'real_qty', None):
                try:
                    import allocation as _alloc
                    _slice = float(_alloc.get('master').get('slice_usd', 12.0))
                except Exception:
                    _slice = 12.0
                try:
                    import being_ledger as _bl
                    _qty = _slice / signal.entry_price if signal.entry_price else 0
                    _bl.record_close(
                        'master', signal.symbol, profit * _qty, real=False,
                        meta={'strat': 'scalping_engine',
                              'tf': signal.timeframe,
                              'pips': round(profit_pips, 2)})
                except Exception:
                    pass

            # Update performance metrics
            self.daily_profit += profit
            self.total_profit += profit

            # Remove from active positions
            del self.active_positions[position_id]

            # Log result
            status = "✅ WIN" if success else "❌ LOSS"
            self.logger.info(
                f"{status} Scalp: {signal.symbol} {signal.timeframe} "
                f"Profit: {profit:.6f} ({profit_pips:.1f} pips) "
                f"Duration: {duration:.1f}s"
            )

        except Exception as e:
            self.logger.error(f"Error closing scalp position: {e}")

    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol (live public ticker)."""
        try:
            pub = getattr(self, '_pub', None)
            if pub is None:
                import ccxt as _ccxt
                pub = _ccxt.bybit({'enableRateLimit': True})
                self._pub = pub
            t = pub.fetch_ticker(symbol)
            return float(t.get('last') or 0.0)
        except Exception as e:
            self.logger.error(f"Error getting current price: {e}")
            return 0.0

    # === REAL EXECUTION (relay graft, 2026-10-19) ===================
    # The 2025 engine's execution tail was simulated (store + log).
    # These two methods give it a real testnet execution core on the
    # signing relay - the same pattern as the swarm/continuous
    # executors: live-ticker sizing, conflict guard, margin backoff,
    # allocation-governed slice/cap, ledger-recorded closes.
    def _real_open(self, signal) -> None:
        # Continuous profitability allowance (Peters' design -
        # replaces a hard M30 gate, which froze stale evidence):
        # NO station is demoted. Each real open is allowed only
        # while its timeframe's RECENT measured expectancy (last 40
        # ledger closes for that timeframe) is not clearly negative.
        # A cold station is simply not used for this trade; it keeps
        # analyzing and learning, and re-enters by itself when its
        # window turns profitable again.
        try:
            import time as _tt
            if _tt.time() - getattr(self, '_tf_allow_ts', 0) > 300:
                self._tf_allow_ts = _tt.time()
                import json as _jj
                from collections import defaultdict as _dd
                _acc = _dd(list)
                with open('/app/runtime/being_ledger.jsonl') as _f:
                    for _ln in _f:
                        try:
                            _r = _jj.loads(_ln)
                        except Exception:
                            continue
                        if _r.get('being') == 'master':
                            _tf = (_r.get('meta') or {}).get('tf')
                            if _tf:
                                _acc[_tf].append(float(_r.get('pnl') or 0))
                self._tf_allow = {}
                for _tf, _ps in _acc.items():
                    _recent = _ps[-40:]
                    self._tf_allow[_tf] = not (
                        len(_recent) >= 25
                        and sum(_recent) / len(_recent) < -0.005)
            if not self._tf_allow.get(getattr(signal, 'timeframe', ''), True):
                return
        except Exception:
            pass
        import time as _t
        if signal.target_price <= signal.entry_price:
            return  # long-only v1: short signals stay simulated
        if getattr(self, '_real_backoff_until', 0) > _t.time():
            return
        try:
            import allocation as _alloc
            a = _alloc.get('master')
        except Exception:
            a = {'mode': 'real', 'slice_usd': 12.0, 'max_concurrent': 2}
        if a.get('mode') != 'real':
            return
        open_real = sum(1 for sg in self.active_positions.values()
                        if getattr(sg, 'real_qty', None))
        if open_real >= int(a.get('max_concurrent', 2)):
            return
        base = signal.symbol.split('/')[0]
        raw = base + 'USDT'
        try:
            from testnet_client import make_client, qty_str, quantize
            tn = getattr(self, '_tn', None)
            if tn is None:
                tn = make_client()
                self._tn = tn
            for pos in tn.positions():
                if pos.get('symbol') == raw and float(pos.get('positionValue') or 0) >= 1.0:
                    return  # conflict guard: exchange already holds it
            price = self._pub.fetch_ticker(signal.symbol)['last'] \
                if getattr(self, '_pub', None) else None
            if not price:
                import ccxt as _ccxt
                self._pub = _ccxt.bybit({'enableRateLimit': True})
                price = float(self._pub.fetch_ticker(signal.symbol)['last'])
            slice_usd = float(a.get('slice_usd', 12.0))
            qty = slice_usd / float(price)
            try:
                mkt = self._pub.market(signal.symbol + ':USDT')
                step = float(mkt['precision']['amount'])
                qty = quantize(qty, step)
            except Exception:
                qty = round(qty, 3)
            # A quantized qty of 0 (slice below the lot minimum, e.g.
            # BTC at a $12 slice) or a sub-$10 notional is a clean
            # skip - never fall back to the unquantized amount.
            if not qty or qty <= 0 or qty * float(price) < 10.0:
                return
            try:
                tn.set_leverage(raw, 10)
            except Exception:
                pass
            res = tn.create_market_buy(raw, qty_str(qty))
            if isinstance(res, dict) and res.get('orderId'):
                signal.real_qty = qty
                signal.real_entry = float(price)
                self.logger.info(
                    f"REAL scalp buy {raw} qty {qty} @ {price} "
                    f"(strat {signal.strategy} conf {signal.confidence:.2f})")
            else:
                self.logger.warning(f"real open rejected {raw}: {res}")
                if isinstance(res, dict) and '110007' in str(res):
                    self._real_backoff_until = _t.time() + 60
        except Exception as e:
            if '110007' in str(e):
                self._real_backoff_until = _t.time() + 60
            self.logger.warning(f"real open {signal.symbol}: {e}")

    def _real_close(self, signal, exit_price: float) -> None:
        qty = getattr(signal, 'real_qty', None)
        if not qty:
            return
        base = signal.symbol.split('/')[0]
        raw = base + 'USDT'
        try:
            from testnet_client import make_client, qty_str
            tn = getattr(self, '_tn', None)
            if tn is None:
                tn = make_client()
                self._tn = tn
            res = None
            for _ in range(3):
                res = tn.create_market_sell_reduce(raw, qty_str(qty))
                if isinstance(res, dict) and res.get('orderId'):
                    break
            if isinstance(res, dict) and res.get('orderId'):
                pnl = (float(exit_price) - float(signal.real_entry)) * float(qty)
                self.logger.info(f"REAL scalp close {raw} qty {qty} pnl ${pnl:+.4f}")
                try:
                    import being_ledger
                    being_ledger.record_close(
                        'master', signal.symbol, pnl, real=True,
                        meta={'strat': signal.strategy, 'engine': 'scalp',
                              'tf': signal.timeframe})
                except Exception:
                    pass
            else:
                self.logger.error(f"REAL CLOSE FAILED {raw}: {res} - position may be orphaned, check the exchange")
        except Exception as e:
            self.logger.error(f"real close {signal.symbol}: {e}")

    async def _manage_risk(self) -> None:
        """Manage scalping risk"""
        while True:
            try:
                # Check daily loss limits
                if self.daily_profit < -50:  # $50 daily loss limit
                    self.logger.warning("🚨 Daily loss limit reached, stopping scalping")
                    # Stop all active positions
                    for position_id in list(self.active_positions.keys()):
                        del self.active_positions[position_id]

                # Check position limits
                if len(self.active_positions) > self.MAX_POSITIONS:
                    self.logger.warning(
                        f"🚨 Too many positions ({len(self.active_positions)}), closing oldest"
                    )
                    # Close oldest position
                    oldest_position = min(
                        self.active_positions.items(), key=lambda x: x[1].timestamp
                    )
                    del self.active_positions[oldest_position[0]]

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error managing risk: {e}")
                await asyncio.sleep(10)

    async def _track_performance(self) -> None:
        """Track scalping performance"""
        while True:
            try:
                # Calculate win rate
                if self.completed_trades:
                    wins = sum(1 for trade in self.completed_trades if trade.success)
                    self.win_rate = wins / len(self.completed_trades)

                    # Calculate average profit per trade
                    total_profit = sum(trade.profit for trade in self.completed_trades)
                    self.avg_profit_per_trade = total_profit / len(self.completed_trades)

                # Log performance every minute
                self.logger.info(
                    f"📊 Scalping Performance: "
                    f"Active: {len(self.active_positions)}, "
                    f"Completed: {len(self.completed_trades)}, "
                    f"Win Rate: {self.win_rate:.1%}, "
                    f"Daily P&L: ${self.daily_profit:.2f}, "
                    f"Total P&L: ${self.total_profit:.2f}"
                )

                await asyncio.sleep(60)  # Log every minute

            except Exception as e:
                self.logger.error(f"Error tracking performance: {e}")
                await asyncio.sleep(60)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get scalping performance summary"""
        return {
            'active_positions': len(self.active_positions),
            'completed_trades': len(self.completed_trades),
            'daily_profit': self.daily_profit,
            'total_profit': self.total_profit,
            'win_rate': self.win_rate,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'avg_duration': (
                np.mean([t.duration for t in self.completed_trades]) if self.completed_trades else 0
            ),
        }

# Integration function
def integrate_ultra_scalping_engine(
    ultra_core: UltraCore, risk_engine: RiskEngine
) -> UltraScalpingEngine:
    """Integrate Ultra Scalping Engine with core system"""
    return UltraScalpingEngine(ultra_core, risk_engine)
