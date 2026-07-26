"""
SUPREME UNIFIED ENGINE

Master integration layer that synchronizes ALL engines into perfect harmony:
- Wave Flow Engine (market state)
- Pitch Engine (regime detection) 
- Elite Stack (9 decision engines)
- Brain + HiveMind (multi-timeframe intelligence)
- All other advanced systems

Creates a trading consciousness that beats all humans and bots.
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SupremeUnifiedEngine:
    """
    Master engine that orchestrates ALL systems in perfect synchronization
    
    Decision Flow:
    Layer 1: Raw Data → Wave Flow → Pitch → Market State
    Layer 2: Elite Stack (Intent, Liquidity, OCE, SPS, RMF)
    Layer 3: Brain + HiveMind (Multi-TF consensus)
    Layer 4: Advanced Systems (Revolutionary, Divine, Ultra-Rare)
    Layer 5: Supreme Consensus → Final Decision
    """
    
    def __init__(self,
                 wave_engine=None,
                 pitch_engine=None,
                 elite_stack=None,
                 brain=None,
                 hivemind=None,
                 advanced_systems=None):
        """
        Initialize Supreme Unified Engine
        
        Args:
            wave_engine: Wave Flow Engine instance
            pitch_engine: Pitch Engine instance
            elite_stack: Elite Stack Integration instance
            brain: Brain instance
            hivemind: HiveCoordinator instance
            advanced_systems: Dict of advanced system instances
        """
        self.wave_engine = wave_engine
        self.pitch_engine = pitch_engine
        self.elite_stack = elite_stack
        self.brain = brain
        self.hivemind = hivemind
        self.advanced_systems = advanced_systems or {}
        
        # Consensus weights (tunable)
        self.consensus_weights = {
            'elite_stack': 0.40,      # Elite Stack gets highest weight
            'wave_pitch': 0.25,       # Wave + Pitch foundation
            'brain_hivemind': 0.20,   # Multi-TF intelligence
            'advanced': 0.15          # Revolutionary engines
        }
        
        logger.info("=" * 80)
        logger.info("🌟 SUPREME UNIFIED ENGINE INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Wave Flow: {'[OK]' if wave_engine else '[X]'}")
        logger.info(f"   Pitch Engine: {'[OK]' if pitch_engine else '[X]'}")
        logger.info(f"   Elite Stack: {'[OK]' if elite_stack else '[X]'}")
        logger.info(f"   Brain: {'[OK]' if brain else '[X]'}")
        logger.info(f"   HiveMind: {'[OK]' if hivemind else '[X]'}")
        logger.info(f"   Advanced Systems: {len(self.advanced_systems)}")
        logger.info("=" * 80)
    
    async def evaluate_supreme_decision(self,
                                       ohlcv: pd.DataFrame,
                                       symbol: str,
                                       current_price: float,
                                       portfolio_size: float,
                                       **kwargs) -> Dict[str, Any]:
        """
        Ultimate decision evaluation combining ALL engines
        
        Returns supreme decision with full context from all systems
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"🌟 SUPREME EVALUATION: {symbol} @ ${current_price:.2f}")
            logger.info(f"{'='*80}")
            
            # LAYER 1: Foundation (Wave + Pitch)
            logger.info("\n[Layer 1] Wave Flow + Pitch Analysis...")
            wave_output, pitch_output = await self._layer1_foundation(ohlcv)
            
            # LAYER 2: Elite Stack (9 engines)
            logger.info("\n[Layer 2] Elite Stack Evaluation...")
            elite_context = await self._layer2_elite_stack(
                ohlcv, symbol, current_price, portfolio_size,
                wave_output, pitch_output, **kwargs
            )
            
            # LAYER 3: Brain + HiveMind
            logger.info("\n[Layer 3] Brain + HiveMind Multi-TF...")
            brain_decision, hivemind_decision = await self._layer3_intelligence(
                ohlcv, symbol, current_price
            )
            
            # LAYER 4: Advanced Systems
            logger.info("\n[Layer 4] Advanced System Signals...")
            advanced_signals = await self._layer4_advanced_systems(
                ohlcv, symbol, current_price
            )
            
            # LAYER 5: Supreme Consensus
            logger.info("\n[Layer 5] Supreme Consensus Calculation...")
            final_decision = self._layer5_consensus(
                elite_context,
                wave_output,
                pitch_output,
                brain_decision,
                hivemind_decision,
                advanced_signals
            )
            
            # Build supreme context
            supreme_context = {
                'symbol': symbol,
                'current_price': current_price,
                'timestamp': datetime.now(),
                
                # Layer 1
                'wave_state': wave_output.get('state') if wave_output else None,
                'wave_flow_score': wave_output.get('flow_score', 0.5) if wave_output else 0.5,
                'chaos_score': wave_output.get('chaos_score', 0.5) if wave_output else 0.5,
                'pitch_value': pitch_output.get('pitch_value', 0.5) if pitch_output else 0.5,
                'pitch_regime': pitch_output.get('regime') if pitch_output else None,
                
                # Layer 2 - Elite Stack
                'elite_context': elite_context,
                'elite_action': elite_context.get_final_action() if elite_context else 'WAIT',
                'elite_confidence': elite_context.oce.confidence if elite_context and elite_context.oce else 0.0,
                
                # Layer 3 - Intelligence
                'brain_decision': brain_decision,
                'hivemind_decision': hivemind_decision,
                
                # Layer 4 - Advanced
                'advanced_signals': advanced_signals,
                
                # Layer 5 - Final
                'final_action': final_decision['action'],
                'final_confidence': final_decision['confidence'],
                'consensus_score': final_decision['consensus_score'],
                'size_multiplier': final_decision['size_multiplier'],
                'reason_summary': final_decision['reasons']
            }
            
            # Log summary
            self._log_supreme_summary(supreme_context)
            
            return supreme_context
            
        except Exception as e:
            logger.error(f"Supreme evaluation error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_safe_default()
    
    async def _layer1_foundation(self, ohlcv: pd.DataFrame) -> Tuple[Dict, Dict]:
        """Layer 1: Wave Flow + Pitch foundation"""
        wave_output = {}
        pitch_output = {}
        
        try:
            # Wave Flow
            if self.wave_engine and hasattr(self.wave_engine, 'calculate_wave_flow'):
                wave_result = self.wave_engine.calculate_wave_flow(ohlcv)
                wave_output = {
                    'state': wave_result.state,
                    'flow_score': wave_result.wave_flow_score,
                    'chaos_score': wave_result.chaos_score,
                    'confidence': wave_result.confidence
                }
                logger.info(f"   Wave: {wave_result.state} | Flow={wave_result.wave_flow_score:.2f} | Chaos={wave_result.chaos_score:.2f}")
            
            # Pitch
            if self.pitch_engine and hasattr(self.pitch_engine, 'evaluate'):
                pitch_result = self.pitch_engine.evaluate(ohlcv, wave_output)
                pitch_output = {
                    'pitch_value': pitch_result.pitch_value,
                    'regime': pitch_result.regime,
                    'bent_params': pitch_result.bent_params
                }
                logger.info(f"   Pitch: {pitch_result.regime} | Value={pitch_result.pitch_value:.2f}")
        
        except Exception as e:
            logger.warning(f"Layer 1 error: {e}")
        
        return wave_output, pitch_output
    
    async def _layer2_elite_stack(self,
                                  ohlcv: pd.DataFrame,
                                  symbol: str,
                                  current_price: float,
                                  portfolio_size: float,
                                  wave_output: Dict,
                                  pitch_output: Dict,
                                  **kwargs) -> Optional[Any]:
        """Layer 2: Elite Stack 9-engine evaluation"""
        if not self.elite_stack:
            return None
        
        try:
            from elite_stack.models import SymbolClass
            
            # Determine symbol class
            symbol_class = self._get_symbol_class(symbol)
            
            # Evaluate elite context
            elite_context = self.elite_stack.evaluate_elite_context(
                ohlcv=ohlcv,
                current_price=current_price,
                wave_state=wave_output.get('state'),
                wave_flow_score=wave_output.get('flow_score', 0.5),
                chaos_score=wave_output.get('chaos_score', 0.5),
                pitch_value=pitch_output.get('pitch_value', 0.5),
                pitch_regime=pitch_output.get('regime'),
                volatility=kwargs.get('volatility', 0.02),
                baseline_volatility=kwargs.get('baseline_volatility', 0.02),
                symbol=symbol,
                venue_type=kwargs.get('venue_type', 'CEX'),
                symbol_class=symbol_class,
                portfolio_size=portfolio_size,
                proposed_entry=kwargs.get('proposed_entry', current_price),
                proposed_size=kwargs.get('proposed_size', portfolio_size * 0.05),
                proposed_direction=kwargs.get('proposed_direction', 1),
                stop_loss_pct=kwargs.get('stop_loss_pct', 0.02),
                take_profit_pct=kwargs.get('take_profit_pct', 0.03),
                bar_id=len(ohlcv)
            )
            
            final_action = elite_context.get_final_action()
            logger.info(f"   Elite Stack: {final_action}")
            
            if elite_context.oce:
                logger.info(f"   OCE: {elite_context.oce.oce_decision} | Score={elite_context.oce.oce_score:.2f}")
            if elite_context.rmf:
                logger.info(f"   RMF: RegretTAKE={elite_context.rmf.regret_take:.2f} | RegretSKIP={elite_context.rmf.regret_skip:.2f}")
            
            return elite_context
            
        except Exception as e:
            logger.warning(f"Layer 2 error: {e}")
            return None
    
    async def _layer3_intelligence(self,
                                   ohlcv: pd.DataFrame,
                                   symbol: str,
                                   current_price: float) -> Tuple[Optional[str], Optional[str]]:
        """Layer 3: Brain + HiveMind multi-timeframe intelligence"""
        brain_decision = None
        hivemind_decision = None
        
        try:
            # Brain
            if self.brain and hasattr(self.brain, 'decide'):
                brain_result = await self.brain.decide(ohlcv, symbol)
                brain_decision = brain_result.get('action')
                logger.info(f"   Brain: {brain_decision}")
            
            # HiveMind
            if self.hivemind and hasattr(self.hivemind, 'coordinate'):
                hivemind_result = await self.hivemind.coordinate(symbol)
                hivemind_decision = hivemind_result.get('consensus_action')
                logger.info(f"   HiveMind: {hivemind_decision}")
        
        except Exception as e:
            logger.warning(f"Layer 3 error: {e}")
        
        return brain_decision, hivemind_decision
    
    async def _layer4_advanced_systems(self,
                                      ohlcv: pd.DataFrame,
                                      symbol: str,
                                      current_price: float) -> Dict[str, Any]:
        """Layer 4: Advanced system signals (Revolutionary, Divine, etc.)"""
        signals = {}
        
        try:
            for system_name, system in self.advanced_systems.items():
                if hasattr(system, 'evaluate'):
                    result = await system.evaluate(ohlcv, symbol, current_price)
                    signals[system_name] = result
                    logger.info(f"   {system_name}: {result.get('signal', 'N/A')}")
        
        except Exception as e:
            logger.warning(f"Layer 4 error: {e}")
        
        return signals
    
    def _layer5_consensus(self,
                         elite_context,
                         wave_output,
                         pitch_output,
                         brain_decision,
                         hivemind_decision,
                         advanced_signals) -> Dict[str, Any]:
        """
        Layer 5: Supreme Consensus
        
        Weighted voting across all layers to achieve unbeatable decision
        """
        # Collect votes
        votes = {
            'TAKE': 0.0,
            'SKIP': 0.0,
            'WAIT': 0.0
        }
        
        reasons = []
        
        # Elite Stack vote (40% weight)
        if elite_context:
            elite_action = elite_context.get_final_action()
            votes[elite_action] += self.consensus_weights['elite_stack']
            reasons.append(f"Elite Stack: {elite_action}")
        
        # Wave + Pitch vote (25% weight)
        wave_vote = self._interpret_wave_pitch(wave_output, pitch_output)
        votes[wave_vote] += self.consensus_weights['wave_pitch']
        reasons.append(f"Wave+Pitch: {wave_vote}")
        
        # Brain + HiveMind vote (20% weight)
        brain_vote = self._interpret_brain_hivemind(brain_decision, hivemind_decision)
        votes[brain_vote] += self.consensus_weights['brain_hivemind']
        reasons.append(f"Brain+Hive: {brain_vote}")
        
        # Advanced systems vote (15% weight)
        advanced_vote = self._interpret_advanced(advanced_signals)
        votes[advanced_vote] += self.consensus_weights['advanced']
        reasons.append(f"Advanced: {advanced_vote}")
        
        # Determine winner
        winner = max(votes, key=votes.get)
        consensus_score = votes[winner]
        
        # Calculate confidence
        vote_margin = votes[winner] - sorted(votes.values())[-2]  # Margin over second place
        confidence = min(consensus_score + vote_margin, 1.0)
        
        # Size multiplier
        size_multiplier = 1.0
        if elite_context:
            size_multiplier = elite_context.get_size_multiplier()
        
        # Adjust size based on consensus strength
        size_multiplier *= consensus_score
        
        return {
            'action': winner,
            'consensus_score': consensus_score,
            'confidence': confidence,
            'size_multiplier': size_multiplier,
            'votes': votes,
            'reasons': reasons
        }
    
    def _interpret_wave_pitch(self, wave_output: Dict, pitch_output: Dict) -> str:
        """Interpret Wave + Pitch """
        # IMPULSE + hot/normal regime = bullish → TAKE if flow high
        # CORRECTIVE = WAIT
        # CHAOS = SKIP
        
        wave_state = wave_output.get('state', 'UNKNOWN')
        flow_score = wave_output.get('flow_score', 0.5)
        chaos = wave_output.get('chaos_score', 0.5)
        
        if chaos > 0.7:
            return 'SKIP'
        elif wave_state == 'IMPULSE' and flow_score > 0.6:
            return 'TAKE'
        elif wave_state == 'CORRECTIVE':
            return 'WAIT'
        else:
            return 'WAIT'
    
    def _interpret_brain_hivemind(self, brain_decision, hivemind_decision) -> str:
        """Interpret Brain + HiveMind"""
        # Both agree → follow
        # Disagree → WAIT
        if brain_decision == hivemind_decision and brain_decision in ['TAKE', 'SKIP', 'WAIT']:
            return brain_decision
        return 'WAIT'
    
    def _interpret_advanced(self, advanced_signals: Dict) -> str:
        """Interpret advanced system signals"""
        # Aggregate advanced signals
        bullish = 0
        bearish = 0
        
        for system_name, signal_data in advanced_signals.items():
            signal = signal_data.get('signal', 'NEUTRAL')
            if signal in ['BUY', 'LONG', 'TAKE']:
                bullish += 1
            elif signal in ['SELL', 'SHORT', 'SKIP']:
                bearish += 1
        
        if bullish > bearish and bullish >= 2:
            return 'TAKE'
        elif bearish > bullish and bearish >= 2:
            return 'SKIP'
        else:
            return 'WAIT'
    
    def _get_symbol_class(self, symbol: str):
        """Determine symbol class for Elite Stack"""
        from elite_stack.models import SymbolClass
        
        symbol_upper = symbol.upper()
        if "BTC" in symbol_upper or "ETH" in symbol_upper:
            return SymbolClass.CRYPTO_LARGE
        elif "XAU" in symbol_upper or "XAG" in symbol_upper:
            return SymbolClass.METAL
        elif any(x in symbol_upper for x in ["EUR", "USD", "GBP", "JPY"]):
            return SymbolClass.FX_MAJOR
        else:
            return SymbolClass.CRYPTO_ALT
    
    def _log_supreme_summary(self, context: Dict):
        """Log supreme decision summary"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🌟 SUPREME DECISION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Symbol: {context['symbol']}")
        logger.info(f"Final Action: {context['final_action']}")
        logger.info(f"Consensus Score: {context['consensus_score']:.2f}")
        logger.info(f"Confidence: {context['final_confidence']:.2f}")
        logger.info(f"Size Multiplier: {context['size_multiplier']:.2f}")
        logger.info(f"\nReasons:")
        for reason in context['reason_summary']:
            logger.info(f"  • {reason}")
        logger.info(f"{'='*80}\n")
    
    def _get_safe_default(self) -> Dict:
        """Safe default on error"""
        return {
            'final_action': 'WAIT',
            'final_confidence': 0.0,
            'consensus_score': 0.0,
            'size_multiplier': 0.0,
            'reason_summary': ['Error occurred, defaulting to WAIT']
        }
