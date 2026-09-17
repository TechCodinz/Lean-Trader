"""Nine-strategy alpha ensemble plus authenticated-wallet risk sizing for RPB."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Tuple

ALPHA_AGREE_BONUS = float(os.getenv("RPB_ALPHA_AGREE_BONUS", "7"))
ALPHA_MIN_PROB = float(os.getenv("RPB_ALPHA_MIN_PROB", "0.58"))
ALPHA_TIMEFRAME = os.getenv("RPB_ALPHA_TIMEFRAME", "5m")
ALPHA_CANDLES = int(os.getenv("RPB_ALPHA_CANDLES", "120") or 120)
ALPHA_CACHE_SECONDS = float(os.getenv("RPB_ALPHA_CACHE_SECONDS", "45") or 45)
EXECUTABLE_FLOOR_USD = float(os.getenv("RPB_EXECUTABLE_FLOOR_USD", "3.50"))


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


class AlphaEnsemble:
    def __init__(self) -> None:
        self.available = False
        self.reason = "not_initialised"
        self._router = None
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._last_attribution: Dict[str, List[str]] = {}
        try:
            from alpha_engines import AlphaRouter
            self._router = AlphaRouter()
            self.available = True
            self.reason = "ready"
        except Exception as exc:
            self.reason = f"{type(exc).__name__}: {exc}"

    def strategy_names(self) -> List[str]:
        if not self.available:
            return []
        try:
            return [s.name for s in self._router.strats]
        except Exception:
            return []

    def _frame(self, exchange: Any, symbol: str):
        now = time.time()
        cached = self._cache.get(symbol)
        if cached and now - cached[0] < ALPHA_CACHE_SECONDS:
            return cached[1]
        try:
            import pandas as pd
            rows = exchange.fetch_ohlcv(symbol, timeframe=ALPHA_TIMEFRAME, limit=ALPHA_CANDLES)
            if not rows or len(rows) < 60:
                return None
            # Historical alpha strategies use both naming conventions. Keep
            # canonical OHLCV names and aliases so all nine strategies can run.
            frame = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "vol"])
            frame["timestamp"] = frame["ts"]
            frame["volume"] = frame["vol"]
            self._cache[symbol] = (now, frame)
            return frame
        except Exception:
            return None

    def evaluate(self, exchange: Any, symbol: str, signal: str, confidence: float):
        detail: Dict[str, Any] = {"applied": False, "reason": "", "attributed_strategies": []}
        if not self.available or signal != "BUY":
            detail["reason"] = self.reason if not self.available else "alpha_is_long_only"
            return confidence, 1.0, detail
        frame = self._frame(exchange, symbol)
        if frame is None:
            detail["reason"] = "insufficient_real_candles"
            return confidence, 1.0, detail
        try:
            decision = self._router.pick(frame, symbol, ALPHA_TIMEFRAME)
        except Exception as exc:
            detail["reason"] = f"alpha_error:{type(exc).__name__}"
            return confidence, 1.0, detail

        prob = _f(getattr(decision, "prob", 0.0))
        side = getattr(decision, "side", None)
        size_mult = _f(getattr(decision, "size_mult", 1.0), 1.0)
        votes = getattr(decision, "votes", {}) or {}
        positive = [
            name for name, vote in sorted(votes.items(), key=lambda kv: -_f(kv[1]))
            if _f(vote) > 0.05
        ][:4]
        self._last_attribution[symbol] = positive
        detail.update(
            {
                "prob": round(prob, 4),
                "side": side,
                "size_mult": round(size_mult, 3),
                "top_votes": dict(sorted(votes.items(), key=lambda kv: -abs(_f(kv[1])))[:4]),
                "attributed_strategies": positive,
                "notes": str(getattr(decision, "notes", ""))[:240],
                "timeframe": ALPHA_TIMEFRAME,
            }
        )
        if side != "buy" or prob < ALPHA_MIN_PROB:
            detail["reason"] = f"alpha_no_conviction_p{prob:.2f}"
            return confidence, 1.0, detail
        adjusted = min(99.0, float(confidence) + ALPHA_AGREE_BONUS)
        detail.update({"applied": True, "reason": f"alpha_agrees_p{prob:.2f}", "confidence_before": round(float(confidence), 2), "confidence_after": round(adjusted, 2)})
        return adjusted, max(0.5, min(2.0, size_mult)), detail

    def attribution_for(self, symbol: str) -> List[str]:
        return list(self._last_attribution.get(symbol, []))

    def record_result(self, symbol: str, realized_net_pnl: float, strategies: List[str] | None = None) -> None:
        if not self.available:
            return
        names = list(strategies or self._last_attribution.get(symbol, []))
        if not names:
            return
        # AlphaRouter's reward scale is percentage-like. Preserve sign and
        # bound the update so a single micro trade cannot dominate history.
        reward = max(-100.0, min(100.0, float(realized_net_pnl) * 100.0))
        for name in names:
            try:
                self._router.update_reliability(symbol, ALPHA_TIMEFRAME, name, reward)
            except Exception:
                continue

    def health(self) -> Dict[str, Any]:
        return {"available": self.available, "reason": self.reason, "strategies": self.strategy_names(), "timeframe": ALPHA_TIMEFRAME}


class RiskGovernor:
    """Kelly/exposure sizing over authenticated wallet state.

    Risk never creates execution authority. If the historical manager is
    unavailable, the proposed size is returned unchanged rather than blocking
    a functioning RPB.
    """

    def __init__(self) -> None:
        self.available = False
        self.reason = "not_initialised"
        self._manager = None
        try:
            from core.risk_manager import RiskManager
            self._manager = RiskManager()
            self.available = True
            self.reason = "ready"
        except Exception as exc:
            self.reason = f"{type(exc).__name__}: {exc}"

    def sync_wallet(self, portfolio_value: float) -> None:
        if not self.available:
            return
        try:
            self._manager.update_portfolio_value(max(0.0, _f(portfolio_value)))
        except Exception:
            pass

    def sync_position(self, symbol: str, amount: float, price: float) -> None:
        if not self.available:
            return
        try:
            self._manager.update_position(symbol, _f(amount), _f(price))
        except Exception:
            pass

    def cap_position(self, symbol: str, proposed_usd: float, confidence: float, size_multiplier: float = 1.0):
        detail: Dict[str, Any] = {"applied": False, "reason": ""}
        proposed = max(0.0, _f(proposed_usd))
        multiplied = proposed * max(0.5, min(2.0, _f(size_multiplier, 1.0)))
        if not self.available:
            detail["reason"] = self.reason
            return max(EXECUTABLE_FLOOR_USD, multiplied), detail
        try:
            from core.order_manager import OrderSide
            kelly = _f(
                self._manager.calculate_position_size(
                    symbol,
                    OrderSide.BUY,
                    max(0.0, min(1.0, _f(confidence) / 100.0)),
                    0.003,
                    0.02,
                )
            )
            metrics = self._manager.get_risk_metrics()
        except Exception as exc:
            detail["reason"] = f"risk_error:{type(exc).__name__}"
            return max(EXECUTABLE_FLOOR_USD, multiplied), detail
        capped = min(multiplied, kelly) if kelly > 0 else multiplied
        final = max(EXECUTABLE_FLOOR_USD, capped)
        detail.update(
            {
                "applied": True,
                "proposed_usd": round(proposed, 6),
                "after_alpha_usd": round(multiplied, 6),
                "kelly_usd": round(kelly, 6),
                "final_usd": round(final, 6),
                "drawdown": round(_f(metrics.get("current_drawdown")), 4),
                "exposure_ratio": round(_f(metrics.get("exposure_ratio")), 4),
                "risk_level": metrics.get("risk_level"),
                "reason": "kelly_cap" if capped < multiplied else "ladder_within_risk",
            }
        )
        return final, detail

    def health(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False, "reason": self.reason}
        try:
            return {"available": True, **self._manager.get_risk_metrics()}
        except Exception as exc:
            return {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
