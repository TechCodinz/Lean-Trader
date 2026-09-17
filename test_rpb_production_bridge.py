import json
from pathlib import Path

from rpb_production_bridge import RPBProductionBridge


def test_bridge_reads_symbol_evidence_without_execution_authority(tmp_path):
    fabric = tmp_path / "vps_evolution_fabric.json"
    fabric.write_text(
        json.dumps(
            {
                "cycles": 6103,
                "capabilities": {
                    "microstructure": {
                        "symbol": "BTC/USDT",
                        "direction": "buy",
                        "confidence": 0.81,
                        "spread_bps": 4.2,
                    },
                    "other": {
                        "symbol": "ETH/USDT",
                        "direction": "sell",
                        "confidence": 0.72,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    bridge = RPBProductionBridge(fabric_path=fabric)
    signal, confidence, detail = bridge.evaluate(
        "BTC/USDT", "BUY", 85.0, {"price": 100.0}
    )

    assert signal == "BUY"
    assert confidence >= 85.0
    assert detail["available"] is True
    assert detail["matched_evidence"] >= 1
    assert detail["cycles"] == 6103
    assert not hasattr(bridge, "create_order")
    assert not hasattr(bridge, "route_order")
    assert not hasattr(bridge, "execute_trade")


def test_bridge_fails_open_when_missing(tmp_path):
    bridge = RPBProductionBridge(fabric_path=tmp_path / "missing.json")
    signal, confidence, detail = bridge.evaluate(
        "BTC/USDT", "BUY", 88.0, {"price": 100.0}
    )

    assert signal == "BUY"
    assert confidence == 88.0
    assert detail["available"] is False
    assert detail["reason"] == "fabric_missing"


def test_bridge_never_invents_direction(tmp_path):
    fabric = tmp_path / "vps_evolution_fabric.json"
    fabric.write_text(
        json.dumps(
            {
                "cycles": 10,
                "evidence": [
                    {
                        "symbol": "BTC/USDT",
                        "direction": "sell",
                        "confidence": 0.99,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    bridge = RPBProductionBridge(fabric_path=fabric)
    signal, confidence, detail = bridge.evaluate(
        "BTC/USDT", "BUY", 91.0, {"price": 100.0}
    )

    assert signal == "BUY"
    assert 0.0 <= confidence <= 99.0
    assert detail["available"] is True
