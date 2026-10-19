#!/usr/bin/env python3
"""
SENTIENT BRAIN SERVICE v2 - the adjudication loop, running.

The 2026 wrapper constructed the brain and slept; nothing ever
routed a signal through it. v2 runs the loop the bus was designed
for: raw signals (hedge fund, news, fleet) -> SentientTradingBrain
.process_signal (StrategyValidator gates live vs validation) ->
decisions published back onto the bus for any executor to read.

The validator hydrates from /app/runtime/strategy_capacity.json -
the learned state the bus bridge maintains from real closes - and
re-reads it every cycle, so this brain and the bridge's brain
adjudicate from one shared memory. This service executes nothing.
"""
import asyncio
import json
import logging
import os
import time
import urllib.parse
import urllib.request

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - SENTIENT - %(message)s')
logger = logging.getLogger('SENTIENT')

CURSOR = '/app/runtime/sentient_cursor.json'
CAPACITY = '/app/runtime/strategy_capacity.json'
CYCLE = 20


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
        with open(CURSOR) as f:
            return set(json.load(f).get('processed') or [])
    except Exception:
        return set()


def save_cursor(processed):
    try:
        os.makedirs(os.path.dirname(CURSOR), exist_ok=True)
        tmp = CURSOR + '.tmp'
        with open(tmp, 'w') as f:
            json.dump({'processed': sorted(processed)[-2000:]}, f)
        os.replace(tmp, CURSOR)
    except Exception:
        pass


def fingerprint(sig):
    return (f"{sig.get('timestamp')}|{sig.get('source')}|"
            f"{sig.get('symbol')}|{sig.get('signal')}")


async def main():
    import signal_bus
    from data_hub import MarketDataHub
    from SENTIENT_TRADING_BRAIN import SentientTradingBrain

    brain = SentientTradingBrain(data_hub=MarketDataHub(),
                                 execution_orchestrator=None)
    processed = load_cursor()
    logger.info(f'Sentient brain adjudicating (validator knows '
                f'{len(brain.validator.strategy_scores)} strategies)')
    tg('🧠 Sentient Brain live: adjudicating bus signals through the '
       'StrategyValidator (live vs validation) and publishing decisions.')

    while True:
        try:
            # Track the bridge's learning as it accrues
            try:
                with open(CAPACITY) as f:
                    brain.validator.strategy_scores = \
                        json.load(f).get('scores') or {}
            except Exception:
                pass
            for _item in signal_bus.get_pending_signals():
                sig = _item[1] if isinstance(_item, tuple) else _item
                fp = fingerprint(sig)
                if fp in processed:
                    continue
                meta = sig.get('metadata') or {}
                strategy = meta.get('strategy') or sig.get('source', 'unknown')
                norm = {
                    'strategy': strategy,
                    'symbol': sig.get('symbol', 'UNKNOWN'),
                    'side': sig.get('signal', 'BUY'),
                    'confidence': float(sig.get('confidence', 0)) / 100.0,
                }
                out = await brain.process_signal(norm)
                approved = bool(out.get('sentient_approved'))
                signal_bus.publish_decision(
                    'sentient_brain', norm['symbol'],
                    'APPROVE_LIVE' if approved else 'VALIDATE_TESTNET',
                    int(float(sig.get('confidence', 0))),
                    f"strategy '{strategy}': "
                    f"{'validator-approved' if approved else 'not yet approved - validation only'}",
                    metadata={'side': norm['side'], 'strategy': strategy})
                processed.add(fp)
                logger.info(f"adjudicated {norm['symbol']} {norm['side']} "
                            f"({strategy}) -> "
                            f"{'APPROVE_LIVE' if approved else 'VALIDATE_TESTNET'}")
            save_cursor(processed)
        except Exception as e:
            logger.warning(f'cycle: {e}')
        await asyncio.sleep(CYCLE)


if __name__ == '__main__':
    asyncio.run(main())
