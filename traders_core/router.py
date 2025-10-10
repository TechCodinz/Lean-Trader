# router.py
import os
from pprint import pprint
from typing import Any, Dict, List, Optional

import ccxt


class ExchangeRouter:
    def __init__(self):
        self.mode = os.getenv("MARKET_MODE", os.getenv("EXCHANGE_MODE", "spot")).lower()
        # mode: spot | swap (linear USDT perp) | futures
        self.live = os.getenv("ENABLE_LIVE", "false").strip().lower() in ("1", "true", "yes", "on")
        self.paper = os.getenv("EXCHANGE_ID", "paper").lower() == "paper"
        self.testnet = os.getenv("BYBIT_TESTNET", "false").strip().lower() in ("1", "true", "yes", "on")
        self.quote_as_notional = (
            os.getenv("CCXT_QUOTE_AS_NOTIONAL", "true").strip().lower() in ("1", "true", "yes", "on")
        )

        # cache
        self.markets: Dict[str, Any] = {}
        self.id: str = os.getenv("EXCHANGE_ID", "bybit").lower()

        if self.paper:
            start_cash = float(os.getenv("PAPER_START_CASH", "5000"))
            self.ex = PaperBroker(start_cash)
        else:
            ex_id = self.id
            apiKey = os.getenv("API_KEY", "") or os.getenv(f"{ex_id.upper()}_API_KEY", "")
            secret = os.getenv("API_SECRET", "") or os.getenv(f"{ex_id.upper()}_API_SECRET", "")
            opts: Dict[str, Any] = {
                "enableRateLimit": True,
                "timeout": int(os.getenv("CCXT_TIMEOUT_MS", "20000")),
                "options": {
                    # respect futures default type
                    "defaultType": os.getenv("CCXT_DEFAULT_TYPE", "spot").lower(),
                },
            }
            # Testnet URLs where applicable
            if ex_id == "bybit" and self.testnet:
                opts["urls"] = {
                    "api": {
                        "public": "https://api-testnet.bybit.com",
                        "private": "https://api-testnet.bybit.com",
                    }
                }
            # Gate swap needs defaultType=swap for futures
            if ex_id == "gateio" and self.mode.startswith("swap"):
                opts["options"]["defaultType"] = "swap"

            self.ex = getattr(ccxt, ex_id)({"apiKey": apiKey, "secret": secret, **opts})
            # try to set unified params for linear
            try:
                if self.mode in ("swap", "linear") and hasattr(self.ex, "set_sandbox_mode"):
                    self.ex.set_sandbox_mode(bool(self.testnet))
            except Exception:
                pass

        self.markets = self._load_markets_safe()

    # -------- info / account --------
    def info(self) -> Dict[str, Any]:
        return {
            "paper": self.paper,
            "testnet": self.testnet,
            "mode": self.mode,
            "live": self.live,
            "id": self.id,
        }

    def account(self) -> Dict[str, Any]:
        try:
            if self.paper:
                return {
                    "ok": True,
                    "paper_cash": getattr(self.ex, "cash", 0.0),
                }
            if hasattr(self, "safe_fetch_balance"):
                return {"ok": True, "balance": self.safe_fetch_balance()}
            try:
                return {"ok": True, "balance": self.ex.fetch_balance()}
            except Exception:
                # fallback to an empty balance instead of raising
                return {"ok": True, "balance": {}}
        except Exception as _e:
            return {"ok": False, "error": str(_e)}

    def sample_symbols(self) -> List[str]:
        seeds = [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
            "DOGE/USDT",
        ]
        return [s for s in seeds if s in self.markets]

    # -------- data helpers --------
    def fetch_ohlcv(self, symbol: str, tf: str = "1m", limit: int = 120):
        # Prefer router's safe wrapper when available.
        # Fall back to direct exchange fetch with guarded errors.
        ex = getattr(self, "ex", None)
        try:
            if ex is None:
                return []
            try:
                return ex.fetch_ohlcv(
                    symbol,
                    timeframe=tf,
                    limit=limit,
                )
            except Exception as _e:
                print(
                    "[traders_core.router] fetch_ohlcv raw fetch failed for",
                    symbol,
                    _e,
                )
                return []
        except Exception as _e:
            print("[traders_core.router] fetch_ohlcv error for", symbol, _e)
            return []

    def last_price(self, symbol: str) -> float:
        try:
            t = self.safe_fetch_ticker(symbol)
            return float(t.get("last") or t.get("close") or 0)
        except Exception:
            return 0.0

    # -------- safe helpers (uniform APIs) --------
    def _load_markets_safe(self) -> Dict[str, Any]:
        try:
            mkts = {}
            try:
                mkts = self.ex.load_markets() or {}
            except Exception:
                pass
            if not isinstance(mkts, dict):
                # Some adapters might return a list; convert to dict if possible
                try:
                    mkts = {m.get("symbol") or m.get("id"): m for m in (mkts or []) if isinstance(m, dict)}
                except Exception:
                    mkts = {}
            return mkts
        except Exception as e:
            print("[router] load_markets error:", e)
            return {}

    def safe_fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        try:
            return self.ex.fetch_ticker(symbol) or {}
        except Exception as e:
            print("[router] fetch_ticker failed for", symbol, e)
            return {}

    def safe_fetch_balance(self) -> Dict[str, Any]:
        try:
            return self.ex.fetch_balance() or {}
        except Exception as e:
            print("[router] fetch_balance failed:", e)
            return {}

    def safe_fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 120) -> List[List[float]]:
        try:
            return self.ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit) or []
        except Exception as e:
            print("[router] fetch_ohlcv failed for", symbol, e)
            return []

    def spot_symbols(self, quote: str = "USDT") -> List[str]:
        try:
            syms: List[str] = []
            for sym, m in self.markets.items():
                if (m.get("spot") or m.get("type") == "spot") and str(m.get("quote", "")).upper() == quote.upper():
                    syms.append(sym)
            return syms
        except Exception:
            return []

    def linear_symbols(self, quote: str = "USDT") -> List[str]:
        try:
            syms: List[str] = []
            for sym, m in self.markets.items():
                # CCXT unified market flags
                if (m.get("swap") or m.get("linear")) and str(m.get("quote", "")).upper() == quote.upper():
                    syms.append(sym)
            return syms
        except Exception:
            return []

    def safe_place_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None, params: Optional[Dict[str, Any]] = None):
        params = params or {}
        try:
            order_type = "market" if not price else "limit"
            px = None if order_type == "market" else float(price)
            # precision helpers
            try:
                if px is not None:
                    px = float(self.ex.price_to_precision(symbol, px))
                amount = float(self.ex.amount_to_precision(symbol, amount))
            except Exception:
                pass
            o = self.ex.create_order(symbol, order_type, side, amount, px, params)
            return {"ok": True, "order": o}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def safe_close_position(self, symbol: str):
        try:
            params = {"reduceOnly": True}
            side = "sell"
            # Try to infer position direction to close oppositely (best-effort)
            return self.safe_place_order(symbol, side, 0.0, params=params)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # -------- spot --------
    def place_spot_market(self, symbol: str, side: str, qty: float = None, notional: float = None):
        try:
            if notional and self.quote_as_notional:
                px = self.last_price(symbol)
                qty = float(notional) / px
            # prefer router/adapter safe helpers first
            if hasattr(self.ex, "safe_place_order"):
                order = self.ex.safe_place_order(symbol, side, qty)
            elif hasattr(self.ex, "create_order"):
                try:
                    order = safe_create_order(self.ex, "market", symbol, side, qty)
                except Exception:
                    order = place_market(self.ex, symbol, side, qty)
            else:
                # last-resort: use shared helper; it has internal fallbacks
                order = place_market(self.ex, symbol, side, qty)

            # Normalize result: if the underlying adapter returned an error dict
            if isinstance(order, dict) and (order.get("ok") is False or order.get("error")):
                return {"ok": False, "error": order.get("error") or order}
            return {"ok": True, "result": order}
        except Exception as _e:
            return {"ok": False, "error": str(_e)}

    # -------- linear futures (USDT-perp) --------
    def place_futures_market(
        self,
        symbol: str,
        side: str,
        qty: float,
        leverage: int = None,
        close: bool = False,
    ):
        try:
            params = {}
            if leverage and hasattr(self.ex, "set_leverage"):
                try:
                    self.ex.set_leverage(leverage, symbol)
                except Exception:
                    # ignore errors when setting leverage
                    pass
            if close:
                params["reduceOnly"] = True
            if hasattr(self.ex, "safe_place_order"):
                order = self.ex.safe_place_order(
                    symbol,
                    side,
                    qty,
                    params=params,
                )
            elif hasattr(self.ex, "create_order"):
                try:
                    order = safe_create_order(
                        self.ex,
                        "market",
                        symbol,
                        side,
                        qty,
                        price=None,
                        params=params,
                    )
                except Exception:
                    order = place_market(self.ex, symbol, side, qty)
            else:
                order = place_market(self.ex, symbol, side, qty)
            if isinstance(order, dict) and (order.get("ok") is False or order.get("error")):
                return {"ok": False, "error": order.get("error") or order}
            return {"ok": True, "result": order}
        except Exception as _e:
            return {"ok": False, "error": str(_e)}

    # -------- quick scanner --------
    def scan_top_movers(self, topn: int = 10, quote: str = "USDT", limit: int = 120):
        movers = []
        for sym in list(self.markets.keys()):
            if not sym.endswith("/" + quote):
                continue

            try:
                bars = self.fetch_ohlcv(
                    sym,
                    "1m",
                    limit=limit,
                )
                if not bars:
                    continue

                c0 = bars[0][4]
                c1 = bars[-1][4]
                change = (c1 - c0) / c0
                movers.append(
                    {
                        "symbol": sym,
                        "change": change,
                        "last": c1,
                    }
                )
            except Exception:
                # ignore symbol-level errors
                pass
        movers.sort(
            key=lambda x: x["change"],
            reverse=True,
        )
        return movers[:topn]

if __name__ == "__main__":
    r = ExchangeRouter()
    pprint(r.info())
    pprint(r.account())
    pprint(r.sample_symbols())
    pprint(r.scan_top_movers(5))
