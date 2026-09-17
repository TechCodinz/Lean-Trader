from rpb_fill_reconciliation import (
    aggregate_order_trades,
    reconstruct_epoch_positions,
)


def test_aggregate_order_trades_recovers_delayed_market_fill():
    trades = [
        {
            "order": "abc-123",
            "symbol": "DOT/USDT",
            "side": "buy",
            "amount": 1.5,
            "price": 1.02,
            "cost": 1.53,
            "timestamp": 10,
            "fee": {"currency": "DOT", "cost": 0.0015},
        },
        {
            "order": "other",
            "symbol": "DOT/USDT",
            "side": "buy",
            "amount": 9.0,
            "price": 1.0,
            "cost": 9.0,
            "timestamp": 11,
        },
    ]

    fill = aggregate_order_trades("abc-123", "DOT/USDT", trades)

    assert fill["filled"] == 1.5
    assert fill["cost"] == 1.53
    assert fill["average"] == 1.02
    assert fill["fee_base"] == 0.0015
    assert fill["order_id"] == "abc-123"


def test_reconstruct_epoch_positions_uses_only_post_epoch_trades_and_caps_to_balance():
    trades = [
        {
            "order": "old",
            "symbol": "DOT/USDT",
            "side": "buy",
            "amount": 50.0,
            "price": 1.0,
            "cost": 50.0,
            "timestamp": 999,
        },
        {
            "order": "new-1",
            "symbol": "DOT/USDT",
            "side": "buy",
            "amount": 2.0,
            "price": 1.0,
            "cost": 2.0,
            "timestamp": 1000,
        },
        {
            "order": "new-2",
            "symbol": "DOT/USDT",
            "side": "buy",
            "amount": 2.0,
            "price": 1.1,
            "cost": 2.2,
            "timestamp": 1001,
        },
    ]
    balance = {"total": {"DOT": 3.9}}

    positions = reconstruct_epoch_positions(trades, balance, since_ms=1000)

    assert len(positions) == 1
    row = positions[0]
    assert row["symbol"] == "DOT/USDT"
    assert abs(row["quantity"] - 3.9) < 1e-12
    # Original post-epoch basis is 4.2 for 4.0 DOT. Capping to 3.9 scales cost.
    assert abs(row["entry_cost"] - 4.095) < 1e-12
    assert abs(row["average_entry"] - 1.05) < 1e-12
    assert row["source"] == "authenticated_testnet_epoch_trade_history"


def test_reconstruct_epoch_positions_accounts_for_sell_and_does_not_reopen_closed_symbol():
    trades = [
        {
            "order": "buy",
            "symbol": "ETH/USDT",
            "side": "buy",
            "amount": 0.01,
            "price": 2000.0,
            "cost": 20.0,
            "timestamp": 2000,
        },
        {
            "order": "sell",
            "symbol": "ETH/USDT",
            "side": "sell",
            "amount": 0.01,
            "price": 2010.0,
            "cost": 20.1,
            "timestamp": 2001,
        },
    ]
    balance = {"total": {"ETH": 0.5}}

    positions = reconstruct_epoch_positions(trades, balance, since_ms=2000)

    assert positions == []
