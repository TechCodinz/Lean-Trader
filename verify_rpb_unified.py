#!/usr/bin/env python3
"""Offline/stdlb verification for the unified RPB assembly.

No network or exchange order is made here. Runtime/Testnet authority is proven
separately by the deployment handoff after these local contracts pass.
"""

from __future__ import annotations

import json
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
    missing = _timeframe_signal([])
    check(rising.get("direction") == "BUY", f"rising candles did not vote BUY: {rising}")
    check(falling.get("direction") == "SELL", f"falling candles did not vote SELL: {falling}")
    check(float(rising.get("score", 0)) > 0, "rising score was not positive")
    check(float(falling.get("score", 0)) < 0, "falling score was not negative")
    check(missing.get("direction") == "NEUTRAL" and missing.get("usable") is False, missing)
    print("VERIFY_SCALPING_REAL_OHLCV=PASS")


def verify_bridge():
    from rpb_production_bridge import RPBProductionBridge

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "fabric.json"
        path.write_text(
            json.dumps({
                "cycles": 6103,
                "evidence": {
                    "BTC/USDT": {
                        "direction": "BUY",
                        "confidence": 0.82,
                        "microstructure": {"edge_bps": 18.0},
                    }
                },
            }),
            encoding="utf-8",
        )
        bridge = RPBProductionBridge(fabric_path=path)
        signal, adjusted, detail = bridge.evaluate("BTC/USDT", "BUY", 85.0)
        check(signal == "BUY", f"bridge changed direction: {signal}")
        check(adjusted >= 85.0, f"matching evolution evidence reduced confidence: {detail}")
        check(detail.get("available") is True, f"evolution bridge did not load: {detail}")
        check(detail.get("cycles") == 6103, f"evolution cycles lost: {detail}")
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


def verify_adoption_parser_and_clock():
    from rpb_adopt_positions import _adoption_record, extract_position_rows

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
    positions = extract_position_rows(state)
    check(len(positions) == 1, f"position adoption parser found {len(positions)} positions")
    check(positions[0]["quantity"] == 2.0, positions[0])
    record = _adoption_record(positions[0])
    check(float(record.get("entry_timestamp") or 0.0) > 0.0, record)
    check(record.get("strategy") == "adopted_production_position", record)
    print("VERIFY_POSITION_ADOPTION=PASS")


def verify_basis_reconstruction():
    from rpb_adopt_positions import reconstruct_cost_basis_from_trades

    trades = [
        {
            "timestamp": 1,
            "side": "buy",
            "amount": 10.0,
            "price": 2.0,
            "cost": 20.0,
            "fee": {"currency": "USDT", "cost": 0.02},
        },
        {
            "timestamp": 2,
            "side": "sell",
            "amount": 4.0,
            "price": 3.0,
            "cost": 12.0,
            "fee": {"currency": "USDT", "cost": 0.01},
        },
    ]
    rebuilt = reconstruct_cost_basis_from_trades("DOT/USDT", 6.0, trades)
    check(rebuilt.get("ok") is True, rebuilt)
    check(abs(float(rebuilt.get("entry_cost")) - 12.012) < 1e-9, rebuilt)
    check(abs(float(rebuilt.get("average_entry")) - 2.002) < 1e-9, rebuilt)

    incomplete = reconstruct_cost_basis_from_trades(
        "DOT/USDT",
        1.0,
        [{"timestamp": 1, "side": "sell", "amount": 1.0, "price": 4.0, "cost": 4.0}],
    )
    check(incomplete.get("ok") is False, incomplete)
    check(incomplete.get("reason") == "trade_history_does_not_cover_inventory", incomplete)
    print("VERIFY_AUTHENTICATED_BASIS_RECONSTRUCTION=PASS")


def verify_dust_quarantine_policy():
    from rpb_adopt_positions import build_report
    from rpb_adoption_dust import assess_dust_from_market

    evidence = assess_dust_from_market(
        "DOT/USDT",
        0.0015,
        prices=[0.94, 0.95, 0.93],
        market={
            "limits": {
                "cost": {"min": 1.0},
                "amount": {"min": 0.01},
            }
        },
        hard_cap_usd=0.05,
    )
    check(evidence.get("ok") is True, evidence)

    tiny = {
        "symbol": "DOT/USDT",
        "quantity": 0.0015,
        "average_entry": 0.0,
        "entry_cost": 0.0,
        "basis_reconstruction_reason": "trade_history_does_not_cover_inventory",
        "dust_quarantine": evidence,
    }
    report = build_report({}, {"total": {"DOT": 0.0015}}, rows=[tiny])
    check(report.get("ok") is True, report)
    check(len(report.get("quarantined_dust") or []) == 1, report)
    check(not report.get("ambiguous"), report)

    material = dict(tiny)
    material["quantity"] = 2.0
    material.pop("dust_quarantine", None)
    blocked = build_report({}, {"total": {"DOT": 2.0}}, rows=[material])
    check(blocked.get("ok") is False, blocked)
    check(len(blocked.get("ambiguous") or []) == 1, blocked)
    print("VERIFY_AUTHENTICATED_DUST_QUARANTINE=PASS")


def main():
    verify_scalping()
    verify_bridge()
    verify_ledger()
    verify_adoption_parser_and_clock()
    verify_basis_reconstruction()
    verify_dust_quarantine_policy()
    print("VERIFY_RPB_UNIFIED=PASS")


if __name__ == "__main__":
    main()
