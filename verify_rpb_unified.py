#!/usr/bin/env python3
"""Offline/stdlb verification for the unified RPB assembly.

This script makes no network or exchange calls. It verifies the critical
contracts that can be proven without VPS credentials: real-candle scalping,
evolution-fabric advice, authenticated-fill ledger math, and position-adoption
parsing. Runtime/Testnet authority is verified separately by the deployment
script before the execution cutover.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def rows(direction: int, count: int = 80):
    out = []
    price = 100.0
    for i in range(count):
        drift = direction * (0.35 + (i % 5) * 0.02)
        opening = price
        closing = max(0.01, opening + drift)
        out.append([
            i * 60_000,
            opening,
            max(opening, closing) + 0.08,
            min(opening, closing) - 0.08,
            closing,
            1000.0 + i * 12.0,
        ])
        price = closing
    return out


def verify_scalping():
    from rpb_scalping import _timeframe_signal

    rising = _timeframe_signal(rows(1))
    falling = _timeframe_signal(rows(-1))
    check(rising.get("direction") == "BUY", f"rising candles did not vote BUY: {rising}")
    check(falling.get("direction") == "SELL", f"falling candles did not vote SELL: {falling}")
    check(float(rising.get("score", 0)) > 0, "rising score was not positive")
    check(float(falling.get("score", 0)) < 0, "falling score was not negative")
    print("VERIFY_SCALPING_REAL_OHLCV=PASS")


def verify_bridge():
    from rpb_production_bridge import ProductionIntelligenceBridge

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "fabric.json"
        path.write_text(
            json.dumps(
                {
                    "cycles": 6103,
                    "evidence": {
                        "BTC/USDT": {
                            "direction": "BUY",
                            "confidence": 0.82,
                            "microstructure": {"edge_bps": 18.0},
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        bridge = ProductionIntelligenceBridge(path=path)
        adjusted, detail = bridge.adjust("BTC/USDT", "BUY", 85.0)
        check(adjusted >= 85.0, f"matching evolution evidence reduced confidence: {detail}")
        check(detail.get("available") is True, f"evolution bridge did not load: {detail}")
    print("VERIFY_EVOLUTION_BRIDGE=PASS")


def verify_ledger():
    from rpb_position_lifecycle import PositionLedger

    with tempfile.TemporaryDirectory() as td:
        ledger = PositionLedger(path=Path(td) / "positions.json")
        opened = ledger.open_position(
            "BTC/USDT",
            {
                "order_id": "entry-1",
                "filled": 1.0,
                "average": 100.0,
                "cost": 100.0,
                "fee_quote": 0.10,
                "fee_base": 0.0,
            },
            strategy="verify",
            signal_price=100.0,
        )
        check(opened is not None, "authenticated-shaped BUY fill was not recorded")
        closed = ledger.close_position(
            "BTC/USDT",
            {
                "order_id": "exit-1",
                "filled": 1.0,
                "average": 101.0,
                "cost": 101.0,
                "fee_quote": 0.10,
                "fee_base": 0.0,
            },
            "take_profit",
        )
        check(closed is not None, "authenticated-shaped SELL fill was not settled")
        check(abs(float(closed["realized_net_pnl"]) - 0.80) < 1e-9, closed)
    print("VERIFY_LEDGER_NET_PNL=PASS")


def verify_adoption_parser():
    from rpb_adopt_positions import extract_positions

    state = {
        "positions": {
            "DOT/USDT": {
                "symbol": "DOT/USDT",
                "quantity": 2.0,
                "average_entry": 5.0,
                "cost_basis": 10.0,
            }
        }
    }
    positions, ambiguous = extract_positions(state)
    check(len(positions) == 1, f"position adoption parser found {len(positions)} positions")
    check(not ambiguous, f"sample position unexpectedly ambiguous: {ambiguous}")
    print("VERIFY_POSITION_ADOPTION=PASS")


def main():
    verify_scalping()
    verify_bridge()
    verify_ledger()
    verify_adoption_parser()
    print("VERIFY_RPB_UNIFIED=PASS")


if __name__ == "__main__":
    main()
