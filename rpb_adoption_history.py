"""Authenticated Bybit Testnet trade-history recovery for RPB handoff.

This module is read-only. It never submits an order. The windowed collector is
kept separate from the adoption logic so old fills are not silently lost when
an exchange caps the default trade-history response to only the newest page.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, List

DAY_MS = 86_400_000


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _trade_key(row: Dict[str, Any]) -> tuple:
    trade_id = str(row.get("id") or "")
    if trade_id:
        return ("id", trade_id)
    return (
        "shape",
        int(_f(row.get("timestamp"))),
        str(row.get("order") or row.get("orderId") or ""),
        str(row.get("side") or ""),
        _f(row.get("amount")),
        _f(row.get("price")),
        _f(row.get("cost")),
    )


def collect_windowed_trades(
    fetch: Callable[..., Any],
    symbol: str,
    *,
    now_ms: int | None = None,
    lookback_days: int = 180,
    window_days: int = 7,
    page_limit: int = 100,
) -> List[Dict[str, Any]]:
    """Collect authenticated fills across bounded historical time windows.

    Bybit's execution history is window-bounded and exchange/client defaults can
    otherwise return only the newest page. Querying explicit windows prevents a
    recent SELL from hiding the older BUY that established the inventory basis.
    """
    now_ms = int(now_ms if now_ms is not None else time.time() * 1000)
    lookback_days = max(1, int(lookback_days))
    window_days = max(1, min(7, int(window_days)))
    page_limit = max(20, min(100, int(page_limit)))

    start_ms = max(0, now_ms - lookback_days * DAY_MS)
    window_ms = window_days * DAY_MS
    seen = set()
    collected: List[Dict[str, Any]] = []

    cursor = start_ms
    while cursor <= now_ms:
        end_ms = min(now_ms, cursor + window_ms - 1)
        params = {"startTime": int(cursor), "endTime": int(end_ms)}
        rows = fetch(symbol, since=int(cursor), limit=page_limit, params=params) or []
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = _trade_key(row)
            if key in seen:
                continue
            seen.add(key)
            collected.append(row)
        if end_ms >= now_ms:
            break
        cursor = end_ms + 1

    collected.sort(key=lambda row: (int(_f(row.get("timestamp"))), str(row.get("id") or "")))
    return collected


def fetch_authenticated_trade_history(symbol: str) -> List[Dict[str, Any]]:
    """Read Bybit Testnet spot fills across explicit historical windows."""
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

    lookback_days = int(os.getenv("RPB_ADOPTION_LOOKBACK_DAYS", "180") or 180)
    window_days = int(os.getenv("RPB_ADOPTION_WINDOW_DAYS", "7") or 7)
    page_limit = int(os.getenv("RPB_ADOPTION_TRADE_LIMIT", "100") or 100)
    return collect_windowed_trades(
        fetch,
        symbol,
        lookback_days=lookback_days,
        window_days=window_days,
        page_limit=page_limit,
    )
