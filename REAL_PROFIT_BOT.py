#!/usr/bin/env python3
"""REAL_PROFIT_BOT unified runtime.

RPB is the single order-producing owner. Public market data, historical
strategy intelligence, production/evolution evidence, risk sizing and learning
all advise RPB; authenticated order placement remains in LeanTrader's universal
execution router.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import ccxt
import requests

from ccxt_exchange_compat import resolve_exchange_class


class REAL_PROFIT_BOT:
    def __init__(self, mode: str = "testnet", universe=None):
        requested = str(mode or os.getenv("EXECUTION_MODE", "testnet")).strip().lower()
        if requested not in {"testnet", "live", "paper"}:
            requested = "testnet"
        self.mode = requested

        # Testnet is the default and remains explicit. Live requires the caller
        # to construct the bot with mode="live" and the router to possess live
        # authority; nothing here auto-promotes an account.
        self.execution_exchange_id = str(
            os.getenv("CCXT_EXCHANGE")
            or os.getenv("EXCHANGE_ID")
            or ("bybit" if self.mode == "testnet" else os.getenv("LEGACY_PROFIT_EXCHANGE", "gateio"))
        ).strip().lower()

        # Market intelligence intentionally uses PUBLIC production market data,
        # even while execution is Testnet. Testnet liquidity/tickers are too
        # sparse to be a useful signal source. No credentials are attached.
        market_exchange_id = str(os.getenv("RPB_MARKET_DATA_EXCHANGE", "bybit")).strip().lower()
        market_class = resolve_exchange_class(ccxt, market_exchange_id)
        market_options: Dict[str, Any] = {"enableRateLimit": True}
        if market_exchange_id == "bybit":
            market_options["options"] = {"defaultType": "spot"}
        self.market_data = market_class(market_options)

        # Telegram credentials/channels stay external to source. A missing
        # channel is a notification issue, never a trading failure.
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
        self.vip_chat_id = os.getenv("TELEGRAM_VIP_CHAT_ID", "")
        self.free_chat_id = os.getenv("TELEGRAM_FREE_CHAT_ID", "")

        self.running = True
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0  # synchronized from authenticated ledger only
        self._last_reasoning = ""
        self._last_alpha_attribution: List[str] = []
        self._alpha_size_multiplier = 1.0

        self.blocked_pairs = set()
        self.last_pair_refresh = 0.0
        self.dynamic_pair_refresh_seconds = float(os.getenv("RPB_PAIR_REFRESH_SECONDS", "60") or 60)
        self.dynamic_pair_min_volume_usd = float(os.getenv("RPB_MIN_24H_VOLUME_USD", "1000000") or 1_000_000)
        self.entry_confidence = float(os.getenv("RPB_ENTRY_CONFIDENCE", "85") or 85)
        self.post_entry_sleep = float(os.getenv("RPB_POST_ENTRY_SLEEP_SECONDS", "0.5") or 0.5)
        self.cycle_sleep = float(os.getenv("RPB_CYCLE_SLEEP_SECONDS", "0.5") or 0.5)
        self.fast_ticker_refresh_seconds = float(os.getenv("RPB_FAST_TICKER_SECONDS", "0.75") or 0.75)
        self._ticker_snapshot: Dict[str, Dict[str, Any]] = {}
        self._ticker_snapshot_at = 0.0

        if universe:
            self.crypto_pairs = [str(x) for x in universe if "/" in str(x)]
            self.universe_source = "provided"
        else:
            self.crypto_pairs = [
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
                "XRP/USDT",
                "ADA/USDT",
                "DOT/USDT",
                "MNT/USDT",
                "USDC/USDT",
            ]
            self.universe_source = "fallback"

        self._connect_components()

        print("🚀 REAL PROFIT BOT INITIALIZED")
        print(f"🧭 EXECUTION MODE: {self.mode.upper()}")
        print(f"💱 EXECUTION VENUE: {self.execution_exchange_id}")
        print("📡 MARKET DATA: public production feeds")
        print(f"📊 STARTING UNIVERSE: {len(self.crypto_pairs)} ({self.universe_source})")

    # --------------------------------------------------------- components

    def _connect_components(self) -> None:
        try:
            from rpb_intelligence import MarketIntelligence
            self.intelligence = MarketIntelligence()
            print(f"🧠 MARKET INTELLIGENCE: {self.intelligence.reason}")
        except Exception as exc:
            self.intelligence = None
            print(f"⚠️ MARKET INTELLIGENCE unavailable: {type(exc).__name__}")

        try:
            from rpb_scalping import ScalpingConfluence
            self.scalping = ScalpingConfluence()
            print(f"⚡ SCALPING CONFLUENCE: {self.scalping.reason}")
        except Exception as exc:
            self.scalping = None
            print(f"⚠️ SCALPING CONFLUENCE unavailable: {type(exc).__name__}")

        try:
            from rpb_alpha_risk import AlphaEnsemble, RiskGovernor
            self.alpha = AlphaEnsemble()
            self.risk = RiskGovernor()
            print(f"🎯 ALPHA ENSEMBLE: {self.alpha.reason} ({len(self.alpha.strategy_names())} strategies)")
            print(f"🛡️ RISK GOVERNOR: {self.risk.reason}")
        except Exception as exc:
            self.alpha = None
            self.risk = None
            print(f"⚠️ ALPHA/RISK unavailable: {type(exc).__name__}")

        try:
            from rpb_production_bridge import RPBProductionBridge
            self.production_bridge = RPBProductionBridge()
            health = self.production_bridge.health()
            print(f"🧬 EVOLUTION FABRIC: {health.get('reason')} cycles={health.get('cycles', 0)}")
        except Exception as exc:
            self.production_bridge = None
            print(f"⚠️ EVOLUTION FABRIC unavailable: {type(exc).__name__}")

        try:
            from rpb_position_lifecycle import ExitEvaluator, PositionLedger
            self.ledger = PositionLedger()
            self.exit_evaluator = ExitEvaluator()
            self.lifecycle_enabled = True
            self.total_profit = self.ledger.realized_net_total()
            self.winning_trades = self.ledger.stats()["authentic_wins"]
            print(f"📒 POSITION LEDGER: open={len(self.ledger.open_symbols())} closed={self.ledger.stats()['closed_positions']}")
        except Exception as exc:
            self.ledger = None
            self.exit_evaluator = None
            self.lifecycle_enabled = False
            print(f"⚠️ POSITION LIFECYCLE unavailable: {type(exc).__name__}")

        try:
            from rpb_telegram import SignalDistributor
            self.signals = SignalDistributor(
                self.send_telegram,
                admin_chat_id=self.admin_chat_id,
                vip_chat_id=self.vip_chat_id,
                free_chat_id=self.free_chat_id,
            )
            print(f"📣 TELEGRAM ROUTES: admin={bool(self.admin_chat_id)} premium={bool(self.vip_chat_id)} free={bool(self.free_chat_id)}")
        except Exception as exc:
            self.signals = None
            print(f"⚠️ TELEGRAM DISTRIBUTION unavailable: {type(exc).__name__}")

    # ------------------------------------------------------------- routing

    def send_telegram(self, message, chat_id=None):
        chat_id = chat_id or self.admin_chat_id
        if not self.telegram_bot_token or not chat_id:
            return False
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
                timeout=10,
            )
            return bool(response.ok)
        except Exception as exc:
            print(f"⚠️ Telegram delivery failed: {type(exc).__name__}")
            return False

    def check_gate_balance(self):
        from src.leantrader.execution.router import route_balance
        try:
            balance = route_balance(mode=self.mode, exchange_id=self.execution_exchange_id) or {}
            free = balance.get("free") or {}
            value = free.get("USDT") if isinstance(free, dict) else None
            if value is None and isinstance(balance.get("USDT"), dict):
                value = balance["USDT"].get("free")
            return float(value or 0.0)
        except Exception as exc:
            print(f"❌ Balance unavailable: {type(exc).__name__}")
            return 0.0

    def _refresh_fast_ticker_snapshot(self, *, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """Refresh one public-production ticker snapshot for the whole scan.

        Historical micro runtimes were fast because they did not perform one
        REST ticker request per symbol. RPB keeps that behavior: one bulk
        snapshot feeds the entire scan, while per-symbol fetch remains a
        fallback only if the venue cannot provide bulk tickers.
        """
        now = time.time()
        if (
            not force
            and self._ticker_snapshot
            and now - self._ticker_snapshot_at < max(0.1, self.fast_ticker_refresh_seconds)
        ):
            return self._ticker_snapshot
        try:
            tickers = self.market_data.fetch_tickers() or {}
            if isinstance(tickers, dict) and tickers:
                self._ticker_snapshot = {
                    str(symbol): dict(ticker)
                    for symbol, ticker in tickers.items()
                    if isinstance(ticker, dict)
                }
                self._ticker_snapshot_at = now
        except Exception:
            pass
        return self._ticker_snapshot

    def get_gate_ticker(self, symbol):
        snapshot = self._refresh_fast_ticker_snapshot()
        ticker = snapshot.get(symbol) if isinstance(snapshot, dict) else None
        if not isinstance(ticker, dict):
            try:
                ticker = self.market_data.fetch_ticker(symbol) or {}
            except Exception:
                return None
        try:
            price = float(ticker.get("last") or ticker.get("close") or 0.0)
            if price <= 0:
                return None
            return {
                "price": price,
                "change": float(ticker.get("percentage") or 0.0),
                "volume": float(ticker.get("quoteVolume") or 0.0),
            }
        except Exception:
            return None

    # ------------------------------------------------------------- universe

    def set_universe(self, symbols) -> int:
        accepted = []
        try:
            from src.leantrader.execution.preflight import normalize_symbol
        except Exception:
            normalize_symbol = lambda value: str(value or "")
        for symbol in symbols or []:
            normalized = normalize_symbol(symbol)
            if normalized:
                accepted.append(normalized)
        if accepted:
            self.crypto_pairs = accepted
            self.universe_source = "orchestrator"
        return len(self.crypto_pairs)

    def _execution_market_symbols(self) -> Optional[set]:
        try:
            from src.leantrader.execution.preflight import load_markets_cached, shared_broker
            broker = shared_broker(
                execution_mode=self.mode,
                exchange_id=self.execution_exchange_id,
                market_mode="spot",
            )
            markets = load_markets_cached(broker) or {}
            return {
                symbol
                for symbol, market in markets.items()
                if isinstance(market, dict)
                and market.get("spot") is True
                and market.get("active") is not False
                and str(market.get("quote") or "").upper() == "USDT"
                and ":" not in symbol
            }
        except Exception:
            return None

    def refresh_dynamic_pairs(self):
        try:
            self.market_data.load_markets()
            tickers = self._refresh_fast_ticker_snapshot(force=True) or {}
            executable = self._execution_market_symbols()
            discovered = []
            for symbol, ticker in tickers.items():
                market = self.market_data.markets.get(symbol) or {}
                if not market.get("spot") or str(market.get("quote") or "").upper() != "USDT":
                    continue
                if market.get("active") is False or ":" in symbol or symbol in self.blocked_pairs:
                    continue
                if executable is not None and symbol not in executable:
                    continue
                try:
                    last = float(ticker.get("last") or 0.0)
                    volume = float(ticker.get("quoteVolume") or 0.0)
                    change = float(ticker.get("percentage") or 0.0)
                except Exception:
                    continue
                if last <= 0 or volume < self.dynamic_pair_min_volume_usd:
                    continue
                discovered.append((symbol, abs(change), volume))
            discovered.sort(key=lambda row: (row[1], row[2]), reverse=True)
            pairs = [row[0] for row in discovered]
            if pairs:
                self.crypto_pairs = pairs
                self.universe_source = "dynamic_public+execution_eligible"
                print(f"🔍 DYNAMIC PAIRS: {len(pairs)} executable liquid USDT spot markets")
                print("🔥 TOP MOVERS: " + ", ".join(pairs[:15]))
            self.last_pair_refresh = time.time()
        except Exception as exc:
            print(f"⚠️ Dynamic pair refresh failed: {type(exc).__name__}")
        return self.crypto_pairs

    # --------------------------------------------------------- intelligence

    def analyze_market(self, symbol):
        ticker_data = self.get_gate_ticker(symbol)
        if not ticker_data:
            return "HOLD", 0.0, 0.0, 0.0, 0.0

        price = ticker_data["price"]
        change = ticker_data["change"]
        volume = ticker_data["volume"]
        signals: List[str] = []
        confidences: List[float] = []

        if abs(change) > 3.0 and volume > 1_000_000:
            signals.append("BUY" if change > 0 else "SELL")
            confidences.append(95.0)
        if volume > 5_000_000 and abs(change) > 2.0:
            signals.append("BUY" if change > 0 else "SELL")
            confidences.append(90.0)
        if symbol in {"BTC/USDT", "ETH/USDT"} and abs(change) > 1.5 and volume > 10_000_000:
            signals.append("BUY" if change > 0 else "SELL")
            confidences.append(85.0)
        if symbol in {"ADA/USDT", "XRP/USDT", "SOL/USDT", "BNB/USDT", "DOT/USDT"} and change > 4.0 and volume > 2_000_000:
            signals.append("BUY")
            confidences.append(90.0)

        if not signals:
            return "HOLD", 50.0, price, change, volume

        best = confidences.index(max(confidences))
        signal = signals[best]
        confidence = confidences[best]
        reasoning: List[str] = [f"24h change {change:+.2f}%", f"24h volume ${volume:,.0f}"]

        if self.intelligence is not None:
            signal, confidence, detail = self.intelligence.evaluate(
                self.market_data, symbol, signal, confidence, price
            )
            if detail.get("applied"):
                reasoning.append(
                    f"RSI {detail.get('rsi')} MACD {detail.get('macd_histogram')} "
                    f"spread {detail.get('spread_bps')}bps imbalance {detail.get('imbalance')}"
                )

        if signal != "HOLD" and self.scalping is not None:
            confidence, detail = self.scalping.evaluate(
                self.market_data, symbol, signal, confidence
            )
            if detail.get("applied"):
                reasoning.append(
                    f"MTF {detail.get('direction')} consensus {detail.get('consensus')} session {detail.get('session')}"
                )

        self._alpha_size_multiplier = 1.0
        self._last_alpha_attribution = []
        if signal == "BUY" and self.alpha is not None:
            confidence, multiplier, detail = self.alpha.evaluate(
                self.market_data, symbol, signal, confidence
            )
            self._alpha_size_multiplier = multiplier
            self._last_alpha_attribution = list(detail.get("attributed_strategies") or [])
            if detail.get("notes"):
                reasoning.append(f"alpha {detail.get('prob')}: {detail.get('notes')}")

        if signal != "HOLD" and self.production_bridge is not None:
            signal, confidence, detail = self.production_bridge.evaluate(
                symbol,
                signal,
                confidence,
                {"price": price, "change": change, "volume": volume},
            )
            if detail.get("available") and detail.get("matched_evidence"):
                reasoning.append(
                    f"evolution cycles={detail.get('cycles')} matches={detail.get('matched_evidence')} "
                    f"agree={detail.get('agree')} conflict={detail.get('conflict')}"
                )

        self._last_reasoning = " | ".join(reasoning)[:1200]
        return signal, confidence, price, change, volume

    # ----------------------------------------------------------- execution

    def execute_trade(self, symbol, signal, price, amount=None, confidence=0.0):
        from src.leantrader.execution import preflight
        from src.leantrader.execution.router import route_order

        side = str(signal or "").lower()
        if side not in {"buy", "sell"}:
            return None

        intent: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "reference_price": float(price or 0.0),
            "order_type": "market",
            "confidence": max(0.0, min(1.0, float(confidence or 0.0))),
            "execution_mode": self.mode,
            "exchange_id": self.execution_exchange_id,
            "market_mode": "spot",
        }

        if amount is not None and float(amount or 0.0) > 0:
            intent["amount"] = float(amount)
        elif side == "buy":
            balance = self.check_gate_balance()
            try:
                from rpb_scalping import target_position_usd
                target_usd, phase = target_position_usd(balance)
            except Exception:
                target_usd, phase = max(3.50, balance * 0.25), "fallback"
            if self.risk is not None:
                self.risk.sync_wallet(balance)
                target_usd, _ = self.risk.cap_position(
                    symbol,
                    target_usd,
                    float(confidence or 0.0) * 100.0,
                    self._alpha_size_multiplier,
                )
            intent["risk_budget"] = min(max(0.0, target_usd), max(0.0, balance))
            print(f"🌱 {phase} sizing: wallet=${balance:.6f} budget=${intent['risk_budget']:.6f}")

        policy = None
        if side == "buy" and float(intent.get("risk_budget") or 0.0) > 0.0:
            # RPB has already produced the final authenticated-wallet risk
            # budget via its growth ladder / risk governor. Do not apply the
            # generic allocation fraction a second time inside preflight.
            # Preflight still retains fee reserve, venue floors, precision,
            # balance checks, and every execution safety check.
            base_policy = preflight.SizingPolicy.from_env()
            policy = preflight.SizingPolicy(
                allocation_fraction=1.0,
                max_fraction=1.0,
                fee_reserve_multiple=base_policy.fee_reserve_multiple,
                absolute_reserve_quote=base_policy.absolute_reserve_quote,
            )

        prepared, blocked = preflight.prepare_order(intent, policy=policy)
        if prepared is None:
            if blocked is not None:
                print(f"⏭️ PRECHECK {symbol} {signal}: {blocked.blocker} {blocked.detail}")
            return blocked.as_dict() if blocked else None

        preflight.record_event("submitted")
        receipt = route_order(prepared.to_payload(), mode=self.mode)
        blocker = preflight.classify_receipt(receipt)
        if blocker is not None:
            preflight.record_blocker(blocker, str(receipt.get("error", ""))[:200])
            print(f"❌ ORDER {symbol} {signal}: {blocker} {receipt.get('error', '')}")
            return receipt

        preflight.record_event("acknowledged")
        preflight.invalidate_balance_cache()

        try:
            from rpb_position_lifecycle import reconcile_fill
            fill = reconcile_fill(receipt, symbol)
            if fill.get("filled", 0.0) > 0:
                preflight.record_event("fills")
        except Exception:
            pass

        return receipt

    # ------------------------------------------------------------ lifecycle

    def _record_buy_fill(self, symbol, receipt, signal_price, confidence=0.0):
        if not self.lifecycle_enabled:
            return None
        from rpb_position_lifecycle import reconcile_fill
        fill = reconcile_fill(receipt, symbol)
        if fill["filled"] <= 0:
            print(f"⚠️ BUY ACK WITHOUT FILL: {symbol} status={fill['raw_status'] or 'unknown'}")
            return None
        session = self.scalping.current_session() if self.scalping is not None else "unknown"
        record = self.ledger.open_position(
            symbol,
            fill,
            strategy="rpb_momentum+intelligence",
            confidence=confidence,
            signal_price=signal_price,
            attribution=self._last_alpha_attribution,
            session=session,
        )
        if not record:
            return None
        if self.risk is not None:
            self.risk.sync_position(symbol, record["sellable_quantity"], record["average_entry"])
        print(
            f"📒 POSITION OPENED: {symbol} qty={record['sellable_quantity']:.12f} "
            f"entry=${record['average_entry']:.8f} cost=${record['entry_cost']:.6f}"
        )
        if self.signals is not None:
            self.signals.broadcast_entry(
                symbol,
                record["average_entry"],
                record["sellable_quantity"],
                record["entry_cost"],
                confidence,
                reasoning=self._last_reasoning,
                take_profit_bps=self.exit_evaluator.take_profit_bps,
                stop_loss_bps=self.exit_evaluator.stop_loss_bps,
            )
        return record

    def _current_spread_bps(self, symbol: str) -> Optional[float]:
        try:
            book = self.market_data.fetch_order_book(symbol, limit=5) or {}
            bids, asks = book.get("bids") or [], book.get("asks") or []
            if not bids or not asks:
                return None
            bid, ask = float(bids[0][0]), float(asks[0][0])
            mid = (bid + ask) / 2.0
            return ((ask - bid) / mid) * 10_000.0 if mid > 0 else None
        except Exception:
            return None

    def manage_owned_positions(self):
        if not self.lifecycle_enabled or not self.ledger.open_symbols():
            return 0
        closed = 0
        for symbol in list(self.ledger.open_symbols()):
            record = self.ledger.positions.get(symbol)
            if not record:
                continue
            ticker = self.get_gate_ticker(symbol)
            if not ticker:
                continue
            price = float(ticker.get("price") or 0.0)
            should_exit, reason, detail = self.exit_evaluator.evaluate(
                record,
                price,
                change_pct=ticker.get("change"),
                spread_bps=self._current_spread_bps(symbol),
            )
            if not should_exit:
                self.ledger.save()
                continue
            print(
                f"🚪 EXIT SIGNAL: {symbol} {reason} move={detail.get('move_bps')}bps "
                f"held={detail.get('held_seconds')}s"
            )
            receipt = self.execute_trade(
                symbol,
                "SELL",
                price,
                amount=record.get("remaining_quantity") or record.get("sellable_quantity"),
                confidence=1.0,
            )
            if isinstance(receipt, dict) and receipt.get("ok") and self._settle_exit(symbol, receipt, reason):
                closed += 1
        return closed

    def _settle_exit(self, symbol, receipt, reason):
        from rpb_position_lifecycle import reconcile_fill
        fill = reconcile_fill(receipt, symbol)
        if fill["filled"] <= 0:
            print(f"⚠️ SELL ACK WITHOUT FILL: {symbol} status={fill['raw_status'] or 'unknown'}")
            return False
        settled = self.ledger.close_position(symbol, fill, reason)
        if not settled:
            return False
        try:
            from src.leantrader.execution import preflight
            preflight.record_event("closes")
            preflight.invalidate_balance_cache()
        except Exception:
            pass
        new_balance = self.check_gate_balance()
        net = float(settled["realized_net_pnl"])
        self.total_profit = self.ledger.realized_net_total()
        self.winning_trades = self.ledger.stats()["authentic_wins"]
        print(
            f"{'🟢' if net >= 0 else '🔴'} POSITION CLOSED: {symbol} {reason} "
            f"gross=${settled['gross_pnl']:+.8f} fees=${settled['total_fees']:.8f} "
            f"NET=${net:+.8f} wallet=${new_balance:.8f}"
        )
        self._feedback_after_close(symbol, settled, new_balance)
        if self.risk is not None:
            self.risk.sync_position(symbol, 0.0, settled["exit_average"])
            self.risk.sync_wallet(new_balance)
        if self.signals is not None:
            self.signals.broadcast_exit(symbol, settled, new_balance)
        return True

    def _feedback_after_close(self, symbol: str, settled: Dict[str, Any], wallet_balance: float) -> None:
        net = float(settled.get("realized_net_pnl") or 0.0)
        if self.scalping is not None:
            self.scalping.record_result(symbol, net)
        if self.alpha is not None:
            self.alpha.record_result(symbol, net, list(settled.get("attribution") or []))

        # Persistent online learner receives only authenticated settled outcome.
        try:
            from src.leantrader.learn.online_learner import update_after_trade
            risk_dollars = max(
                1e-9,
                float(settled.get("entry_cost") or 0.0)
                * (float(getattr(self.exit_evaluator, "stop_loss_bps", 30.0)) / 10_000.0),
            )
            r_mult = max(-10.0, min(10.0, net / risk_dollars))
            update_after_trade(
                symbol,
                "buy",
                r_mult,
                str(settled.get("session") or "unknown").lower(),
            )
        except Exception as exc:
            print(f"⚠️ learner feedback unavailable: {type(exc).__name__}")

        # RPB-owned journal. Production/evolution runtime remains read-only.
        try:
            base = Path(os.getenv("LEANTRADER_DATA_DIR", "runtime"))
            if base.name != "runtime":
                base = base / "runtime"
            base.mkdir(parents=True, exist_ok=True)
            event = {
                "timestamp": time.time(),
                "symbol": symbol,
                "realized_net_pnl": net,
                "wallet_balance": float(wallet_balance or 0.0),
                "exit_reason": settled.get("exit_reason"),
                "hold_seconds": settled.get("hold_seconds"),
                "attribution": settled.get("attribution") or [],
                "session": settled.get("session") or "unknown",
            }
            with (base / "rpb_outcomes.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
        except Exception:
            pass

    # --------------------------------------------------------------- loop

    def run_real_profit_trading(self):
        balance = self.check_gate_balance()
        print(f"🚀 RPB START: mode={self.mode} venue={self.execution_exchange_id} balance=${balance:.8f}")
        self.send_telegram(
            f"🚀 <b>REAL PROFIT BOT ACTIVE</b>\nMode: {self.mode.upper()}\nVenue: {self.execution_exchange_id}\nBalance: ${balance:.6f}"
        )

        while self.running:
            try:
                self._refresh_fast_ticker_snapshot()
                if not self.last_pair_refresh or time.time() - self.last_pair_refresh >= self.dynamic_pair_refresh_seconds:
                    self.refresh_dynamic_pairs()

                # Exit ownership is always checked before fresh entries.
                self.manage_owned_positions()

                for symbol in list(self.crypto_pairs):
                    if symbol in self.blocked_pairs:
                        continue
                    if self.lifecycle_enabled and self.ledger.owns(symbol):
                        self.manage_owned_positions()
                        continue

                    signal, confidence, price, change, volume = self.analyze_market(symbol)
                    if signal != "BUY" or confidence < self.entry_confidence:
                        # Spot RPB does not open shorts. SELL belongs only to
                        # the owned-position lifecycle above.
                        continue

                    receipt = self.execute_trade(
                        symbol,
                        "BUY",
                        price,
                        confidence=float(confidence) / 100.0,
                    )
                    if not isinstance(receipt, dict) or not receipt.get("ok"):
                        continue

                    record = self._record_buy_fill(symbol, receipt, price, confidence)
                    if record:
                        self.total_trades += 1
                        print(
                            f"✅ AUTHENTICATED ENTRY #{self.total_trades}: {symbol} "
                            f"conf={confidence:.2f}% change={change:+.2f}% volume=${volume:,.0f}"
                        )
                        self.manage_owned_positions()
                        time.sleep(max(0.0, self.post_entry_sleep))

                stats = self.ledger.stats() if self.lifecycle_enabled else {}
                print(
                    f"🔄 RPB CYCLE: open={stats.get('open_positions', 0)} "
                    f"closed={stats.get('closed_positions', 0)} "
                    f"realized_net=${stats.get('realized_net_pnl', 0.0):+.8f}"
                )
                time.sleep(max(0.05, self.cycle_sleep))

            except Exception as exc:
                print(f"❌ RPB cycle error: {type(exc).__name__}: {exc}")
                time.sleep(2.0)

    def run(self):
        try:
            self.run_real_profit_trading()
        except KeyboardInterrupt:
            self.running = False
            print("🛑 REAL PROFIT BOT stopped")


if __name__ == "__main__":
    bot = REAL_PROFIT_BOT(mode=os.getenv("EXECUTION_MODE", "testnet"))
    bot.run()


RealProfitBot = REAL_PROFIT_BOT
