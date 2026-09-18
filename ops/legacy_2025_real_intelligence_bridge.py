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

    raw_volatility = avg("volatility")
    raw_momentum = avg("momentum")
    raw_trend = avg("trend")
    directional = max(-1.0, min(1.0, (raw_momentum + raw_trend) * 100.0))
    return {
        "volatility": max(0.0, min(1.0, raw_volatility * 1000.0)),
        "volume": max(0.0, min(2.0, avg("volume"))),
        "momentum": max(0.0, min(1.0, 0.5 + raw_momentum * 100.0)),
        "trend": max(-1.0, min(1.0, raw_trend * 100.0)),
        "market_sentiment": directional,
        "raw_volatility": raw_volatility,
        "raw_momentum": raw_momentum,
        "raw_trend": raw_trend,
        "evidence": "bybit_public_production_ohlcv",
    }


def _real_generate_training_data(self, pair):
    """Return real public OHLCV-derived features; never synthesize training rows."""
    candles = _FEED.ohlcv(pair, "1m", 160)
    valid = [
        row for row in candles
        if isinstance(row, (list, tuple)) and len(row) >= 6 and _f(row[4]) > 0.0
    ]
    closes = [_f(row[4]) for row in valid]
    volumes = [max(0.0, _f(row[5])) for row in valid]
    features = []
    targets = []
    for idx in range(21, len(closes) - 1):
        window = closes[: idx + 1]
        vol_window = volumes[max(0, idx - 10):idx]
        vol_mean = sum(vol_window) / len(vol_window) if vol_window else 0.0
        features.append(
            [
                (closes[idx] / closes[idx - 1] - 1.0),
                (closes[idx] / closes[idx - 3] - 1.0),
                (_ema(window[-30:], 5) / _ema(window[-40:], 13) - 1.0)
                if _ema(window[-40:], 13) > 0.0
                else 0.0,
                (_rsi(window[-30:], 14) - 50.0) / 50.0,
                volumes[idx] / vol_mean if vol_mean > 0.0 else 1.0,
            ]
        )
        targets.append(closes[idx + 1] / closes[idx] - 1.0)

    return {
        "pair": pair,
        "price_data": closes,
        "volume_data": volumes,
        "features": features,
        "targets": targets,
        "evidence": "bybit_public_production_ohlcv",
    }


def _real_train_on_testnet_data(self):
    """Train compatible prediction models only on observed market rows."""
    import numpy as np

    rows = []
    targets = []
    for pair in list(getattr(self, "crypto_pairs", FAST_CRYPTO_PAIRS))[:10]:
        try:
            dataset = self.generate_testnet_data(pair)
            rows.extend(dataset.get("features") or [])
            targets.extend(dataset.get("targets") or [])
        except Exception:
            continue

    if len(rows) < 40 or len(targets) != len(rows):
        print(f"🧪 Real-data training deferred: {len(rows)} samples")
        return

    X = np.asarray(rows, dtype=float)
    y = np.asarray(targets, dtype=float)
    trained = 0
    for model_name, model in getattr(self, "prediction_models", {}).items():
        if not hasattr(model, "fit"):
            continue
        try:
            model.fit(X, y)
            trained += 1
        except Exception:
            continue
    print(
        f"✅ Real-data Evolution training completed: "
        f"samples={len(rows)} models={trained}"
    )


def _real_validate_testnet_strategies(self):
    """Validation summary comes from actual completed trade outcomes."""
    perf = self.get_bot_performance()
    print(
        "🧪 Strategy validation evidence: "
        f"completed={perf.get('total_trades', 0)} "
        f"win_rate={_f(perf.get('win_rate')):.2%} "
        f"realized_net={_f(perf.get('realized_net_pnl')):.8f}"
    )
    return perf


