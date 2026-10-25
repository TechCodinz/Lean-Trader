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
        # DENOMINATION FIX (2026-10-23, Princewill's go-ahead):
        # the design's ratios are unchanged (min : max : stop =
        # 0.5 : 2 : 1) but a 'pip' in this code is 1bp (targets are
        # price * pips/10000) while a Bybit round trip costs ~4bp
        # maker / ~11bp taker - at 0.5-2bp every target hit was a
        # net loss after fees, by arithmetic. Re-denominated x50
        # in the same ratios: 25bp / 100bp / 50bp, clearing the
        # venue cost floor with margin.
        self.MICRO_PIP_TARGET = 25.0  # 25bp minimum target
        self.MAX_PIP_TARGET = 100.0  # 100bp maximum target
        self.TIGHT_STOP_LOSS = 50.0  # 50bp stop loss
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

    def _universe_symbols(self):
        """Top pairs by 24h quote volume, refreshed every 10 min.
        The hardcoded five survive only as an offline fallback."""
        import time as _t
        if (_t.time() - getattr(self, '_uni_ts', 0) < 600
                and getattr(self, '_uni', None)):
            return self._uni
        syms = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
        try:
            pub = getattr(self, '_pub', None)
            if pub is None:
                import ccxt as _c
                pub = _c.bybit({'enableRateLimit': True})
                self._pub = pub
            ticks = pub.fetch_tickers()
            ranked = sorted(
                (x for x in ticks if x.endswith('/USDT:USDT')),
                key=lambda x: -(ticks[x].get('quoteVolume') or 0))
            top = [x.replace(':USDT', '') for x in ranked[:24]]
            # Venue truth (2026-10-21): the ranked list came from
            # MAINNET tickers and carried instruments the execution
            # venue does not list - tokenized stocks (SOXL, SNDK,
            # SKHYNIX), XAU, SPCX - whose candles the router then
            # fabricated as SYNTHETIC BARS (37k servings in one
            # log) while the real arm could never trade them.
            # Intersect with the venue's own listed linear symbols
            # (cached 1h); if the venue read fails, keep the
            # ranked list rather than going blind.
            # Venue truth from the disk spec table the real arm
            # maintains (2026-10-21) - no fetches from the scan
            # loop (WAF). No table yet: keep the ranked list.
            try:
                import json as _uj
                _disk = _uj.load(open(
                    '/app/runtime/venue_instruments.json'))
                _listed = {k[:-4] for k in (_disk or {}).keys()
                           if k.endswith('USDT')}
                if _listed:
                    _kept = [x for x in top
                             if x.split('/')[0] in _listed]
                    if _kept:
                        top = _kept[:24]
                    self.logger.info(
                        f'UNIVERSE venue-kept {len(top)}: '
                        f'{top[:8]}')
            except Exception:
                pass
            if top:
                syms = top
        except Exception:
            pass
        self._uni, self._uni_ts = syms, _t.time()
        return syms

    async def _scan_scalp_opportunities(self, timeframe: str) -> List[ScalpSignal]:
        """Scan for scalping opportunities in specific timeframe"""
        opportunities = []

        try:
            # Get market data for all symbols - the whole market is
            # the hunting ground, ranked by live volume
            symbols = self._universe_symbols()

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

            # Signal-math experiments are paper-only until their ledger
            # measurements are validated; real keeps the legacy path.
            try:
                import allocation as _alloc
                paper = _alloc.get('master').get('mode') == 'paper'
            except Exception:
                paper = False

            # Micro momentum scalping
            momentum_signal = await self._detect_micro_momentum(
                symbol, timeframe, price_data, paper=paper)
            if momentum_signal:
                signals.append(momentum_signal)

            # Spread capture scalping
            spread_signal = await self._detect_spread_capture(symbol, timeframe, price_data)
            if spread_signal:
                signals.append(spread_signal)

            # Volatility scalping
            volatility_signal = await self._detect_volatility_scalp(
                symbol, timeframe, price_data, paper=paper)
            if volatility_signal:
                signals.append(volatility_signal)

            # Do not open opposing paper positions from one market snapshot.
            # Keep every detector on the highest-confidence signal's side.
            sides = {s.target_price > s.entry_price for s in signals}
            if paper and len(sides) > 1:
                selected = max(signals, key=lambda s: s.confidence)
                selected_side = selected.target_price > selected.entry_price
                signals = [s for s in signals
                           if (s.target_price > s.entry_price) == selected_side]

            # MEASUREMENT OVERLAYS (2026-10-25, Princewill's
            # directive): tag every signal with the market REGIME
            # (FractalRegime Hurst voter, hurst_fractal_regime.py)
            # and the VOLUME-PROFILE distance to the point of
            # control (VolumeProfileAnalyzer, critical_features_
            # addon) from this scan's own candles. Record-only:
            # nothing in the trade path reads them; the paper close
            # meta carries them so expectancy can be split by regime
            # and VP position. Cached 60s per (symbol, timeframe).
            # The SMART_SCALPING_ENGINE confluence analyzer was
            # probe-verified a STUB on 2026-10-25 (identical outputs
            # for opposite inputs) and is deliberately NOT wired.
            if signals:
                try:
                    _key = (symbol, timeframe)
                    _now = time.time()
                    _cache = getattr(self, '_overlay_cache', None)
                    if _cache is None:
                        self._overlay_cache = {}
                        _cache = self._overlay_cache
                    _hit = _cache.get(_key)
                    if _hit is None or _now - _hit[0] > 60:
                        _regime = _hurst = _vp = None
                        _closes = price_data.get('prices') or []
                        if len(_closes) >= 50:
                            from hurst_fractal_regime import (
                                FractalRegime as _FR)
                            import pandas as _pd
                            _r = _FR().compute(
                                _pd.DataFrame({'close': _closes}))
                            _hurst = round(
                                float(_r['features']['hurst']), 3)
                            _regime = ('trending' if _hurst > 0.55 else
                                       'reverting' if _hurst < 0.45
                                       else 'neutral')
                        _candles = price_data.get('candles') or []
                        if len(_candles) >= 100:
                            import pandas as _pd
                            from critical_features_addon import (
                                VolumeProfileAnalyzer as _VPA)
                            _df = _pd.DataFrame(
                                [(_c[2], _c[3],
                                  _c[5] if len(_c) > 5 else 0)
                                 for _c in _candles],
                                columns=['high', 'low', 'volume'])
                            _v = _VPA().analyze(_df)
                            if _v.get('poc'):
                                _vp = round(
                                    (current_price - _v['poc'])
                                    / _v['poc'] * 10000, 1)
                        _hit = (_now, _regime, _hurst, _vp)
                        _cache[_key] = _hit
                    for _s in signals:
                        _s._regime = _hit[1]
                        _s._hurst = _hit[2]
                        _s._vp_poc_bp = _hit[3]
                except Exception:
                    pass

        except Exception as e:
            self.logger.error(f"Error analyzing scalp opportunities: {e}")

        return signals

    async def _detect_micro_momentum(
        self, symbol: str, timeframe: str, price_data: Dict[str, Any],
        paper: bool = False
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
                else:
                    # Bearish momentum - sell scalp
                    target_price = current_price * (1 - self.MICRO_PIP_TARGET / 10000)
                    stop_loss = current_price * (1 + self.TIGHT_STOP_LOSS / 10000)

                confidence = abs(momentum) * 1000
                if paper and confidence >= self.MIN_CONFIDENCE:
                    # Preserve the entry cutoff but keep qualifying scores
                    # strictly ordered instead of collapsing them at the cap.
                    confidence = 0.95 - (0.95 - self.MIN_CONFIDENCE) / (
                        1 + confidence - self.MIN_CONFIDENCE)
                confidence = min(0.95, confidence)

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
        self, symbol: str, timeframe: str, price_data: Dict[str, Any],
        paper: bool = False
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
            if paper:
                # Crypto candles annualize by their actual frame, 365 days/year.
                minutes = int(timeframe[1:])  # Master frames are M1/M5/M15/M30.
                volatility = np.std(returns) * np.sqrt(365 * 24 * 60 / minutes)
            else:
                volatility = np.std(returns) * np.sqrt(252)  # Legacy real path

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

                    confidence = abs(short_trend) * 200
                    if paper and confidence >= self.MIN_CONFIDENCE:
                        confidence = 0.90 - (0.90 - self.MIN_CONFIDENCE) / (
                            1 + confidence - self.MIN_CONFIDENCE)
                    confidence = min(0.90, confidence)

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
        self._rehydrate_real()
        _last_recon = time.time()
        while True:
            try:
                # RECONCILE (2026-10-24): rehydrate ran only at
                # boot, so a real position lost from the in-memory
                # book mid-run was never re-tracked - the registry
                # and the exchange still held it while the monitor
                # forgot it. Re-run every 60s; the already-tracked
                # guard inside makes it a no-op for healthy books
                # in every mode (a paper book has no registry).
                if time.time() - _last_recon > 60:
                    _last_recon = time.time()
                    self._rehydrate_real()
            except Exception:
                pass
            try:
                current_time = time.time()

                for position_id, signal in list(self.active_positions.items()):
                    # REAL positions decide in the testnet frame
                    # (exchange mark vs exchange entry); paper
                    # positions keep the analysis frame below.
                    if getattr(signal, 'real_qty', None):
                        _pos = self._testnet_pos(
                            signal.symbol.split('/')[0] + 'USDT')
                        _mark = float((_pos or {}).get('markPrice') or 0)
                        if _mark > 0:
                            _hit = self._real_exit_hit(signal, _mark)
                            if _hit is not None:
                                await self._close_scalp_position(
                                    position_id, signal, _mark, _hit)
                            elif current_time - signal.timestamp > 3600:
                                # REAL-BRANCH CLOCK (2026-10-23,
                                # Princewill: get it resolved): was
                                # 300s, inherited from the engine's
                                # paper scalp convention. It closed
                                # 14 of the first 15 real probation
                                # positions as fee-scale scratches
                                # (~-$0.02 each; closes landed
                                # exactly 300s apart) before the
                                # 25bp target / 50bp stop could ever
                                # trigger. Real positions now get
                                # the fleet-standard 1h backstop so
                                # target/stop decide exits; the
                                # paper branch keeps its 300s.
                                await self._close_scalp_position(
                                    position_id, signal, _mark, False)
                            continue
                    # Check if target or stop loss hit
                    current_price = await self._get_current_price(signal.symbol)

                    if current_price <= 0:
                        continue

                    # RUNNER TRAILING (2026-10-25, Princewill's
                    # directive): a paper position that reaches its
                    # target no longer closes on the spot - the target
                    # ARMS a trailing runner on the codebase's
                    # existing TrailingStopManager
                    # (critical_features_addon). The floor starts at
                    # breakeven and trails the peak by the target
                    # distance - the zoo's 2025 runner design
                    # (ladder TP3 arm) ported to the master. Shorts
                    # feed inverted prices so the one manager serves
                    # both sides. Losers still stop out immediately;
                    # unarmed positions keep the 300s timeout; armed
                    # runners get the fleet's 3600s backstop. If the
                    # addon cannot import, fall back to the legacy
                    # close-at-target so the monitor never breaks.
                    _is_long = signal.target_price > signal.entry_price
                    if getattr(signal, '_runner_armed', False):
                        _mgr = signal._trail_mgr
                        _feed = (current_price if _is_long
                                 else 1.0 / current_price)
                        _fent = (signal.entry_price if _is_long
                                 else 1.0 / signal.entry_price)
                        _stop = _mgr.update(signal.symbol, _feed,
                                            _fent, _fent)
                        _floor = _stop if _is_long else 1.0 / _stop
                        _floor = (max(_floor, signal.entry_price)
                                  if _is_long
                                  else min(_floor, signal.entry_price))
                        _breach = (current_price <= _floor if _is_long
                                   else current_price >= _floor)
                        _stopped = (current_price <= signal.stop_loss
                                    if _is_long
                                    else current_price >= signal.stop_loss)
                        if _breach or _stopped:
                            signal._exit_reason = ('trail' if _breach
                                                   else 'stop')
                            await self._close_scalp_position(
                                position_id, signal, current_price,
                                (current_price >= signal.entry_price)
                                if _is_long else
                                (current_price <= signal.entry_price))
                    elif _is_long:  # Long position, not yet armed
                        if current_price >= signal.target_price:
                            try:
                                from critical_features_addon import (
                                    TrailingStopManager as _TSM)
                                signal._trail_mgr = _TSM(
                                    self.MICRO_PIP_TARGET / 10000)
                                signal._runner_armed = True
                            except Exception:
                                signal._exit_reason = 'target'
                                await self._close_scalp_position(
                                    position_id, signal,
                                    current_price, True)
                        elif current_price <= signal.stop_loss:
                            signal._exit_reason = 'stop'
                            await self._close_scalp_position(
                                position_id, signal, current_price, False
                            )
                    else:  # Short position, not yet armed
                        if current_price <= signal.target_price:
                            try:
                                from critical_features_addon import (
                                    TrailingStopManager as _TSM)
                                signal._trail_mgr = _TSM(
                                    self.MICRO_PIP_TARGET / 10000)
                                signal._runner_armed = True
                            except Exception:
                                signal._exit_reason = 'target'
                                await self._close_scalp_position(
                                    position_id, signal,
                                    current_price, True)
                        elif current_price >= signal.stop_loss:
                            signal._exit_reason = 'stop'
                            await self._close_scalp_position(
                                position_id, signal, current_price, False
                            )

                    # Check timeout - only if the position is still
                    # open: a close above already removed it, and
                    # closing again would book the same trade twice
                    # (duplicate-close bug, fixed 2026-10-25). Unarmed
                    # positions keep 300s; armed runners get the
                    # fleet's 3600s backstop.
                    _limit = (3600 if getattr(signal, '_runner_armed',
                                              False) else 300)
                    if (position_id in self.active_positions
                            and current_time - signal.timestamp > _limit):
                        signal._exit_reason = ('trail_timeout' if _limit
                                               == 3600 else 'timeout')
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
            _rc = True
            try:
                _rc = self._real_close(signal, exit_price)
            except Exception as e:
                self.logger.error(f"real close hook: {e}")
            if getattr(signal, 'real_qty', None) and _rc is False:
                # The close did not execute (illiquid testnet
                # book): the position is still real - keep
                # monitoring it; never book a phantom exit.
                return
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
                              'detector': signal.strategy,
                              'side': ('long' if signal.target_price >
                                       signal.entry_price else 'short'),
                              'confidence': signal.confidence,
                              'entry_ts': signal.timestamp,
                              'signal_id': position_id,
                              'exit_reason': getattr(signal, '_exit_reason', None),
                              'regime': getattr(signal, '_regime', None),
                              'hurst': getattr(signal, '_hurst', None),
                              'vp_poc_bp': getattr(signal, '_vp_poc_bp', None),
                              'tf': signal.timeframe,
                              'pips': round(profit_pips, 2)})
                except Exception:
                    pass

            # Update performance metrics
            self.daily_profit += profit
            self.total_profit += profit

            # Remove from active positions
            if getattr(signal, 'real_entry', 0):
                self._reg_pop(signal.symbol.split('/')[0] + 'USDT')
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

    # === TESTNET PRICE TRUTH (2026-10-20) ==========================
    # The sniper analyzes mainnet prices (its design), but its REAL
    # positions live on testnet, whose marks drift from mainnet on
    # illiquid pairs - the same mismatch that fired phantom stops
    # in the orchestrator (KAS, +6.8%). Real positions therefore
    # enter, exit and book in the exchange's own frame.
    def _tn_client(self):
        tn = getattr(self, '_tn', None)
        if tn is None:
            from testnet_client import make_client
            tn = make_client()
            self._tn = tn
        return tn

    def _testnet_pos(self, raw):
        try:
            for pp in self._tn_client().positions():
                if (pp.get('symbol') or '') == raw:
                    return pp
        except Exception:
            pass
        return None

    def _real_exit_hit(self, signal, mark):
        """Exit decision for a REAL position in the testnet frame:
        entry = exchange avgPrice, now = exchange mark, target/stop
        = the signal's intended fractional distances."""
        entry = float(getattr(signal, 'real_entry', 0) or 0)
        if not entry or not mark or not signal.entry_price:
            return None
        tgt_f = (signal.target_price - signal.entry_price) / signal.entry_price
        stp_f = (signal.stop_loss - signal.entry_price) / signal.entry_price
        if signal.target_price > signal.entry_price:  # long design
            if mark >= entry * (1 + tgt_f):
                return True
            if mark <= entry * (1 + stp_f):
                return False
        else:  # short design
            if mark <= entry * (1 + tgt_f):
                return True
            if mark >= entry * (1 + stp_f):
                return False
        return None

    # === REAL EXECUTION (relay graft, 2026-10-19) ===================
    # The 2025 engine's execution tail was simulated (store + log).
    # These two methods give it a real testnet execution core on the
    # signing relay - the same pattern as the swarm/continuous
    # executors: live-ticker sizing, conflict guard, margin backoff,
    # allocation-governed slice/cap, ledger-recorded closes.
    def _real_open(self, signal) -> None:
        # TF STUDY (2026-10-21, corrected to Princewill's law):
        # a loss triggers STUDY, never a block. The restoration-era
        # allowance judged each timeframe by its last-40 ledger
        # closes and silently refused real opens below -0.005 -
        # a gate, however soft, and one fed ~99% by paper closes
        # whose booking semantics changed repeatedly across the
        # restoration, so its windows contradict each other by era.
        # It had M1 - the primary station, the only one with a
        # positive REAL record - dark on paper noise. The study
        # remains (per-TF expectancy measured and logged, feeding
        # the same learning loop as everything else); the block
        # is gone. Risk lives where the design put it: the tight
        # stop, the 5-minute timeout, the slice, the allocator's
        # mode.
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
                        if _r.get('being') == 'master' and _r.get('real'):
                            _tf = (_r.get('meta') or {}).get('tf')
                            if _tf:
                                _acc[_tf].append(float(_r.get('pnl') or 0))
                for _tf, _ps in sorted(_acc.items()):
                    if _ps:
                        self.logger.info(
                            f'TF STUDY {_tf}: real n={len(_ps)} '
                            f'exp {sum(_ps) / len(_ps):+.4f} '
                            f'(study only - never a block)')
        except Exception:
            pass
        import time as _t
        # Bidirectional (design): the monitor's long/short
        # branches are the engine's original shape; shorts open
        # through the sell-open arm and close buy-reduce.
        _is_short = signal.target_price < signal.entry_price
        _sb = getattr(self, '_sym_backoff', None)
        if _sb is None:
            _sb = self._sym_backoff = {}
        if _sb.get(signal.symbol, 0) > _t.time():
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
            # Execution-frame sizing v2 (2026-10-21): quantities
            # are validated against the venue's lot specs, but
            # the specs are near-static and WAF-expensive to read
            # per signal - the whole fleet egresses as one IP and
            # clustered market-data reads draw 403s while quiet
            # probes pass. So the specs live in a DISK cache
            # (/app/runtime/venue_instruments.json) refreshed by a
            # single budgeted full-list read (at most one attempt
            # per 10 min process-wide), and the sizing price is
            # the signal's own analysis price - entry truth
            # re-anchors to the exchange avgPrice after the fill,
            # as designed. ZERO venue reads in the common path.
            # Unknown spec: quantize 3dp; the per-symbol backoff
            # absorbs a venue rejection.
            _specs = getattr(self, '_spec_mem', None)
            if _specs is None:
                _specs = self._spec_mem = {}
                try:
                    import json as _sj
                    _disk = _sj.load(open(
                        '/app/runtime/venue_instruments.json'))
                    for _k, _v in (_disk or {}).items():
                        _specs[_k] = (float(_v[0]), float(_v[1]))
                    if _specs:
                        self._listed = set(_specs.keys())
                except Exception:
                    pass
            if (not _specs or _t.time() - getattr(
                    self, '_spec_refresh_ts', 0) > 600):
                self._spec_refresh_ts = _t.time()
                try:
                    _ii = tn._req(
                        'GET', '/v5/market/instruments-info',
                        {'category': 'linear', 'limit': 1000})
                    _new = {}
                    for _i in (_ii.get('list') or []):
                        _lot = _i.get('lotSizeFilter') or {}
                        if _i.get('symbol'):
                            _new[_i['symbol']] = (
                                float(_lot.get('minOrderQty') or 0),
                                float(_lot.get('qtyStep') or 0))
                    if _new:
                        _specs.update(_new)
                        self._listed = set(_new.keys())
                        import json as _sj
                        with open(
                                '/app/runtime/venue_instruments'
                                '.json', 'w') as _f:
                            _sj.dump({k: list(v) for k, v
                                      in _new.items()}, _f)
                except Exception:
                    pass
            _listed = getattr(self, '_listed', None)
            if _listed is not None and raw not in _listed:
                return  # the venue does not list this symbol
            _min_qty, _step = _specs.get(raw, (0.0, 0.0))
            price = float(signal.entry_price or 0)
            if not price:
                return
            slice_usd = float(a.get('slice_usd', 12.0))
            qty = slice_usd / float(price)
            qty = quantize(qty, _step) if _step else round(qty, 3)
            if _min_qty and qty < _min_qty:
                if _min_qty * float(price) <= slice_usd * 1.6:
                    qty = _min_qty  # bump to the venue minimum
                else:
                    self.logger.info(
                        f'real open {raw}: venue min {_min_qty} x '
                        f'{price} exceeds slice {slice_usd} - skip')
                    return  # venue minimum exceeds the slice
            if not qty or qty <= 0 or qty * float(price) < 5.5:
                return
            try:
                tn.set_leverage(raw, 10)
            except Exception:
                pass
            # MAKER-FIRST ROUTING (2026-10-21): the exchange
            # record showed ~$0.02/round-trip of spread + taker
            # fees eating the fleet; the maker-first orchestrator
            # was the only arm beating that friction. Post at the
            # touch for a 6s fuse - a fill (or a standing partial)
            # is the entry - else ONE market fallback.
            res = None
            try:
                from testnet_client import maker_open
                _mk = maker_open(tn, raw, _is_short, qty, fuse_s=6)
            except Exception:
                _mk = None
            if _mk:
                res = {'orderId': _mk['orderId']}
                qty = _mk['filled_qty']
                self.logger.info(
                    f'REAL scalp maker fill {raw} qty {qty} '
                    f'@ {_mk.get("avg_price")}')
            else:
                res = (tn.create_market_sell_open(raw, qty_str(qty))
                       if _is_short else
                       tn.create_market_buy(raw, qty_str(qty)))
            if isinstance(res, dict) and res.get('orderId'):
                signal.real_qty = qty
                signal.real_entry = float(price)
                # Entry truth: the exchange avgPrice is the real
                # fill; the sizing ticker is a mainnet quote.
                for _ in range(3):
                    _pp = self._testnet_pos(raw)
                    if _pp and float(_pp.get('avgPrice') or 0) > 0:
                        signal.real_entry = float(_pp['avgPrice'])
                        break
                    time.sleep(1)
                self.logger.info(
                    f"REAL scalp {'sell' if _is_short else 'buy'} {raw} qty {qty} @ {price} "
                    f"(strat {signal.strategy} conf {signal.confidence:.2f})")
                self._reg_put(raw, signal)
            else:
                self.logger.warning(f"real open rejected {raw}: {res}")
                self._sym_backoff[signal.symbol] = _t.time() + 120
        except Exception as e:
            _sb2 = getattr(self, '_sym_backoff', None)
            if _sb2 is None:
                _sb2 = self._sym_backoff = {}
            _sb2[signal.symbol] = _t.time() + 120
            self.logger.warning(f"real open {signal.symbol}: {e}")

    _REG_PATH = '/app/runtime/master_positions.json'

    def _reg_read(self):
        try:
            import json as _j
            return _j.load(open(self._REG_PATH))
        except Exception:
            return {}

    def _reg_write(self, reg):
        try:
            import json as _j
            with open(self._REG_PATH, 'w') as _f:
                _j.dump(reg, _f)
        except Exception:
            pass

    def _reg_put(self, raw, signal):
        reg = self._reg_read()
        reg[raw] = {'qty': float(getattr(signal, 'real_qty', 0) or 0),
                    'entry': float(getattr(signal, 'real_entry', 0) or 0),
                    'tf': signal.timeframe,
                    'strat': signal.strategy, 'ts': time.time()}
        self._reg_write(reg)

    def _reg_pop(self, raw):
        reg = self._reg_read()
        if raw in reg:
            del reg[raw]
            self._reg_write(reg)

    def _rehydrate_real(self):
        """Boot recovery (2026-10-21): real positions lived only
        on in-memory signal objects - a restart orphaned live
        scalps, the zoo adopted them into its own book, and
        master booked ZERO real closes while its opens fired
        (the real count froze at 171 across two restarts). The
        registry persists them now; the exchange verifies them;
        survivors re-enter the monitor with the design geometry
        (10-pip target/stop around the exchange avgPrice, a
        fresh 300s budget, TF/strategy restored from the
        registry)."""
        try:
            reg = self._reg_read()
            if not reg:
                return
            live = {}
            for _p in self._tn_client().positions():
                live[_p.get('symbol')] = _p
            for raw, info in list(reg.items()):
                _p = live.get(raw)
                if not _p or float(_p.get('size') or 0) <= 0:
                    del reg[raw]
                    continue
                # Already tracked in this process: never spawn a
                # duplicate tracker for the same real position.
                if any(getattr(_s, 'real_qty', None)
                       and _s.symbol.split('/')[0] + 'USDT' == raw
                       for _s in self.active_positions.values()):
                    continue
                entry = float(_p.get('avgPrice')
                              or info.get('entry') or 0)
                if entry <= 0:
                    continue
                _short = (_p.get('side') == 'Sell')
                # Geometry: the design's own fractions (25bp
                # target / 50bp stop since the 2026-10-23
                # denomination fix) around the EXCHANGE entry -
                # the old hardcoded 10bp target sat inside the
                # round-trip fee, so a 'winning' rehydrated trade
                # still booked a loss.
                _tgt_f = float(getattr(self, 'MICRO_PIP_TARGET',
                                       25.0)) / 10000.0
                _stp_f = float(getattr(self, 'TIGHT_STOP_LOSS',
                                       50.0)) / 10000.0
                _sig = ScalpSignal(
                    symbol=raw[:-4] + '/USDT',
                    timeframe=info.get('tf') or 'M1',
                    entry_price=entry,
                    target_price=entry * (1 - _tgt_f if _short
                                          else 1 + _tgt_f),
                    stop_loss=entry * (1 + _stp_f if _short
                                       else 1 - _stp_f),
                    confidence=0.75,
                    profit_pips=float(getattr(self, 'MICRO_PIP_TARGET',
                                              25.0)),
                    risk_reward=(_tgt_f / _stp_f) if _stp_f else 1.0,
                    timestamp=time.time(),
                    strategy=info.get('strat') or 'rehydrated')
                _sig.real_qty = abs(float(_p.get('size') or 0))
                _sig.real_entry = entry
                _pid = (f'{_sig.symbol}_{_sig.timeframe}'
                        f'_rehyd_{int(time.time())}')
                self.active_positions[_pid] = _sig
                self.logger.warning(
                    f'REHYDRATED real scalp {raw} '
                    f'qty {_sig.real_qty} @ {entry} '
                    f'({_sig.timeframe}/{_sig.strategy})')
            self._reg_write(reg)
        except Exception as e:
            self.logger.warning(f'rehydrate: {e}')

    def _real_close(self, signal, exit_price: float) -> bool:
        qty = getattr(signal, 'real_qty', None)
        if not qty:
            return True
        base = signal.symbol.split('/')[0]
        raw = base + 'USDT'
        try:
            from testnet_client import qty_str
            tn = self._tn_client()
            # Attempts throttled per symbol: an unfillable pair is
            # retried calmly by the monitor, not every second.
            _att = getattr(self, '_close_attempts', None)
            if _att is None:
                _att = self._close_attempts = {}
            if time.time() - _att.get(raw, 0) < 30:
                return False
            pos = self._testnet_pos(raw)
            if not pos:
                # Already gone from the exchange (closed
                # elsewhere): nothing to execute or book.
                self.logger.warning(
                    f"REAL scalp close {raw}: no exchange position "
                    f"- closed elsewhere, releasing")
                # Evaporated fill (2026-10-21): when the open was
                # accepted but no position ever materialised (empty
                # testnet book), back the symbol off for the same
                # 120s window order failures use - otherwise the scan
                # re-fires on the unfillable book every few seconds
                # (the DOOD loop: an attempt every ~10s all day).
                _sbk = getattr(self, '_sym_backoff', None)
                if _sbk is None:
                    _sbk = self._sym_backoff = {}
                _sbk[signal.symbol] = time.time() + 120
                signal.real_qty = None
                return True
            before = abs(float(pos.get('size') or 0))
            upnl = float(pos.get('unrealisedPnl') or 0)
            _att[raw] = time.time()
            # Touch close first (2026-10-21): the routing wave's
            # smart_close - the same helper the orchestrator arm
            # uses. A reduce-only limit resting at the touch catches
            # the depth flickers that plain market closes keep
            # missing on these books (the real arm's median hold was
            # ~16 minutes against 8-second paper scalps - exits, not
            # entries, were the velocity killer). The market loop
            # below stays as fallback; the shrink check stays judge.
            try:
                from testnet_client import smart_close
                if smart_close(tn, raw, (pos.get('side') == 'Buy'),
                               qty, wait_s=20):
                    _chk = self._testnet_pos(raw)
                    _left = abs(float((_chk or {}).get('size') or 0))
                    if _left < before * 0.01:
                        self.logger.info(
                            f"REAL scalp close {raw} qty {qty} "
                            f"pnl ${upnl:+.4f} (touch fill, exchange "
                            f"uPnL verified)")
                        try:
                            import being_ledger
                            being_ledger.record_close(
                                'master', signal.symbol, upnl,
                                real=True,
                                meta={'strat': signal.strategy,
                                      'engine': 'scalp',
                                      'tf': signal.timeframe,
                                      'exit': 'touch'})
                        except Exception:
                            pass
                        return True
            except Exception as _e:
                self.logger.warning(f'smart close {raw}: {_e}')
            res = None
            _close_fn = (tn.create_market_buy_reduce
                         if (pos.get('side') == 'Sell')
                         else tn.create_market_sell_reduce)
            for _ in range(3):
                res = _close_fn(raw, qty_str(qty))
                if isinstance(res, dict) and res.get('orderId'):
                    break
            if not (isinstance(res, dict) and res.get('orderId')):
                self.logger.error(f"REAL CLOSE FAILED {raw}: {res} - position may be orphaned, check the exchange")
                return False
            for _ in range(3):
                time.sleep(2)
                pos2 = self._testnet_pos(raw)
                after = abs(float((pos2 or {}).get('size') or 0))
                if after < before * 0.99:
                    # Book the exchange's own P&L (its unrealised
                    # P&L at the moment of closing), not engine
                    # math over mainnet prices.
                    self.logger.info(
                        f"REAL scalp close {raw} qty {qty} "
                        f"pnl ${upnl:+.4f} (exchange uPnL, verified)")
                    try:
                        import being_ledger
                        being_ledger.record_close(
                            'master', signal.symbol, upnl, real=True,
                            meta={'strat': signal.strategy,
                                  'engine': 'scalp',
                                  'tf': signal.timeframe})
                    except Exception:
                        pass
                    return True
            self.logger.warning(
                f"REAL scalp close {raw}: order accepted but "
                f"position unchanged (unfilled); not booking")
            return False
        except Exception as e:
            self.logger.error(f"real close {signal.symbol}: {e}")
            return False

    async def _manage_risk(self) -> None:
        """Manage scalping risk"""
        while True:
            try:
                # Check daily loss limits
                if self.daily_profit < -50:  # $50 daily loss limit
                    self.logger.warning("🚨 Daily loss limit reached, stopping scalping")
                    # Stop all active positions. REAL positions are
                    # closed through the verified real close - never
                    # bare-deleted: a bare del orphans the exchange
                    # position (it stays open and untracked while
                    # the registry keeps the profit taker away).
                    # That is how the master's 2026-10-23 real book
                    # was orphaned within minutes of opening.
                    for position_id, _sig in list(self.active_positions.items()):
                        if getattr(_sig, 'real_qty', None):
                            _pos = self._testnet_pos(
                                _sig.symbol.split('/')[0] + 'USDT')
                            _mark = float((_pos or {}).get('markPrice') or 0)
                            await self._close_scalp_position(
                                position_id, _sig,
                                _mark or _sig.entry_price, False)
                        else:
                            del self.active_positions[position_id]

                # Check position limits
                if len(self.active_positions) > self.MAX_POSITIONS:
                    self.logger.warning(
                        f"🚨 Too many positions ({len(self.active_positions)}), closing oldest"
                    )
                    # Evict the oldest PAPER position. A real
                    # position is never evicted by deletion - if
                    # only real positions remain, the oldest is
                    # closed through the verified real close (and
                    # stays tracked if that close cannot fill).
                    _paper = [(pid, sg) for pid, sg
                              in self.active_positions.items()
                              if not getattr(sg, 'real_qty', None)]
                    if _paper:
                        _oldest = min(_paper, key=lambda x: x[1].timestamp)
                        self.logger.warning(
                            f'risk eviction (paper): {_oldest[0]}')
                        del self.active_positions[_oldest[0]]
                    else:
                        _oldest = min(
                            self.active_positions.items(),
                            key=lambda x: x[1].timestamp)
                        _pos = self._testnet_pos(
                            _oldest[1].symbol.split('/')[0] + 'USDT')
                        _mark = float((_pos or {}).get('markPrice') or 0)
                        self.logger.warning(
                            f'risk eviction (real close): {_oldest[0]}')
                        await self._close_scalp_position(
                            _oldest[0], _oldest[1],
                            _mark or _oldest[1].entry_price, False)

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
