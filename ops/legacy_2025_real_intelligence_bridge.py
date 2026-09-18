#!/usr/bin/env python3
"""Runtime compatibility bridge for the October-2025 LeanTrader brain.

This module does not replace the 2025 orchestrator. It reconnects historical
specialists to authentic public market data and authentic runtime outcomes:

* SmartScalpingEngine keeps its historical session/MTF architecture, but its
  old OHLCV placeholder is replaced with real Bybit OHLCV.
* ULTIMATE_EVOLUTION_ENGINE keeps its historical 5-second scalper thread, but
  random BUY/SELL generation and random performance snapshots are replaced by
  market/trade evidence.
* DynamicMarketScanner publishes real snapshots/trending signals into the
  existing CentralDataHub.
* Evolution SQLite state is persisted under the mounted /workspace state.

Private orders are NOT submitted here. The existing UnifiedDecisionEngine ->
ExecutionOrchestrator -> universal router remains the only order path.
"""

from __future__ import annotations

import asyncio
import math
import os
import sqlite3
import statistics
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from src.leantrader.execution.broker_ccxt import BrokerCCXT


FAST_CRYPTO_PAIRS = (
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "DOGE/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "BNB/USDT",
)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _ema(values: Iterable[float], period: int) -> float:
    rows = [float(v) for v in values if _f(v) > 0.0]
    if not rows:
        return 0.0
    period = max(1, int(period))
    alpha = 2.0 / (period + 1.0)
    value = rows[0]
    for row in rows[1:]:
        value = alpha * row + (1.0 - alpha) * value
    return value


def _rsi(values: Iterable[float], period: int = 14) -> float:
    rows = [float(v) for v in values if _f(v) > 0.0]
    if len(rows) < 3:
        return 50.0
    deltas = [b - a for a, b in zip(rows[:-1], rows[1:])]
    sample = deltas[-max(2, min(period, len(deltas))):]
    gains = sum(max(0.0, x) for x in sample) / len(sample)
    losses = sum(max(0.0, -x) for x in sample) / len(sample)
    if losses <= 1e-15:
        return 100.0 if gains > 0.0 else 50.0
    rs = gains / losses
    return 100.0 - (100.0 / (1.0 + rs))


def _returns(closes: List[float]) -> List[float]:
    out: List[float] = []
    for a, b in zip(closes[:-1], closes[1:]):
        if a > 0.0 and b > 0.0:
            out.append((b / a) - 1.0)
    return out


class PublicBybitEvidence:
    """Thread-safe, TTL-cached production public Bybit market evidence."""

    def __init__(self) -> None:
        # paper mode intentionally resolves public reads to the production
        # public endpoint while carrying no private authority.
        self.broker = BrokerCCXT(execution_mode="paper", exchange_id="bybit")
        self.lock = threading.RLock()
        self.cache: Dict[tuple, tuple[float, Any]] = {}

    def _cached(self, key: tuple, ttl: float, loader):
        now = time.time()
        with self.lock:
            row = self.cache.get(key)
            if row and now - row[0] <= ttl:
                return row[1]
        value = loader()
        with self.lock:
            self.cache[key] = (now, value)
        return value

    def ticker(self, symbol: str) -> Dict[str, Any]:
        return dict(
            self._cached(
                ("ticker", symbol),
                2.0,
                lambda: self.broker.fetch_ticker(symbol) or {},
            )
            or {}
        )

    def ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List:
        ttl = 2.0 if timeframe == "1m" else 8.0
        rows = self._cached(
            ("ohlcv", symbol, timeframe, int(limit)),
            ttl,
            lambda: self.broker.fetch_ohlcv(
                symbol, timeframe=timeframe, limit=int(limit)
            )
            or [],
        )
        return list(rows or [])

    def snapshot(self, symbol: str) -> Dict[str, Any]:
        ticker = self.ticker(symbol)
        last = _f(ticker.get("last") or ticker.get("close"))
        return {
            "type": "market_snapshot",
            "symbol": symbol,
            "exchange": "bybit",
            "source": "bybit_public_production",
            "price": last,
            "last": last,
            "bid": _f(ticker.get("bid")),
            "ask": _f(ticker.get("ask")),
            "volume_24h": _f(ticker.get("quoteVolume")),
            "change_24h_pct": _f(ticker.get("percentage")),
            "timestamp": time.time(),
            "authentic_market_data": True,
        }


