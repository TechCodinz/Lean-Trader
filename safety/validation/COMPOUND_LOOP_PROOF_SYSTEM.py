#!/usr/bin/env python3
"""
COMPOUND_LOOP_PROOF_SYSTEM.py
Prove infinite compounding loop with REAL exchange confirmations
Phases 1-6: Counters, confirmations, precision, wallet, TP, verdict
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict
import ccxt

logger = logging.getLogger(__name__)

class CompoundLoopProofSystem:
    """Complete compound loop verification with REAL exchange confirmations"""
    
    def __init__(self, exchange, reports_dir: str = "/root/bot/reports"):
        self.exchange = exchange
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Phase 1: Loop completion counters
        self.counters = {
            'signals_created': 0,
            'orders_sent': 0,
            'orders_rejected': 0,
            'orders_filled': 0,
            'positions_confirmed': 0,
            'tp_orders_placed': 0,
            'partial_tp_executed': 0,
            'final_exit_executed': 0,
            'capital_released_success': 0,
            'capital_released_failure': 0
        }
        
        self.last_emit_time = time.time()
        
        # Phase 2: Exchange confirmations
        self.confirmations_file = self.reports_dir / 'exchange_confirmations.jsonl'
        
        # Phase 3: Order constraints
        self.constraints_file = self.reports_dir / 'order_constraint_blocks.jsonl'
        self.market_limits = {}
        
        # Phase 4: Wallet sanity
        self.wallet_file = self.reports_dir / 'wallet_sanity.jsonl'
        self.last_wallet_check = 0
        
        # Phase 5: TP arming
        self.tp_arming_file = self.reports_dir / 'tp_arming_status.jsonl'
        
        # Phase 6: Completed loops tracking
        self.completed_loops = []
        self.blockers = defaultdict(int)
        
        logger.info("Compound Loop Proof System initialized")
    
    # ========================================================================
    # PHASE 1:Loop Completion Counters
    # ========================================================================
    
    def increment_counter(self, counter_name: str):
        """Increment a counter"""
        if counter_name in self.counters:
            self.counters[counter_name] += 1
    
    def emit_counters(self, force: bool = False):
        """Emit counters every 60 seconds"""
        current_time = time.time()
        
        if force or (current_time - self.last_emit_time >= 60):
            # Calculate completion rate
            signals = self.counters['signals_created']
            exits = self.counters['final_exit_executed']
            
            completion_rate = exits / signals if signals > 0 else 0
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                **self.counters,
                'compound_loop_completion_rate': round(completion_rate, 4)
            }
            
            # Write to file
            metrics_file = self.reports_dir / 'compound_loop_metrics.jsonl'
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
            
            logger.info(f"📊 COMPOUND LOOP METRICS:")
            logger.info(f"   Completion Rate: {completion_rate:.2%}")
            logger.info(f"   Signals: {signals}, Exits: {exits}")
            
            self.last_emit_time = current_time
    
    # ========================================================================
    # PHASE 2: Exchange Confirmation (NO ASSUMED FILLS)
    # ========================================================================
    
    def confirm_order_with_exchange(self, order_id: str, symbol: str, 
                                    timeout: int = 30) -> Dict:
        """
        Confirm order status with exchange (no assumptions)
        
        Returns:
            {
                'confirmed': bool,
                'status': str,  # FILLED/CANCELED/REJECTED/EXPIRED/ORPHAN
                'filled_amount': float,
                'filled_price': float
            }
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                order = self.exchange.fetch_order(order_id, symbol)
                
                status = order['status'].upper()
                
                if status in ['CLOSED', 'FILLED']:
                    # Order filled
                    confirmation = {
                        'timestamp': datetime.now().isoformat(),
                        'order_id': order_id,
                        'symbol': symbol,
                        'confirmed': True,
                        'status': 'FILLED',
                        'filled_amount': order['filled'],
                        'filled_price': order['average'] or order['price'],
                        'exchange_time': order.get('timestamp')
                    }
                    
                    # Log confirmation
                    with open(self.confirmations_file, 'a') as f:
                        f.write(json.dumps(confirmation) + '\n')
                    
                    logger.info(f"[OK] ORDER CONFIRMED: {order_id} - FILLED")
                    
                    self.increment_counter('orders_filled')
                    
                    return confirmation
                
                elif status in ['CANCELED', 'CANCELLED', 'REJECTED', 'EXPIRED']:
                    # Order failed
                    confirmation = {
                        'timestamp': datetime.now().isoformat(),
                        'order_id': order_id,
                        'symbol': symbol,
                        'confirmed': True,
                        'status': status,
                        'filled_amount': 0,
                        'filled_price': 0
                    }
                    
                    with open(self.confirmations_file, 'a') as f:
                        f.write(json.dumps(confirmation) + '\n')
                    
                    logger.warning(f" ORDER {status}: {order_id}")
                    
                    self.increment_counter('orders_rejected')
                    self.blockers[f'order_{status.lower()}'] += 1
                    
                    return confirmation
                
                # Still pending, wait and retry
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error fetching order {order_id}: {e}")
                time.sleep(1)
        
        # Timeout - orphan order
        orphan = {
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'symbol': symbol,
            'confirmed': False,
            'status': 'ORPHAN',
            'filled_amount': 0,
            'filled_price': 0,
            'reason': f'No confirmation after {timeout}s'
        }
        
        with open(self.confirmations_file, 'a') as f:
            f.write(json.dumps(orphan) + '\n')
        
        logger.warning(f" ORPHAN ORDER: {order_id}")
        
        self.blockers['orphan_timeout'] += 1
        
        return orphan
    
    def confirm_position_with_exchange(self, symbol: str) -> Optional[Dict]:
        """Confirm position exists on exchange"""
        try:
            # For spot: check balance
            if self.exchange.options.get('defaultType') == 'spot':
                balance = self.exchange.fetch_balance()
                base_currency = symbol.split('/')[0]
                
                amount = balance.get(base_currency, {}).get('total', 0)
                
                if amount > 0:
                    confirmation = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'confirmed': True,
                        'amount': amount,
                        'type': 'spot_holding'
                    }
                    
                    with open(self.confirmations_file, 'a') as f:
                        f.write(json.dumps(confirmation) + '\n')
                    
                    logger.info(f"[OK] POSITION CONFIRMED: {symbol} - {amount}")
                    
                    self.increment_counter('positions_confirmed')
                    
                    return confirmation
            
            # For futures: fetch positions
            else:
                positions = self.exchange.fetch_positions([symbol])
                
                for pos in positions:
                    if pos['contracts'] > 0:
                        confirmation = {
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol,
                            'confirmed': True,
                            'amount': pos['contracts'],
                            'entry_price': pos.get('entryPrice'),
                            'type': 'futures_position'
                        }
                        
                        with open(self.confirmations_file, 'a') as f:
                            f.write(json.dumps(confirmation) + '\n')
                        
                        logger.info(f"[OK] POSITION CONFIRMED: {symbol}")
                        
                        self.increment_counter('positions_confirmed')
                        
                        return confirmation
            
            return None
            
        except Exception as e:
            logger.error(f"Position confirmation failed: {e}")
            return None
    
    # ========================================================================
    # PHASE 3: Min Order Size + Precision Guarantee
    # ========================================================================
    
    def load_market_constraints(self, symbol: str) -> Dict:
        """Load market constraints for symbol"""
        if symbol in self.market_limits:
            return self.market_limits[symbol]
        
        try:
            markets = self.exchange.load_markets()
            market = markets.get(symbol)
            
            if not market:
                return {}
            
            limits = market.get('limits', {})
            precision = market.get('precision', {})
            
            constraints = {
                'min_amount': limits.get('amount', {}).get('min', 0),
                'max_amount': limits.get('amount', {}).get('max', float('inf')),
                'min_cost': limits.get('cost', {}).get('min', 0),
                'amount_precision': precision.get('amount', 8),
                'price_precision': precision.get('price', 8),
                'step_size': market.get('info', {}).get('lotSizeFilter', {}).get('basePrecision'),
                'tick_size': market.get('info', {}).get('priceFilter', {}).get('tickSize')
            }
            
            self.market_limits[symbol] = constraints
            
            return constraints
            
        except Exception as e:
            logger.error(f"Failed to load constraints for {symbol}: {e}")
            return {}
    
    def validate_and_adjust_order(self, symbol: str, side: str, 
                                  amount: float, price: Optional[float] = None) -> tuple[bool, Dict]:
        """
        Validate order against constraints and adjust if needed
        
        Returns:
            (valid, adjusted_params or reason)
        """
        constraints = self.load_market_constraints(symbol)
        
        if not constraints:
            return True, {'amount': amount, 'price': price}
        
        # Round to precision
        amount_precision = constraints['amount_precision']
        amount_rounded = round(amount, amount_precision)
        
        price_rounded = round(price, constraints['price_precision']) if price else None
        
        # Check minimum amount
        min_amount = constraints['min_amount']
        if amount_rounded < min_amount:
            reason = {
                'blocked': 'MIN_AMOUNT',
                'required': min_amount,
                'provided': amount_rounded
            }
            
            self._log_constraint_block(symbol, side, reason)
            self.blockers['min_amount_violation'] += 1
            
            return False, reason
        
        # Check minimum cost
        if price_rounded:
            cost = amount_rounded * price_rounded
            min_cost = constraints['min_cost']
            
            if cost < min_cost:
                reason = {
                    'blocked': 'MIN_COST',
                    'required': min_cost,
                    'provided': cost
                }
                
                self._log_constraint_block(symbol, side, reason)
                self.blockers['min_cost_violation'] += 1
                
                return False, reason
        
        return True, {'amount': amount_rounded, 'price': price_rounded}
    
    def _log_constraint_block(self, symbol: str, side: str, reason: Dict):
        """Log order blocked by constraints"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'ORDER_BLOCKED_CONSTRAINTS',
            'symbol': symbol,
            'side': side,
            **reason
        }
        
        with open(self.constraints_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.warning(f" ORDER BLOCKED: {reason['blocked']} - {symbol}")
    
    # ========================================================================
    # PHASE 4: Wallet & Account Type Consistency
    # ========================================================================
    
    def check_wallet_sanity(self):
        """Check wallet type matches trading mode"""
        current_time = time.time()
        
        if current_time - self.last_wallet_check < 60:
            return
        
        try:
            account_type = self.exchange.options.get('defaultType', 'unknown')
            balance = self.exchange.fetch_balance()
            
            usdt_free = balance.get('USDT', {}).get('free', 0)
            usdt_used = balance.get('USDT', {}).get('used', 0)
            
            sanity = {
                'timestamp': datetime.now().isoformat(),
                'account_type': account_type,
                'balance_source': 'spot' if account_type == 'spot' else 'margin',
                'usdt_available': usdt_free,
                'usdt_reserved': usdt_used
            }
            
            with open(self.wallet_file, 'a') as f:
                f.write(json.dumps(sanity) + '\n')
            
            logger.info(f"💰 WALLET: {account_type}, ${usdt_free:.2f} available")
            
            self.last_wallet_check = current_time
            
        except Exception as e:
            logger.error(f"Wallet sanity check failed: {e}")
    
    # ========================================================================
    # PHASE 5: TP/Exit Execution Path Validation
    # ========================================================================
    
    def verify_tp_armed(self, trade_id: str, symbol: str, tp_price: float,
                       position_size: float) -> bool:
        """Verify TP is actually armed for position"""
        try:
            # Check for TP order on exchange
            open_orders = self.exchange.fetch_open_orders(symbol)
            
            for order in open_orders:
                # Check if this is a TP/sell order
                if order['side'] == 'sell' and abs(order['price'] - tp_price) < (tp_price * 0.01):
                    # TP order exists
                    armed = {
                        'timestamp': datetime.now().isoformat(),
                        'trade_id': trade_id,
                        'symbol': symbol,
                        'tp_armed': True,
                        'tp_order_id': order['id'],
                        'tp_price': tp_price,
                        'mechanism': 'exchange_tp_order'
                    }
                    
                    with open(self.tp_arming_file, 'a') as f:
                        f.write(json.dumps(armed) + '\n')
                    
                    logger.info(f"[OK] TP ARMED: {trade_id} @ ${tp_price:.2f}")
                    
                    self.increment_counter('tp_orders_placed')
                    
                    return True
            
            # No TP order found
            not_armed = {
                'timestamp': datetime.now().isoformat(),
                'trade_id': trade_id,
                'symbol': symbol,
                'tp_armed': False,
                'reason': 'TP_NOT_ARMED',
                'tp_price': tp_price
            }
            
            with open(self.tp_arming_file, 'a') as f:
                f.write(json.dumps(not_armed) + '\n')
            
            logger.warning(f" TP NOT ARMED: {trade_id}")
            
            self.blockers['tp_not_armed'] += 1
            
            return False
            
        except Exception as e:
            logger.error(f"TP arming check failed: {e}")
            return False
    
    # ========================================================================
    # PHASE 6: Completed Loop Tracking
    # ========================================================================
    
    def record_completed_loop(self, loop_data: Dict):
        """Record a completed compound loop"""
        self.completed_loops.append({
            'timestamp': datetime.now().isoformat(),
            **loop_data
        })
        
        logger.info(f"[OK] COMPLETED LOOP: {loop_data.get('trade_id')}")
    
    def generate_final_verdict(self) -> Dict:
        """Generate compound loop final verdict"""
        logger.info("Generating compound loop final verdict...")
        
        # Calculate completion rate
        signals = self.counters['signals_created']
        exits = self.counters['final_exit_executed']
        
        completion_rate = exits / signals if signals > 0 else 0
        
        # Top 5 blockers
        top_blockers = sorted(self.blockers.items(), key=lambda x: -x[1])[:5]
        
        # Generate verdict
        verdict = {
            'timestamp': datetime.now().isoformat(),
            'completion_rate': round(completion_rate, 4),
            'counters': self.counters,
            'completed_loops_count': len(self.completed_loops),
            'top_blockers': dict(top_blockers),
            'loop_is_functioning': completion_rate > 0.1 and len(self.completed_loops) >= 3
        }
        
        verdict_file = self.reports_dir / 'compound_loop_verdict.json'
        with open(verdict_file, 'w') as f:
            json.dump(verdict, f, indent=2)
        
        # Generate markdown report
        self._generate_markdown_verdict(verdict)
        
        return verdict
    
    def _generate_markdown_verdict(self, verdict: Dict):
        """Generate markdown verdict report"""
        md = f"""# COMPOUND LOOP FINAL VERDICT