def _performance_score(perf: Dict[str, Any]) -> float:
    trades = int(_f(perf.get("total_trades")))
    if trades <= 0:
        return 0.0
    win = max(0.0, min(1.0, _f(perf.get("win_rate"))))
    pf = _f(perf.get("profit_factor"))
    pf_component = 1.0 if math.isinf(pf) else max(0.0, min(1.0, pf / 2.0))
    pnl = _f(perf.get("realized_net_pnl"))
    pnl_component = 1.0 if pnl > 0.0 else 0.0
    return max(0.0, min(1.0, 0.55 * win + 0.30 * pf_component + 0.15 * pnl_component))


def _real_evolve_existing_models(self):
    """Update model score from realized outcomes instead of random increments."""
    self.evolution_cycle = _f(getattr(self, "evolution_cycle", 0.0)) + 1.0
    perf = self.get_bot_performance()
    score = _performance_score(perf)

    if int(_f(perf.get("total_trades"))) > 0:
        for model_dict_name in (
            "technical_models",
            "sentiment_models",
            "arbitrage_models",
            "volatility_models",
            "momentum_models",
            "volume_models",
            "risk_models",
            "forex_models",
            "stock_models",
            "commodity_models",
        ):
            model_dict = getattr(self, model_dict_name, {}) or {}
            for model_data in model_dict.values():
                if isinstance(model_data, dict) and "performance" in model_data:
                    previous = _f(model_data.get("performance"))
                    model_data["performance"] = 0.85 * previous + 0.15 * score
    print(
        f"🔄 Evidence Evolution cycle {self.evolution_cycle:.0f} "
        f"score={score:.4f} completed_trades={int(_f(perf.get('total_trades')))}"
    )


def _real_update_model_performance(self):
    perf = self.get_bot_performance()
    score = _performance_score(perf)
    if int(_f(perf.get("total_trades"))) <= 0:
        print("ℹ️ Model performance unchanged: no authenticated closes yet")
        return
    for model_dict_name in (
        "technical_models",
        "sentiment_models",
        "arbitrage_models",
        "volatility_models",
        "momentum_models",
        "volume_models",
        "risk_models",
        "forex_models",
        "stock_models",
        "commodity_models",
    ):
        for model_data in (getattr(self, model_dict_name, {}) or {}).values():
            if isinstance(model_data, dict) and "performance" in model_data:
                previous = _f(model_data.get("performance"))
                model_data["performance"] = 0.90 * previous + 0.10 * score
    print(f"✅ Model performance updated from realized evidence: {score:.4f}")


def _real_pattern_analysis(self):
    hub = getattr(self, "data_hub", None)
    trades = list(getattr(hub, "recent_trades", []) or []) if hub is not None else []
    by_source: Dict[str, Dict[str, float]] = {}
    for trade in trades:
        if not isinstance(trade, dict):
            continue
        pnl_value = trade.get("realized_net_pnl")
        if pnl_value is None:
            pnl_value = trade.get("realized_pnl")
        if pnl_value is None:
            continue
        source = str(trade.get("source_engine") or trade.get("strategy") or "unknown")
        row = by_source.setdefault(source, {"trades": 0.0, "net": 0.0, "wins": 0.0})
        pnl = _f(pnl_value)
        row["trades"] += 1.0
        row["net"] += pnl
        if pnl > 0.0:
            row["wins"] += 1.0
    return {
        "source_performance": by_source,
        "completed_outcomes": int(sum(x["trades"] for x in by_source.values())),
        "evidence": "central_data_hub_realized_trade_outcomes",
    }


def _no_synthetic_placeholder(*_args, **_kwargs):
    """Historical placeholder lane stays present but emits no fabricated event."""
    return []


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


async def _real_swarm_market_data(self, symbol: str, timeframe: str):
    """Supply every historical SwarmAgent with the same authentic OHLCV fabric."""
    import pandas as pd

    if "/" not in str(symbol) or not str(symbol).upper().endswith("/USDT"):
        return None

    supported = {"1m", "5m", "15m", "30m", "1h", "4h"}
    tf = timeframe if timeframe in supported else "1m"
    try:
        rows = await asyncio.to_thread(_FEED.ohlcv, symbol, tf, 100)
    except Exception:
        return None

    valid = [
        row for row in rows
        if isinstance(row, (list, tuple)) and len(row) >= 6 and _f(row[4]) > 0.0
    ]
    if len(valid) < 50:
        return None

    return pd.DataFrame(
        {
            "timestamp": [_f(row[0]) / 1000.0 for row in valid],
            "open": [_f(row[1]) for row in valid],
            "high": [_f(row[2]) for row in valid],
            "low": [_f(row[3]) for row in valid],
            "close": [_f(row[4]) for row in valid],
            "volume": [_f(row[5]) for row in valid],
        }
    )