_FEED = PublicBybitEvidence()
_INSTALLED = False


def _real_timeframe_signal(self, symbol: str, timeframe: str, ohlcv: List):
    """Historical MTF signal shape, now calculated from actual candles."""
    from SMART_SCALPING_ENGINE import TimeframeSignal
    from datetime import datetime

    valid = [
        row for row in (ohlcv or [])
        if isinstance(row, (list, tuple)) and len(row) >= 6 and _f(row[4]) > 0.0
    ]
    if len(valid) < 20:
        signal = TimeframeSignal(
            timeframe=timeframe,
            direction="NEUTRAL",
            strength=0.0,
            indicators={
                "ema_fast": 0.0,
                "ema_slow": 0.0,
                "rsi": 50.0,
                "volume_ratio": 0.0,
                "trend_strength": 0.0,
                "momentum_bps": 0.0,
                "real_market_data": False,
            },
            timestamp=datetime.now(),
        )
        self.signals_cache[symbol][timeframe] = signal
        return signal

    closes = [_f(row[4]) for row in valid]
    volumes = [max(0.0, _f(row[5])) for row in valid]
    ema_fast = _ema(closes[-34:], 5)
    ema_slow = _ema(closes[-55:], 13)
    rsi = _rsi(closes[-30:], 14)
    previous = closes[-4] if len(closes) >= 4 else closes[0]
    momentum = ((closes[-1] / previous) - 1.0) if previous > 0.0 else 0.0
    trend = ((ema_fast / ema_slow) - 1.0) if ema_slow > 0.0 else 0.0
    prior_volume = volumes[-11:-1]
    volume_mean = sum(prior_volume) / len(prior_volume) if prior_volume else 0.0
    volume_ratio = volumes[-1] / volume_mean if volume_mean > 0.0 else 1.0

    # Preserve the old multi-indicator idea, but derive every vote from
    # observed candles rather than fixed placeholder values.
    votes = [
        1.0 if ema_fast > ema_slow else -1.0 if ema_fast < ema_slow else 0.0,
        1.0 if momentum > 0.0 else -1.0 if momentum < 0.0 else 0.0,
        1.0 if rsi > 52.0 else -1.0 if rsi < 48.0 else 0.0,
    ]
    raw = sum(votes)
    direction = "BUY" if raw > 0.0 else "SELL" if raw < 0.0 else "NEUTRAL"

    # Confidence is evidence strength, not a fabricated probability.
    agreement = abs(raw) / len(votes)
    movement = min(1.0, (abs(trend) + abs(momentum)) * 500.0)
    volume_confirmation = min(1.0, max(0.0, volume_ratio - 0.8) / 1.2)
    strength = max(0.0, min(1.0, 0.60 * agreement + 0.25 * movement + 0.15 * volume_confirmation))
    if direction == "NEUTRAL":
        strength = 0.0

    signal = TimeframeSignal(
        timeframe=timeframe,
        direction=direction,
        strength=strength,
        indicators={
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "rsi": rsi,
            "volume_ratio": volume_ratio,
            "trend_strength": abs(trend),
            "momentum_bps": momentum * 10_000.0,
            "last_price": closes[-1],
            "real_market_data": True,
        },
        timestamp=datetime.now(),
    )
    self.signals_cache[symbol][timeframe] = signal
    return signal


