#!/usr/bin/env python3
"""Run conservative RPB adoption with windowed history and dust quarantine."""

from __future__ import annotations

import rpb_adopt_positions as adoption
from rpb_adoption_dust import annotate_unpriced_dust
from rpb_adoption_history import fetch_authenticated_trade_history


# Patch only read-only evidence sources. The base adoption flow still owns all
# balance matching, ambiguity refusal, idempotence and ledger application.
adoption.fetch_authenticated_trade_history = fetch_authenticated_trade_history
_original_enrich = adoption.enrich_missing_basis_from_authenticated_history


def _enrich_with_history_then_dust(rows):
    enriched = _original_enrich(rows)
    return annotate_unpriced_dust(enriched)


adoption.enrich_missing_basis_from_authenticated_history = _enrich_with_history_then_dust


if __name__ == "__main__":
    raise SystemExit(adoption.main())
