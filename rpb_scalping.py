"""Real multi-timeframe scalping confluence and balance-growth sizing for RPB.

The historical SMART_SCALPING_ENGINE analyzer currently contains placeholder
indicator values. This adapter deliberately computes its votes from the OHLCV
rows supplied by the canonical market-data router instead. It is advisory only:
it may adjust confidence, but it never changes direction, submits an order, or
blocks the original REAL_PROFIT_BOT signal.
"""

from __future__ import annotations

import math
import os
import time
from typing import Any, Dict, Iterable, List, Tuple

CONFLUENCE_TIMEFRAMES = tuple(
    tf.strip()
    for tf in os.getenv("RPB_SCALP_TIMEFRAMES", "5m,15m,1h").split(",")
    if tf.strip()
)
CANDLE_LIMIT = int(os.getenv("RPB_SCALP_CANDLE_LIMIT", "80") or 80)
CACHE_SECONDS = float(os.getenv("RPB_SCALP_CACHE_SECONDS", "30") or 30)
MIN_TIMEFRAMES = max(1, int(os.getenv("RPB_SCALP_MIN_TIMEFRAMES", "2") or 2))
MIN_CONFLUENCE_SCORE = float(os.getenv("RPB_SCALP_MIN_SCORE", "0.15") or 0.15)
CONFLUENCE_AGREE_BONUS = float(os.getenv("RPB_SCALP_AGREE_BONUS", "8") or 8)
CONFLUENCE_CONFLICT_PENALTY = float(os.getenv("RPB_SCALP_CONFLICT_PENALTY", "6") or 6)

GROWTH_LADDER: Tuple[Tuple[float, float, str], ...] = (
    (0.0, 0.25, "Micro"),
    (100.0, 0.20, "Foundation"),
    (300.0, 0.15, "Acceleration"),
    (800.0, 0.12, "Expansion"),
    (2000.0, 0.10, "Maturity"),
)
MIN_GROWTH_FRACTION = float(os.getenv("RPB_GROWTH_MIN_FRACTION", "0.05") or 0.05)
MAX_GROWTH_FRACTION = float(os.getenv("RPB_GROWTH_MAX_FRACTION", "0.35") or 0.35)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else float(default)
    except (TypeError, ValueError):
        return float(default)


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _ema(values: Iterable[float], period: int) -> float:
    seq = [float(v) for v in values]
    if not seq:
        return 0.0
    alpha = 2.0 / (float(period) + 1.0)
    ema = seq[0]
    for value in seq[1:]:
        ema = alpha * value + (1.0 - alpha) * ema
    return float(ema)


