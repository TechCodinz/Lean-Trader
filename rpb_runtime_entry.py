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
    assess_testnet_execution_book,
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
        for q_symbol, q_record in self.quarantine_store.active().items():
            if q_record.get("kind") != "testnet_liquidity":
                self.blocked_pairs.add(q_symbol)
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
        dust_exclusions = {
            symbol
            for symbol, record in self.quarantine_store.active().items()
            if record.get("kind") == "dust"
        }
        report = recover_current_epoch_to_ledger(
            since_ms=epoch,
            mode="testnet",
            exchange_id=self.execution_exchange_id,
            exclude_symbols=dust_exclusions,
        )

        # recover_current_epoch_to_ledger() uses its own PositionLedger
        # instance and persists any newly adopted authenticated positions.
        # Reload this runtime's ledger before filtering permanent dust;
        # otherwise the runtime keeps a stale in-memory view while the file
        # silently contains re-adopted dust positions.
        if self.lifecycle_enabled and self.ledger is not None:
            self.ledger.load()

        self._apply_active_dust_quarantines()
        if report.get("adopted"):
            print(
                "🔗 RPB OWNERSHIP SWEEP: adopted="
                + ",".join(report.get("adopted") or [])
            )
        return report

    def _authenticated_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Return authenticated terminal/open order state without guessing.

        Bybit's unified account API requires ``acknowledged=True`` when
        ``fetch_order`` is used outside its recent-order cache. The generic
        lookup used before this fix therefore returned an empty status for a
        genuinely canceled order and kept RPB fail-closed forever. Prefer the
        acknowledged lookup on Bybit, then fall back to explicit open/closed
        endpoints. Other venues retain the ordinary CCXT fetch_order path.
        """
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
        except Exception:
            return {}

        attempts = []
        if self.execution_exchange_id == "bybit":
            attempts.extend(
                [
                    lambda: exchange.fetch_order(
                        order_id,
                        symbol,
                        {"acknowledged": True},
                    ),
                    lambda: exchange.fetch_open_order(order_id, symbol),
                    lambda: exchange.fetch_closed_order(order_id, symbol),
                ]
            )
        else:
            attempts.append(lambda: exchange.fetch_order(order_id, symbol))

        for fetch_status in attempts:
            try:
                order = fetch_status() or {}
                if isinstance(order, dict) and order:
                    return order
            except Exception:
                continue
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
            elif side == "sell" and self.lifecycle_enabled and self.ledger.owns(symbol):
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

    # ------------------------------------------------ execution liquidity

    def _testnet_entry_liquidity_gate(self, symbol: str) -> Dict[str, Any] | None:
        """Require a genuinely executable two-sided Bybit Testnet book.

        Production market data remains the signal source. This gate only asks
        whether Bybit Testnet can actually support the small entry and a later
        exit before authenticated capital is committed.
        """
        if self.mode != "testnet" or self.execution_exchange_id != "bybit":
            return None

        existing = self.quarantine_store.get(symbol)
        if existing.get("kind") == "testnet_liquidity":
            return {
                "ok": False,
                "prepared": False,
                "blocker": "TESTNET_LIQUIDITY_UNAVAILABLE",
                "detail": str(existing.get("detail") or existing.get("reason") or ""),
                "stage": "execution_liquidity",
            }

        target_quote = float(os.getenv("RPB_EXECUTABLE_FLOOR_USD", "5.10") or 5.10)
        max_spread_bps = float(
            os.getenv("RPB_TESTNET_MAX_ENTRY_SPREAD_BPS", "250") or 250
        )
        take_profit_bps = float(
            getattr(self.exit_evaluator, "take_profit_bps", 50.0) or 50.0
        )
        configured_roundtrip_cap = float(
            os.getenv("RPB_TESTNET_MAX_ROUNDTRIP_FRICTION_BPS", "0") or 0
        )
        economic_roundtrip_cap = max(5.0, take_profit_bps * 0.5)
        max_roundtrip_friction_bps = (
            min(configured_roundtrip_cap, economic_roundtrip_cap)
            if configured_roundtrip_cap > 0
            else economic_roundtrip_cap
        )
        min_depth_multiple = float(
            os.getenv("RPB_TESTNET_MIN_DEPTH_MULTIPLE", "1.25") or 1.25
        )
        ttl_seconds = float(
            os.getenv("RPB_TESTNET_LIQUIDITY_QUARANTINE_SECONDS", "60") or 60
        )

        try:
            from src.leantrader.execution.broker_ccxt import BrokerCCXT

            broker = BrokerCCXT(
                execution_mode="testnet",
                exchange_id="bybit",
                market_mode="spot",
            )
            exchange = broker._make_exchange("testnet", authenticated=False)  # noqa: SLF001
            orderbook = exchange.fetch_order_book(symbol, limit=10) or {}
            assessment = assess_testnet_execution_book(
                orderbook,
                target_quote=target_quote,
                max_spread_bps=max_spread_bps,
                min_depth_multiple=min_depth_multiple,
                max_roundtrip_friction_bps=max_roundtrip_friction_bps,
            )
        except Exception as exc:
            assessment = {
                "ok": False,
                "reason": "orderbook_unavailable",
                "error": type(exc).__name__,
                "spread_bps": None,
                "bid_depth_quote": 0.0,
                "ask_depth_quote": 0.0,
            }

        if assessment.get("ok"):
            return None

        reason = str(assessment.get("reason") or "testnet_liquidity_unavailable")
        spread = assessment.get("spread_bps")
        bid_depth = float(assessment.get("bid_depth_quote") or 0.0)
        ask_depth = float(assessment.get("ask_depth_quote") or 0.0)
        roundtrip = assessment.get("roundtrip_friction_bps")
        detail = (
            f"{reason}; spread_bps={spread}; "
            f"roundtrip_friction_bps={roundtrip}; "
            f"roundtrip_cap_bps={max_roundtrip_friction_bps}; "
            f"bid_depth=${bid_depth:.4f}; ask_depth=${ask_depth:.4f}; "
            f"target=${target_quote:.4f}"
        )
        self.quarantine_store.add(
            symbol,
            kind="testnet_liquidity",
            reason=reason,
            detail=detail,
            ttl_seconds=max(5.0, ttl_seconds),
        )
        print(f"🌊 TESTNET LIQUIDITY SKIP: {symbol} {detail}")
        return {
            "ok": False,
            "prepared": False,
            "blocker": "TESTNET_LIQUIDITY_UNAVAILABLE",
            "detail": detail,
            "stage": "execution_liquidity",
        }

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

        if side == "buy":
            liquidity_block = self._testnet_entry_liquidity_gate(symbol)
            if liquidity_block is not None:
                return liquidity_block

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
            dust_exclusions = {
                symbol
                for symbol, record in PairQuarantineStore().active().items()
                if record.get("kind") == "dust"
            }
            report = recover_current_epoch_to_ledger(
                since_ms=epoch,
                mode="testnet",
                exchange_id=exchange_id,
                exclude_symbols=dust_exclusions,
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
