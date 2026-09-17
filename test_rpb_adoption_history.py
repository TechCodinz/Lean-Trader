from rpb_adoption_history import collect_windowed_trades


def test_collect_windowed_trades_walks_older_windows_and_deduplicates():
    day = 86_400_000
    now = 30 * day
    calls = []

    rows = {
        (0, 7 * day - 1): [
            {"id": "b1", "timestamp": 2 * day, "side": "buy", "amount": 10, "price": 1},
        ],
        (7 * day, 14 * day - 1): [
            {"id": "s1", "timestamp": 10 * day, "side": "sell", "amount": 4, "price": 1.1},
        ],
        (14 * day, 21 * day - 1): [
            {"id": "b2", "timestamp": 18 * day, "side": "buy", "amount": 3, "price": 0.9},
            {"id": "s1", "timestamp": 10 * day, "side": "sell", "amount": 4, "price": 1.1},
        ],
        (21 * day, 28 * day - 1): [],
        (28 * day, 30 * day): [],
    }

    def fake_fetch(symbol, since=None, limit=None, params=None):
        start = int(params["startTime"])
        end = int(params["endTime"])
        calls.append((symbol, since, limit, start, end))
        return rows.get((start, end), [])

    result = collect_windowed_trades(
        fake_fetch,
        "CSPR/USDT",
        now_ms=now,
        lookback_days=30,
        window_days=7,
        page_limit=100,
    )

    assert [row["id"] for row in result] == ["b1", "s1", "b2"]
    assert calls[0][3:] == (0, 7 * day - 1)
    assert calls[-1][3:] == (28 * day, 30 * day)


def test_collect_windowed_trades_keeps_chronological_order_when_api_returns_reverse():
    day = 86_400_000

    def fake_fetch(symbol, since=None, limit=None, params=None):
        return [
            {"id": "new", "timestamp": 6 * day, "side": "buy", "amount": 1, "price": 2},
            {"id": "old", "timestamp": 1 * day, "side": "buy", "amount": 1, "price": 1},
        ]

    result = collect_windowed_trades(
        fake_fetch,
        "DOT/USDT",
        now_ms=7 * day,
        lookback_days=7,
        window_days=7,
        page_limit=100,
    )

    assert [row["id"] for row in result] == ["old", "new"]
