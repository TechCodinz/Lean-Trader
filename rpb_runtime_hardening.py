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
