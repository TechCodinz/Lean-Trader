import unittest
from unittest.mock import patch

from rpb_runtime_entry import UnifiedRPBRuntime


class _FakeLedger:
    def __init__(self):
        self.positions = {"DOT/USDT": {"symbol": "DOT/USDT"}}
        self.load_calls = 0
        self.save_calls = 0

    def load(self):
        self.load_calls += 1
        # Simulate the separate recovery ledger having just written newly
        # adopted dust positions to disk.
        self.positions = {
            "DOT/USDT": {"symbol": "DOT/USDT"},
            "ETH/USDT": {"symbol": "ETH/USDT"},
            "MNT/USDT": {"symbol": "MNT/USDT"},
        }
        return len(self.positions)

    def save(self):
        self.save_calls += 1
        return True


class _FakeQuarantine:
    def active(self):
        return {
            "ETH/USDT": {"kind": "dust"},
            "MNT/USDT": {"kind": "dust"},
        }


class TestOwnershipSweepLedgerSync(unittest.TestCase):
    def test_recovery_reload_happens_before_dust_filter(self):
        runtime = UnifiedRPBRuntime.__new__(UnifiedRPBRuntime)
        runtime.mode = "testnet"
        runtime.execution_exchange_id = "bybit"
        runtime.lifecycle_enabled = True
        runtime.ledger = _FakeLedger()
        runtime.quarantine_store = _FakeQuarantine()
        runtime.blocked_pairs = set()
        runtime._last_epoch_sweep = 0.0
        runtime._epoch_start_ms = lambda: 1789648101000

        with patch(
            "rpb_runtime_entry.recover_current_epoch_to_ledger",
            return_value={
                "ok": True,
                "adopted": [],
            },
        ) as recover:
            runtime._recover_epoch_ownership(force=True)

        recover.assert_called_once_with(
            since_ms=1789648101000,
            mode="testnet",
            exchange_id="bybit",
            exclude_symbols={"ETH/USDT", "MNT/USDT"},
        )

        self.assertEqual(runtime.ledger.load_calls, 1)
        self.assertEqual(set(runtime.ledger.positions), {"DOT/USDT"})
        self.assertEqual(runtime.ledger.save_calls, 1)
        self.assertIn("ETH/USDT", runtime.blocked_pairs)
        self.assertIn("MNT/USDT", runtime.blocked_pairs)


if __name__ == "__main__":
    unittest.main()