Generated: {verdict['timestamp']}

## Completion Rate

**{verdict['completion_rate']:.2%}** ({verdict['counters']['final_exit_executed']} / {verdict['counters']['signals_created']})

## Loop Counters

| Metric | Count |
|--------|-------|
| Signals Created | {verdict['counters']['signals_created']} |
| Orders Sent | {verdict['counters']['orders_sent']} |
| Orders Filled | {verdict['counters']['orders_filled']} |
| Orders Rejected | {verdict['counters']['orders_rejected']} |
| Positions Confirmed | {verdict['counters']['positions_confirmed']} |
| TP Orders Placed | {verdict['counters']['tp_orders_placed']} |
| Partial TP Executed | {verdict['counters']['partial_tp_executed']} |
| Final Exit Executed | {verdict['counters']['final_exit_executed']} |
| Capital Released (Success) | {verdict['counters']['capital_released_success']} |
| Capital Released (Failure) | {verdict['counters']['capital_released_failure']} |

## Top Blockers

"""
        for blocker, count in verdict['top_blockers'].items():
            md += f"- **{blocker}**: {count} occurrences\n"
        
        md += f"""

## Completed Loops

Total: {verdict['completed_loops_count']}

## VERDICT

"""
        
        if verdict['loop_is_functioning']:
            md += """
