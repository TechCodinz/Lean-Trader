import math

def normalize_market_order(exchange, symbol: str, side: str, cost_usdt: float, price: float) -> dict:
    if not exchange:
        raise ValueError("exchange is None")
    ex_id = (getattr(exchange, "id", "") or "").lower()
    side_norm = (side or "buy").lower()
    cost_usdt = float(cost_usdt)
    price = float(price) if price else 0.0
    if cost_usdt <= 0 or price <= 0:
        raise ValueError("cost_usdt and price must be > 0")
    params = {}
    mode = "base_amount"
    if "gate" in ex_id:
        if side_norm == "buy":
            mode = "quote_cost"
            amount = cost_usdt
            params["cost"] = cost_usdt
            if not hasattr(exchange, "options") or exchange.options is None:
                exchange.options = {}
            exchange.options["createMarketBuyOrderRequiresPrice"] = False
            return {"type": "market", "side": "buy", "amount": float(amount), "params": params,
                    "meta": {"mode": mode, "exchange_id": getattr(exchange, "id", "unknown")}}
        base_amount = cost_usdt / price
        return {"type": "market", "side": "sell", "amount": float(base_amount), "params": params,
                "meta": {"mode": mode, "exchange_id": getattr(exchange, "id", "unknown")}}
    base_amount = cost_usdt / price
    return {"type": "market", "side": side_norm, "amount": float(base_amount), "params": params,
            "meta": {"mode": mode, "exchange_id": getattr(exchange, "id", "unknown")}}
