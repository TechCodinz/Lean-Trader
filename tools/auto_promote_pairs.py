#!/usr/bin/env python3
"""
Union-preserving promoter:
- Reads a source log (testnet) for executed and closed trades
- Selects best pairs (min trades, min winrate), blends with most-active executed
- Unions with existing universe_dynamic.json (never wipes existing)
- Writes back to target JSON { pairs: [...], stats: { closed: {}, executed: {} } }

Usage:
  python tools/auto_promote_pairs.py --source /path/to/testnet.log \
      --target /path/to/worktree/universe_dynamic.json \
      --min-trades 1 --min-winrate 0.50 --top 150 --interval 60
"""
import argparse
import json
import re
import time
from pathlib import Path

sym_re = re.compile(r"Symbol:\s+(\S+)")
pnl_re = re.compile(r"P&L:\s*\$([+-]?\d+(?:\.\d+)?)")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--min-trades", type=int, default=1)
    ap.add_argument("--min-winrate", type=float, default=0.50)
    ap.add_argument("--top", type=int, default=150)
    ap.add_argument("--interval", type=int, default=60)
    return ap.parse_args()


def extract_closed(lines):
    stats = {}
    for i, l in enumerate(lines):
        if "\ud83d\udcb0 POSITION CLOSED:" in l or "POSITION CLOSED:" in l:
            blk = lines[i:i+12]
            sym, pnl = None, None
            for w in blk:
                if sym is None:
                    m = sym_re.search(w)
                    if m:
                        sym = m.group(1)
                if pnl is None:
                    m = pnl_re.search(w)
                    if m:
                        try:
                            pnl = float(m.group(1))
                        except Exception:
                            pnl = None
            if sym and pnl is not None:
                d = stats.setdefault(sym, {"trades": 0, "wins": 0, "pnl": 0.0})
                d["trades"] += 1
                d["wins"] += 1 if pnl > 0 else 0
                d["pnl"] += pnl
    for v in stats.values():
        v["winrate"] = v["wins"] / max(1, v["trades"])
    return stats


def extract_executed(lines):
    stats = {}
    for i, l in enumerate(lines):
        if "\u26a1 TRADE EXECUTED:" in l or "\u26a1 EXECUTING:" in l or "TRADE EXECUTED:" in l or "EXECUTING:" in l:
            blk = lines[i:i+8]
            sym = None
            for w in blk:
                m = sym_re.search(w)
                if m:
                    sym = m.group(1)
                    break
            if sym:
                d = stats.setdefault(sym, {"trades": 0})
                d["trades"] += 1
    return stats


def union_keep(existing, picked, top):
    seen = set()
    out = []
    for s in list(existing) + list(picked):
        if s not in seen:
            seen.add(s)
            out.append(s)
        if len(out) >= top:
            break
    return out


def main():
    args = parse_args()
    src = Path(args.source)
    tgt = Path(args.target)
    tgt.parent.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            base = []
            if tgt.exists():
                try:
                    cur = json.loads(tgt.read_text(errors="ignore"))
                    base = cur.get("pairs", []) if isinstance(cur, dict) else (cur if isinstance(cur, list) else [])
                except Exception:
                    base = []

            if not src.exists():
                print(f"[auto-promote] waiting for source: {src}")
                time.sleep(args.interval)
                continue

            L = src.read_text(errors="ignore").splitlines()
            closed = extract_closed(L)
            execd = extract_executed(L)

            picked = []
            # From closed by pnl, winrate
            for s, v in sorted(closed.items(), key=lambda kv: (kv[1]["pnl"], kv[1].get("winrate", 0.0)), reverse=True):
                if v["trades"] >= args.min_trades and v.get("winrate", 0.0) >= args.min_winrate:
                    picked.append(s)
            # Fill with most active executed
            if len(picked) < args.top:
                for s, v in sorted(execd.items(), key=lambda kv: kv[1]["trades"], reverse=True):
                    if s not in picked:
                        picked.append(s)
                    if len(picked) >= args.top:
                        break

            final = union_keep(base, picked, args.top)
            tmp = tgt.with_suffix(".tmp")
            tmp.write_text(json.dumps({"pairs": final, "stats": {"closed": closed, "executed": execd}}, indent=2))
            tmp.replace(tgt)
            print(f"[auto-promote] pairs={len(final)} (seed={len(base)} closed={len(closed)} exec={len(execd)}) -> {tgt}")
        except Exception as e:
            print(f"[auto-promote] ERROR: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
