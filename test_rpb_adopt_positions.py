from rpb_adopt_positions import extract_position_rows


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
