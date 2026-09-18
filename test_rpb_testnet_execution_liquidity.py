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


if __name__ == "__main__":
    unittest.main()
