#!/usr/bin/env python3
"""Adopt authenticated production Testnet positions into the RPB ledger.

The utility is idempotent and conservative. It imports only positions with
quantity plus cost-basis evidence and only when the authenticated Bybit Testnet
account still holds at least that quantity. Extra exchange inventory is never
assumed to belong to RPB.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _symbol(value: Any) -> str:
    text = str(value or "").strip().upper().replace("-", "/").replace("_", "/")
    if ":" in text:
        text = text.split(":", 1)[0]
    if "/" not in text and text.endswith("USDT") and len(text) > 4:
        text = f"{text[:-4]}/USDT"
    return text


def extract_position_rows(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    positions = state.get("positions") or state.get("open_positions") or {}
    cost_map = (
        state.get("position_cost_basis")
        or state.get("cost_basis")
        or state.get("position_costs")
        or {}
    )
    rows: List[Dict[str, Any]] = []

    if isinstance(positions, list):
        iterable = []
        for item in positions:
            if isinstance(item, dict):
                iterable.append((item.get("symbol") or item.get("pair") or item.get("market"), item))
    elif isinstance(positions, dict):
        iterable = list(positions.items())
    else:
        iterable = []

    for raw_symbol, raw in iterable:
        symbol = _symbol(raw_symbol)
        if not symbol or not symbol.endswith("/USDT"):
            continue

        item = dict(raw) if isinstance(raw, dict) else {"quantity": raw}
        basis = cost_map.get(symbol) if isinstance(cost_map, dict) else None
        if basis is None and isinstance(cost_map, dict):
            basis = cost_map.get(symbol.replace("/", ""))
        if isinstance(basis, dict):
            merged = dict(basis)
            merged.update(item)
            item = merged
        elif basis is not None and not isinstance(basis, dict):
            item.setdefault("entry_cost", basis)

        qty = _f(
            item.get("remaining_quantity")
            or item.get("sellable_quantity")
            or item.get("quantity")
            or item.get("qty")
            or item.get("amount")
            or item.get("size")
        )
        average = _f(
            item.get("average_entry")
            or item.get("entry_price")
            or item.get("avg_entry")
            or item.get("average")
            or item.get("price")
        )
        cost = _f(
            item.get("entry_cost")
            or item.get("cost_basis")
            or item.get("cost")
            or item.get("notional")
        )
        if cost <= 0 and qty > 0 and average > 0:
            cost = qty * average
        if average <= 0 and qty > 0 and cost > 0:
            average = cost / qty

        rows.append({
            "symbol": symbol,
            "quantity": qty,
            "average_entry": average,
            "entry_cost": cost,
            "entry_fee_quote": _f(
                item.get("entry_fee_quote") or item.get("entry_fee") or item.get("fee")
            ),
            "entry_timestamp": _f(
                item.get("entry_timestamp") or item.get("opened_at") or item.get("timestamp")
            ),
            "source": "vps_testnet_execution",
        })

    return rows


def _exchange_quantities(balance: Dict[str, Any]) -> Dict[str, float]:
    totals = balance.get("total") if isinstance(balance.get("total"), dict) else {}
    free = balance.get("free") if isinstance(balance.get("free"), dict) else {}
    result: Dict[str, float] = {}
    for base in set(totals) | set(free):
        result[str(base).upper()] = _f(
            totals.get(base) if totals.get(base) is not None else free.get(base)
        )
    return result


def build_report(state: Dict[str, Any], balance: Dict[str, Any], existing_symbols=None) -> Dict[str, Any]:
    existing = set(existing_symbols or [])
    holdings = _exchange_quantities(balance)
    report = {
        "ok": True,
        "adoptable": [],
        "already_owned": [],
        "ambiguous": [],
        "mismatched": [],
    }

    for row in extract_position_rows(state):
        symbol = row["symbol"]
        if symbol in existing:
            report["already_owned"].append(row)
            continue
        qty = _f(row["quantity"])
        avg = _f(row["average_entry"])
        cost = _f(row["entry_cost"])
        if qty <= 0 or avg <= 0 or cost <= 0:
            report["ambiguous"].append({**row, "reason": "missing_quantity_or_cost_basis"})
            continue
        base = symbol.split("/", 1)[0]
        held = _f(holdings.get(base))
        tolerance = max(1e-12, qty * 0.01)
        if held + tolerance < qty:
            report["mismatched"].append({
                **row,
                "authenticated_total": held,
                "reason": "exchange_holds_less_than_recorded",
            })
            continue
        report["adoptable"].append({**row, "authenticated_total": held})

    if report["ambiguous"] or report["mismatched"]:
        report["ok"] = False
    return report


def _adoption_record(row: Dict[str, Any]) -> Dict[str, Any]:
    """Build an RPB ledger record without inheriting a zero/unknown hold clock."""
    stamp = _f(row.get("entry_timestamp"))
    if stamp <= 0:
        # Cost basis remains historical, but an unknown timestamp must not make
        # the 30-second lifecycle treat the position as millions of seconds old
        # and force an immediate timeout close at handoff.
        stamp = time.time()
    return {
        "symbol": row["symbol"],
        "remaining_quantity": row["quantity"],
        "sellable_quantity": row["quantity"],
        "average_entry": row["average_entry"],
        "entry_cost": row["entry_cost"],
        "entry_fee_quote": row.get("entry_fee_quote", 0.0),
        "entry_timestamp": stamp,
        "strategy": "adopted_production_position",
        "confidence": 0.0,
        "attribution": ["production_state_handoff"],
        "session": "adopted",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="/intelligence/runtime/vps_testnet_execution.json")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    state_path = Path(args.state)
    if not state_path.exists():
        print(json.dumps({"ok": False, "error": "state_missing", "path": str(state_path)}))
        return 3
    state = json.loads(state_path.read_text(encoding="utf-8"))

    from src.leantrader.execution.router import route_balance
    balance = route_balance(mode="testnet", exchange_id="bybit") or {}
    if not balance:
        print(json.dumps({"ok": False, "error": "authenticated_balance_unavailable"}))
        return 4

    from rpb_position_lifecycle import PositionLedger
    ledger = PositionLedger()
    report = build_report(state, balance, ledger.open_symbols())

    if args.apply and report["ok"]:
        adopted = []
        for row in report["adoptable"]:
            if ledger.adopt_position(_adoption_record(row)):
                adopted.append(row["symbol"])
        report["applied"] = adopted

    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    return 0 if report["ok"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
