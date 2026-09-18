"""Small, persistent safety primitives for the unified RPB runtime.

These helpers do not place orders and do not grant execution authority. They
only preserve unresolved authenticated order ownership and bounded pair
quarantines across container restarts.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


def _atomic_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def assess_testnet_execution_book(
    orderbook: Any,
    *,
    target_quote: float,
    max_spread_bps: float = 250.0,
    min_depth_multiple: float = 1.25,
    depth_levels: int = 5,
    max_roundtrip_friction_bps: Optional[float] = None,
) -> Dict[str, Any]:
    """Decide whether a Testnet spot book can support a small round trip.

    Public production data may generate the signal, but authenticated Testnet
    execution must have both entry-side and exit-side liquidity. This helper is
    deliberately pure: it does not place orders or grant authority.
    """

    book = orderbook if isinstance(orderbook, dict) else {}
    raw_bids = book.get("bids") if isinstance(book.get("bids"), list) else []
    raw_asks = book.get("asks") if isinstance(book.get("asks"), list) else []

    def _levels(rows):
        out = []
        for row in rows or []:
            try:
                price = float(row[0])
                qty = float(row[1])
            except (TypeError, ValueError, IndexError):
                continue
            if price > 0.0 and qty > 0.0:
                out.append((price, qty))
        return out

    bids = _levels(raw_bids)
    asks = _levels(raw_asks)
    if not bids and not asks:
        return {
            "ok": False,
            "reason": "missing_two_sided_liquidity",
            "spread_bps": None,
            "bid_depth_quote": 0.0,
            "ask_depth_quote": 0.0,
        }
    if not asks:
        return {
            "ok": False,
            "reason": "missing_ask_liquidity",
            "spread_bps": None,
            "bid_depth_quote": sum(p * q for p, q in bids[:depth_levels]),
            "ask_depth_quote": 0.0,
        }
    if not bids:
        return {
            "ok": False,
            "reason": "missing_bid_liquidity",
            "spread_bps": None,
            "bid_depth_quote": 0.0,
            "ask_depth_quote": sum(p * q for p, q in asks[:depth_levels]),
        }

    best_bid = bids[0][0]
    best_ask = asks[0][0]
    mid = (best_bid + best_ask) / 2.0
    spread_bps = ((best_ask - best_bid) / mid) * 10_000.0 if mid > 0.0 else float("inf")

    bid_depth = sum(p * q for p, q in bids[:depth_levels])
    ask_depth = sum(p * q for p, q in asks[:depth_levels])
    required_depth = max(0.0, float(target_quote or 0.0)) * max(
        1.0, float(min_depth_multiple or 1.0)
    )

    def _buy_base_for_quote(levels, quote_budget):
        remaining_quote = max(0.0, float(quote_budget or 0.0))
        acquired_base = 0.0
        spent_quote = 0.0
        for price, qty in levels[:depth_levels]:
            level_quote = price * qty
            take_quote = min(remaining_quote, level_quote)
            if take_quote <= 0.0:
                break
            acquired_base += take_quote / price
            spent_quote += take_quote
            remaining_quote -= take_quote
            if remaining_quote <= 1e-12:
                break
        return acquired_base, spent_quote, remaining_quote

    def _sell_base_for_quote(levels, base_qty):
        remaining_base = max(0.0, float(base_qty or 0.0))
        proceeds_quote = 0.0
        sold_base = 0.0
        for price, qty in levels[:depth_levels]:
            take_base = min(remaining_base, qty)
            if take_base <= 0.0:
                break
            sold_base += take_base
            proceeds_quote += take_base * price
            remaining_base -= take_base
            if remaining_base <= 1e-12:
                break
        return sold_base, proceeds_quote, remaining_base

    acquired_base, spent_quote, buy_shortfall = _buy_base_for_quote(
        asks,
        max(0.0, float(target_quote or 0.0)),
    )
    sold_base, exit_quote, sell_shortfall = _sell_base_for_quote(
        bids,
        acquired_base,
    )
    roundtrip_friction_bps = None
    if spent_quote > 0.0 and buy_shortfall <= 1e-12 and sell_shortfall <= 1e-12:
        roundtrip_friction_bps = max(
            0.0,
            ((spent_quote - exit_quote) / spent_quote) * 10_000.0,
        )

    if best_ask <= best_bid or spread_bps < 0.0:
        return {
            "ok": False,
            "reason": "crossed_or_invalid_book",
            "spread_bps": spread_bps,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_depth_quote": bid_depth,
            "ask_depth_quote": ask_depth,
            "required_depth_quote": required_depth,
        }

    if spread_bps > max(0.0, float(max_spread_bps or 0.0)):
        return {
            "ok": False,
            "reason": "spread_too_wide",
            "spread_bps": spread_bps,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_depth_quote": bid_depth,
            "ask_depth_quote": ask_depth,
            "required_depth_quote": required_depth,
        }

    if (
        bid_depth + 1e-12 < required_depth
        or ask_depth + 1e-12 < required_depth
        or buy_shortfall > 1e-12
        or sell_shortfall > 1e-12
    ):
        return {
            "ok": False,
            "reason": "insufficient_roundtrip_depth",
            "spread_bps": spread_bps,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_depth_quote": bid_depth,
            "ask_depth_quote": ask_depth,
            "required_depth_quote": required_depth,
            "roundtrip_friction_bps": roundtrip_friction_bps,
        }

    if (
        max_roundtrip_friction_bps is not None
        and roundtrip_friction_bps is not None
        and roundtrip_friction_bps
        > max(0.0, float(max_roundtrip_friction_bps or 0.0))
    ):
        return {
            "ok": False,
            "reason": "roundtrip_friction_too_high",
            "spread_bps": spread_bps,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_depth_quote": bid_depth,
            "ask_depth_quote": ask_depth,
            "required_depth_quote": required_depth,
            "roundtrip_friction_bps": roundtrip_friction_bps,
            "max_roundtrip_friction_bps": max_roundtrip_friction_bps,
        }

    return {
        "ok": True,
        "reason": "executable",
        "spread_bps": spread_bps,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "bid_depth_quote": bid_depth,
        "ask_depth_quote": ask_depth,
        "required_depth_quote": required_depth,
        "roundtrip_friction_bps": roundtrip_friction_bps,
    }


def extract_order_id(receipt: Any) -> str:
    if not isinstance(receipt, dict):
        return ""
    order = receipt.get("order") if isinstance(receipt.get("order"), dict) else {}
    return str(order.get("id") or receipt.get("order_id") or "")


def is_dust_block(result: Any) -> bool:
    """True only for an owned SELL remainder that is below the venue floor."""
    if not isinstance(result, dict):
        return False
    if str(result.get("blocker") or "") != "CAPITAL_BELOW_EXECUTABLE_MINIMUM":
        return False
    detail = str(result.get("detail") or "").lower()
    return "requested" in detail and "below the venue floor" in detail


def definitive_exchange_reject_reason(error: Any) -> str:
    """Classify exchange refusals that will repeat unchanged this session."""
    text = str(error or "").lower()
    if "only available to the china region" in text or '"retcode":170209' in text:
        return "region_restricted_market"
    if "maximum allowed per order" in text or '"retcode":170381' in text:
        return "venue_max_order_constraint"
    return ""


class PendingExecutionStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        configured = os.getenv(
            "RPB_PENDING_PATH",
            "/rpb-data/runtime/rpb_pending_execution.json",
        )
        self.path = Path(path) if path else Path(configured)

    def get(self) -> Dict[str, Any]:
        payload = _read_json(self.path)
        current = payload.get("pending")
        return current if isinstance(current, dict) else {}

    def set(self, record: Dict[str, Any]) -> None:
        payload = {
            "updated_at": time.time(),
            "pending": dict(record or {}),
        }
        _atomic_json(self.path, payload)

    def clear(self) -> None:
        _atomic_json(self.path, {"updated_at": time.time(), "pending": {}})


class PairQuarantineStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        configured = os.getenv(
            "RPB_QUARANTINE_PATH",
            "/rpb-data/runtime/rpb_quarantined_pairs.json",
        )
        self.path = Path(path) if path else Path(configured)

    def _items(self) -> Dict[str, Dict[str, Any]]:
        payload = _read_json(self.path)
        raw = payload.get("items")
        return {
            str(symbol): dict(record)
            for symbol, record in (raw.items() if isinstance(raw, dict) else [])
            if isinstance(record, dict)
        }

    def active(self) -> Dict[str, Dict[str, Any]]:
        now = time.time()
        output: Dict[str, Dict[str, Any]] = {}
        for symbol, record in self._items().items():
            expires_at = float(record.get("expires_at") or 0.0)
            if expires_at > 0 and expires_at <= now:
                continue
            output[symbol] = record
        return output

    def symbols(self) -> set[str]:
        return set(self.active())

    def get(self, symbol: str) -> Dict[str, Any]:
        return dict(self.active().get(str(symbol), {}))

    def add(
        self,
        symbol: str,
        *,
        kind: str,
        reason: str,
        detail: str = "",
        record: Optional[Dict[str, Any]] = None,
        ttl_seconds: float = 0.0,
    ) -> None:
        items = self._items()
        now = time.time()
        items[str(symbol)] = {
            "symbol": str(symbol),
            "kind": str(kind),
            "reason": str(reason),
            "detail": str(detail)[:1000],
            "created_at": now,
            "expires_at": now + float(ttl_seconds) if ttl_seconds and ttl_seconds > 0 else 0.0,
            "record": dict(record or {}),
        }
        _atomic_json(self.path, {"updated_at": now, "items": items})
