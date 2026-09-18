import unittest
from unittest.mock import patch

from REAL_PROFIT_BOT import REAL_PROFIT_BOT


class _FakeMarketData:
    def __init__(self):
        self.bulk_calls = 0
        self.single_calls = 0

    def fetch_tickers(self):
        self.bulk_calls += 1
        return {
            "DOT/USDT": {"last": 1.10, "percentage": 4.2, "quoteVolume": 2_000_000},
            "SOL/USDT": {"last": 100.0, "percentage": 2.1, "quoteVolume": 5_000_000},
        }

    def fetch_ticker(self, symbol):
        self.single_calls += 1
        raise AssertionError("fast path should use one bulk ticker snapshot")


class TestRPBFastPath(unittest.TestCase):
    def test_bulk_ticker_snapshot_serves_multiple_symbols(self):
        bot = REAL_PROFIT_BOT.__new__(REAL_PROFIT_BOT)
        bot.market_data = _FakeMarketData()
        bot._ticker_snapshot = {}
        bot._ticker_snapshot_at = 0.0
        bot.fast_ticker_refresh_seconds = 1.0

        first = bot.get_gate_ticker("DOT/USDT")
        second = bot.get_gate_ticker("SOL/USDT")

        self.assertEqual(bot.market_data.bulk_calls, 1)
        self.assertEqual(bot.market_data.single_calls, 0)
        self.assertEqual(first["price"], 1.10)
        self.assertEqual(second["price"], 100.0)

    def test_rpb_risk_budget_is_not_fractioned_twice(self):
        bot = REAL_PROFIT_BOT.__new__(REAL_PROFIT_BOT)
        bot.mode = "testnet"
        bot.execution_exchange_id = "bybit"
        bot.risk = None
        bot._alpha_size_multiplier = 1.0
        bot.check_gate_balance = lambda: 13.5

        captured = {}

        class _Prepared:
            def to_payload(self):
                return {"symbol": "DOT/USDT", "side": "buy", "qty": 1.0}

        def fake_prepare(intent, policy=None):
            captured["intent"] = dict(intent)
            captured["policy"] = policy
            return _Prepared(), None

        with patch("src.leantrader.execution.preflight.prepare_order", side_effect=fake_prepare), \
             patch("src.leantrader.execution.preflight.record_event"), \
             patch("src.leantrader.execution.preflight.classify_receipt", return_value=None), \
             patch("src.leantrader.execution.preflight.invalidate_balance_cache"), \
             patch("src.leantrader.execution.router.route_order", return_value={
                 "ok": True,
                 "executed": True,
                 "order": {"id": "x", "filled": 1.0, "average": 1.0, "cost": 1.0},
             }):
            bot.execute_trade("DOT/USDT", "BUY", 1.0, confidence=0.99)

        self.assertGreater(captured["intent"]["risk_budget"], 0.0)
        self.assertIsNotNone(captured["policy"])
        self.assertEqual(captured["policy"].allocation_fraction, 1.0)
        self.assertEqual(captured["policy"].max_fraction, 1.0)


if __name__ == "__main__":
    unittest.main()
