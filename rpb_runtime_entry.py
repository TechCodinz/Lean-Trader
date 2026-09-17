#!/usr/bin/env python3
"""Canonical entrypoint for the sole authenticated RPB Testnet runtime."""

from __future__ import annotations

import os

from REAL_PROFIT_BOT import REAL_PROFIT_BOT
from rpb_fill_reconciliation import (
    reconcile_authenticated_receipt,
    recover_current_epoch_to_ledger,
)


class UnifiedRPBRuntime(REAL_PROFIT_BOT):
    """RPB with authenticated delayed-fill reconciliation attached.

    This does not add a second strategy or execution owner. It only makes the
    existing RPB wait for the exchange's actual fill before deciding whether a
    submitted order created an owned position.
    """

    def execute_trade(self, symbol, signal, price, amount=None, confidence=0.0):
        receipt = super().execute_trade(
            symbol,
            signal,
            price,
            amount=amount,
            confidence=confidence,
        )
        if not isinstance(receipt, dict) or not receipt.get("ok"):
            return receipt

        from rpb_position_lifecycle import reconcile_fill

        before = reconcile_fill(receipt, symbol)
        if float(before.get("filled") or 0.0) > 0:
            return receipt

        reconciled = reconcile_authenticated_receipt(
            receipt,
            symbol,
            mode=self.mode,
            exchange_id=self.execution_exchange_id,
            timeout_seconds=float(os.getenv("RPB_FILL_RECONCILE_SECONDS", "6") or 6),
        )
        after = reconcile_fill(reconciled, symbol)
        if float(after.get("filled") or 0.0) > 0:
            try:
                from src.leantrader.execution import preflight

                preflight.record_event("fills")
            except Exception:
                pass
            print(
                f"🔗 AUTHENTICATED FILL RECONCILED: {symbol} {str(signal).upper()} "
                f"qty={float(after.get('filled') or 0.0):.12f} "
                f"avg=${float(after.get('average') or 0.0):.8f} "
                f"source={reconciled.get('rpb_fill_source', 'authenticated')}"
            )
        return reconciled


def _epoch_start_ms() -> int:
    raw = str(os.getenv("RPB_EPOCH_START_MS", "") or "").strip()
    if raw:
        try:
            return max(0, int(float(raw)))
        except (TypeError, ValueError):
            pass
    path = os.getenv(
        "RPB_EPOCH_START_PATH",
        "/rpb-data/runtime/rpb_epoch_start_ms",
    )
    try:
        text = open(path, "r", encoding="utf-8").read().strip()
        return max(0, int(float(text)))
    except Exception:
        return 0


def main() -> int:
    mode = str(os.getenv("EXECUTION_MODE", "testnet") or "testnet").lower()
    exchange_id = str(os.getenv("CCXT_EXCHANGE", "bybit") or "bybit").lower()
    epoch = _epoch_start_ms()

    if mode == "testnet" and epoch > 0:
        try:
            report = recover_current_epoch_to_ledger(
                since_ms=epoch,
                mode="testnet",
                exchange_id=exchange_id,
            )
            print("🔗 RPB EPOCH RECOVERY:", report)
        except Exception as exc:
            # Recovery failure must fail closed for execution: continuing to buy
            # while existing current-epoch fills are unowned would repeat the
            # capital leak we are repairing.
            print(f"❌ RPB EPOCH RECOVERY FAILED: {type(exc).__name__}: {exc}")
            return 8

    bot = UnifiedRPBRuntime(mode=mode)
    bot.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
