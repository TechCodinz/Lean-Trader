"""Read-only classification of residual Testnet inventory as non-executable dust.

This module never invents cost basis and never submits an order. It may mark a
residual position as quarantinable only when authenticated Testnet market
metadata/ticker evidence shows the residual is both economically tiny and below
an exchange execution minimum. This applies even when cost basis is known,
because non-executable dust should not become an endlessly retried RPB exit.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def assess_dust_from_market(
    symbol: str,
    quantity: float,
    *,
    prices: Iterable[Any],
    market: Dict[str, Any],
    hard_cap_usd: float = 0.05,
) -> Dict[str, Any]:
    """Pure dust policy used by both runtime and offline verification."""
    qty = _f(quantity)
    price_candidates = [_f(x) for x in prices]
    price_candidates = [x for x in price_candidates if x > 0]
    price = max(price_candidates) if price_candidates else 0.0

    limits = market.get("limits") if isinstance(market, dict) else {}
    limits = limits if isinstance(limits, dict) else {}
    cost_limits = limits.get("cost") if isinstance(limits.get("cost"), dict) else {}
    amount_limits = limits.get("amount") if isinstance(limits.get("amount"), dict) else {}
    min_notional = _f(cost_limits.get("min"))
    min_amount = _f(amount_limits.get("min"))

    if qty <= 0 or price <= 0:
        return {"ok": False, "reason": "dust_price_or_quantity_unavailable"}

    notional = qty * price
    below_exchange_minimum = bool(
        (min_notional > 0 and notional < min_notional)
        or (min_amount > 0 and qty < min_amount)
    )
    tiny = notional <= max(0.0, _f(hard_cap_usd, 0.05))

    return {
        "ok": bool(tiny and below_exchange_minimum),
        "reason": (
            "authenticated_non_executable_dust"
            if tiny and below_exchange_minimum
            else "inventory_not_safe_to_quarantine_as_dust"
        ),
        "symbol": str(symbol or ""),
        "quantity": qty,
        "price": price,
        "notional": notional,
        "min_notional": min_notional,
        "min_amount": min_amount,
        "hard_cap_usd": max(0.0, _f(hard_cap_usd, 0.05)),
    }


def inspect_authenticated_testnet_dust(symbol: str, quantity: float) -> Dict[str, Any]:
    """Read Bybit Testnet metadata/ticker only; no order is submitted."""
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

    market = exchange.market(symbol)
    ticker = exchange.fetch_ticker(symbol) or {}
    prices = [
        ticker.get("last"),
        ticker.get("close"),
        ticker.get("bid"),
        ticker.get("ask"),
    ]
    hard_cap = _f(os.getenv("RPB_ADOPTION_DUST_MAX_USD", "0.05"), 0.05)
    evidence = assess_dust_from_market(
        symbol,
        quantity,
        prices=prices,
        market=market if isinstance(market, dict) else {},
        hard_cap_usd=hard_cap,
    )
    evidence["source"] = "authenticated_bybit_testnet_market_metadata"
    return evidence


def annotate_unpriced_dust(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Annotate any residual position that is proven tiny and non-executable."""
    annotated: List[Dict[str, Any]] = []
    for original in rows or []:
        row = dict(original)
        qty = _f(row.get("quantity"))
        if qty > 0:
            try:
                evidence = inspect_authenticated_testnet_dust(
                    str(row.get("symbol") or ""), qty
                )
            except Exception as exc:
                evidence = {
                    "ok": False,
                    "reason": f"dust_evidence_error:{type(exc).__name__}",
                }
            if evidence.get("ok") is True:
                row["dust_quarantine"] = evidence
            else:
                row["dust_quarantine_reason"] = str(
                    evidence.get("reason") or "dust_evidence_unavailable"
                )
        annotated.append(row)
    return annotated
