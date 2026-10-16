import json, time
from pathlib import Path
LEDGER = Path('/tmp/pnl_ledger.jsonl')

def record(engine, symbol, side, entry, exit_px, qty):
    pnl_usd = (exit_px - entry) * qty
    if side == 'SELL': pnl_usd = -pnl_usd
    pnl_pct = (exit_px - entry) / entry * 100 if entry else 0
    if side == 'SELL': pnl_pct = -pnl_pct
    entry_data = {
        'ts': time.time(), 'engine': engine, 'symbol': symbol,
        'side': side, 'entry': entry, 'exit': exit_px, 'qty': qty,
        'pnl_usd': round(pnl_usd, 4), 'pnl_pct': round(pnl_pct, 2)
    }
    with open(LEDGER, 'a') as f:
        f.write(json.dumps(entry_data) + '\n')
    return entry_data

def summary():
    if not LEDGER.exists(): return "No trades yet"
    trades = [json.loads(l) for l in open(LEDGER)]
    total = sum(t['pnl_usd'] for t in trades)
    wins = sum(1 for t in trades if t['pnl_usd'] > 0)
    return f"Trades: {len(trades)} | Wins: {wins} | P&L: \${total:.2f}"
