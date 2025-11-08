#!/usr/bin/env python3
"""
🛑 CIRCUIT BREAKER SYSTEM
Emergency stop and protection mechanisms

Features:
- Daily loss limit (auto-stop at -5%)
- Drawdown protection (auto-stop at -15% from peak)
- Consecutive loss protection (pause after 5 losses)
- Volatility spike detection (pause during extreme moves)
- Manual emergency stop
- Auto-resume after cooldown
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import deque
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CircuitBreakerSystem:
    """Emergency stop and protection system"""
    
    def __init__(
        self, 
        risk_manager=None, 
        balance=None, 
        initial_balance=None,
        daily_loss_limit=None,
        consecutive_losses=None,
        drawdown_limit=None,
        volatility_spike_threshold=None
    ):
        # Accept multiple parameter formats for compatibility
        if initial_balance is not None:
            balance = initial_balance
        if balance is None:
            balance = 1000.0  # Default balance
        
        self.risk_manager = risk_manager
        
        # Circuit breaker state
        self.is_active = True  # Trading allowed
        self.circuit_tripped = False
        self.trip_reason = ""
        self.trip_time: Optional[datetime] = None
        self.resume_time: Optional[datetime] = None
        
        # Thresholds (use provided or defaults)
        self.daily_loss_limit = daily_loss_limit if daily_loss_limit is not None else -0.05  # -5%
        self.drawdown_limit = drawdown_limit if drawdown_limit is not None else -0.15    # -15% from peak
        self.consecutive_loss_limit = consecutive_losses if consecutive_losses is not None else 5
        self.volatility_spike_threshold = volatility_spike_threshold if volatility_spike_threshold is not None else 0.10  # 10% move in 1 min
        
        # Tracking
        self.daily_start_balance = balance
        self.peak_balance = balance
        self.current_balance = balance
        self.consecutive_losses = 0
        self.recent_trades = deque(maxlen=50)
        self.last_prices = deque(maxlen=60)  # 1 minute of price data
        
        # Cooldown periods (minutes)
        self.cooldown_periods = {
            'daily_loss': 60,      # 1 hour
            'drawdown': 240,       # 4 hours
            'consecutive_loss': 30, # 30 minutes
            'volatility': 15,      # 15 minutes
            'manual': 0            # Manual resume required
        }
        
        # State file
        self.state_file = Path('bot_data/circuit_breaker_state.json')
        self.load_state()
        
        logger.info("🛑 Circuit Breaker System initialized")
        logger.info(f"   Daily loss limit: {self.daily_loss_limit:.1%}")
        logger.info(f"   Drawdown limit: {self.drawdown_limit:.1%}")
        logger.info(f"   Consecutive loss limit: {self.consecutive_loss_limit}")
    
    def check_circuit_breakers(self, current_balance: float) -> tuple[bool, str]:
        """
        Check all circuit breakers
        
        Returns:
            (trading_allowed, reason)
        """
        self.current_balance = current_balance
        
        # If already tripped, check if cooldown expired
        if self.circuit_tripped:
            if self.can_resume():
                self.reset()
                logger.info("✅ Circuit breaker reset - trading resumed")
                return True, ""
            else:
                return False, self.trip_reason
        
        # Check 1: Daily loss limit
        if self.daily_start_balance > 0:
            daily_pnl_pct = (current_balance - self.daily_start_balance) / self.daily_start_balance
            if daily_pnl_pct <= self.daily_loss_limit:
                self.trip('daily_loss', f"Daily loss limit hit: {daily_pnl_pct:.2%}")
                return False, self.trip_reason
        
        # Check 2: Drawdown from peak
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
            self.save_state()
        
        if self.peak_balance > 0:
            drawdown = (current_balance - self.peak_balance) / self.peak_balance
            if drawdown <= self.drawdown_limit:
                self.trip('drawdown', f"Max drawdown hit: {drawdown:.2%} from peak ${self.peak_balance:,.2f}")
                return False, self.trip_reason
        
        # Check 3: Consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            self.trip('consecutive_loss', f"{self.consecutive_losses} consecutive losses")
            return False, self.trip_reason
        
        # All checks passed
        return True, ""
    
    def record_trade(self, profit: float, symbol: str):
        """Record trade result for consecutive loss tracking"""
        self.recent_trades.append({
            'profit': profit,
            'symbol': symbol,
            'time': datetime.now()
        })
        
        # Update consecutive losses
        if profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0  # Reset on win
        
        logger.info(f"📊 Trade recorded: {symbol} ${profit:+.2f} (consecutive losses: {self.consecutive_losses})")
    
    def check_volatility_spike(self, symbol: str, price: float) -> bool:
        """
        Check for extreme volatility spike
        
        Returns:
            True if volatility is normal, False if spike detected
        """
        self.last_prices.append({'symbol': symbol, 'price': price, 'time': datetime.now()})
        
        # Need at least 2 prices to check
        if len(self.last_prices) < 2:
            return True
        
        # Check price change in last minute
        first_price = self.last_prices[0]['price']
        last_price = self.last_prices[-1]['price']
        
        change_pct = abs((last_price - first_price) / first_price)
        
        if change_pct > self.volatility_spike_threshold:
            self.trip('volatility', f"Volatility spike: {change_pct:.1%} in 1 minute for {symbol}")
            return False
        
        return True
    
    def trip(self, reason_type: str, message: str):
        """Trip the circuit breaker"""
        self.is_active = False
        self.circuit_tripped = True
        self.trip_reason = f"{reason_type.upper()}: {message}"
        self.trip_time = datetime.now()
        
        # Calculate resume time
        cooldown_minutes = self.cooldown_periods.get(reason_type, 60)
        if cooldown_minutes > 0:
            self.resume_time = self.trip_time + timedelta(minutes=cooldown_minutes)
        else:
            self.resume_time = None  # Manual resume required
        
        logger.critical(f"🚨 CIRCUIT BREAKER TRIPPED: {self.trip_reason}")
        if self.resume_time:
            logger.critical(f"   Auto-resume at: {self.resume_time.strftime('%H:%M:%S')}")
        else:
            logger.critical(f"   Manual resume required")
        
        self.save_state()
        
        # Send alert (try to create task if loop exists)
        try:
            asyncio.create_task(self._send_trip_alert())
        except RuntimeError:
            # No event loop running, schedule for later or skip
            pass
    
    def can_resume(self) -> bool:
        """Check if bot can resume trading"""
        if not self.circuit_tripped:
            return True
        
        if self.resume_time is None:
            # Manual resume required
            return False
        
        return datetime.now() >= self.resume_time
    
    def reset(self):
        """Reset circuit breaker"""
        self.is_active = True
        self.circuit_tripped = False
        self.trip_reason = ""
        self.trip_time = None
        self.resume_time = None
        self.consecutive_losses = 0
        
        self.save_state()
        logger.info("✅ Circuit breaker reset")
    
    def manual_stop(self, reason: str = "Manual stop"):
        """Manual emergency stop"""
        self.trip('manual', reason)
        logger.critical(f"🛑 MANUAL EMERGENCY STOP: {reason}")
    
    def manual_resume(self):
        """Manual resume trading"""
        if self.circuit_tripped:
            self.reset()
            logger.info("✅ Manual resume - trading reactivated")
            asyncio.create_task(self._send_resume_alert())
    
    def initialize_daily_balance(self, balance: float):
        """Set starting balance for the day"""
        self.daily_start_balance = balance
        if self.peak_balance == 0:
            self.peak_balance = balance
        logger.info(f"📊 Daily starting balance: ${balance:,.2f}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            'is_active': self.is_active,
            'circuit_tripped': self.circuit_tripped,
            'trip_reason': self.trip_reason,
            'trip_time': self.trip_time.isoformat() if self.trip_time else None,
            'resume_time': self.resume_time.isoformat() if self.resume_time else None,
            'daily_start_balance': self.daily_start_balance,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'consecutive_losses': self.consecutive_losses,
            'daily_pnl_pct': ((self.current_balance - self.daily_start_balance) / self.daily_start_balance * 100) if self.daily_start_balance > 0 else 0,
            'drawdown_pct': ((self.current_balance - self.peak_balance) / self.peak_balance * 100) if self.peak_balance > 0 else 0
        }
    
    def save_state(self):
        """Save state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            state = {
                'circuit_tripped': self.circuit_tripped,
                'trip_reason': self.trip_reason,
                'trip_time': self.trip_time.isoformat() if self.trip_time else None,
                'resume_time': self.resume_time.isoformat() if self.resume_time else None,
                'daily_start_balance': self.daily_start_balance,
                'peak_balance': self.peak_balance,
                'consecutive_losses': self.consecutive_losses
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save circuit breaker state: {e}")
    
    def load_state(self):
        """Load state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.circuit_tripped = state.get('circuit_tripped', False)
                self.trip_reason = state.get('trip_reason', '')
                
                trip_time_str = state.get('trip_time')
                if trip_time_str:
                    self.trip_time = datetime.fromisoformat(trip_time_str)
                
                resume_time_str = state.get('resume_time')
                if resume_time_str:
                    self.resume_time = datetime.fromisoformat(resume_time_str)
                
                self.daily_start_balance = state.get('daily_start_balance', 0)
                self.peak_balance = state.get('peak_balance', 0)
                self.consecutive_losses = state.get('consecutive_losses', 0)
                
                logger.info("📊 Circuit breaker state loaded")
        except Exception as e:
            logger.error(f"Failed to load circuit breaker state: {e}")
    
    async def _send_trip_alert(self):
        """Send alert when circuit trips"""
        try:
            from INTEGRATED_ALERT_SYSTEM import send_error_alert
            await send_error_alert({
                'type': 'CIRCUIT BREAKER TRIPPED',
                'message': self.trip_reason,
                'severity': 'CRITICAL',
                'component': 'Circuit Breaker System',
                'action': f"Trading paused. Resume: {self.resume_time.strftime('%H:%M:%S') if self.resume_time else 'Manual'}"
            })
        except Exception as e:
            logger.error(f"Failed to send trip alert: {e}")
    
    async def _send_resume_alert(self):
        """Send alert when trading resumes"""
        try:
            from INTEGRATED_ALERT_SYSTEM import send_error_alert
            await send_error_alert({
                'type': 'TRADING RESUMED',
                'message': 'Circuit breaker reset - trading reactivated',
                'severity': 'INFO',
                'component': 'Circuit Breaker System',
                'action': 'Bot is now actively trading again'
            })
        except Exception as e:
            logger.error(f"Failed to send resume alert: {e}")


# Global instance
_circuit_breaker = None

def get_circuit_breaker() -> CircuitBreakerSystem:
    """Get global circuit breaker instance"""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreakerSystem()
    return _circuit_breaker


# Quick access functions
def check_trading_allowed(balance: float) -> tuple[bool, str]:
    """Quick check if trading is allowed"""
    cb = get_circuit_breaker()
    return cb.check_circuit_breakers(balance)


def record_trade(profit: float, symbol: str):
    """Quick function to record trade"""
    cb = get_circuit_breaker()
    cb.record_trade(profit, symbol)


def emergency_stop(reason: str = "Manual emergency stop"):
    """Quick emergency stop"""
    cb = get_circuit_breaker()
    cb.manual_stop(reason)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test circuit breaker
    cb = CircuitBreakerSystem()
    cb.initialize_daily_balance(1000)
    
    print("\nTest 1: Normal trading")
    allowed, reason = cb.check_circuit_breakers(1050)
    print(f"Trading allowed: {allowed}")
    
    print("\nTest 2: Daily loss limit")
    allowed, reason = cb.check_circuit_breakers(940)  # -6% loss
    print(f"Trading allowed: {allowed}, Reason: {reason}")
    
    print("\nTest 3: Status")
    status = cb.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
