"""Tail live/testnet logs and forward compact trade/PNL lines to Telegram.

Usage: python -u -m tools.pnl_watcher
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Iterable

import requests


def _env(k: str, d: str = "") -> str:
    v = os.getenv(k)
    return v if v is not None else d


def _tg_send(text: str) -> None:
    if _env("TELEGRAM_ENABLED", "false").strip().lower() not in ("1", "true", "yes", "on"):
        return
    token = _env("TG_BOT_TOKEN") or _env("TELEGRAM_BOT_TOKEN")
    chat = _env("TG_ADMIN_CHAT_ID") or _env("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat, "parse_mode": "HTML", "text": text},
            timeout=8,
        )
    except Exception:
        pass


def _follow(path: Path) -> Iterable[str]:
    # simple file follower without inotify; safe in containers
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    f = None
    while f is None:
        try:
            f = path.open("r", encoding="utf-8", errors="ignore")
            f.seek(0, os.SEEK_END)
        except Exception:
            time.sleep(1)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.25)
            continue
        yield line.rstrip("\n")


FILTER_POS = (
    "create_order",
    "order_placed",
    "filled",
    "execut",
    "realizedPNL",
    "tp",
    "sl",
    "reduceOnly",
)
FILTER_NOISE = (
    "load_markets",
    "fetch_markets",
    "using safe default market list",
)


def _worker(path: Path):
    for line in _follow(path):
        low = line.lower()
        if any(k in low for k in FILTER_NOISE):
            continue
        if any(k in low for k in FILTER_POS):
            _tg_send(f"<code>{line}</code>")


def main():
    root = Path(__file__).resolve().parent.parent
    logs = [
        root / "runtime" / "logs" / "live_console.log",
        root / "reports" / "daemon_console_testnet.log",
    ]
    threads = []
    for p in logs:
        t = threading.Thread(target=_worker, args=(p,), daemon=True)
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())