async def _real_analyze_all_timeframes(self, symbol: str):
    # The restored CEX lane is Bybit spot. FX engines remain present, but an FX
    # symbol is not fabricated into a crypto market.
    if "/" not in str(symbol) or not str(symbol).upper().endswith("/USDT"):
        self.mtf_analyzer.signals_cache.pop(symbol, None)
        return 0

    count = 0
    for timeframe in self.mtf_analyzer.TIMEFRAMES:
        try:
            rows = await asyncio.to_thread(_FEED.ohlcv, symbol, timeframe, 80)
            if len(rows) < 20:
                continue
            self.mtf_analyzer.analyze_timeframe(symbol, timeframe, rows)
            count += 1
        except Exception:
            continue
    if count < 3:
        self.mtf_analyzer.signals_cache.pop(symbol, None)
    return count


def _real_session_pairs(original):
    def wrapped(session: str):
        rows = list(original(session) or [])
        for symbol in FAST_CRYPTO_PAIRS:
            if symbol not in rows:
                rows.append(symbol)
        return rows
    return wrapped


async def _real_smart_scan(self):
    """Run the historical SmartScalper and annotate only observed evidence."""
    original = getattr(self, "_legacy_real_original_scan_markets", None)
    if original is None:
        return []
    signals = await original()
    for signal in signals or []:
        if not isinstance(signal, dict):
            continue
        symbol = str(signal.get("symbol") or "")
        try:
            snap = await asyncio.to_thread(_FEED.snapshot, symbol)
        except Exception:
            snap = {}
        price = _f(snap.get("price"))
        if price > 0.0:
            signal["price"] = price
        signal["real_market_data"] = bool(price > 0.0)
        signal["market_data_source"] = snap.get("source", "bybit_public_production")
    return signals


async def _real_learning_update_evolution(self, trade_data):
    """Feed authenticated trade outcomes into the existing Evolution instance."""
    evolution = (getattr(self, "ai_systems", {}) or {}).get("evolution")
    if evolution is None or not isinstance(trade_data, dict):
        return

    record = {
        "timestamp": trade_data.get("timestamp") or time.time(),
        "symbol": trade_data.get("symbol"),
        "side": trade_data.get("side"),
        "status": trade_data.get("status"),
        "realized_net_pnl": _f(
            trade_data.get("realized_net_pnl")
            if trade_data.get("realized_net_pnl") is not None
            else trade_data.get("realized_pnl")
        ),
        "fill_source": trade_data.get("fill_source"),
        "execution_mode": trade_data.get("execution_mode"),
        "exchange": trade_data.get("exchange"),
        "evidence": "central_data_hub_trade",
    }

    history = getattr(evolution, "performance_history", None)
    if isinstance(history, list):
        history.append(record)
        del history[:-2000]

    connection = getattr(evolution, "live_bot_connection", None)
    if isinstance(connection, dict):
        feed = connection.setdefault("performance_feed", [])
        feed.append(record)
        del feed[:-2000]
        connection["last_trade_time"] = record["timestamp"]


