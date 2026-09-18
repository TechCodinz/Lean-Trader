import unittest

from rpb_fill_reconciliation import reconstruct_epoch_positions


class TestRPBRecoveryPrecision(unittest.TestCase):
    def test_float_residual_snaps_to_authenticated_balance(self):
        trades = [
            {
                "order": "buy-dot",
                "symbol": "DOT/USDT",
                "side": "buy",
                "amount": 1.6126,
                "price": 1.04858,
                "cost": 1.690940108,
                "timestamp": 1000,
            },
            {
                "order": "sell-dot",
                "symbol": "DOT/USDT",
                "side": "sell",
                "amount": 1.6125,
                "price": 1.04862,
                "cost": 1.69089975,
                "timestamp": 1001,
            },
        ]
        balance = {"total": {"DOT": 0.0001}}

        positions = reconstruct_epoch_positions(trades, balance, since_ms=1000)

        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["symbol"], "DOT/USDT")
        # Authenticated exchange balance is the final quantity arbiter when the
        # trade-history residual differs only by floating-point arithmetic.
        self.assertEqual(positions[0]["quantity"], 0.0001)


if __name__ == "__main__":
    unittest.main()
