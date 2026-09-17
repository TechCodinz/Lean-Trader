"""Best-effort admin/premium/free distribution for authenticated RPB events."""

from __future__ import annotations

import os
import threading
from typing import Any, Callable, Dict, List

FREE_CHANNEL_DELAY_SECONDS = float(os.getenv("RPB_FREE_DELAY_SECONDS", "90"))
FREE_CHANNEL_EVERY_N = int(os.getenv("RPB_FREE_EVERY_N", "2") or 2)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


class SignalDistributor:
    def __init__(self, send: Callable[..., Any], *, admin_chat_id: str = "", vip_chat_id: str = "", free_chat_id: str = "") -> None:
        self._send = send
        self.admin_chat_id = str(admin_chat_id or "")
        self.vip_chat_id = str(vip_chat_id or "")
        self.free_chat_id = str(free_chat_id or "")
        self._free_counter = 0
        self._timers: List[threading.Timer] = []

    def _deliver(self, chat_id: str, message: str) -> bool:
        if not chat_id or not message:
            return False
        try:
            return bool(self._send(message, chat_id))
        except Exception:
            return False

    def _later(self, chat_id: str, message: str, delay: float) -> None:
        if not chat_id:
            return
        if delay <= 0:
            self._deliver(chat_id, message)
            return
        timer = threading.Timer(delay, self._deliver, args=(chat_id, message))
        timer.daemon = True
        timer.start()
        self._timers = [t for t in self._timers if t.is_alive()][-50:] + [timer]

    def broadcast_entry(self, symbol: str, entry_price: float, quantity: float, cost: float, confidence: float, *, reasoning: str = "", take_profit_bps: float = 0.0, stop_loss_bps: float = 0.0) -> None:
        entry = _f(entry_price)
        target = entry * (1 + take_profit_bps / 10_000.0) if take_profit_bps else 0.0
        stop = entry * (1 - stop_loss_bps / 10_000.0) if stop_loss_bps else 0.0
        premium = (
            f"🟢 <b>PREMIUM SIGNAL — ENTRY</b>\n\n"
            f"💎 <b>{symbol}</b>\n📥 <b>Entry:</b> ${entry:.8f}\n"
            f"📦 <b>Size:</b> {_f(quantity):.8f}\n💵 <b>Allocated:</b> ${_f(cost):.4f}\n"
            f"🔥 <b>Confidence:</b> {_f(confidence):.0f}%"
        )
        if target:
            premium += f"\n🎯 <b>Target:</b> ${target:.8f}"
        if stop:
            premium += f"\n🛡 <b>Stop:</b> ${stop:.8f}"
        if reasoning:
            premium += f"\n\n🧠 <b>Why:</b> {reasoning[:600]}"
        self._deliver(self.vip_chat_id, premium)
        self._free_counter += 1
        if FREE_CHANNEL_EVERY_N > 0 and self._free_counter % FREE_CHANNEL_EVERY_N == 0:
            self._later(
                self.free_chat_id,
                f"📈 <b>SIGNAL — ENTRY</b>\n\n💰 <b>{symbol}</b>\n📥 <b>Entry zone:</b> ${entry:.6f}\n🔥 <b>Confidence:</b> {_f(confidence):.0f}%",
                FREE_CHANNEL_DELAY_SECONDS,
            )

    def broadcast_exit(self, symbol: str, settled: Dict[str, Any], wallet_balance: float) -> None:
        net = _f(settled.get("realized_net_pnl"))
        emoji = "🟢" if net >= 0 else "🔴"
        premium = (
            f"{emoji} <b>PREMIUM SIGNAL — CLOSED</b>\n\n"
            f"💎 <b>{symbol}</b>\n📥 <b>Entry:</b> ${_f(settled.get('average_entry')):.8f}\n"
            f"📤 <b>Exit:</b> ${_f(settled.get('exit_average')):.8f}\n"
            f"🚪 <b>Reason:</b> {settled.get('exit_reason')}\n⏱ <b>Held:</b> {_f(settled.get('hold_seconds')):.1f}s\n\n"
            f"📊 <b>Gross:</b> ${_f(settled.get('gross_pnl')):+.6f}\n"
            f"🧾 <b>Fees:</b> ${_f(settled.get('total_fees')):.6f}\n"
            f"{emoji} <b>NET:</b> ${net:+.6f}\n👛 <b>Wallet:</b> ${_f(wallet_balance):.6f}"
        )
        self._deliver(self.vip_chat_id, premium)
        if FREE_CHANNEL_EVERY_N > 0 and self._free_counter % FREE_CHANNEL_EVERY_N == 0:
            self._later(
                self.free_chat_id,
                f"{emoji} <b>RESULT — {symbol}</b>\n\nNET ${net:+.6f} · {settled.get('exit_reason')}",
                FREE_CHANNEL_DELAY_SECONDS,
            )
