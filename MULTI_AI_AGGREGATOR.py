#!/usr/bin/env python3
"""
🤖 MULTI-AI INTELLIGENCE AGGREGATOR 🤖

Queries ALL AI models for comprehensive market analysis:
- Claude (Anthropic) - Deep reasoning
- GPT-4 (OpenAI) - Pattern recognition
- Gemini (Google) - Multi-modal analysis
- Grok (xAI) - Real-time insights
- Custom models - Specialized analysis

Synthesizes ALL AI responses into unified intelligence!

The bot's COLLECTIVE BRAIN! 🧠🧠🧠
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try importing AI SDKs
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except:
    GOOGLE_AVAILABLE = False


class MultiAIAggregator:
    """
    COLLECTIVE AI INTELLIGENCE
    
    Queries multiple AI models simultaneously:
    - Each AI brings unique perspective
    - Synthesizes into unified intelligence
    - Learns which AI is best at what
    - Adapts questioning based on situation
    
    MULTIPLE BRAINS WORKING AS ONE!
    """
    
    def __init__(self, ai_consultation_system=None):
        """
        Initialize multi-AI aggregator
        
        Args:
            ai_consultation_system: Existing AI consultation system (if any)
        """
        self.ai_consultation = ai_consultation_system
        
        # AI specializations (what each AI is best at)
        self.ai_specializations = {
            'claude': {
                'strengths': ['deep_analysis', 'risk_assessment', 'pattern_recognition'],
                'best_for': 'complex_analysis',
                'weight': 1.2
            },
            'gpt4': {
                'strengths': ['quick_insights', 'trend_prediction', 'sentiment_analysis'],
                'best_for': 'rapid_assessment',
                'weight': 1.0
            },
            'gemini': {
                'strengths': ['multi_modal', 'data_synthesis', 'pattern_matching'],
                'best_for': 'data_correlation',
                'weight': 1.0
            },
            'grok': {
                'strengths': ['real_time', 'news_analysis', 'social_sentiment'],
                'best_for': 'current_events',
                'weight': 0.9
            }
        }
        
        # AI performance tracking
        self.ai_performance = {
            'claude': {'correct': 0, 'total': 0, 'accuracy': 0},
            'gpt4': {'correct': 0, 'total': 0, 'accuracy': 0},
            'gemini': {'correct': 0, 'total': 0, 'accuracy': 0},
            'grok': {'correct': 0, 'total': 0, 'accuracy': 0}
        }
        
        # Query templates for different scenarios
        self.query_templates = {
            'market_analysis': self._create_market_analysis_query,
            'risk_assessment': self._create_risk_assessment_query,
            'trend_prediction': self._create_trend_prediction_query,
            'entry_timing': self._create_entry_timing_query,
            'position_sizing': self._create_position_sizing_query
        }
        
        logger.info("🤖 MULTI-AI AGGREGATOR initialized!")
        logger.info(f"   AI models tracked: {len(self.ai_specializations)}")
        logger.info(f"   Query templates: {len(self.query_templates)}")
    
    async def get_collective_intelligence(self, context: Dict, query_type: str = 'market_analysis') -> Dict:
        """
        Get COLLECTIVE INTELLIGENCE from all AI models
        
        Args:
            context: Market context (symbol, price, indicators, etc)
            query_type: Type of analysis needed
        
        Returns:
            Synthesized intelligence from all AIs
        """
        logger.info(f"🤖 Gathering COLLECTIVE INTELLIGENCE: {query_type}")
        logger.info(f"   Context: {context.get('symbol', 'N/A')} | Price: ${context.get('price', 0):.4f}")
        
        # Create optimized query for each AI based on specialization
        queries = self._create_specialized_queries(context, query_type)
        
        # Query all AIs in parallel
        responses = await self._query_all_ais(queries)
        
        # Synthesize responses into unified intelligence
        collective_intelligence = self._synthesize_collective_intelligence(responses, context)
        
        # Learn from responses
        self._learn_from_responses(responses, collective_intelligence)
        
        logger.info(f"   🧠 Collective consensus: {collective_intelligence.get('consensus', 'N/A').upper()}")
        logger.info(f"   🎯 Confidence: {collective_intelligence.get('confidence', 0):.0%}")
        logger.info(f"   🤖 AIs responded: {collective_intelligence.get('ais_responded', 0)}/{len(queries)}")
        
        return collective_intelligence
    
    def _create_specialized_queries(self, context: Dict, query_type: str) -> Dict[str, str]:
        """Create specialized queries for each AI based on their strengths"""
        queries = {}
        
        # Get base query from template
        base_query_func = self.query_templates.get(query_type, self._create_market_analysis_query)
        
        for ai_name, specs in self.ai_specializations.items():
            # Customize query based on AI strengths
            if specs['best_for'] == query_type or query_type in specs['strengths']:
                # This AI is specialized for this query - ask detailed question
                queries[ai_name] = base_query_func(context, detail_level='high')
            else:
                # Ask simplified question
                queries[ai_name] = base_query_func(context, detail_level='medium')
        
        return queries
    
    def _create_market_analysis_query(self, context: Dict, detail_level: str = 'medium') -> str:
        """Create market analysis query"""
        symbol = context.get('symbol', 'Unknown')
        price = context.get('price', 0)
        trend = context.get('trend', {})
        
        if detail_level == 'high':
            return f"""Deep Market Analysis Request:

