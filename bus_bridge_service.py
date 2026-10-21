#!/usr/bin/env python3
"""
BUS BRIDGE - the learning loop of the being, finally closed.

The 2025 design: SENSORS -> signals -> BRAINS -> decisions ->
EXECUTORS -> outcomes -> LEARNERS. In this restoration the outcome
leg was never reconnected: OnlineLearner and the SentientBrain sat
idle (the sentient service literally slept in a heartbeat loop)
because nothing fed them results.

The capacity ledger (being_ledger.jsonl) is now the being's outcome
stream - every close from every being lands there with symbol, P&L,
real/paper flag and entry strategy. This bridge tails it and feeds:

- online_learner.reward_from_exit_safe(symbol, pnl) for EVERY close
  (paper is the learning environment; real is the proof).
- SentientTradingBrain.learn_from_trade(...) for REAL closes only,
  mode='testnet' - which internally feeds StrategyValidator, the
  testnet-probation machinery: a strategy earns 'approved' status
  only with enough testnet trades at a high enough win rate.

Validator state is persisted every cycle to
/app/runtime/strategy_capacity.json (durable across restarts, and
readable by the governor later). The bridge has NO trading power:
it learns and reports, nothing else.
"""
import json
import logging
import os
import time
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - BUS_BRIDGE - %(message)s')
logger = logging.getLogger('BUS_BRIDGE')

LEDGER = '/app/runtime/being_ledger.jsonl'
CURSOR_PATH = '/app/runtime/bridge_cursor.json'
CAPACITY_PATH = '/app/runtime/strategy_capacity.json'
CYCLE = 30


def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN')
    cid = os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not cid:
        return
    try:
        data = urllib.parse.urlencode({'chat_id': cid, 'text': msg}).encode()
        urllib.request.urlopen(
            urllib.request.Request(
                f'https://api.telegram.org/bot{tok}/sendMessage', data=data),
            timeout=10)
    except Exception:
        pass


def load_cursor():
    try:
        return int(json.load(open(CURSOR_PATH)).get('offset', 0))
    except Exception:
        return 0


def save_cursor(offset):
    try:
        with open(CURSOR_PATH, 'w') as f:
            json.dump({'offset': offset}, f)
    except Exception:
        pass


def read_new_rows(offset):
    rows = []
    try:
        size = os.path.getsize(LEDGER)
        if offset > size:
            offset = 0
        with open(LEDGER, 'rb') as f:
            f.seek(offset)
            chunk = f.read()
        new_offset = offset + len(chunk)
        for line in chunk.decode(errors='ignore').splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        return rows, new_offset
    except FileNotFoundError:
        return [], offset


