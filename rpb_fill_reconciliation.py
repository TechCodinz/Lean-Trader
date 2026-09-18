"""Authenticated fill reconciliation for the unified RPB runtime.

The exchange can accept and fill a market order before CCXT's immediate
``fetch_order`` view reports a non-zero fill. RPB must never interpret that
short propagation delay as "no position" because the quote balance has already
been spent. This module resolves that race from authenticated order/trade
history and can recover only positions created during the current RPB epoch.

It never creates orders and never grants execution authority.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Set


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _trade_order_id(trade: Dict[str, Any]) -> str:
    value = trade.get("order") or trade.get("orderId")
    if value:
        return str(value)
    info = trade.get("info") if isinstance(trade.get("info"), dict) else {}
    return str(info.get("orderId") or info.get("orderID") or "")


def _fee_parts(entry: Dict[str, Any], symbol: str) -> tuple[float, float]:
    base = str(symbol or "").split("/", 1)[0].upper()
    quote = str(symbol or "").split("/", 1)[1].upper() if "/" in str(symbol or "") else ""
    fee_quote = 0.0
    fee_base = 0.0
    fee = entry.get("fee") if isinstance(entry.get("fee"), dict) else None
    fees = entry.get("fees") if isinstance(entry.get("fees"), list) else []
    rows = ([fee] if fee else []) + [x for x in fees if isinstance(x, dict)]
    seen = set()
    for row in rows:
        key = (str(row.get("currency") or "").upper(), _f(row.get("cost")))
        if key in seen:
            continue
        seen.add(key)
        currency, amount = key
        if amount <= 0:
            continue
        if currency == base:
            fee_base += amount
        elif not currency or currency == quote:
            fee_quote += amount
        else:
            # Non-base fee currencies are conservatively counted as quote-like
            # cost for PnL bookkeeping rather than silently discarded.
            fee_quote += amount
    return fee_quote, fee_base


def aggregate_order_trades(
    order_id: str,
    symbol: str,
    trades: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build one normalized authenticated fill from trades for ``order_id``."""
    wanted = str(order_id or "")
    matches = [
        t
        for t in trades or []
        if isinstance(t, dict)
        and str(t.get("symbol") or symbol) == symbol
        and _trade_order_id(t) == wanted
    ]
    if not wanted or not matches:
        return {
            "order_id": wanted,
            "status": "unknown",
            "filled": 0.0,
            "average": 0.0,
            "cost": 0.0,
            "fee_quote": 0.0,
            "fee_base": 0.0,
            "reconciled": False,
            "raw_status": "",
            "source": "authenticated_trade_history",
        }

    filled = 0.0
    cost = 0.0
    fee_quote = 0.0
    fee_base = 0.0
    for trade in matches:
        amount = _f(trade.get("amount"))
        price = _f(trade.get("price"))
        trade_cost = _f(trade.get("cost")) or (amount * price)
        if amount <= 0 or trade_cost < 0:
            continue
        filled += amount
        cost += trade_cost
        q_fee, b_fee = _fee_parts(trade, symbol)
        fee_quote += q_fee
        fee_base += b_fee

    average = cost / filled if filled > 0 else 0.0
    return {
        "order_id": wanted,
        "status": "closed" if filled > 0 else "unknown",
        "filled": filled,
        "average": average,
        "cost": cost,
        "fee_quote": fee_quote,
        "fee_base": fee_base,
        "reconciled": filled > 0,
        "raw_status": "closed" if filled > 0 else "",
        "source": "authenticated_trade_history",
    }


