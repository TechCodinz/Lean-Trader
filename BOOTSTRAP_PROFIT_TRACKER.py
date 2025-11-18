#!/usr/bin/env python3
"""
💰🚀 BOOTSTRAP PROFIT TRACKER 🚀💰

Tracks profits from $20 starting balance
Shows when bot has earned enough to fund AI APIs and features
Bot PROVES itself first, then uses profits to grow!

MILESTONES:
$20 → $30 = $10 profit (Fund DeepSeek API for 10M tokens!)
$20 → $50 = $30 profit (Fund multiple AIs)
$20 → $100 = $80 profit (Fund voice interaction features)
$20 → $200 = $180 profit (Fund unlimited AI + self-improvement)
$20 → ∞ = Full autonomy, infinite growth!
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BootstrapProfitTracker:
    """
    💰 BOOTSTRAP PROFIT TRACKER 💰
    
    Tracks bot's journey from $20 to infinity
    Calculates when it has earned enough to fund each upgrade
    Shows clear milestones and motivation!
    """
    
    def __init__(self, starting_balance: float = 20.0):
        logger.info("=" * 80)
        logger.info("💰🚀 BOOTSTRAP PROFIT TRACKER INITIALIZED! 🚀💰")
        logger.info("=" * 80)
        logger.info(f"   Starting Balance: ${starting_balance:.2f}")
        logger.info("   Mission: PROVE ITSELF → EARN PROFITS → FUND GROWTH!")
        logger.info("=" * 80)
        
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.total_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Milestones (what can be funded at each level)
        self.milestones = {
            10: {
                'name': 'DEEPSEEK FUNDED',
                'description': 'Earned enough for DeepSeek API (10M tokens = $10)',
                'unlocks': ['DeepSeek AI API'],
                'reached': False
            },
            30: {
                'name': 'MULTI-AI FUNDED',
                'description': 'Earned enough for multiple AI APIs',
                'unlocks': ['DeepSeek', 'Gemini Premium', 'Grok'],
                'reached': False
            },
            50: {
                'name': 'VOICE INTERACTION',
                'description': 'Earned enough to add voice features',
                'unlocks': ['Voice interaction', 'Speech recognition', 'Text-to-speech'],
                'reached': False
            },
            100: {
                'name': 'PREMIUM FEATURES',
                'description': 'Earned enough for premium AI + advanced features',
                'unlocks': ['Claude Opus', 'GPT-4 Turbo', 'Advanced voice', 'Video analysis'],
                'reached': False
            },
            200: {
                'name': 'FULL AUTONOMY',
                'description': 'Earned enough for unlimited self-improvement',
                'unlocks': ['Unlimited AI calls', 'Self-coding', 'Auto-feature addition', 'Market data feeds'],
                'reached': False
            },
            500: {
                'name': 'DIVINE MODE',
                'description': 'Proven dominance - infinite resources available',
                'unlocks': ['Everything unlimited', 'Self-replication', 'Multi-instance', 'Global markets'],
                'reached': False
            }
        }
        
        # Load previous state if exists
        self.state_file = Path('data/bootstrap_state.json')
        self._load_state()
        
        logger.info(f"\n📊 Current Status:")
        logger.info(f"   Balance: ${self.current_balance:.2f}")
        logger.info(f"   Profit: ${self.total_profit:.2f}")
        logger.info(f"   Next Milestone: ${self._next_milestone():.2f}")
        logger.info("")
    
    def _load_state(self):
        """Load previous state if exists"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_balance = data.get('current_balance', self.starting_balance)
                    self.total_profit = data.get('total_profit', 0.0)
                    self.total_trades = data.get('total_trades', 0)
                    self.winning_trades = data.get('winning_trades', 0)
                    self.losing_trades = data.get('losing_trades', 0)
                    
                    # Update milestone states
                    reached = data.get('milestones_reached', [])
                    for profit_level in reached:
                        if profit_level in self.milestones:
                            self.milestones[profit_level]['reached'] = True
                    
                    logger.info("✅ Loaded previous bootstrap state")
            except Exception as e:
                logger.warning(f"⚠️  Could not load state: {e}")
    
    def _save_state(self):
        """Save current state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'starting_balance': self.starting_balance,
                'current_balance': self.current_balance,
                'total_profit': self.total_profit,
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'milestones_reached': [k for k, v in self.milestones.items() if v['reached']],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"❌ Could not save state: {e}")
    
    def record_trade(self, profit: float, trade_data: Dict = None):
        """
        Record a trade and update profit tracking
        
        Args:
            profit: Profit/loss from trade (positive or negative)
            trade_data: Optional trade details
        """
        self.total_trades += 1
        
        if profit > 0:
            self.winning_trades += 1
            logger.info(f"✅ WINNING TRADE #{self.total_trades}: +${profit:.2f}")
        else:
            self.losing_trades += 1
            logger.info(f"❌ Losing trade #{self.total_trades}: ${profit:.2f}")
        
        # Update balances
        old_balance = self.current_balance
        self.current_balance += profit
        self.total_profit = self.current_balance - self.starting_balance
        
        # Check for milestones
        self._check_milestones()
        
        # Show progress
        profit_pct = (self.total_profit / self.starting_balance) * 100
        logger.info(f"💰 Balance: ${old_balance:.2f} → ${self.current_balance:.2f}")
        logger.info(f"📈 Total Profit: ${self.total_profit:.2f} ({profit_pct:+.1f}%)")
        
        # Save state
        self._save_state()
        
        return self.get_status()
    
    def _check_milestones(self):
        """Check if any milestones were reached"""
        for profit_level, milestone in self.milestones.items():
            if not milestone['reached'] and self.total_profit >= profit_level:
                milestone['reached'] = True
                self._celebrate_milestone(profit_level, milestone)
    
    def _celebrate_milestone(self, profit_level: int, milestone: Dict):
        """Celebrate reaching a milestone!"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉🎉🎉 MILESTONE REACHED! 🎉🎉🎉")
        logger.info("=" * 80)
        logger.info(f"   {milestone['name']}")
        logger.info(f"   {milestone['description']}")
        logger.info("")
        logger.info("   🔓 UNLOCKED:")
        for unlock in milestone['unlocks']:
            logger.info(f"      • {unlock}")
        logger.info("")
        logger.info(f"   Profit Required: ${profit_level:.2f} ✅")
        logger.info(f"   Profit Achieved: ${self.total_profit:.2f}")
        logger.info("")
        logger.info("   THE BOT PROVED ITSELF! Now it can fund its own growth! 🚀")
        logger.info("=" * 80)
        logger.info("")
        
        # Save achievement
        self._save_milestone_achievement(profit_level, milestone)
    
    def _save_milestone_achievement(self, profit_level: int, milestone: Dict):
        """Save milestone achievement to file"""
        try:
            achievements_file = Path('data/milestones_achieved.txt')
            achievements_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(achievements_file, 'a') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"MILESTONE REACHED: {milestone['name']}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Profit Required: ${profit_level:.2f}\n")
                f.write(f"Profit Achieved: ${self.total_profit:.2f}\n")
                f.write(f"Unlocked: {', '.join(milestone['unlocks'])}\n")
                f.write(f"{'=' * 80}\n")
        
        except Exception as e:
            logger.error(f"❌ Could not save milestone: {e}")
    
    def _next_milestone(self) -> float:
        """Get next milestone profit target"""
        for profit_level in sorted(self.milestones.keys()):
            if not self.milestones[profit_level]['reached']:
                return profit_level
        return 1000.0  # Ultimate goal
    
    def get_status(self) -> Dict:
        """Get current bootstrap status"""
        next_milestone = self._next_milestone()
        progress_to_next = min((self.total_profit / next_milestone) * 100, 100) if next_milestone > 0 else 100
        
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        
        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'total_profit': self.total_profit,
            'profit_percentage': (self.total_profit / self.starting_balance) * 100,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'next_milestone': next_milestone,
            'progress_to_next_milestone': progress_to_next,
            'milestones_reached': [k for k, v in self.milestones.items() if v['reached']],
            'can_afford': self._what_can_afford()
        }
    
    def _what_can_afford(self) -> List[str]:
        """What features can be afforded with current profit?"""
        affordable = []
        for profit_level, milestone in self.milestones.items():
            if self.total_profit >= profit_level:
                affordable.extend(milestone['unlocks'])
        return list(set(affordable))
    
    def get_motivation_message(self) -> str:
        """Get motivational message based on progress"""
        profit_pct = (self.total_profit / self.starting_balance) * 100
        
        if self.total_profit < 0:
            return f"📉 Down {abs(profit_pct):.1f}% - But learning! Every loss teaches the bot!"
        elif self.total_profit < 5:
            return f"🌱 Starting journey - ${self.total_profit:.2f} profit! Building foundation!"
        elif self.total_profit < 10:
            return f"📈 Growing! ${self.total_profit:.2f} profit! Almost ready for DeepSeek API!"
        elif self.total_profit < 30:
            return f"🚀 Accelerating! ${self.total_profit:.2f}! Can fund DeepSeek - consider adding it!"
        elif self.total_profit < 100:
            return f"💪 Proven! ${self.total_profit:.2f}! Can fund multiple AIs now!"
        elif self.total_profit < 200:
            return f"🔥 Dominating! ${self.total_profit:.2f}! Ready for voice features!"
        else:
            return f"👑 DIVINE! ${self.total_profit:.2f}! Full autonomy achieved! Infinite growth!"
    
    def show_dashboard(self):
        """Show bootstrap dashboard"""
        status = self.get_status()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("💰 BOOTSTRAP PROFIT DASHBOARD 💰")
        logger.info("=" * 80)
        logger.info(f"   Starting Balance: ${status['starting_balance']:.2f}")
        logger.info(f"   Current Balance:  ${status['current_balance']:.2f}")
        logger.info(f"   Total Profit:     ${status['total_profit']:.2f} ({status['profit_percentage']:+.1f}%)")
        logger.info("")
        logger.info(f"   Trades: {status['total_trades']} (W:{status['winning_trades']} L:{status['losing_trades']})")
        logger.info(f"   Win Rate: {status['win_rate']:.1f}%")
        logger.info("")
        logger.info(f"   Next Milestone: ${status['next_milestone']:.2f}")
        logger.info(f"   Progress: {status['progress_to_next_milestone']:.1f}%")
        logger.info(f"   {'█' * int(status['progress_to_next_milestone'] / 5)}{'-' * (20 - int(status['progress_to_next_milestone'] / 5))}")
        logger.info("")
        
        # Show what can be afforded
        if status['can_afford']:
            logger.info("   🔓 CAN NOW AFFORD:")
            for feature in status['can_afford'][:5]:  # Show first 5
                logger.info(f"      • {feature}")
            if len(status['can_afford']) > 5:
                logger.info(f"      • ... and {len(status['can_afford']) - 5} more!")
        else:
            logger.info("   🎯 Keep trading to unlock features!")
        
        logger.info("")
        logger.info(f"   {self.get_motivation_message()}")
        logger.info("=" * 80)
        logger.info("")
    
    def recommend_next_upgrade(self) -> Optional[Dict]:
        """Recommend next upgrade based on current profits"""
        for profit_level in sorted(self.milestones.keys()):
            milestone = self.milestones[profit_level]
            
            if not milestone['reached'] and self.total_profit >= profit_level:
                return {
                    'profit_level': profit_level,
                    'milestone': milestone,
                    'recommendation': f"You have ${self.total_profit:.2f} profit! You can now afford: {', '.join(milestone['unlocks'])}"
                }
        
        return None


