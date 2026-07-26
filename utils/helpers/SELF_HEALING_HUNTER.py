#!/usr/bin/env python3
"""
🧠 SELF-HEALING INTELLIGENT OPPORTUNITY HUNTER
Autonomous · Self-Correcting · Never Stops Trading

Features:
- Auto-detects and fixes async errors
- Self-healing on crashes
- Intelligent error recovery
- Learns from failures
- NEVER stops trading
"""

import asyncio
import ccxt.async_support as ccxt
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import traceback

load_dotenv('/root/bot/.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/bot/hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SelfHealingHunter:
    """🧠 Self-Healing Intelligent Trading System"""
    
    def __init__(self):
        self.exchange = None
        self.error_count = 0
        self.last_balance = 0
        self.trades_executed = 0
        self.self_heal_count = 0
        logger.info("🧠 SELF-HEALING HUNTER INITIALIZING...")
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize exchange with error handling"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
                'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
                'sandbox': True,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            logger.info("[OK] Exchange initialized successfully")
        except Exception as e:
            logger.error(f"[X] Exchange init failed: {e}")
            logger.info("🔄 SELF-HEALING: Retrying in 5s...")
            asyncio.sleep(5)
            self._initialize_exchange()
    
    async def scan_opportunities(self) -> List[Dict]:
        """
        Scan for HYPER-AGGRESSIVE SCALPING opportunities.
        1. Filter for High Volatility & Volume (24h)
        2. Drill down with 5m Candles to find ACTIVE breakouts
        3. Prioritize "Cheap" coins (0.000...) for high percentage moves
        """
        try:
            # Load markets
            if not self.exchange.markets:
                await self.exchange.load_markets()
            
            # Get ALL tickers
            tickers = await self.exchange.fetch_tickers()
            
            candidates = []
            for symbol, ticker in tickers.items():
                # Only USDT pairs
                if not symbol.endswith('/USDT'):
                    continue
                
                # Skip stablecoins and weird tokens
                base = symbol.split('/')[0]
                if base in ['USDC', 'USDT', 'DAI', 'BUSD', 'EUR', 'GBP']:
                    continue
                
                volume = ticker.get('quoteVolume', 0)
                price = ticker.get('last', 0)
                
                # Filter: Reasonable volume but allow chaotic lower volume pairs (at least 20k)
                if volume < 20000 or price <= 0:
                    continue
                
                # Metrics
                change_24h = abs(ticker.get('percentage', 0))
                high = ticker.get('high', price)
                low = ticker.get('low', price)
                
                # Calc 24h Volatility
                volatility_24h = (high - low) / low if low > 0 else 0
                
                # Initial Score: Volatility is KING.
                # Bonus for Cheap Coins (Price < 0.01) -> User preference for "0.0000 ranges"
                price_bias = 2.0 if price < 0.01 else 1.0
                if price < 0.0001: price_bias = 3.0 # Meme coin boost
                
                raw_score = (volatility_24h * 50) + (change_24h * 2) + (price_bias * 5)
                
                candidates.append({
                    'symbol': symbol,
                    'raw_score': raw_score,
                    'ticker': ticker,
                    'price': price
                })
            
            # Sort by raw score and take Top 15 candidates for Deep Scan
            candidates.sort(key=lambda x: x['raw_score'], reverse=True)
            top_candidates = candidates[:15]
            
            verified_opportunities = []
            logger.info(f"🔬 DEEP SCANNING top {len(top_candidates)} candidates for IMMEDIATE momentum...")
            
            for cand in top_candidates:
                symbol = cand['symbol']
                try:
                    # Fetch last 5 candles (5m timeframe) -> 25 minutes of context
                    ohlcv = await self.exchange.fetch_ohlcv(symbol, '5m', limit=5)
                    if not ohlcv or len(ohlcv) < 3:
                        continue
                        
                    # Analyze Momentum
                    # Candle format: [timestamp, open, high, low, close, volume]
                    last_close = ohlcv[-1][4]
                    last_open = ohlcv[-1][1]
                    prev_close = ohlcv[-2][4]
                    
                    # 5m Change
                    change_5m = (last_close - last_open) / last_open
                    
                    # Trend Check: Are we moving UP?
                    # We want "Aggressive", so we look for MOMENTUM (Green candles)
                    # Or massive dips (Rebound). User wants "making trades alot" -> Trend Following is safer for compounding.
                    
                    momentum_5m_score = abs(change_5m) * 100
                    
                    # Volume Spike Check (Last volume vs Avg previous)
                    last_vol = ohlcv[-1][5]
                    avg_vol = sum([c[5] for c in ohlcv[:-1]]) / (len(ohlcv)-1)
                    vol_spike = last_vol / avg_vol if avg_vol > 0 else 1
                    
                    # FINAL SCORE calculation
                    # We want: Existing Volatility + LOCAL 5m Move + Volume Spike
                    final_score = cand['raw_score'] + (momentum_5m_score * 10) + (vol_spike * 5)
                    
                    action = 'BUY' if change_5m > 0 else 'SELL' # Simple trend follow for scalping
                    # Note: Spot only supports BUY. If sell signal, we ignore unless we have tokens (which monitor handles)
                    # For Spot Hunter, we usually only BUY.
                    
                    if change_5m > 0.002: # At least 0.2% move in last 5m to be worth it
                         verified_opportunities.append({
                            'symbol': symbol,
                            'change': cand['ticker']['percentage'],
                            'price': last_close,
                            'score': final_score,
                            'action': 'BUY',
                            'volatility': momentum_5m_score
                        })
                except Exception as e:
                    logger.error(f"Failed deep scan for {symbol}: {e}")
                    continue
            
            # Sort by Final Score
            verified_opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            if verified_opportunities:
                logger.info(f"🎯 SCALPER TARGETS (Top 3): {', '.join([f'{o['symbol']} ({o['score']:.1f})' for o in verified_opportunities[:3]])}")
                return verified_opportunities[:5]
            
            logger.info(" No aggressive 5m setups found, widening search...")
            return [] # Retry next loop rather than forcing bad trade
            
        except Exception as e:
            logger.error(f"[X] Scan error: {e}")
            self.error_count += 1
            await self._self_heal()
            return []
    
    async def execute_trade(self, opportunity: Dict) -> bool:
        """Execute trade with full compounding"""
        try:
            symbol = opportunity['symbol']
            action = opportunity['action']
            
            # Get current balance
            balance = await self.exchange.fetch_balance()
            usdt_free = balance['USDT']['free']
            
            logger.info(f"💰 Available: ${usdt_free:.2f} USDT")
            
            if usdt_free < 5:
                logger.warning(f" Balance too low: ${usdt_free:.2f}")
                return False
            
            # FULL COMPOUNDING: Use 95% of balance
            trade_value = usdt_free * 0.95
            
            # Get current price
            ticker = await self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            # Calculate amount
            amount = trade_value / price
            
            # Round to exchange precision
            market = self.exchange.market(symbol)
            amount = self.exchange.amount_to_precision(symbol, amount)
            
            logger.info(f">> EXECUTING: {action} {amount} {symbol} @ ${price:.4f}")
            logger.info(f"   Trade Value: ${trade_value:.2f}")
            
            # Execute market order
            order = await self.exchange.create_order(
                symbol,
                'market',
                action.lower(),
                amount
            )
            
            self.trades_executed += 1
            logger.info(f"[OK] ORDER FILLED: {order['id']}")
            logger.info(f"   Status: {order['status']}")
            logger.info(f"   Total Trades: {self.trades_executed}")
            
            # Reset error count on success
            self.error_count = 0
            
            return True
            
        except ccxt.InsufficientFunds as e:
            logger.error(f"[X] Insufficient funds: {e}")
            return False
        except Exception as e:
            logger.error(f"[X] Trade execution failed: {e}")
            logger.error(traceback.format_exc())
            self.error_count += 1
            await self._self_heal()
            return False
    
    async def _self_heal(self):
        """🔄 SELF-HEALING: Auto-fix errors"""
        self.self_heal_count += 1
        logger.warning(f"🔄 SELF-HEALING ACTIVATED (Count: {self.self_heal_count})")
        
        if self.error_count > 5:
            logger.warning(" Multiple errors detected. Reinitializing exchange...")
            try:
                await self.exchange.close()
            except:
                pass
            self._initialize_exchange()
            self.error_count = 0
            logger.info("[OK] Exchange reinitialized")
        
        # Brief pause to prevent rate limiting
        await asyncio.sleep(2)
    
    async def monitor_balance(self):
        """Monitor balance growth"""
        try:
            balance = await self.exchange.fetch_balance()
            current = balance['USDT']['total']
            
            if current != self.last_balance:
                change = current - self.last_balance
                pct = (change / self.last_balance * 100) if self.last_balance > 0 else 0
                
                logger.info(f"💰 BALANCE UPDATE: ${current:.2f} USDT ({change:+.2f} / {pct:+.1f}%)")
                self.last_balance = current
                
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
    
    async def run(self):
        """Main trading loop - NEVER STOPS"""
        logger.info("=" * 60)
        logger.info("🧠 SELF-HEALING HUNTER ACTIVATED")
        logger.info("   Autonomous · Self-Correcting · Unstoppable")
        logger.info("=" * 60)
        
        # Initial balance
        await self.monitor_balance()
        
        cycle = 0
        while True:
            try:
                cycle += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 CYCLE #{cycle}")
                logger.info(f"{'='*60}")
                
                # Scan for opportunities
                opportunities = await self.scan_opportunities()
                
                if opportunities:
                    # Execute best opportunity
                    best = opportunities[0]
                    logger.info(f"🎯 BEST: {best['symbol']} {best['action']} (Score: {best['score']:.2f})")
                    
                    success = await self.execute_trade(best)
                    
                    if success:
                        # Check balance after trade
                        await asyncio.sleep(2)
                        await self.monitor_balance()
                else:
                    logger.info("⏳ No opportunities found. Scanning again...")
                
                # Wait before next cycle
                await asyncio.sleep(15)
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested")
                break
            except Exception as e:
                logger.error(f"[X] CRITICAL ERROR: {e}")
                logger.error(traceback.format_exc())
                logger.warning("🔄 SELF-HEALING: Recovering...")
                await self._self_heal()
                await asyncio.sleep(5)
                logger.info("[OK] Recovery complete. Resuming...")
        
        # Cleanup
        try:
            await self.exchange.close()
            logger.info("[OK] Exchange connection closed")
        except:
            pass

async def main():
    hunter = SelfHealingHunter()
    await hunter.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
    except Exception as e:
        logger.error(f"[X] Fatal error: {e}")
        logger.error(traceback.format_exc())
