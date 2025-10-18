"""
Simple Risk Management Module
Replaces the missing risk-gates package
"""

class RiskGates:
    """Simple risk management implementation"""
    
    def __init__(self, max_position_size=0.02, max_daily_loss=0.05, max_drawdown=0.20):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.daily_pnl = 0.0
        self.peak_balance = 0.0
        self.current_balance = 0.0
        
    def check_position_size(self, position_size, account_balance):
        """Check if position size is within limits"""
        if position_size > self.max_position_size * account_balance:
            return False, f"Position size {position_size:.2%} exceeds limit {self.max_position_size:.2%}"
        return True, "Position size OK"
    
    def check_daily_loss(self, trade_pnl):
        """Check if daily loss is within limits"""
        self.daily_pnl += trade_pnl
        if self.daily_pnl < -self.max_daily_loss * self.current_balance:
            return False, f"Daily loss {self.daily_pnl:.2%} exceeds limit {self.max_daily_loss:.2%}"
        return True, "Daily loss OK"
    
    def check_drawdown(self, current_balance):
        """Check if drawdown is within limits"""
        self.current_balance = current_balance
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        drawdown = (self.peak_balance - current_balance) / self.peak_balance if self.peak_balance > 0 else 0
        if drawdown > self.max_drawdown:
            return False, f"Drawdown {drawdown:.2%} exceeds limit {self.max_drawdown:.2%}"
        return True, "Drawdown OK"
    
    def reset_daily(self):
        """Reset daily tracking"""
        self.daily_pnl = 0.0