async def _real_swarm_collective_decision(self, signal=None):
    """Fast on-demand 2025 swarm consensus over real data for current signal."""
    source = signal if isinstance(signal, dict) else {}
    data = source.get("data") if isinstance(source.get("data"), dict) else {}
    symbol = str(
        source.get("symbol")
        or data.get("symbol")
        or data.get("pair")
        or "BTC/USDT"
    )
    if "/" not in symbol or not symbol.upper().endswith("/USDT"):
        return {
            "action": "hold",
            "confidence": 0.0,
            "agent_count": 0,
            "symbol": symbol,
            "real_market_data": False,
        }

    now = time.time()
    cache = getattr(self, "_real_consensus_cache", None)
    if not isinstance(cache, dict):
        cache = {}
        self._real_consensus_cache = cache
    cached = cache.get(symbol)
    if cached and now - _f(cached.get("timestamp")) <= 2.0:
        return dict(cached["decision"])

    frame = await _real_swarm_market_data(None, symbol, "1m")
    if frame is None:
        return {
            "action": "hold",
            "confidence": 0.0,
            "agent_count": 0,
            "symbol": symbol,
            "real_market_data": False,
        }

    # Historical agents of one specialization run identical deterministic
    # analysis on the same frame. Evaluate one representative per specialty
    # and retain all 100 agents as vote weights; this is mathematically
    # equivalent without serializing the fast decision path.
    groups: Dict[str, List[Any]] = {}
    for agent in getattr(self, "agents", []):
        groups.setdefault(str(getattr(agent, "specialization", "general")), []).append(agent)

    weighted_votes = []
    for specialization, agents in groups.items():
        if not agents:
            continue
        agent = agents[0]
        try:
            if specialization == "scalping":
                result = await agent._analyze_scalping(frame, symbol, "1m")
            elif specialization == "arbitrage":
                result = await agent._analyze_arbitrage(frame, symbol, "1m")
            elif specialization == "trend":
                result = await agent._analyze_trend(frame, symbol, "1m")
            elif specialization == "black_swan":
                result = await agent._analyze_black_swan(frame, symbol, "1m")
            else:
                result = await agent._analyze_general(frame, symbol, "1m")
        except Exception:
            result = None
        if result is not None and getattr(result, "signal_type", None) in {"buy", "sell"}:
            weighted_votes.append((result, len(agents)))

    buy_count = sum(weight for row, weight in weighted_votes if row.signal_type == "buy")
    sell_count = sum(weight for row, weight in weighted_votes if row.signal_type == "sell")
    buy_weight = sum(
        _f(row.confidence) * weight
        for row, weight in weighted_votes
        if row.signal_type == "buy"
    )
    sell_weight = sum(
        _f(row.confidence) * weight
        for row, weight in weighted_votes
        if row.signal_type == "sell"
    )

    if buy_weight <= 0.0 and sell_weight <= 0.0:
        action = "hold"
        confidence = 0.0
    elif buy_weight > sell_weight:
        action = "buy"
        confidence = buy_weight / max(1, buy_count)
    elif sell_weight > buy_weight:
        action = "sell"
        confidence = sell_weight / max(1, sell_count)
    else:
        action = "hold"
        confidence = 0.0

    decision = {
        "action": action,
        "confidence": max(0.0, min(0.99, confidence)),
        "agent_count": buy_count + sell_count,
        "buy_votes": buy_count,
        "sell_votes": sell_count,
        "symbol": symbol,
        "real_market_data": True,
        "market_data_source": "bybit_public_production",
    }
    cache[symbol] = {"timestamp": now, "decision": dict(decision)}
    return decision


