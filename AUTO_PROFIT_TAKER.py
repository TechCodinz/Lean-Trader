#!/usr/bin/env python3
"""
💰 AUTO PROFIT TAKER
Automatically closes positions when they hit profit targets
This is WHY trades aren't closing - we need this!
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _own_base(sym):
    """Canonical base asset for ownership matching across the
    fleet's symbol dialects ('KASUSDT', 'KAS/USDT' and
    'KAS/USDT:USDT' all name the same perp)."""
    s = str(sym or '').upper()
    for suf in (':USDT', '/USDT', 'USDT'):
        if s.endswith(suf):
            s = s[:-len(suf)]
    return s.split('/')[0]


class AutoProfitTaker:
    """
    Monitors open positions and closes them when profit targets hit
    
    This is CRITICAL - without this, positions never close!
    """
    
    def __init__(self, exchange, data_hub, close_handler=None):
        self.exchange = exchange
        self.data_hub = data_hub
        # Optional paper routing: handler(symbol, side, size, price, reason)
        # settles the close against the paper book instead of real orders.
        self.close_handler = close_handler
        
        # Track open positions
        self.open_positions = {}  # symbol -> position_data
        # Runner symbols (ladder's final slice riding the trailer):
        # never target-close these - the trailing stop owns them.
        self.exempt = set()
        self._owned_bases = set()
        # Intelligent exits (wired 2026-10-28): the fleet's built
        # ladder + runner system from critical_features_addon -
        # partial take-profit rungs bank profit as it appears, TP3
        # arms a runner whose final slice rides a breakeven-floored
        # trailing stop (the pattern the zoo ran; its `exempt` set
        # above exists for exactly this). Fail-soft: if the addon
        # cannot import, the fixed table below runs alone as before.
        try:
            from critical_features_addon import (TrailingStopManager,
                                                 PartialTPManager)
            self.partial = PartialTPManager()
            self.trailer = TrailingStopManager(trail_percent=0.02)
            self.trailer_inv = TrailingStopManager(trail_percent=0.02)
        except Exception:
            self.partial = None
            self.trailer = None
            self.trailer_inv = None
        self.runners = set()
        
        # Profit taking settings
        self.profit_targets = {
            'micro_scalp': 0.005,  # 0.5% for micro scalps
            'quick_scalp': 0.003,  # 0.3% for quick scalps
            'normal': 0.01,  # 1% for normal trades
            'swing': 0.03,  # 3% for swing trades
        }
        
        self.stop_loss = 0.015  # 1.5% stop loss
        
        # Performance tracking
        self.total_closed = 0
        self.total_profit = 0.0
        self.winning_closes = 0
        
        logger.info("💰 Auto Profit Taker initialized")
        logger.info(f"   Quick scalp target: {self.profit_targets['quick_scalp']:.1%}")
        logger.info(f"   Normal target: {self.profit_targets['normal']:.1%}")
        logger.info(f"   Stop loss: {self.stop_loss:.1%}")
    
    def register_position(self, symbol: str, side: str, entry_price: float, 
                         size: float, strategy: str = 'normal'):
        """
        Register a new position that was opened
        """
        self.open_positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'size': size,
            'strategy': strategy,
            'opened_at': datetime.now(),
            'profit_target': self.profit_targets.get(strategy, self.profit_targets['normal'])
        }
        if getattr(self, 'partial', None) is not None:
            try:
                self.partial.add_position(symbol, entry_price, size)
            except Exception:
                pass
        
        logger.info(f"📝 Position registered: {symbol} {side}")
        logger.info(f"   Entry: ${entry_price:.4f}")
        logger.info(f"   Target: {self.profit_targets.get(strategy, 0.01):.1%}")
    
    async def check_and_close_positions(self):
        """
        Check all open positions and close if profit/loss targets hit
        
        Returns list of closed positions
        """
        closed_positions = []
        
        if not self.open_positions:
            return closed_positions
        
        for symbol in list(self.open_positions.keys()):
            try:
                if _own_base(symbol) in getattr(self, '_owned_bases', set()):
                    continue
                position = self.open_positions[symbol]
                
                # Get current price
                ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                if not current_price:
                    continue
                _entry = position['entry_price']
                _is_long = position['side'].lower() == 'buy'
                # Mirrored feed for shorts so the long-built ladder
                # and trailer read profit in the right direction.
                _feed = current_price if _is_long else (2.0 * _entry - current_price)
                _trailer = None
                if getattr(self, 'partial', None) is not None:
                    _trailer = self.trailer if _is_long else self.trailer_inv
                _pnl_feed = (_feed - _entry) / _entry if _entry else 0.0

                if symbol in getattr(self, 'runners', set()):
                    # Runner: the trailing stop owns the final slice.
                    if _trailer is not None:
                        _trailer.update(symbol, _feed, _entry, _entry * 0.98)
                        _stop = _trailer.get_stop(symbol)
                        if _stop is not None and _feed <= _stop:
                            _size = position['size']
                            if getattr(self, 'close_handler', None) is not None:
                                self.close_handler(symbol, position['side'], _size, current_price, 'RUNNER TRAIL STOP')
                            elif _is_long:
                                await asyncio.to_thread(self.exchange.create_market_sell_order, symbol, _size)
                            else:
                                await asyncio.to_thread(self.exchange.create_market_buy_order, symbol, current_price * _size)
                            _rpnl = _size * _entry * _pnl_feed
                            self.total_closed += 1
                            self.total_profit += _rpnl
                            if _rpnl > 0:
                                self.winning_closes += 1
                            closed_positions.append({
                                'symbol': symbol, 'side': position['side'],
                                'entry_price': _entry, 'exit_price': current_price,
                                'size': _size, 'pnl_pct': _pnl_feed,
                                'profit_usd': _rpnl,
                                'reason': f'RUNNER TRAIL STOP: {_pnl_feed:.2%}',
                                'duration': (datetime.now() - position['opened_at']).total_seconds()})
                            logger.info(f"🏃 RUNNER CLOSED {symbol}: trail stop at {_pnl_feed:.2%} ({_rpnl:+.2f} USD)")
                            del self.open_positions[symbol]
                            self.runners.discard(symbol)
                            self.exempt.discard(symbol)
                            if getattr(self, 'partial', None) is not None:
                                self.partial.positions.pop(symbol, None)
                            _trailer.clear(symbol)
                    continue
                if symbol in getattr(self, 'exempt', set()):
                    continue
                
                # Calculate P&L
                entry_price = position['entry_price']
                side = position['side']
                
                if side.lower() == 'buy':
                    # Long position
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    # Short position
                    pnl_pct = (entry_price - current_price) / entry_price
                
                profit_target = position['profit_target']

                # Intelligent ladder (profit side) before the fixed
                # table: one rung per check banks a slice as profit
                # appears; TP3 arms the runner instead of closing.
                # A fired rung is this pass's only action.
                if getattr(self, 'partial', None) is not None:
                    try:
                        _orders = await self.partial.check_tp_levels(symbol, _feed)
                    except Exception:
                        _orders = []
                    _acted = False
                    for _ord in _orders or []:
                        if _ord.get('runner'):
                            self.runners.add(symbol)
                            self.exempt.add(symbol)
                            if _trailer is not None:
                                try:
                                    _trailer.stop_losses[symbol] = max(
                                        _trailer.stop_losses.get(symbol, 0),
                                        _entry * 1.0)
                                    _trailer.highest_prices[symbol] = max(
                                        _trailer.highest_prices.get(symbol, 0),
                                        _feed)
                                except Exception:
                                    pass
                            logger.info(f"🏃 RUNNER armed {symbol}: ladder banked, final slice rides the trailing stop (breakeven floor)")
                            _acted = True
                            continue
                        _rung_size = float(_ord.get('size') or 0)
                        if _rung_size <= 0:
                            continue
                        if getattr(self, 'close_handler', None) is not None:
                            self.close_handler(symbol, side, _rung_size, current_price, _ord.get('tp_level', 'TP'))
                        elif _is_long:
                            await asyncio.to_thread(
                                self.exchange.create_market_sell_order,
                                symbol, _rung_size)
                        else:
                            await asyncio.to_thread(
                                self.exchange.create_market_buy_order,
                                symbol, current_price * _rung_size)
                        position['size'] = max(0.0, position['size'] - _rung_size)
                        _rpnl = _rung_size * _entry * pnl_pct
                        self.total_closed += 1
                        self.total_profit += _rpnl
                        if _rpnl > 0:
                            self.winning_closes += 1
                        closed_positions.append({
                            'symbol': symbol, 'side': side,
                            'entry_price': _entry, 'exit_price': current_price,
                            'size': _rung_size, 'pnl_pct': pnl_pct,
                            'profit_usd': _rpnl,
                            'reason': f"LADDER {_ord.get('tp_level')}: partial banked at {pnl_pct:.2%}",
                            'duration': (datetime.now() - position['opened_at']).total_seconds()})
                        logger.info(f"🪜 LADDER {_ord.get('tp_level')} {symbol}: banked {_rung_size} at {pnl_pct:.2%} ({_rpnl:+.2f} USD)")
                        _acted = True
                    if _acted:
                        continue
                
                # Check if should close
                should_close = False
                close_reason = ""
                
                if pnl_pct >= profit_target:
                    should_close = True
                    close_reason = f"PROFIT TARGET HIT: {pnl_pct:.2%}"
                elif pnl_pct <= -self.stop_loss:
                    should_close = True
                    close_reason = f"STOP LOSS HIT: {pnl_pct:.2%}"
                elif (datetime.now() - position['opened_at']).total_seconds() > 3600:
                    # Time stop - close after 1 hour regardless
                    should_close = True
                    close_reason = f"TIME STOP: 1 hour (P&L: {pnl_pct:.2%})"
                
                if should_close:
                    # Close position
                    size = position['size']
                    
                    if getattr(self, 'close_handler', None) is not None:
                        # Paper-routed close: handler settles against the paper book
                        order = self.close_handler(symbol, side, size, current_price, close_reason)
                    elif side.lower() == 'buy':
                        # Close long = sell
                        order = await asyncio.to_thread(
                            self.exchange.create_market_sell_order,
                            symbol,
                            size
                        )
                    else:
                        # Close short = buy
                        cost = current_price * size
                        order = await asyncio.to_thread(
                            self.exchange.create_market_buy_order,
                            symbol,
                            cost
                        )
                    
                    # Calculate actual profit
                    profit_usd = entry_price * size * pnl_pct
                    
                    # Record closure
                    self.total_closed += 1
                    self.total_profit += profit_usd
                    if profit_usd > 0:
                        self.winning_closes += 1
                    
                    closed_data = {
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'size': size,
                        'pnl_pct': pnl_pct,
                        'profit_usd': profit_usd,
                        'reason': close_reason,
                        'duration': (datetime.now() - position['opened_at']).total_seconds()
                    }
                    
                    closed_positions.append(closed_data)
                    
                    logger.info(f"💰 POSITION CLOSED: {symbol}")
                    logger.info(f"   {close_reason}")
                    logger.info(f"   Profit: ${profit_usd:.2f} ({pnl_pct:.2%})")
                    logger.info(f"   Duration: {closed_data['duration']/60:.1f} minutes")
                    
                    # Remove from tracking
                    del self.open_positions[symbol]
                    self.runners.discard(symbol)
                    self.exempt.discard(symbol)
                    if getattr(self, 'partial', None) is not None:
                        self.partial.positions.pop(symbol, None)
                    if getattr(self, 'trailer', None) is not None:
                        self.trailer.clear(symbol)
                    if getattr(self, 'trailer_inv', None) is not None:
                        self.trailer_inv.clear(symbol)
            
            except Exception as e:
                logger.debug(f"Position check error for {symbol}: {e}")
        
        return closed_positions
    
    def _refresh_owned(self):
        """Ownership wire (2026-10-23): symbols registered to a
        living owner being belong to that owner's exit logic, not
        to this fleet exit manager. The registries the fleet
        already keeps define ownership; refreshed every sync.
        Everything else on the exchange is an orphan - ours."""
        import json as _j
        owned = set()
        for path in ('/app/runtime/orchestrator_positions.json',
                     '/app/runtime/master_positions.json'):
            try:
                with open(path) as f:
                    data = _j.load(f) or {}
                if isinstance(data, dict):
                    for k in data.keys():
                        owned.add(_own_base(k))
            except Exception:
                pass
        try:
            with open('/app/runtime/continuous_sessions.json') as f:
                data = _j.load(f) or {}
            if isinstance(data, dict):
                for k in data.keys():
                    owned.add(_own_base(str(k).split('_')[0]))
        except Exception:
            pass
        self._owned_bases = owned
        return owned

    async def sync_from_exchange(self):
        """Adopt live exchange positions not yet tracked.

        Restored 2026-10-19: present in the Oct 12-14 build, lost in
        the zoo adaptation. Positions register as micro_scalp with
        their real exchange entry price. Returns count adopted.
        """
        adopted = 0
        self._refresh_owned()
        try:
            positions = await asyncio.to_thread(self.exchange.fetch_positions)
        except Exception as e:
            logger.warning(f"sync_from_exchange: fetch_positions failed: {e}")
            return 0
        for p in positions or []:
            try:
                contracts = float(p.get('contracts') or 0)
                if contracts == 0:
                    continue
                symbol = p.get('symbol')
                if not symbol or symbol in self.open_positions:
                    continue
                if _own_base(symbol) in self._owned_bases:
                    continue
                entry = float(p.get('entryPrice') or 0)
                if entry <= 0:
                    continue
                side = 'buy' if contracts > 0 else 'sell'
                self.register_position(symbol, side, entry, abs(contracts),
                                       strategy='micro_scalp')
                adopted += 1
            except Exception as e:
                logger.warning(f"sync_from_exchange: adopt skip: {e}")
        if adopted:
            logger.info(f"sync_from_exchange: adopted {adopted} position(s)")
        return adopted

    def get_stats(self) -> Dict:
        """Get profit taking statistics"""
        return {
            'open_positions': len(self.open_positions),
            'total_closed': self.total_closed,
            'winning_closes': self.winning_closes,
            'win_rate': self.winning_closes / max(self.total_closed, 1) * 100,
            'total_profit': self.total_profit,
            'avg_profit': self.total_profit / max(self.total_closed, 1)
        }
