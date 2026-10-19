#!/usr/bin/env python3
"""
MarketDataHub - the data hub the 2025 systems were designed against.

Several 2025 components take a `data_hub` (HedgeFundArsenal and its
StatisticalArbitrage above all): the hub was supposed to supply real
market data in and carry signals out to the nervous system. It was
never built - wrappers passed None and the one consumer that needed
prices fell back to np.random. This hub is that missing organ:

- get_ratio(a1, a2): the CURRENT real price ratio from live closes.
- ratio_series(a1, a2, n): aligned historical ratios (for priming).
- closes(symbol, n): recent hourly closes.
- publish_signal(signal): onto the signal bus (the nervous system's
  blackboard) + an append-only JSONL record.

Public market data only (ccxt); no keys, no orders.
"""
import json
import logging
import os
import time

logger = logging.getLogger('DATA_HUB')

RECORD = '/app/runtime/hedge_signals.jsonl'


class MarketDataHub:
    def __init__(self):
        import ccxt
        self.ex = ccxt.bybit({'enableRateLimit': True})
        self._closes_cache = {}
        self._cache_ts = {}

    def closes(self, symbol, n=120):
        now = time.time()
        if symbol in self._closes_cache and now - self._cache_ts.get(symbol, 0) < 240:
            return self._closes_cache[symbol][-n:]
        # Perp symbols; and the fetch MUST be since-bounded: an
        # unbounded fetch_ohlcv on this API returns the OLDEST candle
        # page (2020/2021), verified 2026-10-19. since = now - n hours
        # returns the current window.
        fetch_sym = f'{symbol}:USDT' if symbol.endswith('/USDT') else symbol
        since = int((now - (n + 5) * 3600) * 1000)
        rows = self.ex.fetch_ohlcv(fetch_sym, '1h', since, n)
        closes = [float(r[4]) for r in rows]
        self._closes_cache[symbol] = closes
        self._cache_ts[symbol] = now
        return closes

    def get_ratio(self, asset1, asset2):
        c1 = self.closes(asset1, 5)
        c2 = self.closes(asset2, 5)
        if not c1 or not c2 or c2[-1] == 0:
            return None
        return c1[-1] / c2[-1]

    def ratio_series(self, asset1, asset2, n=60):
        c1 = self.closes(asset1, n + 20)
        c2 = self.closes(asset2, n + 20)
        m = min(len(c1), len(c2), n)
        if m <= 0:
            return []
        return [a / b for a, b in zip(c1[-m:], c2[-m:]) if b]

    def prime_stat_arb(self, stat_arb):
        """Seed the pairs ratio histories with REAL ratios so the
        z-scores mean something from the first cycle."""
        for pair in stat_arb.pairs:
            series = self.ratio_series(pair[0], pair[1], 60)
            if series:
                stat_arb.ratio_history[pair].extend(series)
                logger.info(f'primed {pair[0]}/{pair[1]}: {len(series)} real ratios, '
                            f'last {series[-1]:.5f}')

    async def publish_signal(self, signal):
        """Carry a signal onto the bus + the durable record."""
        try:
            import signal_bus
            signal_bus.publish_signal(
                'hedge_fund', signal.get('symbol', '?'),
                signal.get('side', 'BUY'),
                int(float(signal.get('confidence', 0)) * 100),
                metadata={'strategy': signal.get('strategy'),
                          'type': signal.get('type'),
                          'reasoning': signal.get('reasoning'),
                          'z_score': signal.get('z_score')})
        except Exception as e:
            logger.warning(f'bus publish: {e}')
        try:
            os.makedirs(os.path.dirname(RECORD), exist_ok=True)
            with open(RECORD, 'a') as f:
                f.write(json.dumps({'ts': time.time(), **signal}) + '\n')
        except Exception:
            pass
        logger.info(f"🏦 SIGNAL {signal.get('strategy')}: {signal.get('symbol')} "
                    f"{signal.get('side')} conf {signal.get('confidence')}")
