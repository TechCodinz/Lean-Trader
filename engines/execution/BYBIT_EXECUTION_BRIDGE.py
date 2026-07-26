#!/usr/bin/env python3
"""
BYBIT_EXECUTION_BRIDGE.py
Simple bridge to route scalp signals to Bybit Testnet execution
"""

import ccxt
import os
from dotenv import load_dotenv
import logging
import time

logger = logging.getLogger(__name__)

class BybitExecutionBridge:
    """Executes signals on Bybit Testnet"""
    
    def __init__(self):
        load_dotenv()
        self.exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
            'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
            'options': {'defaultType': 'spot'}
        })
        self.exchange.set_sandbox_mode(True)
        self.last_execution = 0
        logger.info("[OK] Bybit Testnet Execution Bridge initialized")
    
    def execute_signal(self, signal):
        """Execute a single signal on Bybit Testnet"""
        try:
            symbol = signal.get('symbol')
            side = signal.get('side', 'buy').lower()
            
            # Turbo Rate limit: max 1 execution per 1 second (High Frequency)
            if time.time() - self.last_execution < 1:
                return None
            
            # Get balance
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            if usdt_balance < 5:
                logger.warning(f"Insufficient balance: ${usdt_balance:.2f}")
                return None
            
            # Calculate quantity based on side
            if side == 'buy':
                # BUY: Use 20% of USDT balance
                position_value = usdt_balance * 0.20
                quantity = position_value / current_price
            else:
                # SELL: Sell 100% of the asset
                base_currency = symbol.split('/')[0]
                asset_balance = balance.get(base_currency, {}).get('free', 0)
                quantity = asset_balance * 0.99  # 99% to avoid rounding issues
                
                if quantity <= 0:
                    logger.warning(f"No {base_currency} to sell!")
                    return None

            # Get market info for minimum order size
            markets = self.exchange.load_markets()
            market = markets.get(symbol)
            if market:
                min_amount = market.get('limits', {}).get('amount', {}).get('min', 0.001)
                # Ensure we meet min amount
                if quantity < min_amount:
                     logger.warning(f"Quantity {quantity} below min {min_amount}")
                     return None

            
            # Place market order for immediate execution
            logger.info(f">> EXECUTING: {side.upper()} {quantity:.6f} {symbol} @ ${current_price:.2f} (Balance: ${usdt_balance:.2f})")
            
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=quantity
            )
            
            self.last_execution = time.time()
            
            logger.info(f"[OK] ORDER PLACED: {order.get('id')} - Status: {order.get('status')}")
            
            return order
            
        except Exception as e:
            logger.error(f"[X] Execution failed for {signal.get('symbol')}: {e}")
            return None
    
    def execute_signals(self, signals=None):
        """Execute multiple signals (called by orchestrator)"""
        if not signals:
            return
        
        if isinstance(signals, dict):
            signals = [signals]
        
        for signal in signals[:5]:  # Max 5 signals per cycle
            self.execute_signal(signal)
    
    def check_balance(self):
        """Check current Bybit Testnet balance"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_total = balance.get('USDT', {}).get('total', 0)
            logger.info(f"💰 Bybit Testnet Balance: ${usdt_total:.2f}")
            return usdt_total
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return 0


# Global singleton instance
_bybit_bridge = None

def get_bybit_bridge():
    """Get or create the global Bybit execution bridge"""
    global _bybit_bridge
    if _bybit_bridge is None:
        _bybit_bridge = BybitExecutionBridge()
    return _bybit_bridge


# For direct testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bridge = get_bybit_bridge()
    
    print(f"Bybit Testnet Balance: ${bridge.check_balance():.2f}")
    
    # Test signal
    test_signal = {
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'confidence': 75
    }
    
    print("\nTest execution:")
    result = bridge.execute_signal(test_signal)
    if result:
        print(f"Success: {result.get('id')}")
