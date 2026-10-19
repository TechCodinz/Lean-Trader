#!/usr/bin/env python3
"""
HEDGE FUND ARSENAL SERVICE v2 - the 2025 arsenal, actually running.

The 2026 wrapper constructed the strategies and heartbeated. Worse,
the pairs engine drew its market ratio from np.random - the data hub
it was designed against was never built. v2:
- Builds the real MarketDataHub (data_hub.py): live prices in,
  signals out onto the signal bus.
- Primes the pairs ratio histories with 60 REAL hourly ratios so
  z-scores are meaningful immediately.
- Runs the arsenal's own loop (stat arb every 5 min, publishing
  through the hub) plus a volatility cycle using the arsenal's own
  VolatilityTrading on real closes (primed with rolling realized
  vols). Signals are published, never executed by this service -
  pairs execution is two-legged and gets its own executor when the
  signal record justifies it.
- SmartOrderRouter is an execution utility (order splitting);
  nothing to run at our slice sizes.
"""
import asyncio
import logging
import os
import time
import urllib.parse
import urllib.request

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - HEDGE_FUND - %(message)s')
logger = logging.getLogger('HEDGE_FUND')

VOL_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']


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


async def vol_cycle(arsenal, hub):
    """Volatility signals from the arsenal's own strategy on real data."""
    vt = arsenal.vol_trading
    # Prime the vol history with rolling realized vols (real closes)
    try:
        closes = hub.closes('BTC/USDT', 120)
        for end in range(40, len(closes), 4):
            v = vt.calculate_realized_volatility(closes[end - 40:end])
            vt.volatility_history.append(v)
        logger.info(f'vol history primed: {len(vt.volatility_history)} points')
    except Exception as e:
        logger.warning(f'vol prime: {e}')
    while True:
        try:
            for sym in VOL_SYMBOLS:
                closes = hub.closes(sym, 60)
                vol = vt.calculate_realized_volatility(closes[-40:])
                sig = vt.generate_volatility_signal(sym, vol)
                if sig:
                    await hub.publish_signal(sig)
        except Exception as e:
            logger.warning(f'vol cycle: {e}')
        await asyncio.sleep(300)


async def main():
    from data_hub import MarketDataHub
    from HEDGE_FUND_ARSENAL import HedgeFundArsenal

    hub = MarketDataHub()
    arsenal = HedgeFundArsenal(hub)
    hub.prime_stat_arb(arsenal.stat_arb)
    logger.info('Hedge Fund Arsenal live - real data hub, primed histories')
    tg('🏦 Hedge Fund Arsenal live: stat-arb (real ratios) + volatility '
       'strategies publishing to the signal bus.')
    await asyncio.gather(
        arsenal.run_hedge_fund_strategies(),
        vol_cycle(arsenal, hub),
    )


if __name__ == '__main__':
    asyncio.run(main())