def main():
    from SENTIENT_TRADING_BRAIN import SentientTradingBrain
    import online_learner as ol

    brain = SentientTradingBrain(data_hub=None, execution_orchestrator=None)
    logger.info('Bus bridge live - feeding learners from the capacity ledger')
    tg('🚌 Bus bridge live: OnlineLearner + SentientBrain now learn from every close.')
    offset = load_cursor()
    fed_learner = fed_brain = 0
    summary_tick = 0
    while True:
        try:
            rows, offset = read_new_rows(offset)
            for r in rows:
                sym = r.get('symbol', 'UNKNOWN')
                pnl = float(r.get('pnl') or 0)
                meta = r.get('meta') or {}
                strat = meta.get('strat') or r.get('being', 'unknown')
                # TRUTH ROUTING (2026-10-21): a being's own real
                # record is an estimate; its exchange twin
                # (source='exchange', written by the truth
                # service from fill prices + fees) is the record
                # the learners, the pair study and the brain are
                # fed. Skip the estimate; the twin follows in
                # the same stream.
                if r.get('real') and r.get('source') != 'exchange':
                    continue
                try:
                    ol.reward_from_exit_safe(sym, pnl)
                    fed_learner += 1
                except Exception as e:
                    logger.warning(f'learner feed {sym}: {e}')
                if r.get('real'):
                    # PAIR STUDY (Princewill's design, 2026-10-20):
                    # EVERY pair is under continuous study, so a
                    # trade goes in on studied ground. Every real
                    # close updates the pair's measured record (wins
                    # AND losses: trades, win rate, expectancy); a
                    # loss additionally writes its full context to
                    # the loss log - the system reads WHY the pair
                    # lost, the swarm deploys on its pattern, and
                    # nothing is ever gated.
                    try:
                        import time as _t
                        base = sym.replace(':USDT', '')
                        sp = '/app/runtime/pair_study.json'
                        try:
                            with open(sp) as f:
                                study = json.load(f)
                        except Exception:
                            study = {}
                        e = study.setdefault(base, {
                            'losses': 0, 'total_lost': 0.0, 'trades': 0,
                            'wins': 0, 'total_pnl': 0.0,
                            'beings': {}, 'strategies': {},
                            'first_seen_ts': _t.time()})
                        e['trades'] = e.get('trades', 0) + 1
                        e['total_pnl'] = round(e.get('total_pnl', 0.0) + pnl, 4)
                        if pnl > 0:
                            e['wins'] = e.get('wins', 0) + 1
                        e['win_rate'] = round(e['wins'] / max(1, e['trades']), 3)
                        e['expectancy'] = round(e['total_pnl'] / max(1, e['trades']), 4)
                        e['last_close_ts'] = _t.time()
                        if pnl < 0:
                            rec = {'ts': _t.time(), 'symbol': base,
                                   'being': r.get('being'), 'pnl': pnl,
                                   'meta': meta}
                            with open('/app/runtime/pair_losses.jsonl', 'a') as f:
                                f.write(json.dumps(rec) + '\n')
                            e['losses'] += 1
                            e['total_lost'] = round(e['total_lost'] + pnl, 4)
                            e['last_loss_ts'] = _t.time()
                            e['last_context'] = {'being': r.get('being'),
                                                 'pnl': pnl, 'meta': meta}
                            bkey = str(r.get('being'))
                            e['beings'][bkey] = e['beings'].get(bkey, 0) + 1
                            skey = str(strat)
                            e['strategies'][skey] = e['strategies'].get(skey, 0) + 1
                            logger.info(f'LOSS STUDY: {base} loss #{e["losses"]} '
                                        f'({pnl:+.4f} by {r.get("being")}) - '
                                        f'pair under study, total {e["total_lost"]:+.4f}')
                        tmp = sp + '.tmp'
                        with open(tmp, 'w') as f:
                            json.dump(study, f, indent=1)
                        os.replace(tmp, sp)
                    except Exception as e:
                        logger.warning(f'pair study {sym}: {e}')
                if r.get('real'):
                    try:
                        brain.learn_from_trade({
                            'strategy': strat,
                            'symbol': sym,
                            'side': 'BUY',
                            'profit': pnl,
                            'trading_mode': 'testnet',
                        })
                        fed_brain += 1
                    except Exception as e:
                        logger.warning(f'brain feed {sym}: {e}')
            if rows:
                save_cursor(offset)
                logger.info(f'fed {len(rows)} outcome(s) '
                            f'(learner total {fed_learner}, brain total {fed_brain})')
            # Persist validator capacity every cycle
            try:
                scores = getattr(brain.validator, 'strategy_scores', {})
                approved = [s for s in scores
                            if brain.validator.is_strategy_approved(s)]
                with open(CAPACITY_PATH, 'w') as f:
                    json.dump({'ts': time.time(), 'scores': scores,
                               'approved': approved}, f, indent=1)
            except Exception as e:
                logger.warning(f'capacity persist: {e}')
            # STUDY SEEDING (Princewill): every NEW pair the
            # system discovers enters study on sight - before any
            # trade - so the analysis is already vast when capital
            # arrives. Watching entries carry no record yet, only
            # presence; closes build their measured record.
            try:
                sp = '/app/runtime/pair_study.json'
                try:
                    with open(sp) as f:
                        study = json.load(f)
                except Exception:
                    study = {}
                added = 0
                for path in ('/tmp/discovered_pairs.json',
                             '/tmp/trending_pairs.json'):
                    try:
                        with open(path) as f:
                            data = json.load(f)
                        items = data.get('pairs', data) if isinstance(data, dict) else data
                        for x in items or []:
                            v = x.get('symbol') if isinstance(x, dict) else x
                            if not v:
                                continue
                            base = str(v).replace(':USDT', '')
                            if '/' not in base:
                                base = base + '/USDT'
                            if base not in study:
                                study[base] = {
                                    'losses': 0, 'total_lost': 0.0,
                                    'trades': 0, 'wins': 0, 'total_pnl': 0.0,
                                    'win_rate': 0.0, 'expectancy': 0.0,
                                    'beings': {}, 'strategies': {},
                                    'first_seen_ts': time.time(),
                                    'watching': True}
                                added += 1
                    except Exception:
                        pass
                if added:
                    tmp = sp + '.tmp'
                    with open(tmp, 'w') as f:
                        json.dump(study, f, indent=1)
                    os.replace(tmp, sp)
                    logger.info(f'STUDY SEED: {added} new pair(s) entered study '
                                f'({len(study)} pairs under study)')
            except Exception as e:
                logger.warning(f'study seed: {e}')
            summary_tick += 1
            if summary_tick >= 20:
                summary_tick = 0
                scores = getattr(brain.validator, 'strategy_scores', {})
                if scores:
                    top = sorted(scores.items(),
                                 key=lambda kv: kv[1].get('total_profit', 0),
                                 reverse=True)[:3]
                    logger.info('validator top: ' + '; '.join(
                        f"{k} wr {v['win_rate']:.0%} n={v['trades']} ${v['total_profit']:+.2f}"
                        for k, v in top))
        except Exception as e:
            logger.warning(f'bridge cycle: {e}')
        time.sleep(CYCLE)


if __name__ == '__main__':
    main()