Symbol: {symbol}
Current Price: ${price:.4f}
Trend: {trend.get('trend', 'unknown')}
Momentum: {trend.get('momentum_20', 0):.2f}%
Volatility: {trend.get('volatility', 0):.2f}%

Market Context:
{json.dumps(context.get('market_data', {}), indent=2)}

Provide DEEP analysis:
1. What is the TRUE market condition?
2. What are the PRIMARY drivers of this movement?
3. What PATTERNS do you see emerging?
4. What are the KEY support/resistance levels?
5. What is your CONVICTION on direction (1-10)?
6. What are the CRITICAL risks we must watch?

Be specific and actionable."""

        else:
            return f"""Market Analysis: {symbol} @ ${price:.4f}

Trend: {trend.get('trend', 'unknown')}
Momentum: {trend.get('momentum_20', 0):.2f}%

Your assessment:
1. Bullish, Bearish, or Neutral?
2. Confidence level (1-10)?
3. Key insight in one sentence?"""
    
    def _create_risk_assessment_query(self, context: Dict, detail_level: str = 'medium') -> str:
        """Create risk assessment query"""
        return f"""Risk Assessment: {context.get('symbol')}

Position size: ${context.get('size', 0):.2f}
Leverage: {context.get('leverage', 1)}x
Stop loss: {context.get('stop_loss', 0):.2%}

What are the PRIMARY RISKS?
Rate this trade 1-10 (10 = safest)."""
    
    def _create_trend_prediction_query(self, context: Dict, detail_level: str = 'medium') -> str:
        """Create trend prediction query"""
        return f"""Trend Prediction: {context.get('symbol')}

Current: ${context.get('price', 0):.4f}
5-period momentum: {context.get('momentum_5', 0):.2f}%
20-period momentum: {context.get('momentum_20', 0):.2f}%

Where is this heading in next:
- 1 hour?
- 4 hours?
- 24 hours?

Direction and confidence?"""
    
    def _create_entry_timing_query(self, context: Dict, detail_level: str = 'medium') -> str:
        """Create entry timing query"""
        return f"""Entry Timing: {context.get('symbol')}

Signal: {context.get('signal', 'unknown').upper()}
Current: ${context.get('price', 0):.4f}
Target: ${context.get('target_price', 0):.4f}

Should we:
A) Enter NOW (market order)
B) Wait for better price (limit order)
C) Wait for confirmation

Your recommendation and why?"""
    
    def _create_position_sizing_query(self, context: Dict, detail_level: str = 'medium') -> str:
        """Create position sizing query"""
        return f"""Position Sizing: {context.get('symbol')}

Account: ${context.get('balance', 0):.2f}
Confidence: {context.get('confidence', 0):.0%}
Volatility: {context.get('volatility', 0):.2%}