def _real_evolution_scalping_signals(self):
    """Keep the 2025 5-second scalper thread, remove its RNG signal source."""
    signals = []
    pairs = (
        getattr(self, "active_engines", {})
        .get("scalper_engine", {})
        .get("pairs", [])
    )
    for pair in pairs:
        if pair not in FAST_CRYPTO_PAIRS:
            continue
        try:
            candles = _FEED.ohlcv(pair, "1m", 30)
            if len(candles) < 20:
                continue
            closes = [_f(row[4]) for row in candles if len(row) >= 6 and _f(row[4]) > 0.0]
            volumes = [max(0.0, _f(row[5])) for row in candles if len(row) >= 6 and _f(row[4]) > 0.0]
            if len(closes) < 20:
                continue

            fast = _ema(closes, 5)
            slow = _ema(closes, 13)
            prev = closes[-4]
            momentum = (closes[-1] / prev - 1.0) if prev > 0.0 else 0.0
            rsi = _rsi(closes, 14)
            volume_base = volumes[-11:-1]
            volume_ratio = (
                volumes[-1] / (sum(volume_base) / len(volume_base))
                if volume_base and sum(volume_base) > 0.0
                else 1.0
            )

            trend_sign = 1 if fast > slow else -1 if fast < slow else 0
            momentum_sign = 1 if momentum > 0 else -1 if momentum < 0 else 0
            rsi_sign = 1 if rsi > 52 else -1 if rsi < 48 else 0
            score = trend_sign + momentum_sign + rsi_sign
            if score == 0:
                continue

            agreement = abs(score) / 3.0
            movement = min(1.0, abs(momentum) * 600.0)
            volume_confirm = min(1.0, max(0.0, volume_ratio - 0.8) / 1.2)
            confidence = max(
                0.0,
                min(0.99, 0.60 * agreement + 0.25 * movement + 0.15 * volume_confirm),
            )

            # The historical engine emitted only when it had a candidate.
            # Keep that behavior, but candidate evidence is now observed.
            if confidence < 0.55:
                continue

            ticker = _FEED.ticker(pair)
            price = _f(ticker.get("last") or ticker.get("close")) or closes[-1]
            signals.append(
                {
                    "pair": pair,
                    "action": "BUY" if score > 0 else "SELL",
                    "confidence": confidence,
                    "price": price,
                    "target_profit": 0.006,
                    "take_profit_pct": 0.006,
                    "stop_loss_pct": 0.003,
                    "target_hold_seconds": 60.0,
                    "source_strategy": "2025_evolution_fast_scalper_real_market",
                    "real_market_data": True,
                    "ema_fast": fast,
                    "ema_slow": slow,
                    "rsi": rsi,
                    "momentum_bps": momentum * 10_000.0,
                    "volume_ratio": volume_ratio,
                    "timestamp": time.time(),
                }
            )
        except Exception:
            continue
    return signals


def _real_market_conditions(self):
    rows = []
    for symbol in ("BTC/USDT", "ETH/USDT"):
        try:
            candles = _FEED.ohlcv(symbol, "1m", 61)
            closes = [_f(row[4]) for row in candles if len(row) >= 6 and _f(row[4]) > 0.0]
            volumes = [max(0.0, _f(row[5])) for row in candles if len(row) >= 6 and _f(row[4]) > 0.0]
            if len(closes) < 20:
                continue
            ret = _returns(closes)
            rows.append(
                {
                    "volatility": statistics.pstdev(ret) if len(ret) >= 2 else 0.0,
                    "momentum": (closes[-1] / closes[-6] - 1.0) if len(closes) >= 6 else 0.0,
                    "trend": (_ema(closes, 5) / _ema(closes, 21) - 1.0) if _ema(closes, 21) > 0.0 else 0.0,
                    "volume": volumes[-1] / (sum(volumes[-11:-1]) / max(1, len(volumes[-11:-1]))) if volumes[-11:-1] and sum(volumes[-11:-1]) > 0.0 else 1.0,
                }
            )
        except Exception:
            continue

    if not rows:
        return {
            "volatility": 0.0,
            "volume": 0.0,
            "momentum": 0.0,
            "trend": 0.0,
            "market_sentiment": 0.0,
            "evidence": "unavailable",
        }

    def avg(key: str) -> float:
        return sum(_f(row.get(key)) for row in rows) / len(rows)

    momentum = avg("momentum")
    trend = avg("trend")
    # This is a price-action direction measure, not external social sentiment.
    directional = max(-1.0, min(1.0, (momentum + trend) * 100.0))
    return {
        "volatility": avg("volatility"),
        "volume": avg("volume"),
        "momentum": momentum,
        "trend": trend,
        "market_sentiment": directional,
        "evidence": "bybit_public_production_ohlcv",
    }


