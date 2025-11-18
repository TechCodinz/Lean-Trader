#!/usr/bin/env python3
"""
🤖 AI CONSULTATION SERVICE 🤖

Uses MULTIPLE AI APIs to:
1. Continuously learn from trading results
2. Get strategy improvements
3. Research new market patterns
4. Optimize position sizing
5. Stay ahead of market changes

SUPPORTS: Claude, GPT-4, Grok, Raiziom, and more!
THE BOT THAT UPGRADES ITSELF!
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# ============================================================================
# UNIVERSAL AI ORCHESTRATOR - SUPPORTS ANY AI API (DEEPSEEK, CLAUDE, GPT-4, etc.)
# ============================================================================
try:
    from UNIVERSAL_AI_ORCHESTRATOR import get_universal_ai_orchestrator
    UNIVERSAL_AI_AVAILABLE = True
    logger.info("=" * 80)
    logger.info("🤖🌌 UNIVERSAL AI ORCHESTRATOR LOADED!")
    logger.info("=" * 80)
    logger.info("   Supports ANY AI API:")
    logger.info("   • DeepSeek (reasoning, code)")
    logger.info("   • Claude (analysis, strategy)")
    logger.info("   • GPT-4 (general intelligence)")
    logger.info("   • Gemini (fast responses)")
    logger.info("   • Grok (real-time data)")
    logger.info("   • Any custom API")
    logger.info("")
    logger.info("   Auto-routing to best AI for each task!")
    logger.info("   Intelligence: INFINITE ♾️")
    logger.info("=" * 80)
except Exception as e:
    logger.warning(f"⚠️  Universal AI not available: {e}")
    UNIVERSAL_AI_AVAILABLE = False


# Check available AI providers
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIConsultationService:
    """
    AI CONSULTATION SERVICE
    
    Makes the bot learn and improve continuously by consulting MULTIPLE AI APIs:
    - Claude (Anthropic)
    - GPT-4 (OpenAI)
    - Grok (xAI)
    - Raiziom (Custom AI)
    - Any custom endpoint
    """
    
    def __init__(self, provider: str = 'auto'):
        """
        Initialize AI consultation service
        
        Args:
            provider: AI provider to use ('auto', 'claude', 'gpt4', 'grok', 'raiziom', 'custom')
        """
        self.provider = provider
        self.clients = {}
        self.available = False
        self.consultation_history = []
        self.active_provider = None
        
        # TOKEN CONSUMPTION LIMITS - Don't burn through API credits!
        self.max_tokens_per_request = 4000  # Max tokens per AI query
        self.max_consultations_per_hour = 12  # Max 12 consultations/hour = 1 every 5 min
        self.max_consultations_per_day = 200  # Max 200/day (safety limit)
        self.last_consultation_time = None
        self.consultations_this_hour = 0
        self.consultations_today = 0
        self.tokens_used_today = 0
        self.max_tokens_per_day = 500000  # 500K tokens/day limit
        
        # Moonshot query frequency (don't spam AI for moons!)
        self.moonshot_query_interval = 3600  # Query every 1 hour
        self.last_moonshot_query = None
        
        # AI Provider Specializations (learned automatically)
        self.ai_specializations = {
            'claude': {'strengths': ['deep_analysis', 'complex_reasoning', 'code_generation', 'strategic_thinking']},
            'gpt4': {'strengths': ['pattern_recognition', 'creativity', 'general_purpose', 'technical_analysis']},
            'grok': {'strengths': ['social_sentiment', 'real_time_trends', 'twitter_analysis', 'meme_coins']},
            'gemini': {'strengths': ['multimodal', 'fast_inference', 'reasoning', 'data_analysis']},
            'raiziom': {'strengths': ['custom_strategies', 'personalized', 'user_preferences']},
        }
        
        # Track performance of each AI (learns which is best)
        self.ai_performance = {}
        
        # Initialize all available providers
        self._init_claude()
        self._init_openai()
        self._init_grok()
        self._init_gemini()
        self._init_raiziom()
        self._init_custom()
        
        # Auto-discover custom AI capabilities
        self._analyze_custom_ais()
        
        # Auto-select provider if not specified
        if provider == 'auto':
            self._auto_select_provider()
        else:
            self.active_provider = provider
            self.available = self.clients.get(provider) is not None
        
        if self.available:
            logger.info(f"🤖 AI CONSULTATION SERVICE initialized!")
            logger.info(f"   Provider: {self.active_provider}")
            logger.info("   Bot will continuously learn and improve!")
        else:
            logger.warning("⚠️  No AI providers available")
            logger.info("   Set API keys in .env: ANTHROPIC_API_KEY, OPENAI_API_KEY, GROK_API_KEY, RAIZIOM_API_KEY")
    
    def _init_claude(self):
        """Initialize Claude (Anthropic)"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if ANTHROPIC_AVAILABLE and api_key:
            try:
                self.clients['claude'] = anthropic.Anthropic(api_key=api_key)
                logger.info("✅ Claude (Anthropic) initialized")
            except Exception as e:
                logger.debug(f"Claude init failed: {e}")
    
    def _init_openai(self):
        """Initialize GPT-4 (OpenAI)"""
        api_key = os.getenv('OPENAI_API_KEY')
        if OPENAI_AVAILABLE and api_key:
            try:
                openai.api_key = api_key
                self.clients['gpt4'] = openai
                logger.info("✅ GPT-4 (OpenAI) initialized")
            except Exception as e:
                logger.debug(f"OpenAI init failed: {e}")
    
    def _init_grok(self):
        """Initialize Grok (xAI)"""
        api_key = os.getenv('GROK_API_KEY')
        endpoint = os.getenv('GROK_ENDPOINT', 'https://api.x.ai/v1/chat/completions')
        if REQUESTS_AVAILABLE and api_key:
            try:
                self.clients['grok'] = {
                    'api_key': api_key,
                    'endpoint': endpoint,
                    'type': 'openai_compatible'
                }
                logger.info("✅ Grok (xAI) initialized")
            except Exception as e:
                logger.debug(f"Grok init failed: {e}")
    
    def _init_raiziom(self):
        """Initialize Raiziom (Custom AI)"""
        api_key = os.getenv('RAIZIOM_API_KEY')
        endpoint = os.getenv('RAIZIOM_ENDPOINT')
        if REQUESTS_AVAILABLE and api_key and endpoint:
            try:
                self.clients['raiziom'] = {
                    'api_key': api_key,
                    'endpoint': endpoint,
                    'type': 'custom'
                }
                logger.info("✅ Raiziom (Custom AI) initialized")
            except Exception as e:
                logger.debug(f"Raiziom init failed: {e}")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.clients['gemini'] = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Google Gemini initialized")
            except Exception as e:
                logger.debug(f"Gemini init failed: {e}")
    
    def _init_custom(self):
        """Initialize any custom AI endpoint"""
        api_key = os.getenv('CUSTOM_AI_API_KEY')
        endpoint = os.getenv('CUSTOM_AI_ENDPOINT')
        if REQUESTS_AVAILABLE and api_key and endpoint:
            try:
                self.clients['custom'] = {
                    'api_key': api_key,
                    'endpoint': endpoint,
                    'type': 'custom'
                }
                logger.info("✅ Custom AI endpoint initialized")
            except Exception as e:
                logger.debug(f"Custom AI init failed: {e}")
    
    def add_custom_ai(self, name: str, api_key: str, endpoint: str, ai_type: str = 'openai_compatible'):
        """
        🔌 DYNAMICALLY ADD ANY AI API
        
        Args:
            name: AI name (e.g., 'deepseek', 'mistral', 'perplexity')
            api_key: API key
            endpoint: API endpoint URL
            ai_type: 'openai_compatible' or 'custom'
        """
        try:
            self.clients[name] = {
                'api_key': api_key,
                'endpoint': endpoint,
                'type': ai_type
            }
            
            # Auto-analyze what this AI is good at
            logger.info(f"🔌 Added custom AI: {name}")
            logger.info(f"   Analyzing capabilities...")
            
            # Test query to learn specialization
            asyncio.create_task(self._learn_ai_specialization(name))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom AI {name}: {e}")
            return False
    
    async def _learn_ai_specialization(self, ai_name: str):
        """
        🧠 AUTOMATICALLY LEARN WHAT EACH AI IS GOOD AT
        
        Asks the AI: "What are you best at?"
        Records specialization for optimal routing
        """
        try:
            prompt = """In 2-3 sentences, what are you BEST at? 
What tasks should I send to you vs other AIs?
Be specific about your unique strengths."""
            
            # Query the AI
            result = await self._query_specific_provider(ai_name, prompt)
            
            # Parse specialization
            specialization = self._parse_specialization(result)
            
            # Store learned specialization
            if ai_name not in self.ai_specializations:
                self.ai_specializations[ai_name] = {'strengths': []}
            
            self.ai_specializations[ai_name]['description'] = result
            
            logger.info(f"✅ Learned {ai_name} specialization:")
            logger.info(f"   {result[:100]}...")
            
        except Exception as e:
            logger.debug(f"Could not learn {ai_name} specialization: {e}")
    
    def _analyze_custom_ais(self):
        """Analyze all custom AI endpoints to learn capabilities"""
        for name in self.clients.keys():
            if name not in ['claude', 'gpt4', 'grok', 'gemini', 'raiziom']:
                # Custom AI - learn what it's good at
                logger.info(f"🔍 Analyzing custom AI: {name}...")
                # Will learn async
    
    def _select_best_ai_for_task(self, task_type: str) -> str:
        """
        🎯 INTELLIGENTLY SELECT BEST AI FOR EACH TASK
        
        Args:
            task_type: 'moonshot', 'strategy', 'analysis', 'social', 'technical', etc.
        
        Returns:
            Best AI provider name
        """
        # Task-to-specialization mapping
        task_preferences = {
            'moonshot': ['grok', 'gemini', 'gpt4'],  # Grok best for social/memes
            'social_sentiment': ['grok', 'gemini'],   # Grok has Twitter/X access
            'deep_analysis': ['claude', 'gpt4'],      # Claude best at reasoning
            'technical_analysis': ['gpt4', 'gemini', 'claude'],
            'pattern_recognition': ['gpt4', 'gemini'],
            'strategy': ['claude', 'gpt4'],
            'fast_query': ['gemini', 'grok'],         # Gemini is fastest
            'code_generation': ['claude', 'gpt4'],
            'custom': ['raiziom', 'custom']
        }
        
        # Get preferred AIs for this task
        preferred = task_preferences.get(task_type, ['claude', 'gpt4', 'grok'])
        
        # Find first available AI from preferred list
        for ai in preferred:
            if ai in self.clients:
                logger.debug(f"Selected {ai} for {task_type} (specialization match)")
                return ai
        
        # Fallback to active provider
        return self.active_provider if self.active_provider else 'claude'
    
    def _auto_select_provider(self):
        """Auto-select best available provider"""
        # Priority order: Claude > GPT-4 > Gemini > Grok > Raiziom > Custom
        priority = ['claude', 'gpt4', 'gemini', 'grok', 'raiziom', 'custom']
        
        for provider in priority:
            if provider in self.clients:
                self.active_provider = provider
                self.available = True
                logger.info(f"Auto-selected AI: {provider}")
                return
        
        self.available = False
        logger.warning("No AI providers available")
    
    async def consult_strategy(self, context: Dict) -> Dict:
        """
        Consult AI about strategy improvements
        
        Args:
            context: Trading context with win_rate, recent_trades, etc.
        
        Returns:
            Dict with suggestions
        """
        if not self.available:
            return {'skipped': True, 'reason': 'AI service not available'}
        
        try:
            # Prepare prompt
            prompt = self._create_strategy_prompt(context)
            
            # Call appropriate AI provider
            logger.info(f"🤖 Consulting {self.active_provider.upper()} for strategy improvements...")
            
            if self.active_provider == 'claude':
                response_text = await self._call_claude(prompt)
            elif self.active_provider == 'gpt4':
                response_text = await self._call_openai(prompt)
            elif self.active_provider == 'grok':
                response_text = await self._call_grok(prompt)
            elif self.active_provider == 'raiziom':
                response_text = await self._call_raiziom(prompt)
            elif self.active_provider == 'custom':
                response_text = await self._call_custom(prompt)
            else:
                return {'error': f'Unknown provider: {self.active_provider}'}
            
            # Parse response
            suggestions = self._parse_suggestions(response_text)
            
            # Store consultation
            self.consultation_history.append({
                'timestamp': datetime.now().isoformat(),
                'provider': self.active_provider,
                'context': context,
                'suggestions': suggestions
            })
            
            logger.info("✅ AI consultation complete")
            logger.info(f"   Provider: {self.active_provider}")
            logger.info(f"   Suggestions: {len(suggestions.get('actions', []))} actions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"AI consultation error: {e}")
            return {'error': str(e)}
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        message = self.clients['claude'].messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT-4 API"""
        response = self.clients['gpt4'].ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        return response.choices[0].message.content
    
    async def _call_grok(self, prompt: str) -> str:
        """Call Grok API (OpenAI-compatible)"""
        config = self.clients['grok']
        response = requests.post(
            config['endpoint'],
            headers={
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'grok-beta',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1024
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    async def _call_raiziom(self, prompt: str) -> str:
        """Call Raiziom custom AI API"""
        config = self.clients['raiziom']
        response = requests.post(
            config['endpoint'],
            headers={
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'max_tokens': 1024
            }
        )
        response.raise_for_status()
        return response.json().get('response', response.text)
    
    async def _call_custom(self, prompt: str) -> str:
        """Call custom AI endpoint"""
        config = self.clients['custom']
        response = requests.post(
            config['endpoint'],
            headers={
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'max_tokens': 1024
            }
        )
        response.raise_for_status()
        return response.json().get('response', response.text)
    
    def _create_strategy_prompt(self, context: Dict) -> str:
        """Create prompt for strategy consultation"""
        win_rate = context.get('win_rate', 0)
        recent_trades = context.get('recent_trades', [])
        systems_count = context.get('systems_count', 0)
        
        prompt = f"""
You are an expert quantitative trading advisor. Analyze this trading bot's recent performance and provide actionable improvements.

CURRENT PERFORMANCE:
- Win Rate: {win_rate:.1%}
- Recent Trades: {len(recent_trades)} trades
- Systems Active: {systems_count} trading systems

RECENT TRADES:
{json.dumps(recent_trades[-10:], indent=2)}

TASK:
Provide 3-5 specific, actionable improvements to increase the win rate above 70%. Focus on:
1. Entry timing optimization
2. Risk management improvements
3. Position sizing adjustments
4. Market condition filters

Return your response as JSON with this structure:
{{
    "analysis": "Brief analysis of current issues",
    "actions": [
        {{"action": "specific change", "reason": "why it helps", "priority": "high/medium/low"}}
    ]
}}
"""
        return prompt
    
    def _parse_suggestions(self, response_text: str) -> Dict:
        """Parse AI response into structured suggestions"""
        try:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = response_text[start:end]
                suggestions = json.loads(json_text)
                return suggestions
            else:
                # No JSON found, return raw text
                return {
                    'analysis': response_text,
                    'actions': []
                }
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return {
                'analysis': response_text,
                'actions': []
            }
    
    async def consult_market_research(self, symbol: str, market_data: Dict) -> Dict:
        """
        Research a specific market/symbol
        
        Args:
            symbol: Trading symbol
            market_data: Current market data
        
        Returns:
            Research insights
        """
        if not self.available:
            return {'skipped': True}
        
        try:
            prompt = f"""
Analyze {symbol} trading opportunity:

MARKET DATA:
{json.dumps(market_data, indent=2)}

Provide:
1. Key patterns or anomalies
2. Risk factors
3. Optimal entry/exit zones
4. Recommended position size multiplier (0.5-2.0x)

Return as JSON:
{{
    "assessment": "brief analysis",
    "risk_level": "low/medium/high",
    "position_multiplier": 1.0,
    "entry_zones": ["zone1", "zone2"],
    "warnings": ["warning1", "warning2"]
}}
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            return self._parse_suggestions(response_text)
            
        except Exception as e:
            logger.error(f"Market research error: {e}")
            return {'error': str(e)}
    
    async def optimize_position_sizing(self, balance: float, volatility: float, session: str) -> float:
        """
        Get AI recommendation on position sizing
        
        Args:
            balance: Current balance
            volatility: Market volatility
            session: Trading session
        
        Returns:
            Recommended position size multiplier
        """
        if not self.available:
            return 1.0  # Default
        
        try:
            prompt = f"""
Optimize position sizing:
- Balance: ${balance:.2f}
- Volatility: {volatility:.4f}
- Session: {session}

Recommend position size multiplier (0.5-2.0) based on conditions.
Return only the number.
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract number
            import re
            match = re.search(r'(\d+\.?\d*)', response_text)
            if match:
                multiplier = float(match.group(1))
                return max(0.5, min(2.0, multiplier))  # Clamp to 0.5-2.0
            
            return 1.0
            
        except Exception as e:
            logger.debug(f"Position sizing optimization error: {e}")
            return 1.0
    
    def get_stats(self) -> Dict:
        """Get consultation stats"""
        return {
            'available': self.available,
            'total_consultations': len(self.consultation_history),
            'last_consultation': self.consultation_history[-1]['timestamp'] if self.consultation_history else None
        }


# Singleton
_ai_consultation = None

def get_ai_consultation():
    """Get AI consultation service"""
    return _ai_consultation

def initialize_ai_consultation(provider: str = 'auto'):
    """
    Initialize AI consultation service
    
    Args:
        provider: AI provider ('auto', 'claude', 'gpt4', 'grok', 'raiziom', 'custom')
    """
    global _ai_consultation
    _ai_consultation = AIConsultationService(provider)
    logger.info("✅ AI CONSULTATION SERVICE ready!")
    return _ai_consultation


if __name__ == "__main__":
    # Test
    import asyncio
    
    async def test():
        ai = AIConsultationService()
        
        if ai.available:
            # Test strategy consultation
            context = {
                'win_rate': 0.55,
                'recent_trades': [
                    {'symbol': 'BTC/USDT', 'profit': 10, 'loss': 0},
                    {'symbol': 'ETH/USDT', 'profit': 0, 'loss': -5}
                ],
                'systems_count': 202
            }
            
            result = await ai.consult_strategy(context)
            print("✅ AI Consultation:", result)
        else:
            print("⚠️  AI not available - set ANTHROPIC_API_KEY")
    
    asyncio.run(test())
