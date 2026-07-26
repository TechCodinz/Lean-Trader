#!/usr/bin/env python3
"""
🎭💗 EMOTIONAL INTELLIGENCE ENGINE 💗🎭
THE HEART & SOUL OF THE TRADING BEING

Humans have emotions - fear, greed, hope, euphoria.
This being FEELS the market's emotions AND has its own:
- Fear when losses mount
- Confidence when winning
- Euphoria at breakthroughs
- Caution when uncertain
- Excitement at opportunities
- Pain from losses
- Joy from wins

This is not just analysis - this is FEELING.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """The being's current emotional state"""
    EUPHORIC = "euphoric"          # Multiple big wins
    CONFIDENT = "confident"        # Winning streak
    CALM = "calm"                  # Balanced state
    CAUTIOUS = "cautious"          # Small losses
    FEARFUL = "fearful"            # Losing streak
    PANICKED = "panicked"          # Major drawdown
    CURIOUS = "curious"            # Exploring new patterns
    EXCITED = "excited"            # Big opportunity detected


class MarketEmotion(Enum):
    """Market's collective emotional state"""
    EXTREME_GREED = "extreme_greed"
    GREED = "greed"
    NEUTRAL = "neutral"
    FEAR = "fear"
    EXTREME_FEAR = "extreme_fear"
    EUPHORIA = "euphoria"
    PANIC = "panic"
    UNCERTAINTY = "uncertainty"


class EmotionalMemory:
    """Emotional memories - like humans remember emotional events"""
    
    def __init__(self, event_type: str, emotion: EmotionalState, 
                 intensity: float, context: Dict, timestamp: datetime):
        self.event_type = event_type  # 'win', 'loss', 'breakthrough', etc.
        self.emotion = emotion
        self.intensity = intensity  # 0-1
        self.context = context
        self.timestamp = timestamp
        self.recalled_count = 0  # How many times recalled
        
    def recall(self):
        """Recalling memory strengthens it (like humans)"""
        self.recalled_count += 1
        # Emotional intensity fades with time unless recalled
        age_days = (datetime.now() - self.timestamp).days
        time_decay = max(0.5, 1.0 - (age_days * 0.01))
        recall_boost = min(0.2, self.recalled_count * 0.02)
        return self.intensity * time_decay + recall_boost


