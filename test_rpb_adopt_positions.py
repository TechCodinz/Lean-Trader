from rpb_adopt_positions import (
    build_report,
    extract_position_rows,
    reconstruct_cost_basis_from_trades,
)


def test_extract_position_rows_preserves_quantity_and_cost_basis():
    state = {
        "positions": {
            "DOT/USDT": {
                "quantity": 1.25,
                "average_entry": 4.0,
                "entry_cost": 5.0,
            }
        }
    }
    rows = extract_position_rows(state)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "DOT/USDT"
    assert rows[0]["quantity"] == 1.25
    assert rows[0]["average_entry"] == 4.0
    assert rows[0]["entry_cost"] == 5.0


def test_extract_position_rows_uses_position_cost_basis_map():
    state = {
        "positions": {"CSPR/USDT": 100.0},
        "position_cost_basis": {
            "CSPR/USDT": {"average_entry": 0.02, "entry_cost": 2.0}
        },
    }
    rows = extract_position_rows(state)
    assert rows[0]["quantity"] == 100.0
    assert rows[0]["average_entry"] == 0.02
    assert rows[0]["entry_cost"] == 2.0


def test_reconstruct_cost_basis_from_authenticated_buy_history():
    trades = [
        {
            "timestamp": 1,
            "side": "buy",
            "amount": 100.0,
            "price": 0.02,
            "cost": 2.0,
            "fee": {"currency": "USDT", "cost": 0.002},
        },
        {
            "timestamp": 2,
            "side": "buy",
            "amount": 50.0,
            "price": 0.03,
            "cost": 1.5,
            "fee": {"currency": "USDT", "cost": 0.0015},
        },
    ]
    rebuilt = reconstruct_cost_basis_from_trades("CSPR/USDT", 150.0, trades)
    assert rebuilt["ok"] is True
    assert abs(rebuilt["entry_cost"] - 3.5035) < 1e-12
    assert abs(rebuilt["average_entry"] - (3.5035 / 150.0)) < 1e-12


def test_reconstruct_cost_basis_reduces_remaining_basis_after_sell():
    trades = [
        {"timestamp": 1, "side": "buy", "amount": 10.0, "price": 2.0, "cost": 20.0},
        {"timestamp": 2, "side": "sell", "amount": 4.0, "price": 3.0, "cost": 12.0},
    ]
    rebuilt = reconstruct_cost_basis_from_trades("DOT/USDT", 6.0, trades)
    assert rebuilt["ok"] is True
    assert abs(rebuilt["entry_cost"] - 12.0) < 1e-12
    assert abs(rebuilt["average_entry"] - 2.0) < 1e-12


def test_reconstruct_cost_basis_refuses_incomplete_history():
    trades = [
        {"timestamp": 1, "side": "sell", "amount": 1.0, "price": 4.0, "cost": 4.0},
    ]
    rebuilt = reconstruct_cost_basis_from_trades("DOT/USDT", 1.0, trades)
    assert rebuilt["ok"] is False
    assert rebuilt["reason"] == "trade_history_does_not_cover_inventory"


def test_build_report_allows_explicit_authenticated_dust_quarantine():
    rows = [
        {
            "symbol": "DOT/USDT",
            "quantity": 0.0015,
            "average_entry": 0.0,
            "entry_cost": 0.0,
            "basis_reconstruction_reason": "trade_history_does_not_cover_inventory",
            "dust_quarantine": {
                "ok": True,
                "authenticated_total": 0.0015,
                "price": 0.94,
                "notional": 0.00141,
                "min_notional": 1.0,
                "reason": "authenticated_non_executable_dust",
            },
        }
    ]
    balance = {"total": {"DOT": 0.0015}}
    report = build_report({}, balance, rows=rows)
    assert report["ok"] is True
    assert report["ambiguous"] == []
    assert len(report["quarantined_dust"]) == 1
    assert report["quarantined_dust"][0]["symbol"] == "DOT/USDT"


def test_build_report_quarantines_non_executable_dust_even_with_known_basis():
    rows = [
        {
            "symbol": "JASMY/USDT",
            "quantity": 0.03989,
            "average_entry": 0.0052,
            "entry_cost": 0.000207428,
            "dust_quarantine": {
                "ok": True,
                "price": 0.0053,
                "notional": 0.000211417,
                "min_notional": 1.0,
                "reason": "authenticated_non_executable_dust",
            },
        }
    ]
    balance = {"total": {"JASMY": 0.03989}}
    report = build_report({}, balance, rows=rows)
    assert report["ok"] is True
    assert report["adoptable"] == []
    assert len(report["quarantined_dust"]) == 1
    assert report["quarantined_dust"][0]["symbol"] == "JASMY/USDT"


def test_build_report_still_blocks_unpriced_material_inventory():
    rows = [
        {
            "symbol": "DOT/USDT",
            "quantity": 2.0,
            "average_entry": 0.0,
            "entry_cost": 0.0,
            "basis_reconstruction_reason": "trade_history_does_not_cover_inventory",
        }
    ]
    balance = {"total": {"DOT": 2.0}}
    report = build_report({}, balance, rows=rows)
    assert report["ok"] is False
    assert len(report["ambiguous"]) == 1
    assert report["quarantined_dust"] == []
