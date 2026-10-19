#!/usr/bin/env python3
"""
NEWS BUS SERVICE - the news organ, publishing to the nervous system.

news_service.py is a complete library (RSS harvest -> VADER-scored,
per-symbol filtered news) that nothing ever called. This service
drives it: every 30 minutes it harvests, aggregates the sentiment
of the top stories per watched symbol, and publishes a signal onto
the signal bus when sentiment is materially one-sided - where the
sentient brain adjudicates it like any other organ's signal.
Republishes only when the aggregate moves (>=0.1) or 4h pass.
Executes nothing.
"""
import logging
import os
import time
import urllib.parse
import urllib.request

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - NEWS_BUS - %(message)s')
logger = logging.getLogger('NEWS_BUS')

SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT',
           'XRP/USDT', 'ADA/USDT']
CYCLE = 1800
MIN_ARTICLES = 3
MIN_SENTIMENT = 0.20


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


def main():
    import news_service
    import signal_bus

    last_pub = {}  # symbol -> (agg, ts)
    logger.info('News bus service live - harvesting RSS, publishing sentiment')
    tg('📰 News organ live: RSS sentiment now publishes to the signal bus.')
    while True:
        try:
            added = news_service.harvest_rss()
            rows = news_service.build_clean()
            logger.info(f'harvest: +{added} new, {rows} clean rows')
            for sym in SYMBOLS:
                items = news_service.filtered_news_for(sym, False, top_n=8)
                # Recency: the raw file carries a 2025 backlog - only
                # the last 72h of news may move a signal.
                cutoff = time.time() - 72 * 3600
                items = [i for i in items if i.get('ts', 0) >= cutoff]
                if len(items) < MIN_ARTICLES:
                    continue
                wsum = sum(i['score'] for i in items) or 1.0
                agg = sum(i['sent'] * i['score'] for i in items) / wsum
                if abs(agg) < MIN_SENTIMENT:
                    continue
                prev = last_pub.get(sym)
                now = time.time()
                if prev and abs(agg - prev[0]) < 0.1 and now - prev[1] < 4 * 3600:
                    continue
                signal_bus.publish_signal(
                    'news', sym, 'BUY' if agg > 0 else 'SELL',
                    int(abs(agg) * 100),
                    metadata={'strategy': 'News Sentiment',
                              'articles': len(items),
                              'agg_sentiment': round(agg, 3),
                              'top_title': items[0]['title'][:110]})
                last_pub[sym] = (agg, now)
                logger.info(f'published {sym} {"BUY" if agg > 0 else "SELL"} '
                            f'sent {agg:+.3f} over {len(items)} articles')
        except Exception as e:
            logger.warning(f'cycle: {e}')
        time.sleep(CYCLE)


if __name__ == '__main__':
    main()
