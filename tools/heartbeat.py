"""Write a heartbeat file every 30s and optional Telegram ping for admin."""

import json
import os
import time
from pathlib import Path

import requests

RUNTIME = Path(__file__).resolve().parent.parent / "runtime"
HB = RUNTIME / "heartbeat.json"
RUNTIME.mkdir(parents=True, exist_ok=True)

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
            data={"chat_id": chat, "text": text},
            timeout=8,
        )
    except Exception:
        pass

def main(interval: int = 30, ping_minutes: int = 5):
    last_ping = 0
    while True:
        now = int(time.time())
        data = {"ts": now, "status": "ok"}
        try:
            HB.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass
        if now - last_ping >= ping_minutes * 60:
            _tg_send(f"Heartbeat OK {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(now))}")
            last_ping = now
        time.sleep(interval)

if __name__ == "__main__":
    main()
