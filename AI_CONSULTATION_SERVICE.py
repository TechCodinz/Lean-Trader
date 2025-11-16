#!/usr/bin/env python3
"""
🤖 AI CONSULTATION SERVICE 🤖

Uses Claude/Anthropic API to:
1. Continuously learn from trading results
2. Get strategy improvements
3. Research new market patterns
4. Optimize position sizing
5. Stay ahead of market changes

THE BOT THAT UPGRADES ITSELF!
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic not installed. Run: pip install anthropic")


class AIConsultationService:
    """
    AI CONSULTATION SERVICE
    
    Makes the bot learn and improve continuously by consulting Claude API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI consultation service
        
        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.available = False
        self.consultation_history = []
        
        # Initialize if API key available
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.available = True
                logger.info("🤖 AI CONSULTATION SERVICE initialized!")
                logger.info("   Bot will continuously learn and improve!")
            except Exception as e:
                logger.warning(f"AI service initialization failed: {e}")
        else:
            if not ANTHROPIC_AVAILABLE:
                logger.warning("⚠️  AI consultation disabled: anthropic not installed")
            elif not self.api_key:
                logger.warning("⚠️  AI consultation disabled: ANTHROPIC_API_KEY not set")
    
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
            
            # Call Claude API
            logger.info("🤖 Consulting Claude for strategy improvements...")
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            response_text = message.content[0].text
            suggestions = self._parse_suggestions(response_text)
            
            # Store consultation
            self.consultation_history.append({
                'timestamp': datetime.now().isoformat(),
                'context': context,
                'suggestions': suggestions
            })
            
            logger.info("✅ AI consultation complete")
            logger.info(f"   Suggestions: {len(suggestions.get('actions', []))} actions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"AI consultation error: {e}")
            return {'error': str(e)}
    
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

def initialize_ai_consultation(api_key: Optional[str] = None):
    """Initialize AI consultation service"""
    global _ai_consultation
    _ai_consultation = AIConsultationService(api_key)
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
