#!/usr/bin/env python3
"""
Ultra Healthcheck
- Verifies code wiring and env integration
- Optionally summarizes live/testnet logs (markers + KPIs)

Usage examples:
  python tools/ultra_healthcheck.py \
    --live-log   /root/ultra_e29e8df4_live.log \
    --test-log   /root/ultra_e29e8df4_testnet.log \
    --env        /root/trading_bot/.env

Outputs a concise human summary and a JSON blob.
"""
import os
import re
import json
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # optional

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "RUN": ROOT / "RUN_BOT.py",
    "CUO": ROOT / "COMPLETE_UNIFIED_ORCHESTRATOR.py",
    "CEO": ROOT / "EXECUTION_ORCHESTRATOR.py",
}

LOG_MARKERS = [
    r"Trading Universe",
    r"Dynamic Universe merged",
    r"EXECUTION LOOP",
    r"SteadyProfitCatcher",
    r"ULTRA GOLDMINE",
    r"DIVINE INTELLIGENCE",
    r"Quantum",
    r"Telegram",
    r"Real Profit engine gated",
]


def read_text(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except Exception:
        return ""


def grep_any(patterns, text) -> dict:
    return {pat: (re.search(pat, text, flags=re.I) is not None) for pat in patterns}


def wired_engines(cuo_text: str):
    return sorted(set(re.findall(r"self\\.trading_engines\\['([^']+)'\\]", cuo_text)))


def orchestrator_funcs(cuo_text: str):
    names = ["initialize_all_systems", "wire_all_systems", "start_all_orchestrators"]
    return {n: (re.search(rf"\bdef\s+{re.escape(n)}\b", cuo_text) is not None) for n in names}


def parse_kpis(log_path: Path):
    if not log_path.exists():
        return {"present": False, "trades_executed": 0, "positions_closed": 0, "realized_total_usd": 0.0}
    L = log_path.read_text(errors="ignore").splitlines()
    execd = sum(1 for l in L if "TRADE EXECUTED" in l)
    closed = 0
    pnl_sum = 0.0
    pnl_re = re.compile(r"P&L:\s*\$([+-]?\d+(?:\.\d+)?)")
    for l in L:
        if "POSITION CLOSED" in l:
            closed += 1
        m = pnl_re.search(l)
        if m:
            try:
                pnl_sum += float(m.group(1))
            except Exception:
                pass
    return {"present": True, "trades_executed": execd, "positions_closed": closed, "realized_total_usd": round(pnl_sum, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-log", dest="live_log", default=str(Path.home() / "ultra_e29e8df4_live.log"))
    ap.add_argument("--test-log", dest="test_log", default=str(Path.home() / "ultra_e29e8df4_testnet.log"))
    ap.add_argument("--env", dest="env_path", default=str(Path.home() / "trading_bot/.env"))
    args = ap.parse_args()

    # Load env (optional)
    env_loaded = False
    tok_present = False
    env_path = Path(args.env_path)
    if load_dotenv is not None and env_path.exists():
        try:
            load_dotenv(dotenv_path=env_path, override=False)
            env_loaded = True
            tok_present = bool(os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
        except Exception:
            pass

    run_txt = read_text(FILES["RUN"]) if FILES["RUN"].exists() else ""
    cuo_txt = read_text(FILES["CUO"]) if FILES["CUO"].exists() else ""
    ceo_txt = read_text(FILES["CEO"]) if FILES["CEO"].exists() else ""

    # Code wiring checks
    engines = wired_engines(cuo_txt)
    funcs = orchestrator_funcs(cuo_txt)
    code_markers = {
        "RUN_loads_env": ("load_dotenv" in run_txt) or (".env" in run_txt),
        "CUO_dynamic_merge": ("universe_dynamic.json" in cuo_txt) and ("Dynamic Universe merged" in cuo_txt),
        "CUO_realprofit_gate": ("ENABLE_REAL_PROFIT_ENGINE" in cuo_txt) and ("Real Profit engine gated" in cuo_txt),
        "CEO_env_overrides": all(s in ceo_txt for s in [
            "MAX_RISK_PER_TRADE", "MAX_POSITION_PCT", "MIN_POSITION_USD",
            "MAX_OPEN_POSITIONS", "MAX_DAILY_LOSS", "MIN_CONFIDENCE_",
        ]),
        "CEO_symbol_sanitizer": ("_sanitize_symbol" in ceo_txt),
    }

    # Log markers
    live_markers = {}
    test_markers = {}
    live_log = Path(args.live_log)
    test_log = Path(args.test_log)
    if live_log.exists():
        live_text = live_log.read_text(errors="ignore")
        live_markers = grep_any(LOG_MARKERS, live_text)
    if test_log.exists():
        test_text = test_log.read_text(errors="ignore")
        test_markers = grep_any(["EXECUTING|TRADE EXECUTED|POSITION CLOSED"], test_text)

    # KPIs
    kpi_live = parse_kpis(live_log)
    kpi_test = parse_kpis(test_log)

    summary_ok = all(funcs.values()) and code_markers["RUN_loads_env"] and code_markers["CEO_env_overrides"]

    # Human summary
    print("=== Ultra Healthcheck ===")
    print(f"Env loaded: {'yes' if env_loaded else 'no'} | Telegram token: {'yes' if tok_present else 'no'}")
    print(f"Orchestrator funcs: {funcs}")
    print(f"Wired engines: {engines}")
    print(f"Code markers: {code_markers}")
    if live_markers:
        print(f"Live markers: {live_markers}")
    if test_markers:
        print(f"Test markers: {test_markers}")
    print(f"KPIs live: {kpi_live}")
    print(f"KPIs test: {kpi_test}")
    print(f"Overall code wiring OK: {'yes' if summary_ok else 'no'}")

    print("\nJSON:")
    print(json.dumps({
        "env_loaded": env_loaded,
        "telegram_token_present": tok_present,
        "orchestrator_funcs": funcs,
        "wired_engines": engines,
        "code_markers": code_markers,
        "live_markers": live_markers,
        "test_markers": test_markers,
        "kpi_live": kpi_live,
        "kpi_test": kpi_test,
        "ok": summary_ok,
    }, indent=2))


if __name__ == "__main__":
    main()
