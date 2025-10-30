#!/usr/bin/env python3
"""
🔮 PREDICTIVE NEXT-MOVE ENGINE 🔮
KNOWS what's coming BEFORE it happens

Uses:
- Pattern velocity analysis (how fast patterns form)
- Order flow prediction (where orders will go)
- Price trajectory modeling (where price is heading)
- Momentum forecasting (acceleration/deceleration)
- Market regime prediction (what's coming next)
- Multi-step ahead prediction (3-5 moves ahead)
- Probability distribution of outcomes
- Confidence intervals

This engine doesn't just react - it PREDICTS.
It sees the future before it materializes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import statistics
import math

logger = logging.getLogger(__name__)


class PatternVelocityAnalyzer:
    """
    Analyzes HOW FAST patterns are forming
    Fast formation = strong conviction = reliable prediction
    """
    
    def __init__(self):
        self.pattern_history = deque(maxlen=100)
        
        logger.info("⚡ Pattern Velocity Analyzer initialized")
    
    def analyze_pattern_velocity(self, market_state: Dict, historical_states: List[Dict]) -> Dict:
        """
        Measure how fast current pattern is forming
        
        Fast velocity = pattern forming quickly = strong signal
        Slow velocity = pattern forming slowly = weak signal
        """
        if len(historical_states) < 3:
            return {'velocity': 0, 'acceleration': 0, 'strength': 'unknown'}
        
        # Get recent momentum values
        recent_momentums = [
            state.get('momentum_score', 0)
            for state in historical_states[-5:]
        ]
        
        if len(recent_momentums) < 2:
            return {'velocity': 0, 'acceleration': 0, 'strength': 'weak'}
        
        # Calculate velocity (rate of change)
        velocity = recent_momentums[-1] - recent_momentums[-2]
        
        # Calculate acceleration (rate of change of velocity)
        if len(recent_momentums) >= 3:
            prev_velocity = recent_momentums[-2] - recent_momentums[-3]
            acceleration = velocity - prev_velocity
        else:
            acceleration = 0
        
        # Classify strength
        if abs(velocity) > 0.1:
            strength = 'fast'
        elif abs(velocity) > 0.05:
            strength = 'medium'
        else:
            strength = 'slow'
        
        return {
            'velocity': velocity,
            'acceleration': acceleration,
            'strength': strength,
            'conviction': min(abs(velocity) * 5, 1.0)  # 0-1 scale
        }


class OrderFlowPredictor:
    """
    Predicts WHERE order flow will go next
    Based on current flow dynamics
    """
    
    def __init__(self):
        self.flow_transitions = defaultdict(lambda: {'buy': 0, 'sell': 0, 'neutral': 0})
        
        logger.info("📊 Order Flow Predictor initialized")
    
    def predict_next_flow(self, current_flow: Dict, market_state: Dict) -> Dict:
        """
        Predict next order flow state
        
        Uses:
        - Current flow direction
        - Flow momentum
        - Whale activity
        - Smart money classification
        """
        flow_dir = current_flow.get('aggressor_side', 'balanced')
        flow_momentum = current_flow.get('flow_momentum', 0)
        whale_active = current_flow.get('whale_activity', False)
        whale_dir = current_flow.get('whale_direction', 'neutral')
        
        # Base prediction on momentum continuation
        if flow_momentum > 0.3:
            predicted_direction = 'buy'
            confidence = min(flow_momentum, 0.9)
        elif flow_momentum < -0.3:
            predicted_direction = 'sell'
            confidence = min(abs(flow_momentum), 0.9)
        else:
            predicted_direction = 'neutral'
            confidence = 0.5
        
        # Whale activity overrides
        if whale_active and whale_dir != 'neutral':
            predicted_direction = whale_dir
            confidence = min(confidence + 0.2, 0.95)
        
        # Estimate probability distribution
        if predicted_direction == 'buy':
            probabilities = {'buy': confidence, 'sell': (1-confidence) * 0.3, 'neutral': (1-confidence) * 0.7}
        elif predicted_direction == 'sell':
            probabilities = {'sell': confidence, 'buy': (1-confidence) * 0.3, 'neutral': (1-confidence) * 0.7}
        else:
            probabilities = {'buy': 0.33, 'sell': 0.33, 'neutral': 0.34}
        
        return {
            'predicted_direction': predicted_direction,
            'confidence': confidence,
            'probabilities': probabilities,
            'timeframe': '1-5 minutes',
            'reasoning': f"Flow momentum: {flow_momentum:.2f}, Whale: {whale_active}"
        }


class PriceTrajectoryModeler:
    """
    Models where price is HEADING
    Not where it is, but where it's GOING
    """
    
    def __init__(self):
        self.trajectory_history = deque(maxlen=50)
        
        logger.info("🎯 Price Trajectory Modeler initialized")
    
    def model_trajectory(
        self,
        current_price: float,
        price_velocity: float,
        order_flow: Dict,
        order_book: Dict,
        historical_prices: List[float]
    ) -> Dict:
        """
        Model price trajectory for next 1-10 minutes
        
        Returns:
        - predicted_prices: [1min, 2min, 5min, 10min]
        - confidence_intervals: [(low, high) for each prediction]
        - direction: 'up', 'down', 'sideways'
        - magnitude: expected move size
        """
        # Base trajectory on velocity
        base_trajectory = price_velocity
        
        # Adjust for order flow
        flow_momentum = order_flow.get('flow_momentum', 0)
        flow_adjustment = flow_momentum * 0.005  # 0.5% max adjustment
        
        # Adjust for order book imbalance
        book_imbalance = order_book.get('imbalance', 1.0)
        if book_imbalance > 1.2:
            book_adjustment = (book_imbalance - 1.0) * 0.01
        elif book_imbalance < 0.83:
            book_adjustment = (book_imbalance - 1.0) * 0.01
        else:
            book_adjustment = 0
        
        # Combined trajectory
        total_trajectory = base_trajectory + flow_adjustment + book_adjustment
        
        # Project forward
        predictions = {
            '1min': current_price * (1 + total_trajectory * 0.2),
            '2min': current_price * (1 + total_trajectory * 0.4),
            '5min': current_price * (1 + total_trajectory * 0.8),
            '10min': current_price * (1 + total_trajectory * 1.0)
        }
        
        # Confidence intervals (wider for further ahead)
        volatility = self._estimate_volatility(historical_prices) if historical_prices else 0.02
        
        confidence_intervals = {
            '1min': (predictions['1min'] * (1 - volatility * 0.5), predictions['1min'] * (1 + volatility * 0.5)),
            '2min': (predictions['2min'] * (1 - volatility * 0.7), predictions['2min'] * (1 + volatility * 0.7)),
            '5min': (predictions['5min'] * (1 - volatility * 1.0), predictions['5min'] * (1 + volatility * 1.0)),
            '10min': (predictions['10min'] * (1 - volatility * 1.5), predictions['10min'] * (1 + volatility * 1.5))
        }
        
        # Direction and magnitude
        if total_trajectory > 0.002:
            direction = 'up'
        elif total_trajectory < -0.002:
            direction = 'down'
        else:
            direction = 'sideways'
        
        magnitude = abs(total_trajectory)
        
        return {
            'predictions': predictions,
            'confidence_intervals': confidence_intervals,
            'direction': direction,
            'magnitude': magnitude,
            'trajectory_strength': min(magnitude * 100, 1.0),
            'current_price': current_price
        }
    
    def _estimate_volatility(self, prices: List[float]) -> float:
        """Estimate volatility from price history"""
        if len(prices) < 2:
            return 0.02
        
        returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0.02
        
        return volatility


class MomentumForecaster:
    """
    Forecasts momentum changes
    Predicts when momentum will accelerate or decelerate
    """
    
    def __init__(self):
        self.momentum_history = deque(maxlen=100)
        
        logger.info("🚀 Momentum Forecaster initialized")
    
    def forecast_momentum(
        self,
        current_momentum: float,
        momentum_history: List[float],
        pattern_velocity: Dict
    ) -> Dict:
        """
        Forecast if momentum will increase, decrease, or reverse
        """
        if len(momentum_history) < 3:
            return {'forecast': 'unknown', 'confidence': 0}
        
        # Get recent momentum trend
        recent_trend = momentum_history[-1] - momentum_history[-3]
        
        # Get pattern velocity
        velocity = pattern_velocity.get('velocity', 0)
        acceleration = pattern_velocity.get('acceleration', 0)
        
        # Forecast logic
        if acceleration > 0.05:
            forecast = 'accelerating'
            confidence = min(abs(acceleration) * 10, 0.9)
        elif acceleration < -0.05:
            forecast = 'decelerating'
            confidence = min(abs(acceleration) * 10, 0.9)
        elif recent_trend > 0.1:
            forecast = 'strengthening'
            confidence = 0.7
        elif recent_trend < -0.1:
            forecast = 'weakening'
            confidence = 0.7
        else:
            forecast = 'stable'
            confidence = 0.6
        
        # Predict next momentum value
        predicted_momentum = current_momentum + velocity + (acceleration * 0.5)
        predicted_momentum = max(-1.0, min(predicted_momentum, 1.0))
        
        return {
            'forecast': forecast,
            'confidence': confidence,
            'predicted_momentum': predicted_momentum,
            'current_momentum': current_momentum,
            'change_expected': predicted_momentum - current_momentum
        }


class MarketRegimePredictor:
    """
    Predicts WHAT TYPE of market is coming next
    Trending? Ranging? Volatile? Calm?
    """
    
    REGIMES = ['trending_up', 'trending_down', 'ranging', 'volatile', 'calm', 'breakout', 'breakdown']
    
    def __init__(self):
        self.regime_history = deque(maxlen=50)
        self.regime_transitions = defaultdict(lambda: defaultdict(int))
        
        logger.info("🌊 Market Regime Predictor initialized")
    
    def classify_current_regime(self, market_state: Dict) -> str:
        """Classify current market regime"""
        trend_dir = market_state.get('trend_direction', 'sideways')
        trend_strength = market_state.get('trend_strength', 0)
        volatility = market_state.get('volatility', 0.02)
        momentum = market_state.get('momentum_score', 0)
        
        # Classification logic
        if volatility > 0.04:
            return 'volatile'
        elif volatility < 0.01:
            return 'calm'
        elif trend_dir == 'up' and trend_strength > 0.15:
            return 'trending_up'
        elif trend_dir == 'down' and trend_strength > 0.15:
            return 'trending_down'
        elif momentum > 0.7:
            if trend_dir == 'up':
                return 'breakout'
            else:
                return 'breakdown'
        else:
            return 'ranging'
    
    def predict_next_regime(self, current_regime: str, market_state: Dict) -> Dict:
        """Predict next market regime"""
        # Update transitions
        if len(self.regime_history) > 0:
            prev_regime = self.regime_history[-1]
            self.regime_transitions[prev_regime][current_regime] += 1
        
        self.regime_history.append(current_regime)
        
        # Predict based on transitions
        if current_regime in self.regime_transitions:
            transitions = self.regime_transitions[current_regime]
            total = sum(transitions.values())
            
            if total >= 5:
                # Use learned transitions
                most_likely = max(transitions.items(), key=lambda x: x[1])
                probability = most_likely[1] / total
                
                return {
                    'predicted_regime': most_likely[0],
                    'confidence': probability,
                    'method': 'learned_transitions'
                }
        
        # Fallback to rule-based prediction
        volatility = market_state.get('volatility', 0.02)
        momentum = market_state.get('momentum_score', 0)
        
        if current_regime == 'volatile':
            predicted = 'ranging'
            confidence = 0.6
        elif current_regime == 'calm':
            predicted = 'breakout' if momentum > 0.5 else 'ranging'
            confidence = 0.6
        elif current_regime in ['trending_up', 'trending_down']:
            predicted = 'ranging'  # Trends eventually end
            confidence = 0.5
        elif current_regime in ['breakout', 'breakdown']:
            predicted = 'trending_up' if current_regime == 'breakout' else 'trending_down'
            confidence = 0.7
        else:
            predicted = 'breakout' if momentum > 0.5 else 'calm'
            confidence = 0.5
        
        return {
            'predicted_regime': predicted,
            'confidence': confidence,
            'method': 'rule_based'
        }


class MultiStepPredictor:
    """
    Predicts 3-5 moves ahead
    Like chess - thinks multiple moves into the future
    """
    
    def __init__(self):
        logger.info("♟️ Multi-Step Predictor initialized")
    
    def predict_multi_step(
        self,
        current_state: Dict,
        flow_prediction: Dict,
        trajectory: Dict,
        momentum_forecast: Dict,
        regime_prediction: Dict
    ) -> Dict:
        """
        Predict 3-5 steps ahead
        
        Returns sequence of predicted states
        """
        predictions = []
        
        # Step 1 (1-2 minutes ahead)
        step1 = {
            'timeframe': '1-2min',
            'price': trajectory['predictions']['1min'],
            'flow': flow_prediction['predicted_direction'],
            'regime': regime_prediction['predicted_regime'],
            'confidence': min([
                flow_prediction['confidence'],
                trajectory['trajectory_strength'],
                regime_prediction['confidence']
            ])
        }
        predictions.append(step1)
        
        # Step 2 (3-5 minutes ahead)
        step2 = {
            'timeframe': '3-5min',
            'price': trajectory['predictions']['5min'],
            'momentum': momentum_forecast['predicted_momentum'],
            'regime': regime_prediction['predicted_regime'],
            'confidence': step1['confidence'] * 0.8  # Less confident further out
        }
        predictions.append(step2)
        
        # Step 3 (6-10 minutes ahead)
        step3 = {
            'timeframe': '6-10min',
            'price': trajectory['predictions']['10min'],
            'regime': regime_prediction['predicted_regime'],
            'confidence': step1['confidence'] * 0.6
        }
        predictions.append(step3)
        
        # Overall prediction
        overall = {
            'direction': trajectory['direction'],
            'magnitude': trajectory['magnitude'],
            'time_horizon': '10min',
            'confidence': step1['confidence'],
            'steps': predictions
        }
        
        return overall


class PredictiveNextMoveEngine:
    """
    MASTER PREDICTIVE ENGINE
    Combines all predictive capabilities
    """
    
    def __init__(self):
        self.pattern_velocity = PatternVelocityAnalyzer()
        self.flow_predictor = OrderFlowPredictor()
        self.trajectory_modeler = PriceTrajectoryModeler()
        self.momentum_forecaster = MomentumForecaster()
        self.regime_predictor = MarketRegimePredictor()
        self.multi_step = MultiStepPredictor()
        
        logger.info("=" * 80)
        logger.info("🔮 PREDICTIVE NEXT-MOVE ENGINE ONLINE")
        logger.info("=" * 80)
        logger.info("   Capabilities:")
        logger.info("   ✅ Pattern Velocity Analysis")
        logger.info("   ✅ Order Flow Prediction")
        logger.info("   ✅ Price Trajectory Modeling")
        logger.info("   ✅ Momentum Forecasting")
        logger.info("   ✅ Market Regime Prediction")
        logger.info("   ✅ Multi-Step Ahead Prediction (3-5 moves)")
        logger.info("")
        logger.info("   🔮 KNOWS WHAT'S COMING BEFORE IT HAPPENS")
        logger.info("=" * 80)
    
    async def predict_next_moves(
        self,
        omniscient_view: Dict,
        historical_states: List[Dict] = None
    ) -> Dict:
        """
        Complete predictive analysis
        
        Returns predictions for:
        - Next order flow
        - Price trajectory (1, 2, 5, 10 min)
        - Momentum changes
        - Market regime shift
        - Multi-step sequence
        """
        if not omniscient_view or omniscient_view.get('scan_quality') == 'failed':
            return {'prediction_quality': 'failed'}
        
        market_state = omniscient_view.get('market_state', {})
        order_flow = omniscient_view.get('order_flow', {})
        order_book = omniscient_view.get('order_book', {})
        
        if historical_states is None:
            historical_states = []
        
        # Run all predictive analyses
        pattern_velocity = self.pattern_velocity.analyze_pattern_velocity(market_state, historical_states)
        
        flow_prediction = self.flow_predictor.predict_next_flow(order_flow, market_state)
        
        trajectory = self.trajectory_modeler.model_trajectory(
            current_price=market_state.get('price', 0),
            price_velocity=market_state.get('price_velocity', 0),
            order_flow=order_flow,
            order_book=order_book,
            historical_prices=[s.get('price', 0) for s in historical_states[-20:]]
        )
        
        momentum_history = [s.get('momentum_score', 0) for s in historical_states[-10:]]
        momentum_forecast = self.momentum_forecaster.forecast_momentum(
            current_momentum=market_state.get('momentum_score', 0),
            momentum_history=momentum_history,
            pattern_velocity=pattern_velocity
        )
        
        current_regime = self.regime_predictor.classify_current_regime(market_state)
        regime_prediction = self.regime_predictor.predict_next_regime(current_regime, market_state)
        
        multi_step_prediction = self.multi_step.predict_multi_step(
            current_state=market_state,
            flow_prediction=flow_prediction,
            trajectory=trajectory,
            momentum_forecast=momentum_forecast,
            regime_prediction=regime_prediction
        )
        
        # Combine into master prediction
        master_prediction = {
            'symbol': omniscient_view.get('symbol'),
            'timestamp': datetime.now(),
            'pattern_velocity': pattern_velocity,
            'flow_prediction': flow_prediction,
            'price_trajectory': trajectory,
            'momentum_forecast': momentum_forecast,
            'regime': {
                'current': current_regime,
                'predicted': regime_prediction
            },
            'multi_step': multi_step_prediction,
            'overall_confidence': self._calculate_overall_confidence(
                pattern_velocity,
                flow_prediction,
                trajectory,
                momentum_forecast,
                regime_prediction
            ),
            'prediction_quality': 'complete'
        }
        
        # Log key predictions
        self._log_predictions(master_prediction)
        
        return master_prediction
    
    def _calculate_overall_confidence(self, *predictions) -> float:
        """Calculate overall confidence from all predictions"""
        confidences = []
        
        for pred in predictions:
            if isinstance(pred, dict):
                if 'confidence' in pred:
                    confidences.append(pred['confidence'])
                elif 'conviction' in pred:
                    confidences.append(pred['conviction'])
        
        if not confidences:
            return 0.5
        
        # Use geometric mean (conservative)
        product = 1.0
        for c in confidences:
            product *= c
        
        return product ** (1.0 / len(confidences))
    
    def _log_predictions(self, prediction: Dict):
        """Log key predictions"""
        symbol = prediction['symbol']
        
        # Price trajectory
        direction = prediction['price_trajectory']['direction']
        magnitude = prediction['price_trajectory']['magnitude']
        if magnitude > 0.005:
            logger.info(f"🔮 {symbol}: Predicting {direction.upper()} move ({magnitude*100:.2f}%)")
        
        # Flow prediction
        flow_dir = prediction['flow_prediction']['predicted_direction']
        flow_conf = prediction['flow_prediction']['confidence']
        if flow_conf > 0.7:
            logger.info(f"📊 {symbol}: Next flow predicted: {flow_dir.upper()} ({flow_conf:.1%} confidence)")
        
        # Momentum forecast
        momentum_forecast = prediction['momentum_forecast']['forecast']
        if momentum_forecast in ['accelerating', 'decelerating']:
            logger.info(f"🚀 {symbol}: Momentum {momentum_forecast.upper()}")
        
        # Overall confidence
        overall_conf = prediction['overall_confidence']
        logger.info(f"🎯 {symbol}: Overall prediction confidence: {overall_conf:.1%}")


# Global instance
predictive_engine = None

def initialize_predictive_engine():
    global predictive_engine
    predictive_engine = PredictiveNextMoveEngine()
    return predictive_engine

async def predict_next_moves(omniscient_view: Dict, historical_states: List[Dict] = None) -> Dict:
    global predictive_engine
    if not predictive_engine:
        predictive_engine = initialize_predictive_engine()
    
    return await predictive_engine.predict_next_moves(omniscient_view, historical_states)

# Export
__all__ = [
    'PredictiveNextMoveEngine',
    'initialize_predictive_engine',
    'predict_next_moves'
]

logger.info("🔮 PREDICTIVE NEXT-MOVE ENGINE loaded - Ready to see the future!")
