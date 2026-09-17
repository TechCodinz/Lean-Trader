"""Authenticated owned-position lifecycle for REAL_PROFIT_BOT.

An acknowledgement is not a fill. Positions are created only from a non-zero
exchange fill, persisted across restarts, and closed only from authenticated
SELL fills. Realized PnL is net of recorded entry/exit fees.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = 2
TAKE_PROFIT = "take_profit"
TRAILING_PROFIT = "trailing_profit"
STOP_LOSS = "stop_loss"
MOMENTUM_DECAY = "momentum_decay"
DYNAMIC_TIMEOUT = "dynamic_timeout"
MICROSTRUCTURE_DETERIORATION = "microstructure_deterioration"


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)) or default)
    except (TypeError, ValueError):
        return float(default)


def reconcile_fill(order_or_receipt: Any, symbol: str = "") -> Dict[str, Any]:
    """Normalize the router/broker receipt into authenticated fill facts."""
    receipt = order_or_receipt if isinstance(order_or_receipt, dict) else {}
    order = receipt.get("order") if isinstance(receipt.get("order"), dict) else receipt
    order = order if isinstance(order, dict) else {}

    result = {
        "order_id": str(order.get("id") or ""),
        "client_order_id": str(order.get("clientOrderId") or (order.get("info") or {}).get("orderLinkId") or ""),
        "status": str(order.get("status") or "unknown").lower(),
        "filled": _f(order.get("filled")),
        "average": _f(order.get("average")) or _f(order.get("price")),
        "cost": _f(order.get("cost")),
        "fee_quote": 0.0,
        "fee_base": 0.0,
        "reconciled": bool(receipt.get("executed") or order.get("id") or order.get("status")),
        "raw_status": str(order.get("status") or ""),
    }

    if result["cost"] <= 0 and result["filled"] > 0 and result["average"] > 0:
        result["cost"] = result["filled"] * result["average"]

    base = str(symbol or order.get("symbol") or "").split("/")[0].upper()
    fee = order.get("fee")
    fees = order.get("fees") if isinstance(order.get("fees"), list) else []
    entries = ([fee] if isinstance(fee, dict) else []) + [x for x in fees if isinstance(x, dict)]
    seen = set()
    for entry in entries:
        key = (entry.get("currency"), entry.get("cost"))
        if key in seen:
            continue
        seen.add(key)
        cost = _f(entry.get("cost"))
        currency = str(entry.get("currency") or "").upper()
        if currency and currency == base:
            result["fee_base"] += cost
        else:
            result["fee_quote"] += cost
    return result


class PositionLedger:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else self._default_path()
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.closed: List[Dict[str, Any]] = []
        self.load()

    @staticmethod
    def _default_path() -> Path:
        base = os.getenv("LEANTRADER_DATA_DIR", "").strip()
        candidate = Path(base) / "runtime" if base else Path("runtime")
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate / "rpb_positions.json"

    def load(self) -> int:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return 0
        if not isinstance(payload, dict):
            return 0
        self.positions = {str(k): v for k, v in (payload.get("positions") or {}).items() if isinstance(v, dict)}
        self.closed = [x for x in (payload.get("closed") or []) if isinstance(x, dict)][-1000:]
        return len(self.positions)

    def save(self) -> bool:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "updated_at": time.time(),
            "positions": self.positions,
            "closed": self.closed[-1000:],
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            os.replace(tmp, self.path)
            return True
        except Exception:
            return False

    def open_position(
        self,
        symbol: str,
        fill: Dict[str, Any],
        *,
        strategy: str = "rpb",
        confidence: float = 0.0,
        signal_price: float = 0.0,
        attribution: Optional[List[str]] = None,
        session: str = "unknown",
    ) -> Optional[Dict[str, Any]]:
        filled = _f(fill.get("filled"))
        average = _f(fill.get("average")) or _f(signal_price)
        if filled <= 0 or average <= 0:
            return None
        sellable = max(0.0, filled - _f(fill.get("fee_base")))
        if sellable <= 0:
            return None
        record = {
            "symbol": symbol,
            "order_id": fill.get("order_id", ""),
            "client_order_id": fill.get("client_order_id", ""),
            "filled_quantity": filled,
            "sellable_quantity": sellable,
            "remaining_quantity": sellable,
            "average_entry": average,
            "entry_cost": _f(fill.get("cost")) or filled * average,
            "entry_fee_quote": _f(fill.get("fee_quote")),
            "entry_fee_base": _f(fill.get("fee_base")),
            "entry_timestamp": time.time(),
            "strategy": strategy,
            "confidence": _f(confidence),
            "attribution": list(attribution or []),
            "session": session,
            "peak_price": average,
            "exit_state": "open",
        }
        self.positions[symbol] = record
        self.save()
        return record

    def adopt_position(self, record: Dict[str, Any]) -> bool:
        symbol = str(record.get("symbol") or "")
        if not symbol or symbol in self.positions:
            return False
        qty = _f(record.get("remaining_quantity") or record.get("sellable_quantity") or record.get("quantity"))
        entry = _f(record.get("average_entry") or record.get("entry_price"))
        cost = _f(record.get("entry_cost") or record.get("cost_basis"))
        if qty <= 0 or entry <= 0 or cost <= 0:
            return False
        adopted = dict(record)
        adopted.update({"symbol": symbol, "remaining_quantity": qty, "sellable_quantity": qty, "average_entry": entry, "entry_cost": cost, "adopted": True, "exit_state": "open"})
        adopted.setdefault("entry_timestamp", time.time())
        adopted.setdefault("peak_price", entry)
        self.positions[symbol] = adopted
        self.save()
        return True

    def close_position(self, symbol: str, exit_fill: Dict[str, Any], exit_reason: str) -> Optional[Dict[str, Any]]:
        record = self.positions.get(symbol)
        if record is None:
            return None
        sold = _f(exit_fill.get("filled"))
        if sold <= 0:
            return None
        proceeds = _f(exit_fill.get("cost")) or sold * _f(exit_fill.get("average"))
        exit_fee = _f(exit_fill.get("fee_quote"))
        owned = _f(record.get("sellable_quantity")) or _f(record.get("filled_quantity"))
        portion = min(1.0, sold / owned) if owned > 0 else 1.0
        cost_basis = _f(record.get("entry_cost")) * portion
        entry_fee = _f(record.get("entry_fee_quote")) * portion
        gross = proceeds - cost_basis
        fees = entry_fee + exit_fee
        net = gross - fees
        settled = {
            **record,
            "exit_order_id": exit_fill.get("order_id", ""),
            "exit_quantity": sold,
            "exit_average": _f(exit_fill.get("average")),
            "exit_proceeds": proceeds,
            "exit_fee_quote": exit_fee,
            "exit_reason": exit_reason,
            "exit_timestamp": time.time(),
            "hold_seconds": time.time() - _f(record.get("entry_timestamp"), time.time()),
            "gross_pnl": gross,
            "total_fees": fees,
            "realized_net_pnl": net,
            "exit_state": "closed",
        }
        remaining = max(0.0, owned - sold)
        if remaining > max(1e-12, owned * 0.001):
            record["remaining_quantity"] = remaining
            record["sellable_quantity"] = remaining
            record["entry_cost"] = _f(record.get("entry_cost")) * (1.0 - portion)
            record["entry_fee_quote"] = _f(record.get("entry_fee_quote")) * (1.0 - portion)
            self.positions[symbol] = record
        else:
            self.positions.pop(symbol, None)
        self.closed.append(settled)
        self.save()
        return settled

    def owns(self, symbol: str) -> bool:
        return symbol in self.positions

    def open_symbols(self) -> List[str]:
        return list(self.positions)

    def realized_net_total(self) -> float:
        return sum(_f(x.get("realized_net_pnl")) for x in self.closed)

    def stats(self) -> Dict[str, Any]:
        wins = [x for x in self.closed if _f(x.get("realized_net_pnl")) > 0]
        return {
            "open_positions": len(self.positions),
            "closed_positions": len(self.closed),
            "realized_net_pnl": self.realized_net_total(),
            "authentic_wins": len(wins),
            "authentic_win_rate": 100.0 * len(wins) / len(self.closed) if self.closed else 0.0,
            "total_fees": sum(_f(x.get("total_fees")) for x in self.closed),
        }


class ExitEvaluator:
    def __init__(self) -> None:
        self.take_profit_bps = _env_float("RPB_TAKE_PROFIT_BPS", 50.0)
        self.stop_loss_bps = _env_float("RPB_STOP_LOSS_BPS", 30.0)
        self.trailing_arm_bps = _env_float("RPB_TRAILING_ARM_BPS", 35.0)
        self.trailing_give_back_bps = _env_float("RPB_TRAILING_GIVEBACK_BPS", 15.0)
        self.max_hold_seconds = _env_float("RPB_MAX_HOLD_SECONDS", 30.0)
        self.momentum_decay_bps = _env_float("RPB_MOMENTUM_DECAY_BPS", 20.0)
        self.max_spread_bps = _env_float("RPB_MAX_EXIT_SPREAD_BPS", 80.0)

    def evaluate(
        self,
        record: Dict[str, Any],
        price: float,
        *,
        now: Optional[float] = None,
        change_pct: Optional[float] = None,
        spread_bps: Optional[float] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        now = time.time() if now is None else now
        entry = _f(record.get("average_entry"))
        if entry <= 0 or price <= 0:
            return False, "", {"reason": "no_usable_mark"}
        move_bps = ((price - entry) / entry) * 10_000.0
        peak = max(_f(record.get("peak_price")) or entry, price)
        record["peak_price"] = peak
        give_back_bps = ((peak - price) / peak) * 10_000.0 if peak > 0 else 0.0
        held = now - _f(record.get("entry_timestamp"), now)
        detail = {"move_bps": round(move_bps, 2), "give_back_bps": round(give_back_bps, 2), "held_seconds": round(held, 3), "peak_price": peak}
        eps = 1e-9
        if move_bps + eps >= self.take_profit_bps:
            return True, TAKE_PROFIT, detail
        if move_bps - eps <= -self.stop_loss_bps:
            return True, STOP_LOSS, detail
        armed_move = ((peak - entry) / entry) * 10_000.0
        if armed_move >= self.trailing_arm_bps and give_back_bps >= self.trailing_give_back_bps:
            return True, TRAILING_PROFIT, detail
        if spread_bps is not None and _f(spread_bps) > self.max_spread_bps and move_bps > 0:
            return True, MICROSTRUCTURE_DETERIORATION, detail
        if change_pct is not None and _f(change_pct) < 0 and move_bps > -self.stop_loss_bps / 2:
            # A rolling 24h sign flip is only an early-exit hint when the
            # position itself has not already hit the hard stop.
            if move_bps < self.momentum_decay_bps:
                return True, MOMENTUM_DECAY, detail
        if held >= self.max_hold_seconds:
            return True, DYNAMIC_TIMEOUT, detail
        return False, "", detail
