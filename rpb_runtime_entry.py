#!/usr/bin/env python3
"""Canonical entrypoint for the sole authenticated RPB Testnet runtime."""

from __future__ import annotations

import os
import time
from typing import Any, Dict

from REAL_PROFIT_BOT import REAL_PROFIT_BOT
from rpb_fill_reconciliation import (
    reconcile_authenticated_receipt,
    recover_current_epoch_to_ledger,
)
from rpb_runtime_hardening import (
    PairQuarantineStore,
    PendingExecutionStore,
    definitive_exchange_reject_reason,
    extract_order_id,
    is_dust_block,
)


class UnifiedRPBRuntime(REAL_PROFIT_BOT):
    """RPB with authenticated delayed-fill ownership and runtime hardening.

    This is still the same single strategy/execution owner. The additions here
    only make authenticated order ownership fail closed, stop impossible dust
    exits from looping forever, and remember deterministic venue restrictions.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pending_store = PendingExecutionStore()
        self.quarantine_store = PairQuarantineStore()
        self._last_epoch_sweep = 0.0
        self._pending_notice_at = 0.0
        self._exit_reason_context = ""
        self.blocked_pairs.update(self.quarantine_store.symbols())
        self._apply_active_dust_quarantines()

    # ----------------------------------------------------- ownership recovery

    def _epoch_start_ms(self) -> int:
        return _epoch_start_ms()

    def _apply_active_dust_quarantines(self) -> None:
        """Keep exchange dust auditable without treating it as an active trade."""
        if not self.lifecycle_enabled or self.ledger is None:
            return
        changed = False
        for symbol, q in self.quarantine_store.active().items():
            if q.get("kind") != "dust":
                continue
            if symbol in self.ledger.positions:
                self.ledger.positions.pop(symbol, None)
                changed = True
            self.blocked_pairs.add(symbol)
        if changed:
            self.ledger.save()

    def _recover_epoch_ownership(self, *, force: bool = False) -> Dict[str, Any]:
        epoch = self._epoch_start_ms()
        if self.mode != "testnet" or epoch <= 0:
            return {"ok": True, "adopted": []}
        interval = float(os.getenv("RPB_OWNERSHIP_SWEEP_SECONDS", "5") or 5)
        now = time.time()
        if not force and now - self._last_epoch_sweep < max(1.0, interval):
            return {"ok": True, "adopted": []}
        self._last_epoch_sweep = now
        report = recover_current_epoch_to_ledger(
            since_ms=epoch,
            mode="testnet",
            exchange_id=self.execution_exchange_id,
        )
        self._apply_active_dust_quarantines()
        if report.get("adopted"):
            print(
                "🔗 RPB OWNERSHIP SWEEP: adopted="
                + ",".join(report.get("adopted") or [])
            )
        return report

    def _authenticated_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if not order_id:
            return {}
        try:
            from src.leantrader.execution.broker_ccxt import BrokerCCXT

            broker = BrokerCCXT(
                execution_mode=self.mode,
                exchange_id=self.execution_exchange_id,
                market_mode="spot",
            )
            exchange = broker._make_exchange(self.mode, authenticated=True)  # noqa: SLF001
            order = exchange.fetch_order(order_id, symbol) or {}
            return order if isinstance(order, dict) else {}
        except Exception:
            return {}

    def _resolve_pending_execution(self, *, force: bool = False) -> bool:
        pending = self.pending_store.get()
        if not pending:
            return True

        symbol = str(pending.get("symbol") or "")
        side = str(pending.get("side") or "").lower()
        order_id = str(pending.get("order_id") or "")
        receipt = pending.get("receipt") if isinstance(pending.get("receipt"), dict) else {}

        try:
            self._recover_epoch_ownership(force=True)
        except Exception as exc:
            now = time.time()
            if now - self._pending_notice_at >= 10:
                print(f"⚠️ PENDING OWNERSHIP SWEEP unavailable: {type(exc).__name__}")
                self._pending_notice_at = now

        if side == "buy" and self.lifecycle_enabled and self.ledger.owns(symbol):
            self.pending_store.clear()
            print(f"🔗 PENDING BUY OWNERSHIP RESOLVED: {symbol} order={order_id}")
            return True
        if side == "sell" and self.lifecycle_enabled and not self.ledger.owns(symbol):
            self.pending_store.clear()
            print(f"🔗 PENDING SELL OWNERSHIP RESOLVED: {symbol} order={order_id}")
            return True

        reconciled = reconcile_authenticated_receipt(
            receipt,
            symbol,
            mode=self.mode,
            exchange_id=self.execution_exchange_id,
            timeout_seconds=1.0 if not force else 2.0,
        )
        from rpb_position_lifecycle import reconcile_fill

        fill = reconcile_fill(reconciled, symbol)
        if float(fill.get("filled") or 0.0) > 0:
            if side == "buy":
                if not self.ledger.owns(symbol):
                    record = super()._record_buy_fill(
                        symbol,
                        reconciled,
                        float(pending.get("signal_price") or fill.get("average") or 0.0),
                        float(pending.get("confidence") or 0.0),
                    )
                    if not record:
                        return False
            elif side == "sell" and self.ledger.owns(symbol):
                if not self._settle_exit(
                    symbol,
                    reconciled,
                    str(pending.get("exit_reason") or "delayed_authenticated_fill"),
                ):
                    return False
            self.pending_store.clear()
            print(
                f"🔗 PENDING {side.upper()} FILL RESOLVED: {symbol} "
                f"order={order_id} qty={float(fill.get('filled') or 0.0):.12f}"
            )
            return True

        status_order = self._authenticated_order_status(order_id, symbol)
        status = str(status_order.get("status") or "").lower()
        if status in {"canceled", "cancelled", "rejected", "expired"}:
            self.pending_store.clear()
            print(
                f"🧹 PENDING ORDER CLEARED WITHOUT FILL: {symbol} "
                f"order={order_id} status={status}"
            )
            return True

        now = time.time()
        if now - self._pending_notice_at >= 10:
            age = now - float(pending.get("submitted_at") or now)
            print(
                f"⏳ PENDING AUTHENTICATED ORDER: {symbol} {side.upper()} "
                f"order={order_id} age={age:.1f}s; new BUYs paused"
            )
            self._pending_notice_at = now
        return False

    # ----------------------------------------------------------- execution

    def execute_trade(self, symbol, signal, price, amount=None, confidence=0.0):
        side = str(signal or "").lower()

        # Never stack fresh BUY exposure on top of an acknowledged order whose
        # authenticated fill state has not yet been resolved.
        if side == "buy" and not self._resolve_pending_execution():
            return {
                "ok": False,
                "prepared": False,
                "blocker": "PENDING_AUTHENTICATED_ORDER",
                "detail": "previous acknowledged order still awaiting authenticated fill state",
                "stage": "ownership",
            }

        receipt = super().execute_trade(
            symbol,
            signal,
            price,
            amount=amount,
            confidence=confidence,
        )

        if not isinstance(receipt, dict):
            return receipt

        if not receipt.get("ok"):
            reason = definitive_exchange_reject_reason(receipt.get("error"))
            if reason:
                ttl = 86400.0 if reason == "region_restricted_market" else 3600.0
                self.quarantine_store.add(
                    symbol,
                    kind="exchange_reject",
                    reason=reason,
                    detail=str(receipt.get("error") or ""),
                    ttl_seconds=ttl,
                )
                self.blocked_pairs.add(symbol)
                print(f"🚫 PAIR QUARANTINED: {symbol} reason={reason}")
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

        order_id = extract_order_id(receipt)
        if order_id:
            self.pending_store.set(
                {
                    "symbol": symbol,
                    "side": side,
                    "order_id": order_id,
                    "submitted_at": time.time(),
                    "signal_price": float(price or 0.0),
                    "confidence": float(confidence or 0.0),
                    "exit_reason": self._exit_reason_context,
                    "receipt": receipt,
                }
            )
            out = dict(receipt)
            out["rpb_pending_fill"] = True
            print(
                f"⏳ ACK PERSISTED FOR AUTHENTICATED RECONCILIATION: "
                f"{symbol} {side.upper()} order={order_id}"
            )
            return out

        return reconciled

    def _record_buy_fill(self, symbol, receipt, signal_price, confidence=0.0):
        if isinstance(receipt, dict) and receipt.get("rpb_pending_fill"):
            return None
        return super()._record_buy_fill(symbol, receipt, signal_price, confidence)

    # ------------------------------------------------------------ lifecycle

    def _quarantine_dust(self, symbol: str, record: Dict[str, Any], result: Dict[str, Any], price: float) -> None:
        preserved = dict(record)
        preserved.update(
            {
                "dust_mark_price": float(price or 0.0),
                "dust_detail": str(result.get("detail") or ""),
                "dust_quarantined_at": time.time(),
            }
        )
        self.quarantine_store.add(
            symbol,
            kind="dust",
            reason="owned_remainder_below_venue_sell_floor",
            detail=str(result.get("detail") or ""),
            record=preserved,
            ttl_seconds=0.0,
        )
        self.ledger.positions.pop(symbol, None)
        self.ledger.save()
        self.blocked_pairs.add(symbol)
        print(
            f"🧹 DUST QUARANTINED: {symbol} qty="
            f"{float(record.get('remaining_quantity') or record.get('sellable_quantity') or 0.0):.12f} "
            f"mark=${float(price or 0.0):.8f}"
        )

    def manage_owned_positions(self):
        if not self.lifecycle_enabled:
            return 0

        try:
            self._recover_epoch_ownership()
        except Exception as exc:
            print(f"⚠️ RPB ownership sweep unavailable: {type(exc).__name__}")

        pending_resolved = self._resolve_pending_execution()
        pending = self.pending_store.get() if not pending_resolved else {}
        pending_symbol = str(pending.get("symbol") or "")
        pending_side = str(pending.get("side") or "").lower()

        if not self.ledger.open_symbols():
            return 0

        closed = 0
        for symbol in list(self.ledger.open_symbols()):
            if pending_side == "sell" and symbol == pending_symbol:
                continue
            record = self.ledger.positions.get(symbol)
            if not record:
                continue
            ticker = self.get_gate_ticker(symbol)
            if not ticker:
                continue
            price = float(ticker.get("price") or 0.0)
            should_exit, reason, detail = self.exit_evaluator.evaluate(
                record,
                price,
                change_pct=ticker.get("change"),
                spread_bps=self._current_spread_bps(symbol),
            )
            if not should_exit:
                self.ledger.save()
                continue

            print(
                f"🚪 EXIT SIGNAL: {symbol} {reason} move={detail.get('move_bps')}bps "
                f"held={detail.get('held_seconds')}s"
            )
            self._exit_reason_context = reason
            try:
                receipt = self.execute_trade(
                    symbol,
                    "SELL",
                    price,
                    amount=record.get("remaining_quantity") or record.get("sellable_quantity"),
                    confidence=1.0,
                )
            finally:
                self._exit_reason_context = ""

            if isinstance(receipt, dict) and is_dust_block(receipt):
                self._quarantine_dust(symbol, record, receipt, price)
                continue
            if isinstance(receipt, dict) and receipt.get("rpb_pending_fill"):
                continue
            if isinstance(receipt, dict) and receipt.get("ok") and self._settle_exit(symbol, receipt, reason):
                closed += 1
        return closed


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
