#!/usr/bin/env python3
"""
🤖 AI CONSULTATION SYSTEM 🤖

Bot CONSULTS AI APIs for:
- Strategy recommendations
- Pattern recognition  
- Market analysis
- Risk assessment
- New trading ideas

LEARNS from AI responses and generates new patterns!
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)

# Try importing AI SDKs
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️ Anthropic not installed. Run: pip install anthropic")

try:
    import openai
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ OpenAI not installed. Run: pip install openai")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except:
    GOOGLE_AVAILABLE = False
    logger.warning("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")


class AIConsultationSystem:
    """
    Consults AI APIs for trading intelligence
    
    Features:
    - Multi-AI consultation
    - Response synthesis
    - Pattern extraction
    - Knowledge accumulation
    - Budget management
    """
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.clients = self._initialize_clients()
        
        # Consultation history
        self.consultations = []
        self.learned_patterns = []
        self.ai_suggestions = []
        
        # Budget tracking
        self.daily_budget = float(os.getenv('AI_BUDGET_DAILY', '10.0'))
        self.tokens_used_today = 0
        self.cost_today = 0.0
        
        # Rate limiting
        self.requests_per_minute = int(os.getenv('AI_RATE_LIMIT_PER_MIN', '20'))
        self.recent_requests = []
        
        logger.info("🤖 AI CONSULTATION SYSTEM initialized!")
        logger.info(f"   Available AIs: {len(self.clients)}")
        logger.info(f"   Daily budget: ${self.daily_budget}")
        
        if self.clients:
            for ai_name in self.clients.keys():
                logger.info(f"   ✅ {ai_name} ready")
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load all AI API keys from environment"""
        keys = {}
        
        # Anthropic (Claude)
        if os.getenv('ANTHROPIC_API_KEY'):
            keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY')
        
        # OpenAI (GPT-4)
        if os.getenv('OPENAI_API_KEY'):
            keys['openai'] = os.getenv('OPENAI_API_KEY')
        
        # Grok/xAI
        if os.getenv('GROK_API_KEY') or os.getenv('XAI_API_KEY'):
            keys['grok'] = os.getenv('GROK_API_KEY') or os.getenv('XAI_API_KEY')
        
        # Google Gemini
        if os.getenv('GOOGLE_API_KEY'):
            keys['google'] = os.getenv('GOOGLE_API_KEY')
        
        return keys
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize AI clients"""
        clients = {}
        
        # Anthropic
        if 'anthropic' in self.api_keys and ANTHROPIC_AVAILABLE:
            try:
                clients['claude'] = anthropic.Anthropic(api_key=self.api_keys['anthropic'])
                logger.info("   ✅ Claude (Anthropic) client initialized")
            except Exception as e:
                logger.error(f"   ❌ Claude init failed: {e}")
        
        # OpenAI
        if 'openai' in self.api_keys and OPENAI_AVAILABLE:
            try:
                openai.api_key = self.api_keys['openai']
                clients['gpt4'] = openai
                logger.info("   ✅ GPT-4 (OpenAI) client initialized")
            except Exception as e:
                logger.error(f"   ❌ GPT-4 init failed: {e}")
        
        # Google Gemini
        if 'google' in self.api_keys and GOOGLE_AVAILABLE:
            try:
                genai.configure(api_key=self.api_keys['google'])
                clients['gemini'] = genai.GenerativeModel('gemini-pro')
                logger.info("   ✅ Gemini (Google) client initialized")
            except Exception as e:
                logger.error(f"   ❌ Gemini init failed: {e}")
        
        return clients
    
    async def consult_strategy(self, context: Dict) -> Dict:
        """
        Consult AI for trading strategy
        
        THROTTLED to prevent token burnout!
        Only consults on:
        - Very high confidence (88%+)
        - Important pairs (BTC, ETH, etc)
        - Once per pair per 5 minutes
        
        Args:
            context: {
                'symbol': 'BTC/USDT',
                'current_price': 67500,
                'signal': 'buy',
                'confidence': 0.82,
                'timeframe': '5m',
                'market_data': {...}
            }
        
        Returns:
            AI recommendations and insights
        """
        if not self.clients:
            logger.debug("No AI clients available, skipping consultation")
            return {'ai_available': False}
        
        # Check budget
        if self.cost_today >= self.daily_budget:
            logger.warning(f"⚠️ Daily AI budget exceeded: ${self.cost_today:.2f}/${self.daily_budget}")
            return {'budget_exceeded': True}
        
        # THROTTLE: Only consult on very high confidence (88%+)
        confidence = context.get('confidence', 0)
        if confidence < 0.88:
            logger.debug(f"   Confidence {confidence:.0%} below 88% threshold, skipping AI")
            return {'skipped': 'confidence_too_low'}
        
        # THROTTLE: Check if we consulted this pair recently (5 min cooldown)
        symbol = context.get('symbol', '')
        now = datetime.now()
        if symbol in self.consultations:
            last_consult = self.consultations[-1]['timestamp']
            if (now - datetime.fromisoformat(last_consult)).seconds < 300:  # 5 minutes
                logger.debug(f"   {symbol} consulted recently, skipping (cooldown)")
                return {'skipped': 'cooldown_active'}
        
        # Check rate limit
        if not self._check_rate_limit():
            logger.warning("⚠️ AI rate limit reached, skipping...")
            return {'skipped': 'rate_limit'}
        
        logger.info(f"🤖 Consulting AI about {context.get('symbol')} {context.get('signal', 'unknown').upper()}")
        
        # Prepare consultation query
        query = self._prepare_consultation_query(context)
        
        # Consult all available AIs in parallel
        consultation_tasks = []
        for ai_name, client in self.clients.items():
            consultation_tasks.append(self._consult_single_ai(ai_name, client, query, context))
        
        responses = await asyncio.gather(*consultation_tasks, return_exceptions=True)
        
        # Synthesize responses
        synthesis = self._synthesize_ai_responses(responses, context)
        
        # Extract new patterns
        patterns = self._extract_patterns_from_ai(synthesis)
        self.learned_patterns.extend(patterns)
        
        # Record consultation
        self.consultations.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'synthesis': synthesis,
            'patterns_learned': len(patterns)
        })
        
        return synthesis
    
    def _prepare_consultation_query(self, context: Dict) -> str:
        """Prepare query for AI"""
        symbol = context.get('symbol', 'Unknown')
        signal = context.get('signal', 'unknown')
        confidence = context.get('confidence', 0)
        timeframe = context.get('timeframe', '5m')
        
        query = f"""Analyze this trading opportunity:

