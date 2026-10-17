from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, time
from collections import defaultdict, deque
import pytz
class MarketSession:
    """Trading session detection and management"""
    
    SESSIONS = {
        'ASIAN': {
            'start': time(0, 0),   # 00:00 UTC
            'end': time(8, 0),     # 08:00 UTC
            'major_pairs': ['USDJPY', 'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY'],
            'volatility': 'LOW',
            'characteristics': 'Range-bound, slow moves'
        },
        'LONDON': {
            'start': time(8, 0),   # 08:00 UTC
            'end': time(16, 0),    # 16:00 UTC
            'major_pairs': ['EURUSD', 'GBPUSD', 'EURGBP', 'EURJPY', 'GBPJPY'],
            'volatility': 'HIGH',
            'characteristics': 'Strong trends, high volume'
        },
        'NEW_YORK': {
            'start': time(13, 0),  # 13:00 UTC
            'end': time(21, 0),    # 21:00 UTC
            'major_pairs': ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'XAUUSD'],
            'volatility': 'HIGH',
            'characteristics': 'News-driven, momentum trades'
        },
        'LONDON_NY_OVERLAP': {
            'start': time(13, 0),  # 13:00 UTC
            'end': time(16, 0),    # 16:00 UTC
            'major_pairs': ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTC/USDT', 'ETH/USDT'],
            'volatility': 'VERY_HIGH',
            'characteristics': 'Maximum liquidity, best for scalping'
        }
    }
    
    @staticmethod
    def get_current_session() -> str:
        """Get current trading session"""
        now_utc = datetime.now(pytz.UTC).time()
        
        # Check overlap first (highest priority)
        overlap = MarketSession.SESSIONS['LONDON_NY_OVERLAP']
        if overlap['start'] <= now_utc < overlap['end']:
            return 'LONDON_NY_OVERLAP'
        
        # Check other sessions
        for session_name, session_data in MarketSession.SESSIONS.items():
            if session_name == 'LONDON_NY_OVERLAP':
                continue
            if session_data['start'] <= now_utc < session_data['end']:
                return session_name
        
        return 'ASIAN'  # Default to Asian session
    
    @staticmethod
    def get_optimal_pairs(session: str) -> List[str]:
        """Get optimal trading pairs for current session"""
        return MarketSession.SESSIONS.get(session, {}).get('major_pairs', [])
    
    @staticmethod
    def get_session_volatility(session: str) -> str:
        """Get expected volatility for session"""
        return MarketSession.SESSIONS.get(session, {}).get('volatility', 'MEDIUM')


@dataclass
class TimeframeSignal:
    """Signal from a single timeframe"""
class SessionPerformanceTracker:
    """
    Tracks which markets perform best in which sessions
    Learns over time and optimizes market-session pairs
    """
    
    def __init__(self):
        self.performance: Dict[str, Dict[str, Dict]] = defaultdict(lambda: defaultdict(dict))
        # performance[symbol][session] = {'wins': 0, 'losses': 0, 'avg_profit': 0, 'trades': 0}
        
        self.min_trades_for_confidence = 10  # Need 10 trades before trusting stats
    
    def record_trade(self, symbol: str, session: str, profit: float, success: bool):
        """Record trade result for market-session pair"""
        
        if session not in self.performance[symbol]:
            self.performance[symbol][session] = {
                'wins': 0,
                'losses': 0,
                'total_profit': 0.0,
                'trades': 0,
                'avg_profit': 0.0,
                'win_rate': 0.0
            }
        
        stats = self.performance[symbol][session]
        
        stats['trades'] += 1
        stats['total_profit'] += profit
        
        if success:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        # Update averages
        stats['avg_profit'] = stats['total_profit'] / stats['trades']
        stats['win_rate'] = stats['wins'] / stats['trades']
    
    def get_optimal_markets(self, session: str, min_win_rate: float = 0.60) -> List[Tuple[str, float]]:
        """
        Get best performing markets for a session
        
        Returns:
            List of (symbol, score) sorted by performance
        """
        
        market_scores = []
        
        for symbol, sessions in self.performance.items():
            if session not in sessions:
                continue
            
            stats = sessions[session]
            
            # Need minimum trades for confidence
            if stats['trades'] < self.min_trades_for_confidence:
                continue
            
            # Filter by win rate
            if stats['win_rate'] < min_win_rate:
                continue
            
            # Calculate performance score
            # Score = win_rate * avg_profit * sqrt(trades)
            score = stats['win_rate'] * stats['avg_profit'] * (stats['trades'] ** 0.5)
            
            market_scores.append((symbol, score, stats))
        
        # Sort by score (best first)
        market_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [(symbol, score) for symbol, score, _ in market_scores]
    
    def should_trade_pair(self, symbol: str, session: str) -> Tuple[bool, str]:
        """Check if we should trade this pair in this session"""
        
        # If we don't have data yet, allow trading (learning phase)
        if symbol not in self.performance or session not in self.performance[symbol]:
            return True, "Learning phase - no historical data"
        
        stats = self.performance[symbol][session]
        
        # Not enough data yet
        if stats['trades'] < self.min_trades_for_confidence:
            return True, f"Gathering data: {stats['trades']}/{self.min_trades_for_confidence} trades"
        
        # Check performance
        if stats['win_rate'] < 0.50:
            return False, f"Low win rate: {stats['win_rate']:.1%}"
        
        if stats['avg_profit'] < 0:
            return False, f"Negative avg profit: ${stats['avg_profit']:.2f}"
        
        return True, f"Good performance: {stats['win_rate']:.1%} win rate, ${stats['avg_profit']:.2f} avg"