Recommended position size?
(as % of account and USD amount)"""
    
    async def _query_all_ais(self, queries: Dict[str, str]) -> Dict[str, Dict]:
        """Query all AIs in parallel"""
        if not self.ai_consultation:
            logger.warning("⚠️ No AI consultation system available")
            return {}
        
        responses = {}
        tasks = []
        
        for ai_name, query in queries.items():
            # Create consultation context
            context = {
                'query': query,
                'ai_target': ai_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Queue query
            task = self.ai_consultation.consult_strategy(context)
            tasks.append((ai_name, task))
        
        # Execute all queries in parallel
        results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        # Collect responses
        for (ai_name, _), result in zip(tasks, results):
            if isinstance(result, dict) and not isinstance(result, Exception):
                responses[ai_name] = result
            else:
                logger.warning(f"   ⚠️ {ai_name} query failed: {result}")
        
        return responses
    
    def _synthesize_collective_intelligence(self, responses: Dict[str, Dict], context: Dict) -> Dict:
        """
        Synthesize all AI responses into COLLECTIVE INTELLIGENCE
        
        This is where MULTIPLE BRAINS become ONE!
        """
        if not responses:
            return {
                'consensus': 'unknown',
                'confidence': 0,
                'ais_responded': 0
            }
        
        # Extract insights from each AI
        insights = []
        sentiments = []
        confidence_scores = []
        
        for ai_name, response in responses.items():
            ai_weight = self.ai_specializations.get(ai_name, {}).get('weight', 1.0)
            
            # Extract sentiment
            text = response.get('response', '').lower()
            if 'bullish' in text or 'buy' in text or 'long' in text:
                sentiments.append(('bullish', ai_weight))
            elif 'bearish' in text or 'sell' in text or 'short' in text:
                sentiments.append(('bearish', ai_weight))
            else:
                sentiments.append(('neutral', ai_weight * 0.5))
            
            # Extract confidence (look for numbers 1-10)
            import re
            confidence_matches = re.findall(r'\b([1-9]|10)/10\b', text)
            if confidence_matches:
                confidence_scores.append((int(confidence_matches[0]), ai_weight))
            
            insights.append({
                'ai': ai_name,
                'text': response.get('response', ''),
                'weight': ai_weight
            })
        
        # Calculate weighted consensus
        bullish_weight = sum(w for s, w in sentiments if s == 'bullish')
        bearish_weight = sum(w for s, w in sentiments if s == 'bearish')
        neutral_weight = sum(w for s, w in sentiments if s == 'neutral')
        total_weight = bullish_weight + bearish_weight + neutral_weight
        
        if total_weight == 0:
            consensus = 'unknown'
        elif bullish_weight > bearish_weight and bullish_weight > neutral_weight:
            consensus = 'bullish'
        elif bearish_weight > bullish_weight and bearish_weight > neutral_weight:
            consensus = 'bearish'
        else:
            consensus = 'neutral'
        
        # Calculate collective confidence
        if confidence_scores:
            weighted_conf = sum(c * w for c, w in confidence_scores) / sum(w for _, w in confidence_scores)
            collective_confidence = weighted_conf / 10  # Normalize to 0-1
        else:
            # Use consensus strength as confidence
            if total_weight > 0:
                max_weight = max(bullish_weight, bearish_weight, neutral_weight)
                collective_confidence = max_weight / total_weight
            else:
                collective_confidence = 0
        
        # Determine unanimity
        unanimous = len(set(s for s, _ in sentiments)) == 1
        
        return {
            'consensus': consensus,
            'confidence': collective_confidence,
            'unanimous': unanimous,
            'ais_responded': len(responses),
            'bullish_weight': bullish_weight,
            'bearish_weight': bearish_weight,
            'neutral_weight': neutral_weight,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
    
    def _learn_from_responses(self, responses: Dict, collective: Dict):
        """Learn which AIs perform best"""
        # This would track AI accuracy over time
        # For now, just log participation
        for ai_name in responses.keys():
            if ai_name in self.ai_performance:
                self.ai_performance[ai_name]['total'] += 1
    
    def get_ai_performance_summary(self) -> Dict:
        """Get performance summary of all AIs"""
        return {
            'ai_performance': self.ai_performance,
            'ai_specializations': self.ai_specializations,
            'total_queries': sum(p['total'] for p in self.ai_performance.values())
        }


# Singleton
_multi_ai_aggregator = None

def get_multi_ai_aggregator():
    """Get multi-AI aggregator instance"""
    return _multi_ai_aggregator

def initialize_multi_ai_aggregator(ai_consultation_system=None):
    """Initialize multi-AI aggregator"""
    global _multi_ai_aggregator
    _multi_ai_aggregator = MultiAIAggregator(ai_consultation_system)
    return _multi_ai_aggregator