async def _real_swarm_performance_metrics(self):
    """Never assign random PnL/performance to swarm agents."""
    total_agents = len(getattr(self, "agents", []))
    awareness = getattr(self, "collective_awareness", None)
    active_agents = getattr(awareness, "active_agents", 0)
    signals_count = getattr(awareness, "signals_count", 0)
    self.logger.info(
        f"Swarm Performance: {active_agents}/{total_agents} agents active, "
        f"{signals_count} observed signals; synthetic performance disabled"
    )


async def _no_simulated_swarm_trade(self, signal):
    """The swarm contributes intelligence; universal router owns all orders."""
    self.logger.info(
        f"Swarm execution intent delegated to unified controller: "
        f"{getattr(signal, 'signal_type', 'hold')} "
        f"{getattr(signal, 'symbol', 'UNKNOWN')}"
    )
    return None


async def _real_publish_trending_signals(self):
    """Publish real scanner trends with explicit evidence provenance."""
    top_trending = self.get_trending_opportunities(limit=10)
    for trend in top_trending:
        change = _f(trend.get("price_change_pct"))
        signal = {
            "type": "trending",
            "symbol": trend.get("symbol"),
            "side": "buy" if change > 0.0 else "sell",
            "confidence": min(abs(change) / 10.0, 0.95),
            "source": "DynamicScanner",
            "reasoning": (
                f"Observed 24h move {change:+.2f}% with "
                f"{_f(trend.get('volume_24h')):.2f} quote volume"
            ),
            "timestamp": time.time(),
            "real_market_data": True,
            "market_data_source": "dynamic_market_scanner_real_tickers",
            "exchange": trend.get("exchange"),
        }
        await self.data_hub.publish_signal(signal)
    if top_trending:
        print(f"REAL_TREND_SIGNALS_PUBLISHED {len(top_trending)}")


async def _real_statistical_arbitrage(self):
    """Preserve the 2025 pairs/z-score strategy, replace its random ratio."""
    import numpy as np

    signals = []
    for asset1, asset2, expected_corr in getattr(self, "pairs", []):
        try:
            t1, t2 = await asyncio.gather(
                asyncio.to_thread(_FEED.ticker, asset1),
                asyncio.to_thread(_FEED.ticker, asset2),
            )
            p1 = _f((t1 or {}).get("last") or (t1 or {}).get("close"))
            p2 = _f((t2 or {}).get("last") or (t2 or {}).get("close"))
            if p1 <= 0.0 or p2 <= 0.0:
                continue

            ratio = p1 / p2
            key = (asset1, asset2, expected_corr)
            history = self.ratio_history[key]
            ratios = list(history)

            if len(ratios) >= 20:
                mean_ratio = float(np.mean(ratios))
                std_ratio = float(np.std(ratios))
                if std_ratio > 0.0:
                    z_score = (ratio - mean_ratio) / std_ratio
                    if z_score > 2.0:
                        signals.append(
                            {
                                "type": "stat_arb",
                                "symbol": asset1,
                                "side": "sell",
                                "confidence": min(0.90, 0.70 + abs(z_score) * 0.05),
                                "reasoning": (
                                    f"Real pairs ratio {asset1}/{asset2} "
                                    f"{z_score:.2f} std devs above observed mean"
                                ),
                                "strategy": "Statistical Arbitrage",
                                "z_score": z_score,
                                "observed_ratio": ratio,
                                "asset1_price": p1,
                                "asset2_price": p2,
                                "expected_corr": expected_corr,
                                "real_market_data": True,
                                "market_data_source": "bybit_public_production",
                                "timestamp": time.time(),
                            }
                        )
                    elif z_score < -2.0:
                        signals.append(
                            {
                                "type": "stat_arb",
                                "symbol": asset1,
                                "side": "buy",
                                "confidence": min(0.90, 0.70 + abs(z_score) * 0.05),
                                "reasoning": (
                                    f"Real pairs ratio {asset1}/{asset2} "
                                    f"{z_score:.2f} std devs below observed mean"
                                ),
                                "strategy": "Statistical Arbitrage",
                                "z_score": z_score,
                                "observed_ratio": ratio,
                                "asset1_price": p1,
                                "asset2_price": p2,
                                "expected_corr": expected_corr,
                                "real_market_data": True,
                                "market_data_source": "bybit_public_production",
                                "timestamp": time.time(),
                            }
                        )

            history.append(ratio)
        except Exception:
            continue
    return signals


