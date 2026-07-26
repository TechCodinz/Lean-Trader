"""
AUTOMATIC POSITION CLEANUP CLASS

Add this BEFORE the CompleteUltimateOrchestrator class definition
"""

class AutomaticPositionCleanup:
    """
    Automatically closes dead/stuck positions to free capital
    
    Runs every 5 minutes to check all open positions and closes:
    - Positions older than 24 hours with no profit
    - Positions stuck with no movement for 4 hours
    - Small losses (-2% or less) to free capital
    - Profitable positions at 0.5%+ for stuck trades
    """
    
    def __init__(self, exchange, logger):
        self.exchange = exchange
        self.logger = logger
        self.position_tracking = {}  # {symbol: {'entry_time': time, 'last_activity': time, 'entry_value': value}}
        
        # Configuration
        self.max_age_hours = 24  # Close if no profit after 24h
        self.max_stuck_hours = 4  # Close if no movement for 4h
        self.small_loss_threshold = -0.02  # Close positions down 2% or less
        self.profit_target = 0.005  # Take profit at 0.5% for stuck positions
        
        self.logger.info("🧹 AUTOMATIC POSITION CLEANUP initialized")
        self.logger.info(f"   Max age: {self.max_age_hours}h, Max stuck: {self.max_stuck_hours}h")
        self.logger.info(f"   Small loss threshold: {self.small_loss_threshold:.1%}, Profit target: {self.profit_target:.1%}")
    
    async def cleanup_loop(self):
        """Main cleanup loop - runs continuously"""
        while True:
            try:
                await self.check_and_cleanup()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Position cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def check_and_cleanup(self):
        """Check all positions and close dead ones"""
        try:
            balance = await self.exchange.fetch_balance()
            now = datetime.now()
            
            closed_count = 0
            freed_capital = 0
            
            for currency, amounts in balance.items():
                if currency == 'USDT':
                    continue
                
                free = amounts.get('free', 0)
                if free <= 0:
                    continue
                
                symbol = f"{currency}/USDT"
                
                # Track position
                if symbol not in self.position_tracking:
                    self.position_tracking[symbol] = {
                        'entry_time': now,
                        'last_activity': now,
                        'entry_value': free
                    }
                
                track = self.position_tracking[symbol]
                position_age = (now - track['entry_time']).total_seconds() / 3600
                stuck_time = (now - track['last_activity']).total_seconds() / 3600
                
                # Get current value
                try:
                    ticker = await self.exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    current_value = free * current_price
                    pnl_pct = (current_value - track['entry_value']) / track['entry_value'] if track['entry_value'] > 0 else 0
                    
                    should_close = False
                    reason = ""
                    
                    # Check cleanup conditions
                    if position_age > self.max_age_hours:
                        should_close = True
                        reason = f"Dead (age: {position_age:.1f}h, PnL: {pnl_pct:+.2%})"
                    
                    elif stuck_time > self.max_stuck_hours and pnl_pct < self.profit_target:
                        should_close = True
                        reason = f"Stuck (no movement: {stuck_time:.1f}h, PnL: {pnl_pct:+.2%})"
                    
                    elif pnl_pct >= self.small_loss_threshold and pnl_pct < 0:
                        should_close = True
                        reason = f"Small loss ({pnl_pct:.2%}) - freeing capital"
                    
                    elif pnl_pct >= self.profit_target:
                        should_close = True
                        reason = f"Profit target ({pnl_pct:.2%})"
                    
                    if should_close:
                        # Close position
                        try:
                            self.logger.info(f"🧹 Closing {symbol}: {reason}")
                            order = await self.exchange.create_market_sell_order(symbol, free)
                            
                            closed_count += 1
                            freed_capital += current_value
                            
                            self.logger.info(f"   [OK] Closed: ${current_value:.2f} freed")
                            
                            # Remove from tracking
                            del self.position_tracking[symbol]
                            
                            await asyncio.sleep(0.5)  # Rate limit
                            
                        except Exception as e:
                            self.logger.warning(f"     Failed to close {symbol}: {e}")
                    
                    # Update last activity if price moved significantly
                    if abs(pnl_pct) > 0.001:  # 0.1% movement
                        track['last_activity'] = now
                        track['entry_value'] = current_value
                
                except Exception as e:
                    # Skip if can't get ticker
                    self.logger.debug(f"Could not get ticker for {symbol}: {e}")
            
            if closed_count > 0:
                self.logger.info(f"🧹 CLEANUP COMPLETE: Closed {closed_count} positions, freed ${freed_capital:.2f}")
            
        except Exception as e:
            self.logger.error(f"Cleanup check error: {e}")


