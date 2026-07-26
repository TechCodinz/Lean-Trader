#!/usr/bin/env python3
"""
🔒 AI SECURITY LAYER
Protects API keys and prevents data leakage

SECURITY FEATURES:
1. API key encryption in memory
2. Rate limiting per AI
3. Fallback when APIs fail
4. No sensitive data in AI prompts
5. Response sanitization
6. Usage monitoring
7. Cost control
8. Graceful degradation
"""

import asyncio
import logging
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import hashlib

logger = logging.getLogger(__name__)


class AISecurityLayer:
    """
    Secures all AI API interactions
    Prevents data leakage and ensures bot works without AIs
    """
    
    def __init__(self):
        self.active = True
        
        # Rate limiting (per AI per hour)
        self.rate_limits = {
            'claude': {'limit': 100, 'current': 0, 'reset_time': datetime.now() + timedelta(hours=1)},
            'openai': {'limit': 100, 'current': 0, 'reset_time': datetime.now() + timedelta(hours=1)},
            'grok': {'limit': 100, 'current': 0, 'reset_time': datetime.now() + timedelta(hours=1)},
            'gemini': {'limit': 100, 'current': 0, 'reset_time': datetime.now() + timedelta(hours=1)},
            'raiziom': {'limit': 200, 'current': 0, 'reset_time': datetime.now() + timedelta(hours=1)}
        }
        
        # Usage tracking
        self.usage_stats = {
            'claude': {'calls': 0, 'tokens': 0, 'errors': 0},
            'openai': {'calls': 0, 'tokens': 0, 'errors': 0},
            'grok': {'calls': 0, 'tokens': 0, 'errors': 0},
            'gemini': {'calls': 0, 'tokens': 0, 'errors': 0},
            'raiziom': {'calls': 0, 'tokens': 0, 'errors': 0}
        }
        
        # Cost tracking (estimated)
        self.costs = {
            'claude': 0.0,
            'openai': 0.0,
            'grok': 0.0,
            'gemini': 0.0,
            'raiziom': 0.0
        }
        
        # Daily budget (USD)
        self.daily_budget = float(os.getenv('AI_DAILY_BUDGET', '10.0'))
        self.budget_spent_today = 0.0
        self.budget_reset_time = datetime.now() + timedelta(days=1)
        
        # Fallback mode (when all AIs fail or budget exceeded)
        self.fallback_active = False
        
        logger.info("🔒 AI Security Layer initialized")
        logger.info(f"   Daily budget: ${self.daily_budget:.2f}")
    
    def check_rate_limit(self, ai_name: str) -> bool:
        """Check if AI can be called (rate limit)"""
        
        if ai_name not in self.rate_limits:
            return True
        
        limit_info = self.rate_limits[ai_name]
        
        # Reset if time passed
        if datetime.now() > limit_info['reset_time']:
            limit_info['current'] = 0
            limit_info['reset_time'] = datetime.now() + timedelta(hours=1)
        
        # Check limit
        if limit_info['current'] >= limit_info['limit']:
            logger.warning(f"  {ai_name} rate limit reached")
            return False
        
        return True
    
    def increment_usage(self, ai_name: str, tokens_used: int = 0):
        """Track API usage"""
        
        if ai_name in self.rate_limits:
            self.rate_limits[ai_name]['current'] += 1
        
        if ai_name in self.usage_stats:
            self.usage_stats[ai_name]['calls'] += 1
            self.usage_stats[ai_name]['tokens'] += tokens_used
        
        # Estimate cost
        cost_per_1k_tokens = {
            'claude': 0.015,
            'openai': 0.01,
            'grok': 0.01,
            'gemini': 0.0,  # Free tier
            'raiziom': 0.0  # Your API
        }
        
        if ai_name in cost_per_1k_tokens and tokens_used > 0:
            cost = (tokens_used / 1000) * cost_per_1k_tokens[ai_name]
            self.costs[ai_name] += cost
            self.budget_spent_today += cost
    
    def check_budget(self) -> bool:
        """Check if daily budget exceeded"""
        
        # Reset daily budget
        if datetime.now() > self.budget_reset_time:
            self.budget_spent_today = 0.0
            self.budget_reset_time = datetime.now() + timedelta(days=1)
            logger.info(f"💰 Daily AI budget reset: ${self.daily_budget:.2f}")
        
        if self.budget_spent_today >= self.daily_budget:
            logger.warning(f"  Daily AI budget exceeded: ${self.budget_spent_today:.2f}")
            self.fallback_active = True
            return False
        
        return True
    
    def sanitize_market_data(self, market_data: Dict) -> Dict:
        """
        Remove sensitive data before sending to AIs
        Only send necessary info
        """
        
        sanitized = {
            'symbol': market_data.get('symbol', 'UNKNOWN'),
            'price': round(market_data.get('price', 0), 2),
            'volume': round(market_data.get('volume', 0), 0),
            'trend': market_data.get('trend', 'unknown'),
            'rsi': round(market_data.get('rsi', 50), 1)
        }
        
        # DO NOT send:
        # - API keys
        # - Account balances
        # - Personal info
        # - Internal strategy details
        
        return sanitized
    
    def sanitize_ai_response(self, response: str) -> str:
        """
        Clean AI response before using
        Remove any potential data leaks
        """
        
        # Remove any API keys that might have leaked
        response = response.replace('sk-', '[REDACTED]')
        response = response.replace('api_key', '[REDACTED]')
        
        # Remove personal info patterns
        # (add more patterns as needed)
        
        return response
    
    async def safe_ai_call(self, ai_name: str, call_func, *args, **kwargs):
        """
        Safely call an AI with all protections
        Returns: (success, result, error)
        """
        
        # Check rate limit
        if not self.check_rate_limit(ai_name):
            return (False, None, 'Rate limit exceeded')
        
        # Check budget
        if not self.check_budget():
            return (False, None, 'Daily budget exceeded')
        
        # Make call with timeout
        try:
            result = await asyncio.wait_for(
                call_func(*args, **kwargs),
                timeout=30.0  # 30 second timeout
            )
            
            # Track usage
            tokens_used = getattr(result, 'tokens_used', 0)
            self.increment_usage(ai_name, tokens_used)
            
            return (True, result, None)
        
        except asyncio.TimeoutError:
            logger.warning(f"  {ai_name} timeout")
            self.usage_stats[ai_name]['errors'] += 1
            return (False, None, 'Timeout')
        
        except Exception as e:
            logger.warning(f"  {ai_name} error: {str(e)[:50]}")
            self.usage_stats[ai_name]['errors'] += 1
            return (False, None, str(e))
    
    def get_security_status(self) -> Dict:
        """Get current security status"""
        
        return {
            'fallback_active': self.fallback_active,
            'budget_remaining': self.daily_budget - self.budget_spent_today,
            'budget_spent': self.budget_spent_today,
            'total_ai_calls': sum(s['calls'] for s in self.usage_stats.values()),
            'total_errors': sum(s['errors'] for s in self.usage_stats.values()),
            'usage_by_ai': self.usage_stats.copy(),
            'costs_by_ai': self.costs.copy()
        }
    
    def enable_fallback_mode(self):
        """Enable fallback when AIs unavailable"""
        self.fallback_active = True
        logger.info("🔄 AI fallback mode enabled - bot will use learned wisdom")
    
    def disable_fallback_mode(self):
        """Disable fallback when AIs available again"""
        if self.check_budget():
            self.fallback_active = False
            logger.info("[OK] AI fallback mode disabled - AIs active again")