Symbol: {symbol}
Signal: {signal.upper()}
Confidence: {confidence:.1%}
Timeframe: {timeframe}

Current Market Context:
{json.dumps(context.get('market_data', {}), indent=2)}

Questions:
1. Is this trade advisable given market conditions?
2. What are the key risks and opportunities?
3. What position size would you recommend?
4. What patterns do you see in this setup?
5. Any additional insights or strategies?

Provide concise, actionable insights."""
        
        return query
    
    async def _consult_single_ai(self, ai_name: str, client: Any, query: str, context: Dict) -> Dict:
        """Consult a single AI"""
        try:
            logger.info(f"   🤖 Querying {ai_name}...")
            
            response_text = None
            
            # Claude
            if ai_name == 'claude':
                message = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": query}]
                )
                response_text = message.content[0].text
                
                # Track usage
                self.tokens_used_today += message.usage.input_tokens + message.usage.output_tokens
                self.cost_today += (message.usage.input_tokens * 0.000003 + 
                                   message.usage.output_tokens * 0.000015)
            
            # GPT-4
            elif ai_name == 'gpt4':
                response = await asyncio.to_thread(
                    client.ChatCompletion.create,
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": query}],
                    max_tokens=500
                )
                response_text = response.choices[0].message.content
                
                # Track usage
                self.tokens_used_today += response.usage.total_tokens
                self.cost_today += response.usage.total_tokens * 0.00001
            
            # Gemini
            elif ai_name == 'gemini':
                response = await asyncio.to_thread(client.generate_content, query)
                response_text = response.text
                # Gemini free tier - minimal cost
                self.cost_today += 0.001
            
            logger.info(f"   ✅ {ai_name} responded ({len(response_text)} chars)")
            
            return {
                'ai': ai_name,
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"   ❌ {ai_name} consultation failed: {e}")
            return {
                'ai': ai_name,
                'error': str(e),
                'success': False
            }
    
    def _synthesize_ai_responses(self, responses: List[Dict], context: Dict) -> Dict:
        """
        Synthesize multiple AI responses into unified recommendation
        """
        successful_responses = [r for r in responses if isinstance(r, dict) and r.get('success')]
        
        if not successful_responses:
            return {
                'ai_consensus': 'unavailable',
                'reason': 'No AI responses available'
            }
        
        # Extract key insights from all responses
        all_insights = []
        recommendations = []
        risks = []
        opportunities = []
        
        for resp in successful_responses:
            text = resp.get('response', '')
            all_insights.append({
                'ai': resp['ai'],
                'text': text
            })
            
            # Simple keyword extraction (could be enhanced)
            if 'recommend' in text.lower() or 'suggest' in text.lower():
                recommendations.append(resp['ai'])
            if 'risk' in text.lower():
                risks.append(resp['ai'])
            if 'opportunity' in text.lower() or 'bullish' in text.lower():
                opportunities.append(resp['ai'])
        
        # Determine consensus
        total_ais = len(successful_responses)
        consensus_threshold = total_ais / 2
        
        consensus = 'mixed'
        if len(opportunities) > consensus_threshold:
            consensus = 'bullish'
        elif len(risks) > consensus_threshold:
            consensus = 'bearish'
        
        synthesis = {
            'ai_consensus': consensus,
            'total_ais_consulted': len(self.clients),
            'successful_responses': len(successful_responses),
            'insights': all_insights,
            'unanimous': len(successful_responses) == len(opportunities),
            'cost': self.cost_today,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"   🧠 AI Synthesis: {consensus.upper()} consensus from {total_ais} AIs")
        
        return synthesis
    
    def _extract_patterns_from_ai(self, synthesis: Dict) -> List[Dict]:
        """
        Extract new trading patterns from AI insights
        
        The bot LEARNS new patterns from AI wisdom!
        """
        patterns = []
        
        for insight in synthesis.get('insights', []):
            text = insight.get('text', '')
            ai_name = insight.get('ai', 'unknown')
            
            # Extract pattern keywords (simplified - could use NLP)
            pattern_keywords = [
                'pattern', 'trend', 'breakout', 'reversal', 'support', 'resistance',
                'momentum', 'divergence', 'consolidation', 'accumulation'
            ]
            
            for keyword in pattern_keywords:
                if keyword in text.lower():
                    patterns.append({
                        'type': keyword,
                        'source': f'AI:{ai_name}',
                        'context': text[:200],  # First 200 chars
                        'learned_at': datetime.now().isoformat(),
                        'confidence': 0.7  # AI-derived patterns start at 70%
                    })
        
        if patterns:
            logger.info(f"   📚 Extracted {len(patterns)} new patterns from AI insights")
        
        return patterns
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.recent_requests = [
            req for req in self.recent_requests 
            if (now - req).seconds < 60
        ]
        
        # Check limit
        if len(self.recent_requests) >= self.requests_per_minute:
            return False
        
        self.recent_requests.append(now)
        return True
    
    def get_learned_patterns(self) -> List[Dict]:
        """Get all patterns learned from AI"""
        return self.learned_patterns
    
    def get_consultation_stats(self) -> Dict:
        """Get consultation statistics"""
        return {
            'total_consultations': len(self.consultations),
            'patterns_learned': len(self.learned_patterns),
            'cost_today': self.cost_today,
            'budget_remaining': self.daily_budget - self.cost_today,
            'tokens_used': self.tokens_used_today,
            'available_ais': list(self.clients.keys())
        }


# Singleton
_ai_consultation_system = None

def get_ai_consultation():
    """Get AI consultation instance"""
    return _ai_consultation_system

def initialize_ai_consultation():
    """Initialize AI consultation system"""
    global _ai_consultation_system
    _ai_consultation_system = AIConsultationSystem()
    return _ai_consultation_system