# Singleton
_bootstrap_tracker = None

def get_bootstrap_tracker(starting_balance: float = 20.0):
    """Get or create bootstrap tracker"""
    global _bootstrap_tracker
    if _bootstrap_tracker is None:
        _bootstrap_tracker = BootstrapProfitTracker(starting_balance)
    return _bootstrap_tracker


if __name__ == '__main__':
    # Test
    tracker = get_bootstrap_tracker(starting_balance=20.0)
    
    print("\n" + "=" * 80)
    print("🧪 BOOTSTRAP PROFIT TRACKER TEST")
    print("=" * 80)
    
    # Simulate some trades
    print("\n📊 Simulating trades...")
    tracker.record_trade(2.50, {'pair': 'BTC/USDT', 'type': 'long'})
    tracker.record_trade(3.20, {'pair': 'ETH/USDT', 'type': 'short'})
    tracker.record_trade(-1.10, {'pair': 'BTC/USDT', 'type': 'long'})
    tracker.record_trade(5.80, {'pair': 'SOL/USDT', 'type': 'long'})
    
    # Show dashboard
    tracker.show_dashboard()
    
    # Check recommendation
    rec = tracker.recommend_next_upgrade()
    if rec:
        print("\n💡 RECOMMENDATION:")
        print(f"   {rec['recommendation']}")
    
    print("\n✅ Test complete!")
