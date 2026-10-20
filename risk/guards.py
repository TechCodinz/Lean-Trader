from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class RiskLimits:
    max_loss_per_symbol: float  # currency or % of equity if pct=True
    max_daily_loss: float
    max_account_drawdown: float
    pct: bool = True


class GuardState:
    def __init__(self) -> None:
        self.per_symbol_pnl_today: Dict[str, float] = {}
        self.daily_pnl: float = 0.0
        self.peak_equity: float = 0.0
        self.current_equity: float = 0.0
        self._day: int = dt.datetime.now(dt.UTC).timetuple().tm_yday

    def _maybe_roll_day(self) -> None:
        today = dt.datetime.now(dt.UTC).timetuple().tm_yday
        if today != self._day:
            self._day = today
            self.per_symbol_pnl_today.clear()
            self.daily_pnl = 0.0

    def update_equity(self, equity: float) -> None:
        self._maybe_roll_day()
        try:
            e = float(equity)
        except Exception:
            e = 0.0
        self.current_equity = e
        if e > self.peak_equity:
            self.peak_equity = e

    def record_fill(self, symbol: str, pnl: float) -> None:
        self._maybe_roll_day()
        s = (symbol or "").upper()
        try:
            v = float(pnl)
        except Exception:
            v = 0.0
        self.per_symbol_pnl_today[s] = float(self.per_symbol_pnl_today.get(s, 0.0) + v)
        self.daily_pnl = float(self.daily_pnl + v)

    def trip_reasons(self, limits: RiskLimits) -> List[str]:
        self._maybe_roll_day()
        reasons: List[str] = []
        eq = max(1e-9, float(self.current_equity or 0.0))

        # Per-symbol loss
        if self.per_symbol_pnl_today:
            for sym, pnl in self.per_symbol_pnl_today.items():
                thr = limits.max_loss_per_symbol * (eq if limits.pct else 1.0)
                if pnl <= -abs(thr):
                    reasons.append(f"per_symbol_loss:{sym}:{pnl:.6f}<={-abs(thr):.6f}")
                    break

        # Daily loss
        thr_day = limits.max_daily_loss * (eq if limits.pct else 1.0)
        if self.daily_pnl <= -abs(thr_day):
            reasons.append(f"daily_loss:{self.daily_pnl:.6f}<={-abs(thr_day):.6f}")

        # Account drawdown from peak
        if self.peak_equity > 0:
            dd = 1.0 - (eq / self.peak_equity)
            if dd >= abs(limits.max_account_drawdown if limits.pct else limits.max_account_drawdown / max(1e-9, self.peak_equity)):
                reasons.append(f"drawdown:{dd:.4f}>={abs(limits.max_account_drawdown):.4f}")

        return reasons


def should_halt_trading(state: GuardState, limits: RiskLimits) -> Tuple[bool, List[str]]:
    reasons = state.trip_reasons(limits)
    return (len(reasons) > 0, reasons)


class HaltTrading(Exception):
    """Soft exception to signal routing halt due to risk guards."""


# --- Restoration bridge (2026-10-20) -----------------------------------
# The fleet's 2025 consumers (traders_core/execution/crypto_router.py,
# unified_trading_system.py) import these limit constants FROM
# risk.guards. The values are Princewill's own, from his config.py
# (env-overridable, pct=True). Added so those imports resolve as
# designed; the guard logic above is byte-identical to his original.
import os as _os


def _env_float(name, default):
    try:
        return float(_os.environ.get(name, default))
    except Exception:
        return float(default)


def _env_bool(name, default):
    v = _os.environ.get(name)
    if v is None:
        return bool(default)
    return v.strip().lower() in ("1", "true", "yes", "on")


RISK_MAX_LOSS_PER_SYMBOL: float = _env_float("RISK_MAX_LOSS_PER_SYMBOL", 0.02)
RISK_MAX_DAILY_LOSS: float = _env_float("RISK_MAX_DAILY_LOSS", 0.03)
RISK_MAX_ACCOUNT_DD: float = _env_float("RISK_MAX_ACCOUNT_DD", 0.10)
RISK_LIMITS_PCT: bool = _env_bool("RISK_LIMITS_PCT", True)
