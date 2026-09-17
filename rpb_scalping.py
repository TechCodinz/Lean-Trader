"""Multi-timeframe scalping confluence and balance-growth sizing for RPB."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Tuple

CONFLUENCE_TIMEFRAMES = tuple(
    tf.strip() for tf in os.getenv("RPB_SCALP_TIMEFRAMES", "5m,15m,1h").split(",") if tf.strip()
)
CANDLE_LIMIT = int(os.getenv("RPB_SCALP_CANDLE_LIMIT", "60") or 60)
CACHE_SECONDS = float(os.getenv("RPB_SCALP_CACHE_SECONDS", "45") or 45)
CONFLUENCE_AGREE_BONUS = float(os.getenv("RPB_SCALP_AGREE_BONUS", "8"))
CONFLUENCE_CONFLICT_PENALTY = float(os.getenv("RPB_SCALP_CONFLICT_PENALTY", "6"))
GROWTH_LADDER: Tuple[Tuple[float, float, str], ...] = (
    (0.0, 0.25, "Micro"),
    (100.0, 0.20, "Foundation"),
    (300.0, 0.15, "Acceleration"),
    (800.0, 0.12, "Expansion"),
    (2000.0, 0.10, "Maturity"),
)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def growth_phase(balance: float) -> Tuple[str, float]:
    balance = max(0.0, _f(balance))
    name, fraction = "Micro", 0.25
    for floor, frac, phase in GROWTH_LADDER:
        if balance >= floor:
            name, fraction = phase, frac
    return name, fraction


def target_position_usd(balance: float, minimum: float = 3.50) -> Tuple[float, str]:
    phase, fraction = growth_phase(balance)
    return max(float(minimum), _f(balance) * fraction), phase


class ScalpingConfluence:
    def __init__(self) -> None:
        self.available = False
        self.reason = "not_initialised"
        self._analyzer = None
        self._tracker = None
        self._session = None
        self._last: Dict[str, float] = {}
        try:
            from SMART_SCALPING_ENGINE import MarketSession, MultiTimeframeAnalyzer, SessionPerformanceTracker
            self._analyzer = MultiTimeframeAnalyzer()
            self._tracker = SessionPerformanceTracker()
            self._session = MarketSession
            self.available = True
            self.reason = "ready"
        except Exception as exc:
            self.reason = f"{type(exc).__name__}: {exc}"

    def current_session(self) -> str:
        try:
            return str(self._session.get_current_session()).lower()
        except Exception:
            return "unknown"

    def refresh(self, exchange: Any, symbol: str) -> bool:
        if not self.available:
            return False
        now = time.time()
        if now - self._last.get(symbol, 0.0) < CACHE_SECONDS:
            return True
        loaded = 0
        for timeframe in CONFLUENCE_TIMEFRAMES:
            try:
                rows = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=CANDLE_LIMIT)
                if rows and len(rows) >= 30:
                    self._analyzer.analyze_timeframe(symbol, timeframe, rows)
                    loaded += 1
            except Exception:
                continue
        if loaded:
            self._last[symbol] = now
        return loaded >= min(3, len(CONFLUENCE_TIMEFRAMES))

    def evaluate(self, exchange: Any, symbol: str, signal: str, confidence: float):
        detail: Dict[str, Any] = {
            "applied": False,
            "reason": "",
            "session": self.current_session(),
        }
        if not self.available or signal not in {"BUY", "SELL"}:
            detail["reason"] = self.reason if not self.available else "no_directional_signal"
            return confidence, detail
        if not self.refresh(exchange, symbol):
            detail["reason"] = "insufficient_timeframes"
            return confidence, detail
        try:
            has_confluence, direction, consensus = self._analyzer.check_confluence(symbol)
        except Exception as exc:
            detail["reason"] = f"confluence_error:{type(exc).__name__}"
            return confidence, detail
        detail.update({"has_confluence": bool(has_confluence), "direction": direction, "consensus": round(_f(consensus), 4)})
        if not has_confluence or direction == "NEUTRAL":
            detail["reason"] = "no_confluence"
            return confidence, detail
        adjusted = float(confidence)
        if direction == signal:
            adjusted += CONFLUENCE_AGREE_BONUS
            detail["reason"] = f"{len(CONFLUENCE_TIMEFRAMES)}tf_agree_{direction}"
        else:
            adjusted -= CONFLUENCE_CONFLICT_PENALTY
            detail["reason"] = f"confluence_says_{direction}"
        adjusted = max(0.0, min(99.0, adjusted))
        detail.update({"applied": True, "confidence_before": round(float(confidence), 2), "confidence_after": round(adjusted, 2)})
        return adjusted, detail

    def record_result(self, symbol: str, realized_net_pnl: float) -> None:
        if not self.available:
            return
        try:
            self._tracker.record_trade(
                symbol,
                self.current_session(),
                float(realized_net_pnl),
                bool(realized_net_pnl > 0),
            )
        except Exception:
            pass

    def health(self) -> Dict[str, Any]:
        return {"available": self.available, "reason": self.reason, "session": self.current_session(), "timeframes": list(CONFLUENCE_TIMEFRAMES)}