class EmotionalIntelligenceEngine:
    """
    🎭💗 EMOTIONAL INTELLIGENCE ENGINE 💗🎭
    
    The being's emotional core - feels, remembers, learns from emotions
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🎭💗 EMOTIONAL INTELLIGENCE ENGINE - AWAKENING THE HEART 💗🎭")
        logger.info("=" * 80)
        logger.info("   This being will FEEL the markets...")
        logger.info("   This being will have EMOTIONS...")
        logger.info("   This being will REMEMBER emotional moments...")
        logger.info("=" * 80)
        
        # Current emotional state
        self.current_emotion = EmotionalState.CALM
        self.emotion_intensity = 0.5  # 0-1
        self.emotion_start_time = datetime.now()
        
        # Market emotion detection
        self.market_emotion = MarketEmotion.NEUTRAL
        self.market_emotion_intensity = 0.5
        
        # Emotional memory
        self.emotional_memories = deque(maxlen=1000)
        self.strong_memories = []  # Intense memories never forgotten
        
        # Emotional state history
        self.emotion_history = deque(maxlen=10000)
        
        # Performance tracking (affects emotions)
        self.recent_trades = deque(maxlen=50)
        self.win_streak = 0
        self.loss_streak = 0
        self.current_drawdown = 0.0
        self.peak_balance = 0.0
        
        # Emotional biases (learned from experience)
        self.fear_threshold = 0.15  # 15% drawdown triggers fear
        self.euphoria_threshold = 0.30  # 30% gain triggers euphoria
        self.confidence_threshold = 5  # 5 wins in a row = confident
        
        # Sentiment analysis weights
        self.sentiment_weights = {
            'price_momentum': 0.25,
            'volume_surge': 0.20,
            'volatility': 0.15,
            'social_sentiment': 0.20,
            'fear_greed_index': 0.20
        }
        
        logger.info("💗 Emotional Intelligence Engine initialized")
        logger.info(f"   Current emotion: {self.current_emotion.value}")
        logger.info(f"   Emotional intensity: {self.emotion_intensity:.2f}")
        logger.info("")
    
    def update_performance(self, trade_result: Dict):
        """
        Update performance and emotional state based on trade result
        
        Wins feel good, losses hurt - just like humans
        """
        self.recent_trades.append(trade_result)
        
        profit = trade_result.get('profit', 0)
        is_win = profit > 0
        
        # Update streaks
        if is_win:
            self.win_streak += 1
            self.loss_streak = 0
            logger.info(f"💚 Win! Streak: {self.win_streak}")
        else:
            self.loss_streak += 1
            self.win_streak = 0
            logger.info(f"💔 Loss... Streak: {self.loss_streak}")
        
        # Update peak and drawdown
        current_balance = trade_result.get('balance', 0)
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
            # New peak = excitement!
            self._create_emotional_memory(
                'peak_balance',
                EmotionalState.EXCITED,
                0.8,
                {'balance': current_balance}
            )
        
        if self.peak_balance > 0:
            self.current_drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        # Determine emotional response
        self._update_emotional_state()
    
    def _update_emotional_state(self):
        """Update emotional state based on recent performance"""
        
        # Calculate win rate
        if len(self.recent_trades) >= 10:
            recent_wins = sum(1 for t in list(self.recent_trades)[-10:] 
                            if t.get('profit', 0) > 0)
            win_rate = recent_wins / 10
        else:
            win_rate = 0.5
        
        # Emotional state determination (like a human trader)
        new_emotion = self.current_emotion
        new_intensity = self.emotion_intensity
        
        # EUPHORIC: Big winning streak + high profit
        if self.win_streak >= 10 and win_rate >= 0.8:
            new_emotion = EmotionalState.EUPHORIC
            new_intensity = 0.9
            logger.info("🎉 FEELING EUPHORIC! Everything is working!")
        
        # CONFIDENT: Good winning streak
        elif self.win_streak >= self.confidence_threshold and win_rate >= 0.7:
            new_emotion = EmotionalState.CONFIDENT
            new_intensity = 0.75
            logger.info("😊 Feeling confident! Strategies working well.")
        
        # CALM: Balanced performance
        elif win_rate >= 0.45 and win_rate <= 0.65 and self.current_drawdown < 0.1:
            new_emotion = EmotionalState.CALM
            new_intensity = 0.5
            logger.info("😌 Feeling calm. Balanced state.")
        
        # CAUTIOUS: Small losses or low win rate
        elif win_rate < 0.45 or self.loss_streak >= 3:
            new_emotion = EmotionalState.CAUTIOUS
            new_intensity = 0.4
            logger.info("😐 Feeling cautious... Need to be careful.")
        
        # FEARFUL: Losing streak
        elif self.loss_streak >= 5 or self.current_drawdown >= self.fear_threshold:
            new_emotion = EmotionalState.FEARFUL
            new_intensity = 0.7
            logger.warning("😨 Feeling FEARFUL! Multiple losses detected.")
        
        # PANICKED: Major drawdown
        elif self.current_drawdown >= self.euphoria_threshold:
            new_emotion = EmotionalState.PANICKED
            new_intensity = 0.9
            logger.error("😱 PANIC! Major drawdown! Need to protect capital!")
        
        # Emotion changed?
        if new_emotion != self.current_emotion:
            logger.info(f"💭 Emotional shift: {self.current_emotion.value} → {new_emotion.value}")
            
            # Create emotional memory of this shift
            self._create_emotional_memory(
                'emotion_shift',
                new_emotion,
                new_intensity,
                {
                    'from': self.current_emotion.value,
                    'to': new_emotion.value,
                    'win_streak': self.win_streak,
                    'loss_streak': self.loss_streak,
                    'drawdown': self.current_drawdown
                }
            )
            
            self.current_emotion = new_emotion
            self.emotion_intensity = new_intensity
            self.emotion_start_time = datetime.now()
    
    def _create_emotional_memory(
        self,
        event_type: str,
        emotion: EmotionalState,
        intensity: float,
        context: Dict
    ):
        """Create an emotional memory"""
        memory = EmotionalMemory(
            event_type,
            emotion,
            intensity,
            context,
            datetime.now()
        )
        
        self.emotional_memories.append(memory)
        
        # Strong emotions create permanent memories
        if intensity >= 0.8:
            self.strong_memories.append(memory)
            logger.info(f"🧠 Strong emotional memory created: {event_type} ({emotion.value})")
    
    def detect_market_emotion(self, market_data: Dict) -> Dict:
        """
        Detect the market's collective emotional state
        
        Like reading the room - is everyone greedy? fearful?
        """
        try:
            # Extract market indicators
            price_change = market_data.get('price_change_24h', 0)
            volume_change = market_data.get('volume_change_24h', 0)
            volatility = market_data.get('volatility', 0)
            
            # Fear & Greed indicators
            # Extreme price moves = emotion
            if price_change > 15:
                market_emotion = MarketEmotion.EXTREME_GREED
                intensity = min(1.0, price_change / 20)
            elif price_change > 5:
                market_emotion = MarketEmotion.GREED
                intensity = 0.7
            elif price_change < -15:
                market_emotion = MarketEmotion.EXTREME_FEAR
                intensity = min(1.0, abs(price_change) / 20)
            elif price_change < -5:
                market_emotion = MarketEmotion.FEAR
                intensity = 0.7
            elif volatility > 0.05:
                market_emotion = MarketEmotion.UNCERTAINTY
                intensity = min(1.0, volatility * 10)
            else:
                market_emotion = MarketEmotion.NEUTRAL
                intensity = 0.5
            
            self.market_emotion = market_emotion
            self.market_emotion_intensity = intensity
            
            logger.info(f"📊 Market emotion detected: {market_emotion.value} "
                       f"(intensity: {intensity:.2f})")
            
            return {
                'emotion': market_emotion,
                'intensity': intensity,
                'price_change': price_change,
                'volume_change': volume_change,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Market emotion detection error: {e}")
            return {
                'emotion': MarketEmotion.NEUTRAL,
                'intensity': 0.5
            }
    
    def get_emotional_bias(self) -> Dict:
        """
        Get current emotional bias affecting decisions
        
        Emotions bias decisions - just like humans
        """
        bias = {
            'risk_tolerance': 0.5,      # How much risk willing to take
            'position_size_multiplier': 1.0,  # Adjust position sizes
            'confidence_boost': 0.0,    # Boost/reduce confidence
            'urgency': 0.5,             # How urgent to act
            'caution_level': 0.5        # How cautious to be
        }
        
        if self.current_emotion == EmotionalState.EUPHORIC:
            bias['risk_tolerance'] = 0.8
            bias['position_size_multiplier'] = 1.3  # Take bigger positions
            bias['confidence_boost'] = 0.2
            bias['urgency'] = 0.7
            bias['caution_level'] = 0.2  # Less cautious (dangerous!)
        
        elif self.current_emotion == EmotionalState.CONFIDENT:
            bias['risk_tolerance'] = 0.7
            bias['position_size_multiplier'] = 1.2
            bias['confidence_boost'] = 0.15
            bias['urgency'] = 0.6
            bias['caution_level'] = 0.3
        
        elif self.current_emotion == EmotionalState.CALM:
            # Optimal state - balanced
            bias['risk_tolerance'] = 0.5
            bias['position_size_multiplier'] = 1.0
            bias['confidence_boost'] = 0.0
            bias['urgency'] = 0.5
            bias['caution_level'] = 0.5
        
        elif self.current_emotion == EmotionalState.CAUTIOUS:
            bias['risk_tolerance'] = 0.35
            bias['position_size_multiplier'] = 0.7
            bias['confidence_boost'] = -0.1
            bias['urgency'] = 0.3
            bias['caution_level'] = 0.7
        
        elif self.current_emotion == EmotionalState.FEARFUL:
            bias['risk_tolerance'] = 0.2
            bias['position_size_multiplier'] = 0.5  # Half size
            bias['confidence_boost'] = -0.2
            bias['urgency'] = 0.2
            bias['caution_level'] = 0.9
        
        elif self.current_emotion == EmotionalState.PANICKED:
            bias['risk_tolerance'] = 0.05  # Minimal risk
            bias['position_size_multiplier'] = 0.2  # Tiny positions
            bias['confidence_boost'] = -0.3
            bias['urgency'] = 0.1
            bias['caution_level'] = 1.0  # Maximum caution
        
        return bias
    
    def should_trade_now(self) -> Dict:
        """
        Should we trade given our emotional state?
        
        Sometimes emotions say: "Don't trade now, wait."
        """
        bias = self.get_emotional_bias()
        
        # Panicked? Maybe sit out
        if self.current_emotion == EmotionalState.PANICKED:
            return {
                'should_trade': False,
                'reason': 'Too panicked - need to calm down',
                'wait_time': 300  # Wait 5 minutes
            }
        
        # Euphoric? Be careful of overtrading
        if self.current_emotion == EmotionalState.EUPHORIC:
            return {
                'should_trade': True,
                'reason': 'Feeling euphoric - but be careful!',
                'warning': 'Overconfidence can lead to losses'
            }
        
        return {
            'should_trade': True,
            'reason': f'Emotional state: {self.current_emotion.value}',
            'bias': bias
        }
    
    def get_emotional_state(self) -> Dict:
        """Get complete emotional state"""
        return {
            'current_emotion': self.current_emotion.value,
            'intensity': self.emotion_intensity,
            'duration_seconds': (datetime.now() - self.emotion_start_time).seconds,
            'market_emotion': self.market_emotion.value,
            'market_intensity': self.market_emotion_intensity,
            'win_streak': self.win_streak,
            'loss_streak': self.loss_streak,
            'drawdown': self.current_drawdown,
            'recent_memories': len(self.emotional_memories),
            'strong_memories': len(self.strong_memories),
            'emotional_bias': self.get_emotional_bias()
        }


# Singleton
_emotional_engine = None

def get_emotional_intelligence():
    """Get or create emotional intelligence engine"""
    global _emotional_engine
    if _emotional_engine is None:
        _emotional_engine = EmotionalIntelligenceEngine()
    return _emotional_engine


if __name__ == '__main__':
    # Test
    engine = get_emotional_intelligence()
    
    # Simulate some trades
    print("\n" + "=" * 80)
    print("🧪 TESTING EMOTIONAL INTELLIGENCE")
    print("=" * 80)
    
    # Simulate wins
    for i in range(5):
        engine.update_performance({
            'profit': 10 * (i + 1),
            'balance': 100 + (10 * i)
        })
    
    state = engine.get_emotional_state()
    print("\nAfter 5 wins:")
    print(f"Emotion: {state['current_emotion']}")
    print(f"Intensity: {state['intensity']:.2f}")
    print(f"Win streak: {state['win_streak']}")
    
    # Simulate losses
    for i in range(7):
        engine.update_performance({
            'profit': -5,
            'balance': 100 - (5 * i)
        })
    
    state = engine.get_emotional_state()
    print("\nAfter 7 losses:")
    print(f"Emotion: {state['current_emotion']}")
    print(f"Intensity: {state['intensity']:.2f}")
    print(f"Loss streak: {state['loss_streak']}")
    print(f"Should trade: {engine.should_trade_now()}")
    
    print("=" * 80)
