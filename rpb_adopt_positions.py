#!/usr/bin/env python3
"""Adopt authenticated production Testnet positions into the RPB ledger.

The utility is idempotent and conservative. It imports only positions with
quantity plus cost-basis evidence and only when the authenticated Bybit Testnet
account still holds at least that quantity. When the production state retained
inventory quantity but lost its basis fields, the utility may reconstruct the
remaining basis from authenticated Bybit Testnet trade history. It never
invents a price or basis, and extra exchange inventory is never assumed to
belong to RPB.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def _trade_fees(trade: Dict[str, Any], base: str, quote: str) -> tuple[float, float]:
    """Return (base_fee, quote_fee) only when fee currency is explicit."""
    entries: List[Dict[str, Any]] = []
    fee = trade.get("fee")
    if isinstance(fee, dict):
        entries.append(fee)
    fees = trade.get("fees")
    if isinstance(fees, list):
        entries.extend(x for x in fees if isinstance(x, dict))

    base_fee = 0.0
    quote_fee = 0.0
    seen = set()
    for entry in entries:
        currency = str(entry.get("currency") or "").upper()
        cost = _f(entry.get("cost"))
        key = (currency, cost)
        if key in seen:
            continue
        seen.add(key)
        if cost <= 0:
            continue
        if currency == base:
            base_fee += cost
        elif currency == quote:
            quote_fee += cost
    return base_fee, quote_fee


def reconstruct_cost_basis_from_trades(
    symbol: str,
    target_quantity: float,
    trades: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Rebuild remaining average-cost basis from authenticated spot fills.

    The function refuses histories that begin with a SELL against inventory it
    cannot account for. That keeps a truncated exchange history from being
    silently treated as a complete cost basis.
    """
    symbol = _symbol(symbol)
    target = _f(target_quantity)
    if target <= 0 or "/" not in symbol:
        return {"ok": False, "reason": "invalid_target_quantity"}

    base, quote = symbol.split("/", 1)
    ordered = sorted(
        [x for x in (trades or []) if isinstance(x, dict)],
        key=lambda row: (_f(row.get("timestamp")), str(row.get("id") or "")),
    )

    quantity = 0.0
    cost_basis = 0.0
    entry_fee_quote = 0.0
    covered_trades = 0

    for trade in ordered:
        side = str(trade.get("side") or "").lower()
        amount = _f(trade.get("amount"))
        price = _f(trade.get("price"))
        cost = _f(trade.get("cost"))
        if amount <= 0 or side not in {"buy", "sell"}:
            continue
        if cost <= 0 and price > 0:
            cost = amount * price

        base_fee, quote_fee = _trade_fees(trade, base, quote)

        if side == "buy":
            received = max(0.0, amount - base_fee)
            if received <= 0 or cost <= 0:
                continue
            quantity += received
            cost_basis += cost + quote_fee
            entry_fee_quote += quote_fee
            covered_trades += 1
            continue

        debit = amount + base_fee
        tolerance = max(1e-12, debit * 0.001)
        if debit > quantity + tolerance:
            return {
                "ok": False,
                "reason": "trade_history_does_not_cover_inventory",
                "covered_trades": covered_trades,
            }
        if quantity <= 0:
            return {
                "ok": False,
                "reason": "trade_history_does_not_cover_inventory",
                "covered_trades": covered_trades,
            }
        portion = min(1.0, debit / quantity)
        cost_basis *= max(0.0, 1.0 - portion)
        entry_fee_quote *= max(0.0, 1.0 - portion)
        quantity = max(0.0, quantity - debit)
        covered_trades += 1

    tolerance = max(1e-12, target * 0.01)
    if quantity + tolerance < target or cost_basis <= 0:
        return {
            "ok": False,
            "reason": "trade_history_does_not_cover_inventory",
            "covered_trades": covered_trades,
            "reconstructed_quantity": quantity,
        }

    # If the authenticated history covers more inventory than the production
    # state says belongs to this handoff, adopt only the requested quantity at
    # the reconstructed average cost. Do not claim the extra inventory.
    scale = min(1.0, target / quantity) if quantity > 0 else 0.0
    adopted_cost = cost_basis * scale
    adopted_fee = entry_fee_quote * scale
    if adopted_cost <= 0:
        return {"ok": False, "reason": "reconstructed_cost_non_positive"}

    return {
        "ok": True,
        "average_entry": adopted_cost / target,
        "entry_cost": adopted_cost,
        "entry_fee_quote": adopted_fee,
        "reconstructed_quantity": quantity,
        "covered_trades": covered_trades,
        "reason": "authenticated_testnet_trade_history",
    }


