#!/usr/bin/env python3
"""Run the conservative RPB adoption utility with windowed Testnet history."""

from __future__ import annotations

import rpb_adopt_positions as adoption
from rpb_adoption_history import fetch_authenticated_trade_history


# Patch only the read-only history source used by the existing conservative
# adoption flow. All basis reconstruction, balance matching, ambiguity refusal,
# idempotence, and apply behavior remain in rpb_adopt_positions.py.
adoption.fetch_authenticated_trade_history = fetch_authenticated_trade_history


if __name__ == "__main__":
    raise SystemExit(adoption.main())