def _fill_to_receipt(receipt: Dict[str, Any], fill: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """Attach a normalized fill in the shape existing RPB lifecycle expects."""
    out = dict(receipt or {})
    base = str(symbol or "").split("/", 1)[0].upper()
    quote = str(symbol or "").split("/", 1)[1].upper() if "/" in str(symbol or "") else "USDT"
    fees = []
    if _f(fill.get("fee_quote")) > 0:
        fees.append({"currency": quote, "cost": _f(fill.get("fee_quote"))})
    if _f(fill.get("fee_base")) > 0:
        fees.append({"currency": base, "cost": _f(fill.get("fee_base"))})
    out["ok"] = True
    out["executed"] = True
    out["order"] = {
        "id": str(fill.get("order_id") or ""),
        "symbol": symbol,
        "status": "closed",
        "filled": _f(fill.get("filled")),
        "average": _f(fill.get("average")),
        "cost": _f(fill.get("cost")),
        "fees": fees,
    }
    out["rpb_fill_source"] = str(fill.get("source") or "authenticated_reconciliation")
    return out


def reconcile_authenticated_receipt(
    receipt: Dict[str, Any],
    symbol: str,
    *,
    mode: str = "testnet",
    exchange_id: str = "bybit",
    timeout_seconds: float = 6.0,
) -> Dict[str, Any]:
    """Wait briefly for a just-submitted market order's authenticated fill.

    Existing receipt data is preferred. If it still reports zero fill, poll the
    authenticated order view and then authenticated trade history by order id.
    No second order is ever submitted.
    """
    from rpb_position_lifecycle import reconcile_fill

    initial = reconcile_fill(receipt, symbol)
    if _f(initial.get("filled")) > 0:
        return receipt

    order = receipt.get("order") if isinstance(receipt.get("order"), dict) else {}
    order_id = str(order.get("id") or initial.get("order_id") or "")
    if not order_id:
        return receipt

    try:
        from src.leantrader.execution.broker_ccxt import BrokerCCXT

        broker = BrokerCCXT(
            execution_mode=mode,
            exchange_id=exchange_id,
            market_mode="spot",
        )
        exchange = broker._make_exchange(mode, authenticated=True)  # noqa: SLF001
    except Exception:
        return receipt

    deadline = time.time() + max(0.5, float(timeout_seconds or 0.0))
    since_ms = int((time.time() - 300.0) * 1000)
    while time.time() < deadline:
        try:
            refreshed = exchange.fetch_order(order_id, symbol) or {}
            candidate = _fill_to_receipt(
                receipt,
                {
                    "order_id": order_id,
                    "filled": _f(refreshed.get("filled")),
                    "average": _f(refreshed.get("average")) or _f(refreshed.get("price")),
                    "cost": _f(refreshed.get("cost")),
                    "fee_quote": _fee_parts(refreshed, symbol)[0],
                    "fee_base": _fee_parts(refreshed, symbol)[1],
                    "source": "authenticated_fetch_order",
                },
                symbol,
            )
            if _f(reconcile_fill(candidate, symbol).get("filled")) > 0:
                return candidate
        except Exception:
            pass

        try:
            trades = exchange.fetch_my_trades(symbol, since_ms, 100) or []
            fill = aggregate_order_trades(order_id, symbol, trades)
            if _f(fill.get("filled")) > 0:
                return _fill_to_receipt(receipt, fill, symbol)
        except Exception:
            pass

        time.sleep(0.35)

    return receipt


def reconstruct_epoch_positions(
    trades: Iterable[Dict[str, Any]],
    balance: Dict[str, Any],
    *,
    since_ms: int,
) -> List[Dict[str, Any]]:
    """Rebuild only net-open positions created at/after the current RPB epoch."""
    rows = sorted(
        [
            t for t in trades or []
            if isinstance(t, dict) and int(_f(t.get("timestamp"))) >= int(since_ms)
        ],
        key=lambda t: int(_f(t.get("timestamp"))),
    )
    states: Dict[str, Dict[str, Any]] = {}

    for trade in rows:
        symbol = str(trade.get("symbol") or "")
        if "/" not in symbol:
            continue
        side = str(trade.get("side") or "").lower()
        amount = _f(trade.get("amount"))
        price = _f(trade.get("price"))
        cost = _f(trade.get("cost")) or (amount * price)
        if side not in {"buy", "sell"} or amount <= 0 or cost < 0:
            continue

        state = states.setdefault(
            symbol,
            {
                "qty": 0.0,
                "cost": 0.0,
                "entry_fee_quote": 0.0,
                "first_ts": int(_f(trade.get("timestamp"))),
                "orders": [],
            },
        )
        q_fee, b_fee = _fee_parts(trade, symbol)

        if side == "buy":
            net_amount = max(0.0, amount - b_fee)
            state["qty"] += net_amount
            state["cost"] += cost + q_fee
            state["entry_fee_quote"] += q_fee
            oid = _trade_order_id(trade)
            if oid:
                state["orders"].append(oid)
        else:
            owned = _f(state.get("qty"))
            if owned <= 0:
                continue
            sold = min(owned, amount)
            portion = sold / owned if owned > 0 else 1.0
            state["cost"] *= max(0.0, 1.0 - portion)
            state["entry_fee_quote"] *= max(0.0, 1.0 - portion)
            state["qty"] = max(0.0, owned - sold)

    totals = balance.get("total") if isinstance(balance.get("total"), dict) else {}
    positions: List[Dict[str, Any]] = []
    for symbol, state in states.items():
        qty = _f(state.get("qty"))
        cost = _f(state.get("cost"))
        if qty <= 1e-12 or cost <= 0:
            continue
        base = symbol.split("/", 1)[0].upper()
        held = _f(totals.get(base))
        if held <= 1e-12:
            continue
        adopted_qty = min(qty, held)
        scale = adopted_qty / qty if qty > 0 else 0.0
        adopted_cost = cost * scale
        if adopted_qty <= 1e-12 or adopted_cost <= 0:
            continue
        positions.append(
            {
                "symbol": symbol,
                "quantity": adopted_qty,
                "average_entry": adopted_cost / adopted_qty,
                "entry_cost": adopted_cost,
                "entry_fee_quote": _f(state.get("entry_fee_quote")) * scale,
                "entry_timestamp": _f(state.get("first_ts")) / 1000.0,
                "source": "authenticated_testnet_epoch_trade_history",
                "orders": list(dict.fromkeys(state.get("orders") or [])),
            }
        )
    return positions


def recover_current_epoch_to_ledger(
    *,
    since_ms: int,
    mode: str = "testnet",
    exchange_id: str = "bybit",
    exclude_symbols: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Idempotently attach current-epoch authenticated fills to the RPB ledger."""
    from rpb_position_lifecycle import PositionLedger
    from src.leantrader.execution.broker_ccxt import BrokerCCXT

    broker = BrokerCCXT(
        execution_mode=mode,
        exchange_id=exchange_id,
        market_mode="spot",
    )
    exchange = broker._make_exchange(mode, authenticated=True)  # noqa: SLF001
    balance = exchange.fetch_balance() or {}
    trades = exchange.fetch_my_trades(None, int(since_ms), 100) or []
    reconstructed = reconstruct_epoch_positions(trades, balance, since_ms=int(since_ms))
    excluded = {str(symbol) for symbol in (exclude_symbols or set())}
    if excluded:
        reconstructed = [row for row in reconstructed if row.get("symbol") not in excluded]

    ledger = PositionLedger()
    adopted: List[str] = []
    already_owned: List[str] = []
    for row in reconstructed:
        symbol = row["symbol"]
        if ledger.owns(symbol):
            already_owned.append(symbol)
            continue
        if ledger.adopt_position(
            {
                "symbol": symbol,
                "remaining_quantity": row["quantity"],
                "sellable_quantity": row["quantity"],
                "average_entry": row["average_entry"],
                "entry_cost": row["entry_cost"],
                "entry_fee_quote": row.get("entry_fee_quote", 0.0),
                "entry_timestamp": row.get("entry_timestamp") or time.time(),
                "strategy": "rpb_authenticated_epoch_recovery",
                "confidence": 0.0,
                "attribution": ["authenticated_testnet_epoch_trade_history"],
                "session": "recovered",
            }
        ):
            adopted.append(symbol)

    return {
        "ok": True,
        "since_ms": int(since_ms),
        "authenticated_trades": len(trades),
        "reconstructed": [row["symbol"] for row in reconstructed],
        "adopted": adopted,
        "already_owned": already_owned,
        "excluded": sorted(excluded),
    }
