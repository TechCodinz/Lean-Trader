"""Read-only bridge from the production/evolution fabric into REAL_PROFIT_BOT.

This module deliberately has no exchange credentials and no execution methods.
It consumes persisted production intelligence and turns matching symbol evidence
into a small advisory confidence adjustment. Missing, stale, malformed or
unknown evidence fails open: the original RPB signal remains authoritative.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_PATHS = (
    "/intelligence/runtime/vps_evolution_fabric.json",
    "runtime/vps_evolution_fabric.json",
)

AGREE_BONUS_MAX = float(os.getenv("RPB_EVOLUTION_AGREE_BONUS_MAX", "4"))
CONFLICT_PENALTY_MAX = float(os.getenv("RPB_EVOLUTION_CONFLICT_PENALTY_MAX", "4"))
MAX_EVIDENCE_AGE_SECONDS = float(
    os.getenv("RPB_EVOLUTION_MAX_AGE_SECONDS", "900") or 900
)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _norm_symbol(value: Any) -> str:
    text = str(value or "").strip().upper().replace("-", "/").replace("_", "/")
    if ":" in text:
        text = text.split(":", 1)[0]
    if "/" not in text and text.endswith("USDT") and len(text) > 4:
        text = f"{text[:-4]}/USDT"
    return text


def _direction(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"buy", "long", "bull", "bullish", "up", "positive"}:
        return "BUY"
    if text in {"sell", "short", "bear", "bearish", "down", "negative"}:
        return "SELL"
    return ""


def _confidence(row: Dict[str, Any]) -> float:
    for key in (
        "confidence",
        "probability",
        "prob",
        "score",
        "edge",
        "strength",
        "weight",
    ):
        if key not in row:
            continue
        value = _f(row.get(key))
        if value > 1.0:
            value /= 100.0
        if value < 0:
            value = abs(value)
        return max(0.0, min(1.0, value))
    return 0.5


def _timestamp(row: Dict[str, Any]) -> float:
    for key in ("timestamp", "ts", "updated_at", "created_at", "observed_at", "time"):
        value = row.get(key)
        if value is None:
            continue
        try:
            number = float(value)
            if number > 1e12:
                number /= 1000.0
            if number > 1e9:
                return number
        except (TypeError, ValueError):
            continue
    return 0.0


def _iter_symbol_evidence(node: Any, symbol: str, trail: str = "root") -> Iterable[Dict[str, Any]]:
    """Yield bounded evidence rows mentioning ``symbol`` anywhere in the tree."""
    target = _norm_symbol(symbol)

    if isinstance(node, dict):
        direct_symbol = _norm_symbol(
            node.get("symbol")
            or node.get("pair")
            or node.get("market")
            or node.get("instrument")
        )
        if direct_symbol == target:
            out = dict(node)
            out["_source_path"] = trail
            yield out

        for key, value in node.items():
            key_symbol = _norm_symbol(key)
            child_trail = f"{trail}.{key}"
            if key_symbol == target and isinstance(value, dict):
                out = dict(value)
                out.setdefault("symbol", target)
                out["_source_path"] = child_trail
                yield out
            yield from _iter_symbol_evidence(value, symbol, child_trail)

    elif isinstance(node, list):
        for index, value in enumerate(node[:500]):
            yield from _iter_symbol_evidence(value, symbol, f"{trail}[{index}]")


def _cycles(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 0
    for key in (
        "cycles",
        "evolution_cycles",
        "cycle_count",
        "total_cycles",
        "completed_cycles",
    ):
        try:
            if key in payload:
                return int(payload[key])
        except (TypeError, ValueError):
            pass
    for value in payload.values():
        if isinstance(value, dict):
            found = _cycles(value)
            if found:
                return found
    return 0


class RPBProductionBridge:
    """Advisory-only view of production/evolution intelligence."""

    def __init__(self, fabric_path: Optional[Path] = None) -> None:
        configured = os.getenv("RPB_EVOLUTION_FABRIC_PATH", "").strip()
        if fabric_path is not None:
            self.fabric_path = Path(fabric_path)
        elif configured:
            self.fabric_path = Path(configured)
        else:
            self.fabric_path = next(
                (Path(p) for p in DEFAULT_PATHS if Path(p).exists()),
                Path(DEFAULT_PATHS[0]),
            )
        self._mtime = -1.0
        self._payload: Any = None
        self._last_error = ""

    def _load(self) -> Tuple[Optional[Any], str]:
        path = self.fabric_path
        if not path.exists():
            return None, "fabric_missing"
        try:
            stat = path.stat()
            if self._payload is not None and stat.st_mtime == self._mtime:
                return self._payload, "ready"
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, (dict, list)):
                return None, "fabric_invalid"
            self._payload = payload
            self._mtime = stat.st_mtime
            self._last_error = ""
            return payload, "ready"
        except Exception as exc:
            self._last_error = type(exc).__name__
            return None, f"fabric_error:{type(exc).__name__}"

    def evaluate(
        self,
        symbol: str,
        signal: str,
        confidence: float,
        market_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, float, Dict[str, Any]]:
        """Return the original signal plus a bounded evidence-based adjustment."""
        original_signal = str(signal or "").upper()
        original_confidence = max(0.0, min(99.0, _f(confidence)))
        detail: Dict[str, Any] = {
            "available": False,
            "reason": "",
            "source": str(self.fabric_path),
            "matched_evidence": 0,
            "agree": 0,
            "conflict": 0,
            "cycles": 0,
            "sources": [],
        }

        if original_signal not in {"BUY", "SELL"}:
            detail["reason"] = "no_directional_signal"
            return original_signal, original_confidence, detail

        payload, reason = self._load()
        if payload is None:
            detail["reason"] = reason
            return original_signal, original_confidence, detail

        detail["available"] = True
        detail["cycles"] = _cycles(payload)

        rows: List[Dict[str, Any]] = []
        seen = set()
        now = time.time()
        for row in _iter_symbol_evidence(payload, symbol):
            source = str(row.get("_source_path") or "")
            fingerprint = (source, str(row.get("direction") or row.get("side") or row.get("bias") or ""))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)

            stamp = _timestamp(row)
            if stamp and MAX_EVIDENCE_AGE_SECONDS > 0 and now - stamp > MAX_EVIDENCE_AGE_SECONDS:
                continue
            rows.append(row)
            if len(rows) >= 64:
                break

        detail["matched_evidence"] = len(rows)
        if not rows:
            detail["reason"] = "no_symbol_evidence"
            return original_signal, original_confidence, detail

        agree_weight = 0.0
        conflict_weight = 0.0
        neutral = 0
        for row in rows:
            direction = _direction(
                row.get("direction")
                or row.get("side")
                or row.get("bias")
                or row.get("signal")
                or row.get("regime")
            )
            weight = _confidence(row)
            if direction == original_signal:
                agree_weight += weight
                detail["agree"] += 1
            elif direction in {"BUY", "SELL"}:
                conflict_weight += weight
                detail["conflict"] += 1
            else:
                neutral += 1
            if len(detail["sources"]) < 8:
                detail["sources"].append(str(row.get("_source_path") or "unknown"))

        total_directional = agree_weight + conflict_weight
        adjustment = 0.0
        if total_directional > 0:
            agreement_ratio = agree_weight / total_directional
            conflict_ratio = conflict_weight / total_directional
            adjustment = (
                AGREE_BONUS_MAX * agreement_ratio
                - CONFLICT_PENALTY_MAX * conflict_ratio
            )

        adjusted = max(0.0, min(99.0, original_confidence + adjustment))
        detail["confidence_before"] = round(original_confidence, 3)
        detail["confidence_after"] = round(adjusted, 3)
        detail["adjustment"] = round(adjustment, 3)
        detail["neutral"] = neutral
        detail["reason"] = "production_evolution_evidence"

        # Never manufacture or reverse a trade direction here. RPB owns signal
        # generation; the production fabric is advisory only.
        return original_signal, adjusted, detail

    def health(self) -> Dict[str, Any]:
        payload, reason = self._load()
        return {
            "available": payload is not None,
            "reason": reason,
            "path": str(self.fabric_path),
            "cycles": _cycles(payload) if payload is not None else 0,
            "last_error": self._last_error,
        }