[OK] **COMPOUND LOOP IS FUNCTIONING**

Evidence:
- Completion rate > 10%
- At least 3 completed loops observed
- Entry → Fill → TP/Exit → Capital Released → Next Trade

Loop is operational and compounding.
"""
        else:
            md += """
[X] **COMPOUND LOOP NOT COMPLETING**

Issues:
- Completion rate too low
- OR less than 3 completed loops

Top blockers preventing completion (see above).

Required fixes limited to:
- Order constraints/precision
- Wallet type mismatches
- TP arming logic
- Exchange confirmation handling
"""
        
        md_file = self.reports_dir / 'COMPOUND_LOOP_FINAL_VERDICT.md'
        with open(md_file, 'w') as f:
            f.write(md)
        
        logger.info(f"Final verdict saved: {md_file}")

# Global instance
_proof_system = None

def get_proof_system(exchange):
    """Get global proof system"""
    global _proof_system
    if _proof_system is None:
        _proof_system = CompoundLoopProofSystem(exchange)
    return _proof_system

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    import ccxt
    exchange = ccxt.bybit({'enableRateLimit': True})
    
    proof = CompoundLoopProofSystem(exchange)
    
    # Simulate loop
    proof.increment_counter('signals_created')
    proof.increment_counter('orders_sent')
    proof.increment_counter('orders_filled')
    proof.increment_counter('final_exit_executed')
    
    proof.emit_counters(force=True)
    verdict = proof.generate_final_verdict()
    
    print(json.dumps(verdict, indent=2))