def _real_bot_performance(self):
    hub = getattr(self, "data_hub", None)
    trades = list(getattr(hub, "recent_trades", []) or []) if hub is not None else []
    closed = []
    for row in trades:
        if not isinstance(row, dict):
            continue
        value = row.get("realized_pnl")
        if value is None:
            value = row.get("realized_net_pnl")
        if value is None:
            continue
        closed.append(_f(value))

    if not closed:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "realized_net_pnl": 0.0,
            "evidence": "no_authenticated_closes_yet",
        }

    wins = [x for x in closed if x > 0.0]
    losses = [x for x in closed if x < 0.0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    mean = sum(closed) / len(closed)
    stdev = statistics.pstdev(closed) if len(closed) >= 2 else 0.0

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for pnl in closed:
        equity += pnl
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return {
        "total_trades": len(closed),
        "win_rate": len(wins) / len(closed),
        "profit_factor": gross_profit / gross_loss if gross_loss > 0.0 else (float("inf") if gross_profit > 0.0 else 0.0),
        "sharpe_ratio": mean / stdev if stdev > 0.0 else 0.0,
        "max_drawdown": max_dd,
        "realized_net_pnl": sum(closed),
        "evidence": "central_data_hub_realized_trade_outcomes",
    }


def _real_evolution_database(self):
    path = Path(os.getenv("EVOLUTION_DB_PATH", "/workspace/evolution_engine.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    self.evo_db = sqlite3.connect(str(path), check_same_thread=False)
    cursor = self.evo_db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS model_evolution (
            id INTEGER PRIMARY KEY,
            generation INTEGER,
            model_type TEXT,
            performance_score REAL,
            spawn_time TIMESTAMP,
            parent_models TEXT,
            market_conditions TEXT,
            evolution_data TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pattern_memory (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            market_condition TEXT,
            success_rate REAL,
            profit_factor REAL,
            last_seen TIMESTAMP,
            frequency INTEGER
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_evolution (
            id INTEGER PRIMARY KEY,
            strategy_name TEXT,
            generation INTEGER,
            performance REAL,
            market_adaptation REAL,
            evolution_stage TEXT,
            next_evolution TEXT
        )
        """
    )
    self.evo_db.commit()
    if self.evo_db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
        raise RuntimeError("evolution database quick_check failed")
    print(f"✅ Evolution database initialized: {path}")


def _real_connect_to_runtime(self):
    self.live_bot_connection = {
        "status": "central_data_hub_connected" if getattr(self, "data_hub", None) is not None else "market_data_only",
        "last_trade_time": None,
        "learning_data": [],
        "performance_feed": [],
    }
    print("✅ Evolution engine connected to LeanTrader evidence fabric")


def _real_initialize_ai_clients(self):
    self.anthropic_client = None
    self.openai_client = None

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if anthropic_key:
        try:
            import anthropic
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            print("✅ Anthropic intelligence provider configured")
        except Exception as exc:
            print(f"⚠️ Anthropic provider unavailable: {type(exc).__name__}")
    else:
        print("ℹ️ Anthropic intelligence provider not configured")

    if openai_key:
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=openai_key)
            print("✅ OpenAI intelligence provider configured")
        except Exception as exc:
            print(f"⚠️ OpenAI provider unavailable: {type(exc).__name__}")
    else:
        print("ℹ️ OpenAI intelligence provider not configured")


async def _real_dynamic_scanning(self):
    interval = max(15.0, _f(os.getenv("DYNAMIC_SCAN_SECONDS", "60"), 60.0))
    while True:
        try:
            await self.scan_all_exchanges()
            self.scan_count += 1
            from datetime import datetime
            self.last_scan = datetime.now()

            actual = self._extract_ccxt_exchanges()
            if not actual:
                actual = await self._create_fallback_exchanges()

            # Publish a bounded market snapshot set into the historical hub.
            for exchange_name, exchange in list(actual.items())[:2]:
                try:
                    tickers = await exchange.fetch_tickers()
                except Exception:
                    continue
                candidates = []
                for symbol, ticker in (tickers or {}).items():
                    if "/USDT" not in symbol or ":" in symbol:
                        continue
                    volume = _f((ticker or {}).get("quoteVolume"))
                    candidates.append((volume, symbol, ticker))
                candidates.sort(reverse=True, key=lambda x: x[0])
                for volume, symbol, ticker in candidates[:40]:
                    last = _f((ticker or {}).get("last") or (ticker or {}).get("close"))
                    if last <= 0.0:
                        continue
                    await self.data_hub.publish_market_data(
                        {
                            "type": "market_snapshot",
                            "symbol": symbol,
                            "exchange": exchange_name,
                            "source": "dynamic_market_scanner_real_tickers",
                            "price": last,
                            "last": last,
                            "bid": _f((ticker or {}).get("bid")),
                            "ask": _f((ticker or {}).get("ask")),
                            "volume_24h": volume,
                            "change_24h_pct": _f((ticker or {}).get("percentage")),
                            "timestamp": time.time(),
                            "authentic_market_data": True,
                        }
                    )
                break

            await self.publish_trending_signals()
            print(
                "REAL_MARKET_SCAN "
                f"active_pairs={len(self.active_pairs)} "
                f"trending={len(self.trending_pairs)} "
                f"hub_market={len(getattr(self.data_hub, 'recent_market_data', []))}"
            )
            await asyncio.sleep(interval)
        except Exception as exc:
            print(f"REAL_MARKET_SCAN_ERROR {type(exc).__name__}: {exc}")
            await asyncio.sleep(min(60.0, interval))


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import SMART_SCALPING_ENGINE as smart
    import EVOLUTION_ENGINE as evolution
    import DYNAMIC_MARKET_SCANNER as dynamic

    # Smart scalper: keep class/topology/confluence/session tracker, replace the
    # two placeholder data-analysis functions only.
    smart.MultiTimeframeAnalyzer.analyze_timeframe = _real_timeframe_signal
    smart.SmartScalpingEngine.analyze_all_timeframes = _real_analyze_all_timeframes
    original_pairs = smart.MarketSession.get_optimal_pairs
    smart.MarketSession.get_optimal_pairs = staticmethod(_real_session_pairs(original_pairs))
    if not hasattr(smart.SmartScalpingEngine, "_legacy_real_original_scan_markets"):
        smart.SmartScalpingEngine._legacy_real_original_scan_markets = smart.SmartScalpingEngine.scan_markets
        smart.SmartScalpingEngine.scan_markets = _real_smart_scan

    # Evolution: keep the historical threads/cadence/model arsenal, but remove
    # RNG as trading/performance evidence.
    evolution.ULTIMATE_EVOLUTION_ENGINE.generate_scalping_signals = _real_evolution_scalping_signals
    evolution.ULTIMATE_EVOLUTION_ENGINE.get_current_market_conditions = _real_market_conditions
    evolution.ULTIMATE_EVOLUTION_ENGINE.get_bot_performance = _real_bot_performance
    evolution.ULTIMATE_EVOLUTION_ENGINE.init_evolution_database = _real_evolution_database
    evolution.ULTIMATE_EVOLUTION_ENGINE.connect_to_live_bot = _real_connect_to_runtime
    evolution.ULTIMATE_EVOLUTION_ENGINE.initialize_ai_clients = _real_initialize_ai_clients

    # Dynamic scanner: existing scanning logic remains; its loop now also feeds
    # the CentralDataHub and emits its already-defined trending signals.
    dynamic.DynamicMarketScanner.run_continuous_scanning = _real_dynamic_scanning

    # LearningOrchestrator already exists in the 2025 topology; replace only
    # its no-op Evolution handoff with a real evidence handoff.
    try:
        import COMPLETE_UNIFIED_ORCHESTRATOR as unified
        unified.LearningOrchestrator.update_evolution = _real_learning_update_evolution
    except Exception:
        pass

    _INSTALLED = True
    print("LEGACY_2025_REAL_INTELLIGENCE_BRIDGE_INSTALLED")


def smoke_real_market() -> Dict[str, Any]:
    """Read-only proof used by the activation script before any cutover."""
    ticker = _FEED.ticker("BTC/USDT")
    candles = _FEED.ohlcv("BTC/USDT", "1m", 30)
    last = _f(ticker.get("last") or ticker.get("close"))
    if last <= 0.0 or len(candles) < 20:
        raise RuntimeError("real Bybit market data unavailable")
    return {
        "symbol": "BTC/USDT",
        "last": last,
        "candles": len(candles),
        "source": "bybit_public_production",
    }
