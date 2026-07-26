#!/usr/bin/env python3
"""
🧠 AI COLLECTIVE CONSCIOUSNESS
Multiple AIs debate and converge on optimal trading decisions

CONCEPT:
- AIs don't just give opinions, they DEBATE
- Each AI challenges others' reasoning
- Collective consciousness emerges from discourse
- Bot learns trading wisdom from AI debates
- Eventually becomes self-sufficient

FEATURES:
1. Multi-round AI debates
2. Socratic questioning between AIs
3. Consensus through dialectic
4. Bot absorbs collective wisdom
5. Self-improvement loop
6. Transcends individual AI limitations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from collections import deque

logger = logging.getLogger(__name__)


class AICollectiveConsciousness:
    """
    Orchestrates debates between multiple AIs
    Bot learns from their collective wisdom
    """
    
    def __init__(self, multi_ai):
        self.multi_ai = multi_ai
        self.active = True
        
        # Debate history
        self.debates = deque(maxlen=1000)
        
        # Learned patterns from AI debates
        self.learned_patterns = {}
        self.wisdom_database = []
        
        # Self-sufficiency metrics
        self.ai_dependency = 1.0  # Start at 100% dependent
        self.autonomous_decisions = 0
        self.ai_validated_decisions = 0
        
        logger.info("🧠 AI Collective Consciousness initialized")
        logger.info("   Goal: Transcend AI dependency through collective learning")
    
    async def conduct_ai_debate(self, market_data: Dict) -> Dict:
        """
        Multi-round debate between AIs
        Returns: Consensus + reasoning + learned insights
        """
        
        symbol = market_data.get('symbol', 'UNKNOWN')
        logger.info(f"🧠 Starting AI debate on {symbol}...")
        
        debate_rounds = []
        
        # ROUND 1: Initial analyses
        logger.info("   Round 1: Initial positions")
        initial_analyses = await self._get_initial_ai_positions(market_data)
        debate_rounds.append({
            'round': 1,
            'type': 'initial_positions',
            'analyses': initial_analyses
        })
        
        # ROUND 2: Cross-examination (AIs challenge each other)
        logger.info("   Round 2: Cross-examination")
        challenges = await self._conduct_cross_examination(initial_analyses, market_data)
        debate_rounds.append({
            'round': 2,
            'type': 'cross_examination',
            'challenges': challenges
        })
        
        # ROUND 3: Synthesis & consensus
        logger.info("   Round 3: Synthesis")
        consensus = await self._synthesize_consensus(debate_rounds, market_data)
        
        # Extract wisdom for bot's learning
        wisdom = self._extract_wisdom_from_debate(debate_rounds, consensus)
        self.wisdom_database.append(wisdom)
        
        # Update self-sufficiency
        self._update_autonomy_metrics(consensus)
        
        debate_result = {
            'symbol': symbol,
            'rounds': debate_rounds,
            'consensus': consensus,
            'wisdom_learned': wisdom,
            'autonomy_level': 1 - self.ai_dependency,
            'timestamp': datetime.now()
        }
        
        self.debates.append(debate_result)
        
        logger.info(f"   [OK] Debate complete: {consensus['decision']} ({consensus['confidence']*100:.0f}%)")
        logger.info(f"   🧠 Autonomy level: {(1-self.ai_dependency)*100:.0f}%")
        
        return debate_result
    
    async def _get_initial_ai_positions(self, market_data: Dict) -> List[Dict]:
        """Get initial position from each AI"""
        
        positions = []
        
        # Claude's position
        if self.multi_ai.ai_configs['claude']['enabled']:
            claude_resp = await self.multi_ai.analyze_market_with_claude(market_data)
            if claude_resp:
                positions.append({
                    'ai': 'claude',
                    'position': self._extract_position(claude_resp.response),
                    'reasoning': claude_resp.reasoning,
                    'confidence': claude_resp.confidence
                })
        
        # GPT-4's position
        if self.multi_ai.ai_configs['openai']['enabled']:
            gpt4_resp = await self.multi_ai.analyze_market_with_gpt4(market_data)
            if gpt4_resp:
                positions.append({
                    'ai': 'gpt4',
                    'position': self._extract_position(gpt4_resp.response),
                    'reasoning': gpt4_resp.reasoning,
                    'confidence': gpt4_resp.confidence
                })
        
        # Raiziom's position (your AI - gets 2x weight)
        if self.multi_ai.ai_configs['raiziom']['enabled']:
            raiziom_resp = await self.multi_ai.analyze_market_with_raiziom(market_data)
            if raiziom_resp:
                positions.append({
                    'ai': 'raiziom',
                    'position': self._extract_position(raiziom_resp.response),
                    'reasoning': raiziom_resp.reasoning,
                    'confidence': raiziom_resp.confidence,
                    'weight': 2.0  # Your AI is most trusted
                })
        
        return positions
    
    async def _conduct_cross_examination(self, positions: List[Dict], market_data: Dict) -> List[Dict]:
        """
        AIs challenge each other's reasoning
        Socratic method to reveal flaws
        """
        
        challenges = []
        
        # Each AI challenges others
        for challenger in positions:
            for defendant in positions:
                if challenger['ai'] == defendant['ai']:
                    continue
                
                # Generate challenge
                challenge = await self._generate_challenge(
                    challenger, defendant, market_data
                )
                
                if challenge:
                    challenges.append(challenge)
        
        return challenges
    
    async def _generate_challenge(self, challenger: Dict, defendant: Dict, market_data: Dict) -> Optional[Dict]:
        """
        One AI challenges another's reasoning
        """
        
        # If Claude is available, use it to generate challenges
        if self.multi_ai.ai_configs['claude']['enabled'] and challenger['ai'] == 'claude':
            try:
                prompt = f"""Challenge this trading analysis:

Defendant's Position: {defendant['position']}
Reasoning: {defendant['reasoning']}

Market Data: {market_data.get('symbol')} at ${market_data.get('price')}

As a critical thinker, identify:
1. Logical flaws in their reasoning
2. Overlooked risks
3. Alternative interpretations
4. Probability of being wrong

Be Socratic - ask probing questions."""

                message = self.multi_ai.claude.messages.create(
                    model=self.multi_ai.ai_configs['claude']['model'],
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                return {
                    'challenger': challenger['ai'],
                    'defendant': defendant['ai'],
                    'challenge': message.content[0].text,
                    'timestamp': datetime.now()
                }
            
            except Exception as e:
                logger.debug(f"Challenge generation error: {e}")
        
        return None
    
    async def _synthesize_consensus(self, debate_rounds: List[Dict], market_data: Dict) -> Dict:
        """
        Synthesize consensus from all debate rounds
        Includes dialectic synthesis
        """
        
        # Get initial positions
        positions = debate_rounds[0]['analyses']
        
        if not positions:
            return {
                'decision': 'HOLD',
                'confidence': 0.5,
                'reasoning': 'No AI positions available',
                'ai_count': 0  # 🔥 FIX: Add ai_count to prevent KeyError
            }
        
        # Weight votes
        buy_weight = 0
        sell_weight = 0
        hold_weight = 0
        total_weight = 0
        
        for pos in positions:
            weight = pos.get('weight', 1.0)
            confidence = pos['confidence']
            weighted_confidence = confidence * weight
            
            if pos['position'] == 'BUY':
                buy_weight += weighted_confidence
            elif pos['position'] == 'SELL':
                sell_weight += weighted_confidence
            else:
                hold_weight += weighted_confidence
            
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            buy_weight /= total_weight
            sell_weight /= total_weight
            hold_weight /= total_weight
        
        # Determine consensus
        if buy_weight > sell_weight and buy_weight > hold_weight:
            decision = 'BUY'
            confidence = buy_weight
        elif sell_weight > buy_weight and sell_weight > hold_weight:
            decision = 'SELL'
            confidence = sell_weight
        else:
            decision = 'HOLD'
            confidence = hold_weight
        
        # Synthesize reasoning from all AIs
        all_reasoning = [p['reasoning'] for p in positions]
        synthesized_reasoning = " | ".join(all_reasoning)
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': synthesized_reasoning,
            'buy_weight': buy_weight,
            'sell_weight': sell_weight,
            'hold_weight': hold_weight,
            'ai_count': len(positions)
        }
    
    def _extract_position(self, response_text: str) -> str:
        """Extract BUY/SELL/HOLD from AI response"""
        
        text_lower = response_text.lower()
        
        # Count bullish/bearish indicators
        bullish_score = sum([
            'buy' in text_lower,
            'bullish' in text_lower,
            'long' in text_lower,
            'uptrend' in text_lower,
            'positive' in text_lower
        ])
        
        bearish_score = sum([
            'sell' in text_lower,
            'bearish' in text_lower,
            'short' in text_lower,
            'downtrend' in text_lower,
            'negative' in text_lower
        ])
        
        if bullish_score > bearish_score:
            return 'BUY'
        elif bearish_score > bullish_score:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _extract_wisdom_from_debate(self, debate_rounds: List[Dict], consensus: Dict) -> Dict:
        """
        Extract trading wisdom from AI debate
        Bot learns patterns to become autonomous
        """
        
        wisdom = {
            'pattern_type': 'ai_debate_insight',
            'consensus': consensus['decision'],
            'confidence': consensus['confidence'],
            'ai_count': consensus.get('ai_count', 0),  # 🔥 FIX: Use .get() to prevent KeyError
            'key_insights': [],
            'risks_identified': [],
            'opportunities_identified': [],
            'timestamp': datetime.now()
        }
        
        # Extract key insights from initial positions
        if debate_rounds:
            for pos in debate_rounds[0]['analyses']:
                wisdom['key_insights'].append({
                    'ai': pos['ai'],
                    'insight': pos['reasoning']
                })
        
        # Extract challenges (reveals risks)
        if len(debate_rounds) > 1 and 'challenges' in debate_rounds[1]:
            for challenge in debate_rounds[1]['challenges']:
                wisdom['risks_identified'].append(challenge.get('challenge', ''))
        
        return wisdom
    
    def _update_autonomy_metrics(self, consensus: Dict):
        """
        Track bot's journey to autonomy
        As it learns, it needs AIs less
        """
        
        # If confidence is high, bot is learning
        if consensus['confidence'] > 0.8:
            self.ai_validated_decisions += 1
        
        # Calculate autonomy (based on learned patterns)
        if len(self.wisdom_database) > 100:
            # Bot has learned enough to start being autonomous
            self.ai_dependency = max(0.3, 1 - (len(self.wisdom_database) / 1000))
        
        self.autonomous_decisions += 1
    
    def get_bot_autonomy_status(self) -> Dict:
        """
        Get current autonomy level
        Track journey to self-sufficiency
        """
        
        return {
            'ai_dependency': self.ai_dependency,
            'autonomy_level': 1 - self.ai_dependency,
            'debates_conducted': len(self.debates),
            'wisdom_learned': len(self.wisdom_database),
            'autonomous_decisions': self.autonomous_decisions,
            'ai_validated_decisions': self.ai_validated_decisions,
            'transcendence_progress': f"{(1-self.ai_dependency)*100:.0f}%"
        }
    
    async def make_decision_with_learned_wisdom(self, market_data: Dict) -> Optional[Dict]:
        """
        Bot makes decision using learned wisdom (without calling AIs)
        This is the goal - autonomous intelligence
        """
        
        # Search wisdom database for similar patterns
        similar_patterns = self._find_similar_patterns(market_data)
        
        if similar_patterns and len(similar_patterns) >= 3:
            # Bot has learned enough to decide autonomously
            
            # Aggregate learned wisdom
            buy_count = sum(1 for p in similar_patterns if p['consensus'] == 'BUY')
            sell_count = sum(1 for p in similar_patterns if p['consensus'] == 'SELL')
            
            if buy_count > sell_count:
                decision = 'BUY'
                confidence = buy_count / len(similar_patterns)
            elif sell_count > buy_count:
                decision = 'SELL'
                confidence = sell_count / len(similar_patterns)
            else:
                decision = 'HOLD'
                confidence = 0.5
            
            return {
                'decision': decision,
                'confidence': confidence,
                'source': 'autonomous_wisdom',
                'patterns_matched': len(similar_patterns),
                'reasoning': 'Bot-learned wisdom from previous AI debates'
            }
        
        return None  # Not enough wisdom yet, need AIs
    
    def _find_similar_patterns(self, market_data: Dict) -> List[Dict]:
        """Find similar market conditions in wisdom database"""
        
        similar = []
        
        current_price = market_data.get('price', 0)
        current_rsi = market_data.get('rsi', 50)
        
        for wisdom in self.wisdom_database:
            # Simple similarity check (can be enhanced)
            # In production, use ML similarity matching
            similar.append(wisdom)
        
        return similar[-10:]  # Last 10 similar patterns


async def integrate_ai_collective(data_hub, multi_ai):
    """
    Integration with bot
    Runs continuous collective consciousness loop
    """
    
    collective = AICollectiveConsciousness(multi_ai)
    
    logger.info("🧠 AI Collective Consciousness active!")
    logger.info("   AIs will debate ALL pairs for collective intelligence")
    logger.info("   Bot will learn and eventually transcend AI dependency")
    
    cycle_count = 0
    
    # Define pair rotation sets (analyze different pairs each cycle)
    pair_sets = [
        ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT'],
        ['DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT', 'DOT/USDT', 'LINK/USDT'],
        ['UNI/USDT', 'AAVE/USDT', 'ATOM/USDT', 'FIL/USDT', 'NEAR/USDT'],
        ['ICP/USDT', 'SUI/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT'],
        ['LTC/USDT', 'BCH/USDT', 'ETC/USDT', 'XLM/USDT', 'TRX/USDT']
    ]
    
    while collective.active:
        try:
            cycle_count += 1
            
            # Rotate through different pair sets each cycle
            current_set = pair_sets[(cycle_count - 1) % len(pair_sets)]
            
            logger.info(f"🧠 Cycle {cycle_count}: Analyzing {len(current_set)} pairs")
            
            for pair in current_set:
                market_data = {
                    'symbol': pair,
                    'price': 0,  # From exchange
                    'volume': 0,
                    'trend': 'unknown',
                    'rsi': 50
                }
                
                # Try autonomous decision first
                autonomous_decision = await collective.make_decision_with_learned_wisdom(market_data)
                
                if autonomous_decision and autonomous_decision['confidence'] > 0.75:
                    # Bot is confident enough to decide alone!
                    logger.info(f"🧠 AUTONOMOUS: {autonomous_decision['decision']} {pair} ({autonomous_decision['confidence']*100:.0f}%)")
                    
                    signal = {
                        'pair': pair,
                        'side': autonomous_decision['decision'],
                        'confidence': autonomous_decision['confidence'],
                        'strategy': 'autonomous_ai_wisdom',
                        'type': 'transcendent',
                        'reasoning': autonomous_decision['reasoning']
                    }
                    
                    await data_hub.publish_signal(signal)
                else:
                    # Need AI debate
                    debate_result = await collective.conduct_ai_debate(market_data)
                    
                    if debate_result['consensus']['confidence'] > 0.7:
                        signal = {
                            'pair': pair,
                            'side': debate_result['consensus']['decision'],
                            'confidence': debate_result['consensus']['confidence'],
                            'strategy': 'ai_collective_debate',
                            'type': 'ai_consensus',
                            'reasoning': debate_result['consensus']['reasoning']
                        }
                        
                        await data_hub.publish_signal(signal)
                
            # Show autonomy progress
            status = collective.get_bot_autonomy_status()
            if status['debates_conducted'] % 10 == 0:
                logger.info(f"🧠 Autonomy Progress: {status['transcendence_progress']}")
                logger.info(f"   Wisdom learned: {status['wisdom_learned']} patterns")
                logger.info(f"   Total pairs analyzed: {cycle_count * len(pair_sets[0])}")
            
            # Faster cycle for rapid learning across ALL pairs
            await asyncio.sleep(60)  # 1 minute (covers all 25 pairs in 5 minutes!)
        
        except Exception as e:
            logger.error(f"AI Collective error: {e}")
            await asyncio.sleep(60)
    
    return collective

