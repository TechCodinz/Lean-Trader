from rpb_scalping import _timeframe_signal


def _rows(direction: int, count: int = 80):
    rows = []
    price = 100.0
    for i in range(count):
        drift = direction * (0.35 + (i % 5) * 0.02)
        open_price = price
        close_price = max(0.01, open_price + drift)
        high = max(open_price, close_price) + 0.08
        low = min(open_price, close_price) - 0.08
        volume = 1000.0 + i * 12.0
        rows.append([i * 60_000, open_price, high, low, close_price, volume])
        price = close_price
    return rows


def test_rising_real_candles_vote_buy():
    vote = _timeframe_signal(_rows(1))
    assert vote["direction"] == "BUY"
    assert vote["score"] > 0
    assert vote["ema_fast"] > vote["ema_slow"]
    assert vote["momentum_pct"] > 0


def test_falling_real_candles_vote_sell():
    vote = _timeframe_signal(_rows(-1))
    assert vote["direction"] == "SELL"
    assert vote["score"] < 0
    assert vote["ema_fast"] < vote["ema_slow"]
    assert vote["momentum_pct"] < 0


def test_missing_candles_abstain_instead_of_fabricating():
    vote = _timeframe_signal([])
    assert vote["direction"] == "NEUTRAL"
    assert vote["usable"] is False