def fetch_authenticated_trade_history(symbol: str) -> List[Dict[str, Any]]:
    """Read authenticated Bybit Testnet fills. This function submits no order."""
    from src.leantrader.execution.broker_ccxt import BrokerCCXT

    broker = BrokerCCXT(
        execution_mode="testnet",
        exchange_id="bybit",
        market_mode="spot",
    )
    exchange = broker._make_exchange("testnet", authenticated=True)
    load_markets = getattr(exchange, "load_markets", None)
    if callable(load_markets):
        load_markets()
    fetch = getattr(exchange, "fetch_my_trades", None)
    if not callable(fetch):
        raise RuntimeError("authenticated trade history unavailable")
    limit = max(20, int(os.getenv("RPB_ADOPTION_TRADE_LIMIT", "1000") or 1000))
    rows = fetch(symbol, since=None, limit=limit)
    return [x for x in (rows or []) if isinstance(x, dict)]


def enrich_missing_basis_from_authenticated_history(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for original in rows:
        row = dict(original)
        qty = _f(row.get("quantity"))
        if qty > 0 and (_f(row.get("average_entry")) <= 0 or _f(row.get("entry_cost")) <= 0):
            try:
                trades = fetch_authenticated_trade_history(str(row.get("symbol") or ""))
                rebuilt = reconstruct_cost_basis_from_trades(
                    str(row.get("symbol") or ""), qty, trades
                )
            except Exception as exc:
                rebuilt = {
                    "ok": False,
                    "reason": f"authenticated_trade_history_error:{type(exc).__name__}",
                }
            if rebuilt.get("ok"):
                row["average_entry"] = _f(rebuilt.get("average_entry"))
                row["entry_cost"] = _f(rebuilt.get("entry_cost"))
                row["entry_fee_quote"] = _f(rebuilt.get("entry_fee_quote"))
                row["source"] = "vps_testnet_execution+authenticated_testnet_trade_history"
                row["basis_reconstruction"] = {
                    "reason": rebuilt.get("reason"),
                    "covered_trades": int(rebuilt.get("covered_trades") or 0),
                    "reconstructed_quantity": _f(rebuilt.get("reconstructed_quantity")),
                }
            else:
                row["basis_reconstruction_reason"] = str(
                    rebuilt.get("reason") or "authenticated_trade_history_insufficient"
                )
        enriched.append(row)
    return enriched


def _exchange_quantities(balance: Dict[str, Any]) -> Dict[str, float]:
    totals = balance.get("total") if isinstance(balance.get("total"), dict) else {}
    free = balance.get("free") if isinstance(balance.get("free"), dict) else {}
    result: Dict[str, float] = {}
    for base in set(totals) | set(free):
        result[str(base).upper()] = _f(
            totals.get(base) if totals.get(base) is not None else free.get(base)
        )
    return result


def build_report(
    state: Dict[str, Any],
    balance: Dict[str, Any],
    existing_symbols=None,
    rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    existing = set(existing_symbols or [])
    holdings = _exchange_quantities(balance)
    report = {
        "ok": True,
        "adoptable": [],
        "already_owned": [],
        "ambiguous": [],
        "mismatched": [],
    }

    for row in rows if rows is not None else extract_position_rows(state):
        symbol = row["symbol"]
        if symbol in existing:
            report["already_owned"].append(row)
            continue
        qty = _f(row["quantity"])
        avg = _f(row["average_entry"])
        cost = _f(row["entry_cost"])
        if qty <= 0 or avg <= 0 or cost <= 0:
            report["ambiguous"].append({
                **row,
                "reason": row.get("basis_reconstruction_reason")
                or "missing_quantity_or_cost_basis",
            })
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
    rows = extract_position_rows(state)
    rows = enrich_missing_basis_from_authenticated_history(rows)
    report = build_report(state, balance, ledger.open_symbols(), rows=rows)

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