def _rsi(values: List[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 50.0
    deltas = [values[i] - values[i - 1] for i in range(len(values) - period, len(values))]
    gains = sum(max(delta, 0.0) for delta in deltas) / period
    losses = sum(max(-delta, 0.0) for delta in deltas) / period
    if losses <= 1e-15:
        return 100.0 if gains > 0 else 50.0
    rs = gains / losses
    return 100.0 - (100.0 / (1.0 + rs))


def _timeframe_signal(rows: Any) -> Dict[str, Any]:
    """Return one directional vote computed only from supplied real OHLCV rows."""
    neutral = {
        "usable": False,
        "direction": "NEUTRAL",
        "score": 0.0,
        "ema_fast": 0.0,
        "ema_slow": 0.0,
        "rsi": 50.0,
        "momentum_pct": 0.0,
        "volume_ratio": 0.0,
    }
    if not isinstance(rows, (list, tuple)) or len(rows) < 30:
        return neutral

    closes = [_f(row[4]) for row in rows if isinstance(row, (list, tuple)) and len(row) >= 6]
    volumes = [_f(row[5]) for row in rows if isinstance(row, (list, tuple)) and len(row) >= 6]
    if len(closes) < 30 or len(volumes) != len(closes) or any(v <= 0 for v in closes[-30:]):
        return neutral

    ema_fast = _ema(closes, 12)
    ema_slow = _ema(closes, 26)
    last = closes[-1]
    rsi = _rsi(closes, 14)
    lookback = min(6, len(closes) - 1)
    anchor = closes[-1 - lookback]
    momentum_pct = ((last - anchor) / anchor) * 100.0 if anchor > 0 else 0.0
    recent_vol = volumes[-1]
    baseline_vols = volumes[-21:-1] or volumes[:-1]
    baseline_vol = sum(baseline_vols) / len(baseline_vols) if baseline_vols else recent_vol
    volume_ratio = recent_vol / baseline_vol if baseline_vol > 0 else 1.0

    ema_spread_pct = ((ema_fast - ema_slow) / last) * 100.0 if last > 0 else 0.0
    ema_component = _clip(ema_spread_pct / 0.50, -1.0, 1.0)
    momentum_component = _clip(momentum_pct / 1.00, -1.0, 1.0)
    rsi_component = _clip((rsi - 50.0) / 35.0, -1.0, 1.0)
    trend_sign = 1.0 if momentum_component > 0 else -1.0 if momentum_component < 0 else 0.0
    volume_component = trend_sign * _clip((volume_ratio - 1.0) / 1.5, 0.0, 1.0)

    score = _clip(
        0.40 * ema_component
        + 0.35 * momentum_component
        + 0.20 * rsi_component
        + 0.05 * volume_component,
        -1.0,
        1.0,
    )
    direction = "BUY" if score >= MIN_CONFLUENCE_SCORE else "SELL" if score <= -MIN_CONFLUENCE_SCORE else "NEUTRAL"

    return {
        "usable": True,
        "direction": direction,
        "score": round(score, 6),
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "rsi": round(rsi, 4),
        "momentum_pct": round(momentum_pct, 6),
        "volume_ratio": round(volume_ratio, 6),
    }


def growth_phase(balance: float) -> Tuple[str, float]:
    balance = max(0.0, _f(balance))
    phase_name, fraction = "Micro", GROWTH_LADDER[0][1]
    for floor, frac, name in GROWTH_LADDER:
        if balance >= floor:
            phase_name, fraction = name, frac
    return phase_name, _clip(fraction, MIN_GROWTH_FRACTION, MAX_GROWTH_FRACTION)


def target_position_usd(balance: float, minimum: float = 3.50) -> Tuple[float, str]:
    phase_name, fraction = growth_phase(balance)
    return max(float(minimum), _f(balance) * fraction), phase_name


class ScalpingConfluence:
    """Real-OHLCV MTF confirmation. Advisory only; never an execution gate."""

    def __init__(self) -> None:
        self.available = False
        self.reason = "not_initialised"
        self._tracker = None
        self._session = None
        self._last: Dict[str, float] = {}
        self._votes: Dict[str, Dict[str, Dict[str, Any]]] = {}
        try:
            from SMART_SCALPING_ENGINE import MarketSession, SessionPerformanceTracker
            self._tracker = SessionPerformanceTracker()
            self._session = MarketSession
            self.available = True
            self.reason = "ready_real_ohlcv"
        except Exception as exc:
            self.reason = f"{type(exc).__name__}: {exc}"

    def current_session(self) -> str:
        try:
            value = self._session.get_current_session()
            return str(getattr(value, "value", value)).lower()
        except Exception:
            return "unknown"

    def refresh(self, exchange: Any, symbol: str) -> bool:
        if not self.available:
            return False
        now = time.time()
        cached = self._votes.get(symbol) or {}
        needed = min(MIN_TIMEFRAMES, len(CONFLUENCE_TIMEFRAMES))
        if now - self._last.get(symbol, 0.0) < CACHE_SECONDS and len(cached) >= needed:
            return True

        votes: Dict[str, Dict[str, Any]] = {}
        for timeframe in CONFLUENCE_TIMEFRAMES:
            try:
                rows = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=CANDLE_LIMIT)
            except Exception:
                continue
            vote = _timeframe_signal(rows)
            if vote.get("usable"):
                votes[timeframe] = vote

        if votes:
            self._votes[symbol] = votes
            self._last[symbol] = now
        return len(votes) >= needed

    def _confluence(self, symbol: str) -> Tuple[bool, str, float, Dict[str, Any]]:
        votes = self._votes.get(symbol) or {}
        directional = {tf: vote for tf, vote in votes.items() if vote.get("direction") in {"BUY", "SELL"}}
        needed = min(MIN_TIMEFRAMES, len(CONFLUENCE_TIMEFRAMES))
        if len(directional) < needed:
            return False, "NEUTRAL", 0.0, votes

        buy = [v for v in directional.values() if v["direction"] == "BUY"]
        sell = [v for v in directional.values() if v["direction"] == "SELL"]
        required = max(2 if len(directional) >= 3 else 1, math.ceil(len(directional) * 2.0 / 3.0))
        if len(buy) >= required:
            aligned, direction = buy, "BUY"
        elif len(sell) >= required:
            aligned, direction = sell, "SELL"
        else:
            return False, "NEUTRAL", 0.0, votes

        consensus = len(aligned) / float(len(directional))
        strength = sum(abs(_f(v.get("score"))) for v in aligned) / max(1, len(aligned))
        return strength >= MIN_CONFLUENCE_SCORE, direction, consensus, votes

    def evaluate(self, exchange: Any, symbol: str, signal: str, confidence: float):
        detail: Dict[str, Any] = {"applied": False, "reason": "", "session": self.current_session()}
        if not self.available or signal not in {"BUY", "SELL"}:
            detail["reason"] = self.reason if not self.available else "no_directional_signal"
            return confidence, detail
        if not self.refresh(exchange, symbol):
            detail["reason"] = "insufficient_real_timeframes"
            return confidence, detail

        has_confluence, direction, consensus, votes = self._confluence(symbol)
        detail.update(
            {
                "has_confluence": bool(has_confluence),
                "direction": direction,
                "consensus": round(consensus, 4),
                "votes": {
                    tf: {
                        "direction": vote.get("direction"),
                        "score": vote.get("score"),
                        "rsi": vote.get("rsi"),
                        "momentum_pct": vote.get("momentum_pct"),
                    }
                    for tf, vote in votes.items()
                },
            }
        )
        if not has_confluence or direction == "NEUTRAL":
            detail["reason"] = "no_real_ohlcv_confluence"
            return confidence, detail

        adjusted = float(confidence)
        if direction == signal:
            adjusted += CONFLUENCE_AGREE_BONUS
            detail["reason"] = f"real_mtf_agrees_{direction}"
        else:
            adjusted -= CONFLUENCE_CONFLICT_PENALTY
            detail["reason"] = f"real_mtf_says_{direction}"
        adjusted = _clip(adjusted, 0.0, 99.0)
        detail.update(
            {
                "applied": True,
                "confidence_before": round(float(confidence), 2),
                "confidence_after": round(adjusted, 2),
            }
        )
        return adjusted, detail

    def record_result(self, symbol: str, realized_net_pnl: float) -> None:
        if not self.available:
            return
        try:
            self._tracker.record_trade(symbol, self.current_session(), float(realized_net_pnl), bool(realized_net_pnl > 0))
        except Exception:
            pass

    def session_stats(self, symbol: str) -> Dict[str, Any]:
        if not self.available:
            return {}
        try:
            return dict(self._tracker.performance.get(symbol, {}).get(self.current_session(), {}))
        except Exception:
            return {}

    def health(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "reason": self.reason,
            "session": self.current_session(),
            "timeframes": list(CONFLUENCE_TIMEFRAMES),
            "calculation": "real_ohlcv",
            "cached_symbols": len(self._votes),
        }
