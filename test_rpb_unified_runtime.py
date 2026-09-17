import inspect

from REAL_PROFIT_BOT import REAL_PROFIT_BOT


def test_rpb_accepts_explicit_mode_and_owned_close_amount():
    init_params = inspect.signature(REAL_PROFIT_BOT.__init__).parameters
    trade_params = inspect.signature(REAL_PROFIT_BOT.execute_trade).parameters
    assert "mode" in init_params
    assert "amount" in trade_params


def test_rpb_has_authenticated_position_lifecycle():
    for name in (
        "_record_buy_fill",
        "manage_owned_positions",
        "_settle_exit",
        "_feedback_after_close",
    ):
        assert hasattr(REAL_PROFIT_BOT, name)


def test_rpb_loop_has_no_historical_45_or_15_second_freeze():
    source = inspect.getsource(REAL_PROFIT_BOT.run_real_profit_trading)
    assert "time.sleep(45)" not in source
    assert "time.sleep(15)" not in source


def test_rpb_position_management_precedes_new_entry_scan():
    source = inspect.getsource(REAL_PROFIT_BOT.run_real_profit_trading)
    assert source.index("manage_owned_positions") < source.index("analyze_market")