async def _real_ultra_current_price(self, symbol: str) -> float:
    """Give the historical UltraScalping monitor a real observed price."""
    try:
        ticker = await asyncio.to_thread(_FEED.ticker, symbol)
        return _f((ticker or {}).get("last") or (ticker or {}).get("close"))
    except Exception:
        return 0.0


async def _no_simulated_arbitrage_execution(self, *_args, **_kwargs) -> bool:
    """Never book the old simulated 95%-success arbitrage as real PnL."""
    return False


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
    evolution.ULTIMATE_EVOLUTION_ENGINE.generate_testnet_data = _real_generate_training_data
    evolution.ULTIMATE_EVOLUTION_ENGINE.train_on_testnet_data = _real_train_on_testnet_data
    evolution.ULTIMATE_EVOLUTION_ENGINE.validate_testnet_strategies = _real_validate_testnet_strategies
    evolution.ULTIMATE_EVOLUTION_ENGINE.evolve_existing_models = _real_evolve_existing_models
    evolution.ULTIMATE_EVOLUTION_ENGINE.update_model_performance = _real_update_model_performance
    evolution.ULTIMATE_EVOLUTION_ENGINE.analyze_trading_patterns = _real_pattern_analysis
    evolution.ULTIMATE_EVOLUTION_ENGINE.scan_for_moon_gems = _no_synthetic_placeholder
    evolution.ULTIMATE_EVOLUTION_ENGINE.find_arbitrage_opportunities = _no_synthetic_placeholder
    evolution.ULTIMATE_EVOLUTION_ENGINE.execute_fx_trades = _no_synthetic_placeholder
    evolution.ULTIMATE_EVOLUTION_ENGINE.init_evolution_database = _real_evolution_database
    evolution.ULTIMATE_EVOLUTION_ENGINE.connect_to_live_bot = _real_connect_to_runtime
    evolution.ULTIMATE_EVOLUTION_ENGINE.initialize_ai_clients = _real_initialize_ai_clients

    # Dynamic scanner: existing scanning logic remains; its loop now also feeds
    # the CentralDataHub and emits its already-defined trending signals.
    dynamic.DynamicMarketScanner.run_continuous_scanning = _real_dynamic_scanning
    dynamic.DynamicMarketScanner.publish_trending_signals = _real_publish_trending_signals

    # Other historical specialist modules stay present, but no random/simulated
    # result is permitted to become execution evidence.
    try:
        import HEDGE_FUND_ARSENAL as hedge
        hedge.StatisticalArbitrage.find_pairs_trades = _real_statistical_arbitrage
    except Exception:
        pass

    try:
        import ultra_swarm_consciousness as swarm
        swarm.SwarmAgent._get_market_data = _real_swarm_market_data
        swarm.SwarmConsciousness.collective_decision = _real_swarm_collective_decision
        swarm.SwarmConsciousness._update_performance_metrics = _real_swarm_performance_metrics
        swarm.SwarmConsciousness._execute_testnet_trade = _no_simulated_swarm_trade
    except Exception:
        pass


    try:
        import ultra_scalping_engine as ultra_scalp
        ultra_scalp.UltraScalpingEngine._get_current_price = _real_ultra_current_price
    except Exception:
        pass

    try:
        import ultra_arbitrage_engine as ultra_arb
        ultra_arb.UltraArbitrageEngine._simulate_arbitrage_execution = _no_simulated_arbitrage_execution
    except Exception:
        pass

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
