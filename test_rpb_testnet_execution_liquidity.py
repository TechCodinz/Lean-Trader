import unittest

from rpb_runtime_hardening import assess_testnet_execution_book


class TestTestnetExecutionLiquidity(unittest.TestCase):
    def test_two_sided_liquid_book_passes(self):
        result = assess_testnet_execution_book(
            {
                "bids": [[1.12463, 889.1735], [1.12462, 500.0]],
                "asks": [[1.12465, 131.1404], [1.12466, 300.0]],
            },
            target_quote=5.10,
            max_spread_bps=250.0,
            min_depth_multiple=1.25,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["reason"], "executable")

    def test_missing_asks_is_blocked(self):
        result = assess_testnet_execution_book(
            {"bids": [[0.4392, 102.113]], "asks": []},
            target_quote=5.10,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "missing_ask_liquidity")

    def test_wide_spread_is_blocked_even_with_depth(self):
        result = assess_testnet_execution_book(
            {
                "bids": [[0.63, 800.0]],
                "asks": [[1.10, 20.0]],
            },
            target_quote=5.10,
            max_spread_bps=250.0,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "spread_too_wide")

    def test_roundtrip_depth_is_required(self):
        result = assess_testnet_execution_book(
            {
                "bids": [[1.00, 2.0]],
                "asks": [[1.001, 2.0]],
            },
            target_quote=5.10,
            min_depth_multiple=1.25,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "insufficient_roundtrip_depth")

    def test_sui_like_book_is_blocked_by_roundtrip_friction(self):
        result = assess_testnet_execution_book(
            {
                "bids": [
                    [0.90, 2.64], [0.89, 1.21], [0.88, 1.21],
                    [0.87, 1.21], [0.86, 1.21], [0.85, 1.21],
                ],
                "asks": [
                    [0.92, 1.42], [0.93, 1.42], [0.94, 1.42],
                    [0.95, 1.42], [0.96, 1.42], [0.97, 1.42],
                ],
            },
            target_quote=5.10,
            max_spread_bps=250.0,
            min_depth_multiple=1.0,
            max_roundtrip_friction_bps=25.0,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "roundtrip_friction_too_high")
        self.assertGreater(result["roundtrip_friction_bps"], 25.0)


if __name__ == "__main__":
    unittest.main()
