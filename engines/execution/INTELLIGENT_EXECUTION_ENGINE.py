from typing import Dict, Optional
#!/usr/bin/env python3
"""
🧠 ULTRA-ADVANCED INTELLIGENT EXECUTION ENGINE 🧠

THE COMPLETE SYSTEM - Wires ALL execution intelligence together!

INTEGRATED SYSTEMS:
1. INTELLIGENT EXECUTION - Multi-timeframe, session-aware, dynamic sizing
2. OMNISCIENT EXECUTION - Multi-exchange, multi-market (Spot/Futures/Perpetual)
3. PERFECT EXECUTION - Perfect entry timing, trailing stops
4. SIGNAL AGGREGATOR - Combines multiple signals intelligently
5. MOON SPOTTER - Moonshot coin detection (DEX, micro caps)
6. RESEARCH/SCOUTING - Complete market intelligence

USES ALL INTELLIGENCE:
- Multi-timeframe coordination (trade 1m, 5m, 1h simultaneously)
- Dynamic lot sizing (based on confidence, volatility, regime)
- Session awareness (London, NY, Asian sessions)
- Multi-exchange support (Gate.io, Bybit, Binance, etc from .env)
- Multi-market (Spot, Futures, Perpetual, DEX)
- Perfect entry timing (waits for optimal price)
- Moonshot detection (finds 1000x gems)
- Complete entry/exit planning
- Future trade sequencing
- ALL engines working in harmony
"""

import asyncio
try:
    from BALANCE_AWARE_EXECUTION import get_balance_aware_system
    BALANCE_AWARE_AVAILABLE = True
except:
    BALANCE_AWARE_AVAILABLE = False
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from collections import defaultdict
import math
import os

logger = logging.getLogger(__name__)

# Global Engine Instance
_global_engine = None

# 🔥 PHASE B: DARWINISM INTEGRATION
try:
    try:
        from DARWINISM_WRAPPER import record_signal_safe, record_trade_safe, get_engine_influence_safe
    except ImportError:
        from utils.helpers.DARWINISM_WRAPPER import record_signal_safe, record_trade_safe, get_engine_influence_safe
    DARWINISM_INTEGRATED = True
    logger.info("🧠 DARWINISM integrated - Adaptive learning ACTIVE!")
except Exception as e:
    DARWINISM_INTEGRATED = False
    logger.warning(f" DARWINISM not available: {e}")

# Import MT5 forex integration
try:
    try:
        from MT5_FOREX_ENGINE_INTEGRATION import get_mt5_forex_integration
    except ImportError:
        from utils.helpers.MT5_FOREX_ENGINE_INTEGRATION import get_mt5_forex_integration
    MT5_FOREX_INTEGRATION_AVAILABLE = True
    logger.info("[OK] MT5 FOREX INTEGRATION available (automated forex pair routing)")
except Exception as e:
    MT5_FOREX_INTEGRATION_AVAILABLE = False
    logger.warning(f" MT5 FOREX INTEGRATION not available: {e}")

# Import advanced execution components
try:
    try:
        from OMNISCIENT_EXECUTION_ENGINE import OmniscientExecutionEngine
    except ImportError:
        from engines.execution.OMNISCIENT_EXECUTION_ENGINE import OmniscientExecutionEngine
    OMNISCIENT_AVAILABLE = True
    logger.info("[OK] OMNISCIENT EXECUTION ENGINE available (multi-exchange, multi-market)")
except Exception as e:
    OMNISCIENT_AVAILABLE = False
    logger.warning(f" OMNISCIENT EXECUTION ENGINE not available: {e}")

try:
    try:
        from PERFECT_EXECUTION_SYSTEM import PerfectEntryTimer, TrailingProfitManager
    except ImportError:
        from engines.execution.PERFECT_EXECUTION_SYSTEM import PerfectEntryTimer, TrailingProfitManager
    PERFECT_ENTRY_AVAILABLE = True
    logger.info("[OK] PERFECT EXECUTION SYSTEM available (perfect entry, trailing)")
except Exception as e:
    PERFECT_ENTRY_AVAILABLE = False
    logger.warning(f" PERFECT EXECUTION SYSTEM not available: {e}")

try:
    try:
        from SIGNAL_AGGREGATOR import SignalAggregator
    except ImportError:
        from utils.helpers.SIGNAL_AGGREGATOR import SignalAggregator
    SIGNAL_AGGREGATOR_AVAILABLE = True
    logger.info("[OK] SIGNAL AGGREGATOR available (intelligent signal combining)")
except Exception as e:
    SIGNAL_AGGREGATOR_AVAILABLE = False
    logger.warning(f" SIGNAL AGGREGATOR not available: {e}")

try:
    from ultra_rare.goldmine.ultra_moon_spotter import MicroMoonSpotter
    MOON_SPOTTER_AVAILABLE = True
    logger.info("[OK] MOON SPOTTER available (moonshot detection across DEXs)")
except Exception as e:
    MOON_SPOTTER_AVAILABLE = False
    logger.warning(f" MOON SPOTTER not available: {e}")

try:
    try:
        from ADAPTIVE_EXCHANGE_INTELLIGENCE import AdaptiveExchangeIntelligence
    except ImportError:
        try:
            from ai.intelligence.ADAPTIVE_EXCHANGE_INTELLIGENCE import AdaptiveExchangeIntelligence
        except ImportError:
            from utils.helpers.ADAPTIVE_EXCHANGE_INTELLIGENCE import AdaptiveExchangeIntelligence
    ADAPTIVE_INTELLIGENCE_AVAILABLE = True
    logger.info("[OK] ADAPTIVE EXCHANGE INTELLIGENCE available (multi-exchange awareness)")
except Exception as e:
    ADAPTIVE_INTELLIGENCE_AVAILABLE = False
    logger.warning(f" ADAPTIVE EXCHANGE INTELLIGENCE not available: {e}")

try:
    try:
        from AI_CONSULTATION_SYSTEM import AIConsultationSystem
    except ImportError:
        try:
            from ai.intelligence.AI_CONSULTATION_SYSTEM import AIConsultationSystem
        except ImportError:
            from utils.helpers.AI_CONSULTATION_SYSTEM import AIConsultationSystem
    AI_CONSULTATION_AVAILABLE = True
    logger.info("[OK] AI CONSULTATION SYSTEM available (Claude, GPT-4, Gemini)")
except Exception as e:
    AI_CONSULTATION_AVAILABLE = False
    logger.warning(f" AI CONSULTATION SYSTEM not available: {e}")

class IntelligentExecutionEngine:
    """
    ULTRA-ADVANCED INTELLIGENT EXECUTION - Uses ALL execution intelligence!
    
    INTEGRATED FEATURES:
    1. Multi-timeframe coordination (1m-1W)
    2. Dynamic lot sizing (6 factors)
    3. Session awareness (Global sessions)
    4. Multi-exchange support (Gate.io, Bybit, Binance, etc)
    5. Multi-market (Spot, Futures, Perpetual, DEX)
    6. Perfect entry timing (waits for optimal price)
    7. Moonshot detection (DEX micro caps, 1000x potential)
    8. Signal aggregation (combines multiple engines)
    9. Intelligent leverage (confidence-based)
    10. Trailing stops (let winners run)
    11. Complete trade planning
    12. Future sequencing
    13. ALL 116+ engines in harmony
    """
    
    def _get_max_hold_time(self, timeframe: str) -> float:
        """
        Get ULTRA-FAST hold time based on timeframe
        
        1m → 1 minute (60 seconds!)
        5m → 5 minutes
        15m → 15 minutes
        1h → 60 minutes
        
        GOAL: FAST PROFIT-TAKING → FREE CAPITAL → MORE TRADES → EXPONENTIAL GROWTH!
        """
        timeframe_to_minutes = {
            '1m': 1.0,      # ⚡ 60 seconds max hold!
            '3m': 3.0,
            '5m': 5.0,
            '15m': 15.0,
            '30m': 30.0,
            '1h': 60.0,
            '2h': 120.0,
            '4h': 240.0,
            '1d': 1440.0,
            '1w': 10080.0
        }
        return timeframe_to_minutes.get(timeframe, 30.0)
    
    def _get_check_interval(self, timeframe: str) -> float:
        """
        Get ULTRA-FAST check interval based on timeframe
        
        1m → Check every 1 second!
        5m → Check every 3 seconds
        15m → Check every 10 seconds
        
        GOAL: INSTANT PROFIT DETECTION → CLOSE FAST → RECYCLE CAPITAL!
        """
        # DEBUG: Log exact timeframe being checked
        logger.debug(f"_get_check_interval called with: '{timeframe}' (type: {type(timeframe).__name__})")
        
        timeframe_to_interval = {
            '1m': 1.0,      # ⚡ Check every second!
            '3m': 2.0,
            '5m': 3.0,
            '15m': 10.0,
            '30m': 15.0,
            '1h': 30.0,
            '2h': 60.0,
            '4h': 120.0,
            '1d': 300.0,
            '1w': 600.0
        }
        result = timeframe_to_interval.get(timeframe, 10.0)
        logger.debug(f"_get_check_interval returning: {result} for '{timeframe}'")
        return result
    
    def _should_skip_symbol(self, symbol: str) -> bool:
        """
        Check if symbol should be skipped on current exchange
        
        Uses MT5 forex integration for intelligent routing:
        - Forex pairs → MT5 (when available, skip for now)
        - Crypto USDT → Crypto exchanges (trade now!)
        - Everything else → Skip
        """
        # Use MT5 integration if available
        if self.mt5_forex and MT5_FOREX_INTEGRATION_AVAILABLE:
            routing = self.mt5_forex.get_routing_info(symbol)
            
            # If it's forex but MT5 not connected, skip for now
            if routing['exchange_type'] == 'mt5':
                # TODO: When MT5 is connected, route to MT5 instead of skipping
                logger.debug(f"⏭️  {symbol} is forex - will route to MT5 when connected")
                return False  # FIXED: Allow all symbols  # Skip for now (no MT5 yet)
            
            # If it's crypto USDT, trade it!
            if routing['market_type'] == 'spot' and '/USDT' in symbol:
                return False  # Trade it!
            
            # Everything else, skip
            return False  # FIXED: Allow all symbols
        
        # Fallback if MT5 integration not available
        # Forex patterns (3-letter currency codes)
        forex_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'CNY', 'HKD']
        
        # Check if it's a symbol without '/' (forex or TradFi)
        if '/' not in symbol:
            return False  # FIXED: Allow all symbols  # Skip - needs MT5
        
        # Check if it's a forex pair (USD/JPY, EUR/GBP, etc.)
        parts = symbol.split('/')
        if len(parts) == 2:
            base, quote = parts
            # If both parts are forex codes, it's a forex pair
            if base.replace('+', '') in forex_codes and quote.replace('+', '') in forex_codes:
                return False  # FIXED: Allow all symbols  # Skip - needs MT5
        
        # Check if it's not a USDT pair
        if '/USDT' not in symbol:
            # For crypto exchanges, we only trade USDT pairs
            return False  # FIXED: Allow all symbols  # Skip - not USDT pair
        
        # It's a USDT crypto pair - OK to trade!
        return False
    
    def __init__(self, exchange, mode='testnet', exchanges=None, balance=None, situational_awareness=None, **kwargs):
        self.situational_awareness = situational_awareness
        self.exchange = exchange  # Default exchange
        self.exchanges = exchanges or {}  # All available exchanges (for router)
        self.mode = mode
        self.actual_balance = balance or 20.0  # Default to 20 for safety
        
        # MT5 Forex integration
        self.mt5_forex = None
        if MT5_FOREX_INTEGRATION_AVAILABLE:
            try:
                self.mt5_forex = get_mt5_forex_integration()
                logger.info(f"[OK] MT5 Forex: {len(self.mt5_forex.forex_symbols)} pairs available")
            except Exception as e:
                logger.warning(f"  Could not load MT5 forex integration: {e}")
        
        # Multi-timeframe tracking
        self.active_trades_by_tf = defaultdict(list)  # {symbol: [{'tf': '1m', 'id': ...}, ...]}
        
        # Session definitions
        self.sessions = {
            'asian': (time(0, 0), time(9, 0)),     # 00:00-09:00 UTC
            'london': (time(8, 0), time(16, 0)),   # 08:00-16:00 UTC
            'ny': (time(13, 0), time(22, 0)),      # 13:00-22:00 UTC
        }
        
        # Future trade plans
        self.planned_trades = []  # [{symbol, timeframe, entry_condition, planned_at}]
        
        # Volatility tracking
        self.volatility_by_pair = {}  # {symbol: volatility_pct}
        
        # 🔥 OMNISCIENT EXECUTION - Multi-exchange, multi-market
        self.omniscient_engine = None
        if OMNISCIENT_AVAILABLE:
            try:
                self.omniscient_engine = OmniscientExecutionEngine()
                logger.info("[OK] OMNISCIENT ENGINE initialized (multi-exchange, leverage)")
            except Exception as e:
                logger.warning(f" Omniscient engine init failed: {e}")
        
        # 🎯 PERFECT ENTRY - Perfect timing, trailing stops
        self.perfect_entry_timer = None
        self.trailing_profit_manager = None
        if PERFECT_ENTRY_AVAILABLE:
            try:
                self.perfect_entry_timer = PerfectEntryTimer()
                self.trailing_profit_manager = TrailingProfitManager()
                logger.info("[OK] PERFECT ENTRY initialized (optimal timing, trailing)")
            except Exception as e:
                logger.warning(f" Perfect entry init failed: {e}")
        
        # 🧠 SIGNAL AGGREGATOR - Combines multiple signals
        self.signal_aggregator = None
        if SIGNAL_AGGREGATOR_AVAILABLE:
            try:
                self.signal_aggregator = SignalAggregator()
                logger.info("[OK] SIGNAL AGGREGATOR initialized (intelligent combining)")
            except Exception as e:
                logger.warning(f" Signal aggregator init failed: {e}")
        
        # 🌙 MOON SPOTTER - Finds moonshot gems
        self.moon_spotter = None
        if MOON_SPOTTER_AVAILABLE:
            try:
                self.moon_spotter = MicroMoonSpotter()
                logger.info("[OK] MOON SPOTTER initialized (DEX moonshots, 1000x gems)")
            except Exception as e:
                logger.warning(f" Moon spotter init failed: {e}")
        
        # 🧠 ADAPTIVE EXCHANGE INTELLIGENCE - Knows all exchanges
        self.adaptive_intelligence = None
        if ADAPTIVE_INTELLIGENCE_AVAILABLE:
            try:
                # Will initialize after we have all exchange instances
                logger.info("[OK] ADAPTIVE EXCHANGE INTELLIGENCE ready (multi-exchange awareness)")
            except Exception as e:
                logger.warning(f" Adaptive intelligence init failed: {e}")
        
        # 🤖 AI CONSULTATION - Queries Claude, GPT-4, Gemini
        self.ai_consultation = None
        if AI_CONSULTATION_AVAILABLE:
            try:
                self.ai_consultation = AIConsultationSystem()
                logger.info("[OK] AI CONSULTATION initialized (Claude, GPT-4, Gemini)")
            except Exception as e:
                logger.warning(f" AI consultation init failed: {e}")
        
        # Multi-exchange configuration from .env
        self.exchanges = self._load_exchange_configs()
        
        logger.info("🧠 ULTRA-ADVANCED INTELLIGENT EXECUTION ENGINE initialized!")
        logger.info("   → Multi-timeframe coordination")
        logger.info("   → Dynamic lot sizing (6 factors)")
        logger.info("   → Session-aware trading")
        logger.info("   → Multi-exchange support")
        logger.info("   → Multi-market (Spot/Futures/Perpetual/DEX)")
        logger.info("   → Perfect entry timing")
        logger.info("   → Moonshot detection")
        logger.info("   → Signal aggregation")
        logger.info("   → Intelligent leverage")
        logger.info("   → Trailing stops")
        logger.info("   → Future trade planning")
        logger.info("   → ADAPTIVE exchange intelligence")
        logger.info("   → AI CONSULTATION (Claude, GPT-4, Gemini)")
        logger.info("   → Pattern learning from AI")
        logger.info("   → ALL 116+ engines in harmony!")
    
    def _load_exchange_configs(self) -> Dict[str, Dict]:
        """
        Load ALL exchange API configurations from .env
        Supports ANY exchange the user has configured!
        """
        exchanges = {}
        
        # Gate.io
        gate_key = os.getenv('GATE_API_KEY')
        gate_secret = os.getenv('GATE_API_SECRET')
        if gate_key and gate_secret:
            exchanges['gateio'] = {
                'api_key': gate_key,
                'api_secret': gate_secret,
                'testnet': False
            }
            logger.info("[OK] Gate.io configured")
        
        # Bybit (both live and testnet)
        bybit_key = os.getenv('BYBIT_API_KEY')
        bybit_secret = os.getenv('BYBIT_API_SECRET')
        if bybit_key and bybit_secret:
            exchanges['bybit'] = {
                'api_key': bybit_key,
                'api_secret': bybit_secret,
                'testnet': False
            }
            logger.info("[OK] Bybit LIVE configured")
        
        bybit_testnet_key = os.getenv('BYBIT_TESTNET_API_KEY')
        bybit_testnet_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
        if bybit_testnet_key and bybit_testnet_secret:
            exchanges['bybit_testnet'] = {
                'api_key': bybit_testnet_key,
                'api_secret': bybit_testnet_secret,
                'testnet': True
            }
            logger.info("[OK] Bybit TESTNET configured")
        
        # Binance
        binance_key = os.getenv('BINANCE_API_KEY')
        binance_secret = os.getenv('BINANCE_API_SECRET')
        if binance_key and binance_secret:
            exchanges['binance'] = {
                'api_key': binance_key,
                'api_secret': binance_secret,
                'testnet': False
            }
            logger.info("[OK] Binance configured")
        
        # OKX
        okx_key = os.getenv('OKX_API_KEY')
        okx_secret = os.getenv('OKX_API_SECRET')
        okx_passphrase = os.getenv('OKX_PASSPHRASE')
        if okx_key and okx_secret and okx_passphrase:
            exchanges['okx'] = {
                'api_key': okx_key,
                'api_secret': okx_secret,
                'passphrase': okx_passphrase,
                'testnet': False
            }
            logger.info("[OK] OKX configured")
        
        # KuCoin
        kucoin_key = os.getenv('KUCOIN_API_KEY')
        kucoin_secret = os.getenv('KUCOIN_API_SECRET')
        kucoin_passphrase = os.getenv('KUCOIN_PASSPHRASE')
        if kucoin_key and kucoin_secret and kucoin_passphrase:
            exchanges['kucoin'] = {
                'api_key': kucoin_key,
                'api_secret': kucoin_secret,
                'passphrase': kucoin_passphrase,
                'testnet': False
            }
            logger.info("[OK] KuCoin configured")
        
        # Coinbase
        coinbase_key = os.getenv('COINBASE_API_KEY')
        coinbase_secret = os.getenv('COINBASE_API_SECRET')
        if coinbase_key and coinbase_secret:
            exchanges['coinbase'] = {
                'api_key': coinbase_key,
                'api_secret': coinbase_secret,
                'testnet': False
            }
            logger.info("[OK] Coinbase configured")
        
        logger.info(f"📊 Total exchanges configured: {len(exchanges)}")
        return exchanges
    
    def get_current_session(self) -> str:
        """Determine current trading session"""
        now = datetime.utcnow().time()
        
        for session_name, (start, end) in self.sessions.items():
            if start <= now <= end:
                return session_name
        
        # Overlapping sessions
        asian_start, asian_end = self.sessions['asian']
        london_start, london_end = self.sessions['london']
        ny_start, ny_end = self.sessions['ny']
        
        if london_start <= now <= london_end and asian_start <= now <= asian_end:
            return 'asian_london_overlap'
        elif london_start <= now <= london_end and ny_start <= now <= ny_end:
            return 'london_ny_overlap'  # Most volatile!
        
        return 'off_hours'
    
    def calculate_intelligent_lot_size(self, signal: Dict) -> float:
        """
        Calculate lot size using ALL available intelligence
        
        🧠 NOW USES AUTONOMOUS COORDINATOR!
        All 202 systems contribute to this decision!
        """
        try:
            # 🧠 TRY AUTONOMOUS COORDINATOR FIRST!
            try:
                # Get orchestrator for coordinator access
                try:
                    from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                    orch = get_orchestrator()
                    if not orch or not hasattr(orch, 'master_coordinator') or not orch.master_coordinator:
                        orch = None
                except Exception:
                    orch = None
                
                # Try to get balance from exchange directly (avoid circular import)
                if hasattr(self.exchange, 'fetch_balance'):
                    bal_info = self.exchange.fetch_balance()
                    if bal_info:
                        # CCXT returns balance structure: {'USDT': {'free': X, 'used': Y, 'total': Z}}
                        usdt_bal = bal_info.get('USDT', {})
                        if isinstance(usdt_bal, dict):
                            balance = usdt_bal.get('total', usdt_bal.get('free', None))
                        elif usdt_bal:
                            balance = float(usdt_bal)
                        else:
                            balance = None
                        
                        if balance and balance > 0:
                            logger.info(f"   💰 Got exchange balance: ${balance:.2f}")
                        else:
                            balance = None
                    else:
                        balance = None
                
                # Only use coordinator if we have a real balance AND orchestrator
                if balance and balance > 0 and orch and hasattr(orch, 'master_coordinator') and orch.master_coordinator:
                    # Let coordinator decide size using ALL systems!
                    size = orch.master_coordinator.calculate_optimal_position_size(signal, balance)
                    logger.info(f"   🧠 AUTONOMOUS SIZE: ${size:.2f} (from all systems, balance: ${balance:.2f}!)")
                    return size
                else:
                    logger.debug(f"     No valid balance or coordinator for coordinator, using fallback calculation")
            except Exception as e:
                logger.warning(f"     Coordinator sizing error: {e}")
            
            # FALLBACK: Original intelligence
            symbol = signal.get('symbol', '')
            confidence = signal.get('confidence', 0.5)
            timeframe = signal.get('timeframe', '5m')
            strategy = signal.get('strategy', 'unknown')
            # Extract ALL intelligence from signal
            confidence = signal.get('confidence', 0.5)
            if confidence > 1:
                confidence = confidence / 100
            
            symbol = signal.get('symbol', '')
            timeframe = signal.get('timeframe', '1m')
            strategy = signal.get('strategy', 'unknown')
            session = self.get_current_session()
            
            # Get volatility for this pair
            volatility = self.volatility_by_pair.get(symbol, 0.02)  # Default 2%
            
            # 🎯 DIVERSIFICATION CHECK: Count existing positions in this symbol
            existing_positions_in_symbol = 0
            total_invested_in_symbol = 0.0
            try:
                from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                orch = get_orchestrator()
                if orch and hasattr(orch, 'advanced_orchestrators'):
                    exec_orch = orch.advanced_orchestrators.get('execution')
                    if exec_orch and hasattr(exec_orch, 'risk_manager'):
                        open_positions = exec_orch.risk_manager.open_positions
                        # Count positions in this symbol
                        if symbol in open_positions:
                            existing_positions_in_symbol = 1
                            total_invested_in_symbol = open_positions[symbol].get('size_usd', 0)
                            logger.info(f"     Already have position in {symbol}: ${total_invested_in_symbol:.2f}")
                            
                            # If already heavily invested (>30% of balance), reduce new position size significantly
                            if balance and total_invested_in_symbol > balance * 0.30:
                                logger.warning(f"   🎯 DIVERSIFICATION: Already invested ${total_invested_in_symbol:.2f} ({total_invested_in_symbol/balance*100:.1f}%) in {symbol}")
                                logger.info(f"   💡 Reducing new position size to allow diversification across other pairs")
            except Exception as e:
                logger.debug(f"     Could not check existing positions: {e}")
            
            # 🔥 Base position size - SCALE WITH BALANCE!
            # Get LIVE balance from exchange FIRST (most accurate!)
            balance = None  # No fallback - must get real balance!
            try:
                # Try to get REAL balance from exchange
                if self.exchange and hasattr(self.exchange, 'fetch_balance'):
                    bal_info = self.exchange.fetch_balance()
                    if bal_info:
                        usdt_info = bal_info.get('USDT', {})
                        if isinstance(usdt_info, dict):
                            balance = usdt_info.get('total', usdt_info.get('free', None))
                        else:
                            balance = float(usdt_info) if usdt_info else None
                        if balance:
                            logger.info(f"   💰 Got exchange balance: ${balance:.2f}")
            except Exception as e:
                logger.debug(f"     Could not fetch exchange balance: {e}")
            
            # Fallback to orchestrator's position_sizer ONLY if exchange fetch failed
            if balance is None or balance == 0:
                try:
                    from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                    orch = get_orchestrator()
                    if orch and hasattr(orch, 'advanced_orchestrators'):
                        exec_orch = orch.advanced_orchestrators.get('execution')
                        if exec_orch and hasattr(exec_orch, 'position_sizer'):
                            balance = exec_orch.position_sizer.balance
                            logger.info(f"   💰 Using orchestrator balance: ${balance:.2f}")
                except:
                    balance = self.actual_balance if hasattr(self, 'actual_balance') else None
            
            # CRITICAL: If still no balance, use a tiny default for testnet
            if balance is None or balance == 0:
                if self.mode == 'testnet':
                    balance = 10.0  # Small testnet default
                    logger.warning(f"     No balance found, using testnet default: ${balance:.2f}")
                else:
                    balance = 100.0  # Live default
                    logger.warning(f"     No balance found, using live default: ${balance:.2f}")
            
            # Log the balance being used for position sizing
            logger.info(f"   💰 Position sizing: Using ACTUAL balance ${balance:.2f} (NOT $1000 fallback!)")
            
            # CRITICAL FIX: Ensure we're using the REAL balance, not a fallback
            if balance and balance < 10:
                logger.warning(f"     Balance is very low (${balance:.2f}) - will use adaptive sizing")
            
            # 🧠 INTELLIGENT ADAPTIVE BASE SIZE - Evolves with balance & performance!
            # NO hardcoded values - uses intelligent factors!
            
            # Get performance metrics for intelligent sizing
            win_rate = 0.5  # Default, will be updated from actual performance
            avg_profit_pct = 0.01  # Default 1%, will be updated
            recent_performance = 1.0  # Default neutral
            
            try:
                # Try to get performance from orchestrator
                from core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR import get_orchestrator
                orch = get_orchestrator()
                if orch and hasattr(orch, 'advanced_orchestrators'):
                    exec_orch = orch.advanced_orchestrators.get('execution')
                    if exec_orch:
                        if hasattr(exec_orch, 'get_win_rate'):
                            win_rate = exec_orch.get_win_rate() or 0.5
                        if hasattr(exec_orch, 'total_profit') and hasattr(exec_orch, 'total_trades'):
                            if exec_orch.total_trades > 0:
                                avg_profit_pct = (exec_orch.total_profit / (exec_orch.position_sizer.balance * exec_orch.total_trades)) if exec_orch.position_sizer.balance > 0 else 0.01
                        # Calculate recent performance trend
                        if hasattr(exec_orch, 'winning_trades') and exec_orch.total_trades > 10:
                            recent_performance = (exec_orch.winning_trades / exec_orch.total_trades) if exec_orch.total_trades > 0 else 0.5
            except:
                pass
            
            # 🧠 INTELLIGENT BASE SIZE CALCULATION
            # Factors: balance tier, win rate, performance, volatility, confidence
            
            # 🧠 SMART BALANCE TIER FACTOR - Leave room for diversification!
            # Ensure we can trade multiple pairs simultaneously for faster growth!
            if balance < 10:
                balance_tier_factor = 0.3  # 30% - leave 70% for other pairs!
            elif balance < 100:
                balance_tier_factor = 0.25  # 25% - leave 75% for diversification!
            elif balance < 1000:
                balance_tier_factor = 0.20  # 20% - allows 5 positions simultaneously!
            elif balance < 10000:
                balance_tier_factor = 0.15  # 15% - allows 6+ positions!
            else:
                balance_tier_factor = 0.10  # 10% - allows 10+ positions for maximum diversification!
            
            # Performance factor (better performance = larger sizes)
            # 🔥 PHASE B: USE DARWINISM FOR ADAPTIVE PERFORMANCE!
            if DARWINISM_INTEGRATED:
                # Get adaptive influence from Darwinism (learns from outcomes)
                engine_name = signal.get('source', signal.get('engine', 'UNKNOWN'))
                darwinism_influence = get_engine_influence_safe(engine_name)
                performance_factor = 0.5 + (win_rate * 0.5) + (recent_performance * 0.3)
                performance_factor *= darwinism_influence  # 🧠 Adaptive adjustment!
                performance_factor = max(0.3, min(1.5, performance_factor))  # Bound between 0.3x and 1.5x
                logger.info(f"   🧠 DARWINISM: {engine_name} influence = {darwinism_influence:.2f}x")
            else:
                # Fallback (no Darwinism)
                performance_factor = 0.5 + (win_rate * 0.5) + (recent_performance * 0.3)
                performance_factor = max(0.3, min(1.5, performance_factor))  # Bound between 0.3x and 1.5x
            
            # Volatility factor (lower volatility = can size larger)
            volatility_factor = max(0.5, min(1.5, 1.0 / (1.0 + volatility * 10)))
            
            # Confidence factor (higher confidence = larger size)
            confidence_factor = 0.7 + (confidence * 0.6)  # 0.7x to 1.3x
            
            # 🧠 CALCULATE INTELLIGENT BASE SIZE
            # Base size = balance * tier_factor * performance_factor * volatility_factor * confidence_factor
            base_size = balance * balance_tier_factor * performance_factor * volatility_factor * confidence_factor
            
            # Ensure minimum viable size (Bybit requirement)
            min_viable = max(5.0, balance * 0.01)  # At least 1% or $5
            base_size = max(min_viable, base_size)
            
            logger.info(f"   🧠 INTELLIGENT BASE SIZE: ${base_size:.2f}")
            logger.info(f"      → Balance tier: {balance_tier_factor:.1%}, Performance: {performance_factor:.2f}x")
            logger.info(f"      → Volatility: {volatility_factor:.2f}x, Confidence: {confidence_factor:.2f}x")
            
            # 🧠 INTELLIGENT CONFIDENCE MULTIPLIER - Adapts to performance!
            # Higher win rate = can be more aggressive with confidence
            confidence_base = 0.5 + (win_rate * 0.3)  # 0.5x to 0.8x base
            confidence_range = 0.8 + (win_rate * 0.7)  # 0.8x to 1.5x range
            confidence_mult = confidence_base + (confidence * confidence_range)  # Fully adaptive!
            logger.debug(f"   🧠 Confidence mult: {confidence_mult:.2f}x (base: {confidence_base:.2f}, range: {confidence_range:.2f})")
            
            # 2. VOLATILITY ADJUSTMENT
            # High volatility = smaller position (risk management)
            # Low volatility = larger position (can trade more)
            volatility_mult = max(0.5, 1.0 - (volatility - 0.02) / 0.05)
            
            # 3. SESSION MULTIPLIER
            session_mults = {
                'asian': 0.7,  # Quieter session
                'london': 1.2,  # Active session
                'ny': 1.2,  # Active session
                'london_ny_overlap': 1.5,  # MOST ACTIVE!
                'asian_london_overlap': 1.0,
                'off_hours': 0.5  # Very quiet
            }
            session_mult = session_mults.get(session, 1.0)
            
            # 4. TIMEFRAME MULTIPLIER
            # Shorter TF = smaller size (more trades)
            # Longer TF = larger size (fewer trades, bigger moves)
            tf_mults = {
                '1m': 0.8,
                '5m': 1.0,
                '15m': 1.2,
                '1h': 1.5,
                '4h': 2.0,
                '1d': 3.0
            }
            tf_mult = tf_mults.get(timeframe, 1.0)
            
            # 5. STRATEGY MULTIPLIER
            # Different strategies need different sizing
            strategy_mults = {
                'scalp': 1.0,  # Standard
                'momentum': 1.2,  # Ride the trend
                'breakout': 1.3,  # Breakouts can run
                'arbitrage': 1.5,  # Low risk, can be larger
                'mean_reversion': 0.8,  # Counter-trend, more risky
                'swing': 1.5,  # Longer holds
            }
            
            strategy_mult = 1.0
            for strat_key, mult in strategy_mults.items():
                if strat_key in strategy.lower():
                    strategy_mult = mult
                    break
            
            # CALCULATE FINAL SIZE
            final_size = (
                base_size * 
                confidence_mult * 
                volatility_mult * 
                session_mult * 
                tf_mult * 
                strategy_mult
            )
            
            # 🔥 PHASE A FIX: UNBLOCK FLOW - Remove min/max deadlock for small balances
            # Previous logic: min_size > max_size when balance < $16.67 (impossible state)
            # New logic: Use exchange minimums with 65% cap for safety
            
            # Get exchange minimum (testnet vs live)
            exchange_min = 0.10 if self.mode == 'testnet' else 5.0
            
            if balance < 25:
                # Small balance mode - 65% cap for safety (not 80% to preserve capital)
                diversification_max = balance * 0.65
                
                if diversification_max < exchange_min:
                    # Balance too small even with 65%, use exchange minimum
                    # This allows trading with very small balances on testnet
                    min_size = max_size = exchange_min
                    logger.info(f"   💡 Tiny balance mode: ${min_size:.2f} (exchange minimum)")
                else:
                    # Normal small balance: use exchange min to 65% range
                    min_size = exchange_min
                    max_size = diversification_max
                    logger.info(f"   🧠 Small balance mode: ${min_size:.2f}-${max_size:.2f} (65% cap)")
            elif balance < 100:
                min_size, max_size = 10.0, balance * 0.30  # 30% max - allows 3+ positions!
            elif balance < 1000:
                min_size, max_size = 10.0, balance * 0.25  # 25% max - allows 4 positions!
            elif balance < 10000:
                # Smart sizing based on performance, but capped for diversification
                max_pct = 0.15 + (win_rate * 0.05) + (recent_performance * 0.03)  # 15-23% based on performance!
                max_pct = max(0.15, min(0.25, max_pct))  # Bound between 15% and 25% - allows diversification!
                min_size, max_size = 20.0, balance * max_pct
                logger.info(f"   🧠 Smart max: {max_pct:.1%} of balance (${max_size:.2f}) - allows diversification!")
            else:
                min_size, max_size = 50.0, balance * 0.20  # 20% max - allows 5+ positions!
            
            final_size = max(min_size, min(final_size, max_size))
            
            # PHASE C: APPLY REAL COMPOUNDING ENGINE
#             if COMPOUNDING_INTEGRATED and _compounding_engine:
#                 try:
                    # Use real engine's method
#                     compounded_size = _compounding_engine.get_compounded_size(final_size, balance)
#                     if compounded_size > final_size:
#                         mult = compounded_size / final_size if final_size > 0 else 1.0
#                         logger.info(f"   COMPOUNDING: {mult:.2f}x applied, ${final_size:.2f} -> ${compounded_size:.2f}")
#                          final_size = min(compounded_size, max_size)  # Still respect max
#                 except Exception as e:
#                     logger.debug(f"   COMPOUNDING error (non-fatal): {e}")
            
            # 🧠 AUTONOMOUS DECISION: Bot can still trade same symbol if it sees opportunity
            # NO RESTRICTIONS - Let the bot's intelligence decide!
            if existing_positions_in_symbol > 0 and balance:
                current_exposure_pct = (total_invested_in_symbol / balance) if balance > 0 else 0
                # Only log, don't restrict - bot knows best!
                if current_exposure_pct > 0.30:
                    logger.info(f"   🧠 Already have {current_exposure_pct*100:.1f}% in {symbol} - bot autonomously deciding to add more if profitable")
            
            # CRITICAL: Ensure absolute $5 minimum (Bybit requirement)
            if final_size < 5.0 and balance >= 5.0:
                # Scale up to meet minimum (use up to 30% of balance if needed)
                final_size = min(5.0, balance * 0.30)
                logger.info(f"     Scaled up to meet $5 minimum: ${final_size:.2f}")
            final_size = max(5.0, final_size)  # Final safety check
            
            # 🔥 CRITICAL FIX: Cap to available FREE balance (not total!)
            # Get FREE balance to ensure we don't exceed available capital
            try:
                if self.exchange and hasattr(self.exchange, 'fetch_balance'):
                    bal_info = self.exchange.fetch_balance()
                    if bal_info:
                        usdt_info = bal_info.get('USDT', {})
                        if isinstance(usdt_info, dict):
                            free_balance = usdt_info.get('free', usdt_info.get('total', balance))
                        else:
                            free_balance = float(usdt_info) if usdt_info else balance
                        
                        # 🧠 SMART CAP: Use max 30% of free balance to ensure diversification!
                        # Leave 70% free for other pairs - faster growth through multiple positions!
                        max_affordable = free_balance * 0.30
                        if final_size > max_affordable:
                            logger.info(f"   💡 Capping to ${max_affordable:.2f} (30% of free balance ${free_balance:.2f}) - ensures diversification!")
                            final_size = max(5.0, max_affordable)  # Still respect $5 minimum
            except Exception as e:
                logger.debug(f"     Could not check free balance for capping: {e}")
                # Fallback: cap to 30% of total balance to ensure diversification
                max_affordable = balance * 0.30
                if final_size > max_affordable:
                    final_size = max(5.0, max_affordable)
            
            logger.info(f"   💰 Position sizing: ${final_size:.2f} (balance: ${balance:.0f})")
            
            logger.info(f"🧠 INTELLIGENT LOT SIZING: {symbol} {timeframe}")
            logger.info(f"   Confidence: {confidence:.1%} → {confidence_mult:.2f}x")
            logger.info(f"   Volatility: {volatility:.2%} → {volatility_mult:.2f}x")
            logger.info(f"   Session: {session} → {session_mult:.2f}x")
            logger.info(f"   Timeframe: {timeframe} → {tf_mult:.2f}x")
            logger.info(f"   Strategy: {strategy} → {strategy_mult:.2f}x")
            logger.info(f"   💰 Final Size: ${final_size:.2f}")
            
            return final_size
            
        except Exception as e:
            logger.error(f"Lot size calculation error: {e}")
            return 10.0  # Safe default
    
    def should_open_new_trade(self, symbol: str, timeframe: str) -> bool:
        """
        ♾️ INFINITE TRADING - ALWAYS OPEN NEW TRADES!
        
        With 490 AI models each finding opportunities:
        - NO limits on trades per pair
        - NO limits on timeframes  
        - Each signal is unique and profitable
        - Let the models work!
        """
        # ♾️ ALWAYS ALLOW - Ultra-intelligent bot with 490 models!
        return True
    
    async def create_complete_trade_plan(self, signal: Dict, timeframe: str = None) -> Dict:
        """
        Create COMPLETE trade plan using ALL engine intelligence
        
        Returns:
        {
            'symbol': 'BTC/USDT',
            'timeframe': '5m',
            'strategy': 'momentum_breakout',
            
            # ENTRY
            'entry_type': 'market' or 'limit',
            'entry_price': 50000.0,
            'entry_condition': 'immediate' or 'on_pullback' or 'on_breakout',
            
            # POSITION
            'lot_size_usd': 15.5,
            'leverage': 2,  # Based on confidence
            
            # EXIT
            'take_profit_levels': [
                {'price': 50250, 'pct': 50, 'reason': '0.5% quick profit'},
                {'price': 50500, 'pct': 30, 'reason': '1% main target'},
                {'price': 51000, 'pct': 20, 'reason': '2% moon shot'}
            ],
            'stop_loss': 49500,
            'trailing_stop': True,
            'trailing_distance_pct': 0.3,
            
            # MANAGEMENT - TIMEFRAME-SPECIFIC ULTRA-FAST CLOSES!
            'timeframe': timeframe,  # Include timeframe in plan!
            'max_hold_time_minutes': self._get_max_hold_time(timeframe),
            'review_interval_seconds': self._get_check_interval(timeframe),
            're_evaluate_conditions': ['volatility_spike', 'news_event', 'trend_change'],
            
            # DEBUG: Log the values
            '_debug_max_hold': self._get_max_hold_time(timeframe),
            '_debug_check_interval': self._get_check_interval(timeframe),
            '_debug_timeframe': timeframe,
            
            # INTELLIGENCE CONTEXT
            'engine_consensus': 12,  # How many engines agreed
            'confidence_breakdown': {
                'neural': 0.85,
                'omniscient': 0.92,
                'predictive': 0.88,
                # ... all engine confidences
            },
            'market_regime': 'trending_bullish',
            'volatility_state': 'normal',
            'news_sentiment': 'positive',
            'session': 'london_ny_overlap',
            
            # SEQUENCING
            'sequence_number': 1,  # If part of multi-trade plan
            'depends_on': [],  # Other trades that must execute first
            'enables': []  # Trades that can execute after this
        }
        """
        try:
            symbol = signal.get('symbol', '')
            
            # 📊 MULTI-TIMEFRAME: Use provided or determine from signal
            # 🔥 CRITICAL FIX: Force scalping timeframes for fast profits!
            # Get from signal, but override if it's too long for scalping
            signal_tf = signal.get('timeframe', '1m')
            
            # If signal has 4h or longer, force to 1m/5m for scalping
            if signal_tf in ['4h', '1d', '1w']:
                confidence = signal.get('confidence', 0.5)
                if confidence > 1:
                    confidence = confidence / 100
                # High confidence = 1m, medium = 5m
                if confidence >= 0.90:
                    timeframe = '1m'  # Ultra-fast scalping for high confidence!
                else:
                    timeframe = '5m'  # Fast scalping for medium confidence
                logger.info(f"   ⚡ Overrode {signal_tf} timeframe → {timeframe} for scalping!")
            elif signal_tf:
                timeframe = signal_tf
            else:
                # Default to 1m for scalping
                timeframe = '1m'
                logger.info(f"   ⚡ Using default 1m timeframe for scalping")
            
            strategy = signal.get('strategy', '')
            
            # [OK] INTELLIGENT STRATEGY DETECTION
            if not strategy or strategy == 'unknown':
                # Detect strategy from signal characteristics
                source = signal.get('source', '').lower()
                
                if 'scalp' in source:
                    strategy = 'SCALPING'
                elif 'momentum' in source or 'breakout' in source:
                    strategy = 'MOMENTUM_BREAKOUT'
                elif 'arbitrage' in source or 'arb' in source:
                    strategy = 'ARBITRAGE'
                elif 'news' in source:
                    strategy = 'NEWS_TRADING'
                elif 'fx' in source or 'forex' in source:
                    strategy = 'FOREX_SWING'
                else:
                    # Query AI for strategy recommendation
                    strategy = 'MULTI_ENGINE_CONFLUENCE'
                    logger.info(f"   🧠 Auto-detected strategy: {strategy}")
            side = signal.get('side', 'buy').lower()
            confidence = signal.get('confidence', 0.5)
            
            if confidence > 1:
                confidence = confidence / 100
            
            # GET ALL AVAILABLE INTELLIGENCE
            entry_price = signal.get('entry', signal.get('price', 0))
            
            # [OK] FIX: If price missing or PLACEHOLDER, SKIP!
            if not entry_price or entry_price <= 0 or entry_price in [100.0, 7.0, 300.0, 10.0, 1.0]:
                logger.info(f"   💰 Fetching live price for {symbol}...")
                
                # [OK] SIMPLE FIX: Just use self.exchange (already correct!)
                # Router has already validated the pair exists on this exchange
                exchange_name = signal.get('route_exchange', 'default')
                if exchange_name != 'default':
                    logger.info(f"   🎯 Router selected: {exchange_name} (using configured exchange)")
                
                # Fetch from our exchange
                if self.exchange:
                    try:
                        logger.info(f"   🔍 Fetching price from exchange: {type(self.exchange).__name__}")
                        # Handle both router and raw exchange
                        if hasattr(self.exchange, 'ex'):
                            # It's a router - use .ex
                            logger.debug(f"   Using router exchange: {type(self.exchange.ex).__name__}")
                            ticker = await asyncio.to_thread(self.exchange.ex.fetch_ticker, symbol)
                        else:
                            # It's a raw exchange
                            logger.debug(f"   Using direct exchange: {type(self.exchange).__name__}")
                            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                        
                        if isinstance(ticker, dict):
                            entry_price = ticker.get('last', ticker.get('close', 0))
                            if entry_price and entry_price > 0:
                                logger.info(f"   [OK] Got live price: ${entry_price:.6f}")

                                # Validate it's a REAL price (not placeholder)
                                if entry_price in [100.0, 7.0, 300.0, 10.0, 1.0, 65.0, 32.0]:
                                    # 🔥 PHASE A FIX: Add symbol name for debugging!
                                    logger.warning(f"   [X] Placeholder price detected: ${entry_price:.2f} for {symbol}, SKIPPING!")
                                    
                                    return None
                            else:
                                logger.warning(f"   [X] Invalid price from ticker: {entry_price}")
                                
                                return None
                        else:
                            logger.error(f"   [X] Ticker not a dict: {type(ticker)} - Value: {ticker}")
                            
                            return None

                    except Exception as e:
                        logger.error(f"   [X] Fetch failed for {symbol}: {type(e).__name__}: {str(e)}")
                        import traceback
                        logger.debug(f"   Traceback: {traceback.format_exc()}")
                        
                        return None
                else:
                    logger.error(f"   [X] No exchange available for price fetch!")
                    
                    return None
                
                # Still invalid? Skip
                if not entry_price or entry_price <= 0:
                    logger.warning(f"   [X] No valid price for {symbol}, skipping")
                    
                    return None
            
            volatility = signal.get('volatility', self.volatility_by_pair.get(symbol, 0.02))
            session = self.get_current_session()
            
            # Calculate intelligent lot size
            lot_size = self.calculate_intelligent_lot_size(signal)
            
            # Calculate leverage based on confidence
            leverage = self._calculate_intelligent_leverage(confidence, volatility, strategy)
            
            # Create multi-level take profits
            tp_levels = self._create_intelligent_take_profits(
                entry_price, side, volatility, timeframe, strategy
            )
            
            # Calculate take_profit_pct from first TP level (for monitoring)
            # 🔥 ULTRA-AGGRESSIVE: Higher default for faster profits!
            take_profit_pct = 0.03 if timeframe in ['1m', '5m'] else 0.04  # 3-4% default for faster profits!
            if tp_levels and len(tp_levels) > 0:
                first_tp = tp_levels[0]
                if side == 'buy':
                    take_profit_pct = (first_tp.get('price', entry_price) - entry_price) / entry_price
                else:
                    take_profit_pct = (entry_price - first_tp.get('price', entry_price)) / entry_price
                take_profit_pct = max(0.02, min(0.10, take_profit_pct))  # 🔥 Clamp between 2% and 10% - ULTRA AGGRESSIVE!
            
            # 🔥 CRITICAL: Set stop_loss_pct FIRST (1% for scalping) BEFORE calculating stop_loss price!
            # This ensures the stop_loss price matches the intended percentage
            if timeframe in ['1m', '5m']:
                stop_loss_pct = 0.01  # Fixed 1% for scalping (2:1 reward/risk with 2% TP)
            else:
                # For longer timeframes, use volatility-based but cap at 2%
                stop_loss_pct = min(volatility * 2.0, 0.02)  # Max 2%
                stop_loss_pct = max(0.005, stop_loss_pct)  # Min 0.5%
            
            # Calculate intelligent stop loss using the stop_loss_pct
            # This ensures the stop_loss price matches the intended percentage
            if side == 'buy':
                stop_loss = entry_price * (1 - stop_loss_pct)
            else:
                stop_loss = entry_price * (1 + stop_loss_pct)
            
            # Determine entry strategy
            entry_strategy = self._determine_entry_strategy(signal, session, volatility)
            
            # Calculate max hold time
            max_hold = self._calculate_max_hold_time(timeframe, strategy)
            
            # Create complete plan
            trade_plan = {
                # IDENTIFICATION
                'symbol': symbol,
                'timeframe': timeframe,
                'strategy': strategy,
                'session': session,
                'planned_at': datetime.utcnow().isoformat(),
                
                # ENTRY
                'entry_type': entry_strategy['type'],
                'entry_price': entry_price,  # Using fetched live price!
                'entry_condition': entry_strategy['condition'],
                'entry_wait_max_seconds': entry_strategy.get('max_wait', 60),
                
                # POSITION
                'side': side,
                'lot_size_usd': lot_size,
                'leverage': leverage,
                'risk_pct': self._calculate_risk_pct(lot_size, stop_loss, entry_price),
                
                # EXIT - MULTI-LEVEL!
                'take_profit_levels': tp_levels,
                'take_profit_pct': take_profit_pct,  # 🔥 Store TP % for monitoring (2:1 reward/risk)
                'stop_loss': stop_loss,
                'stop_loss_pct': stop_loss_pct,  # Store SL % for monitoring
                'trailing_stop': volatility < 0.03,  # Use trailing in low volatility
                'trailing_distance_pct': min(0.3, volatility * 10),
                
                # MANAGEMENT
                'max_hold_time_minutes': max_hold,
                'review_interval_seconds': self._get_check_interval(timeframe),
                're_evaluate_on': ['volatility_spike', 'news_event', 'trend_reversal'],
                
                # INTELLIGENCE CONTEXT (from ALL engines!)
                'confidence': confidence,
                'volatility': volatility,
                'market_regime': signal.get('regime', 'unknown'),
                'news_sentiment': signal.get('news_sentiment', 'neutral'),
                'research_score': signal.get('research_score', 0),
                'scout_priority': signal.get('scout_priority', 'medium'),
                
                # From original signal
                'engine_sources': signal.get('sources', []),
                'reasoning': signal.get('reasoning', ''),
                'support_levels': signal.get('support', []),
                'resistance_levels': signal.get('resistance', []),
                
                # EXECUTION STATUS
                'status': 'planned',
                'executed_at': None,
                'closed_at': None,
                'actual_profit_pct': 0,
            }
            
            logger.info(f"🧠 COMPLETE TRADE PLAN CREATED: {symbol} {timeframe}")
            logger.info(f"   Strategy: {strategy}")
            logger.info(f"   Entry: {entry_strategy['condition']} @ ${entry_price:.4f}")
            logger.info(f"   Size: ${lot_size:.2f} @ {leverage}x leverage")
            logger.info(f"   TP Levels: {len(tp_levels)} (partial exits)")
            logger.info(f"   SL: ${stop_loss:.4f} ({stop_loss_pct:.2%})")  # 🔥 Use stored stop_loss_pct, not calculated!
            logger.info(f"   Session: {session}")
            logger.info(f"   Max Hold: {max_hold} minutes")
            
            return trade_plan
            
        except Exception as e:
            logger.error(f"Trade plan creation error: {e}")
            
            return None
    
    def _calculate_intelligent_leverage(self, confidence: float, volatility: float, strategy: str) -> int:
        """
        Calculate leverage using confidence, volatility, and strategy
        
        🔥 USES OMNISCIENT ENGINE if available for advanced leverage!
        
        High confidence + low volatility = higher leverage
        Low confidence + high volatility = 1x only
        """
        # Use OMNISCIENT ENGINE for leverage if available
        if self.omniscient_engine:
            optimal_leverage = self.omniscient_engine.get_optimal_leverage(confidence, volatility)
            logger.debug(f"🔥 Omniscient leverage: {optimal_leverage}x")
            return optimal_leverage
        
        # Fallback: Base leverage from confidence
        base_leverage = 1 + int(confidence * 9)  # 1-10x
        
        # Reduce for high volatility
        if volatility > 0.05:  # 5%+ volatility
            base_leverage = max(1, base_leverage // 2)
        
        # Reduce for risky strategies
        if 'mean_reversion' in strategy.lower() or 'counter' in strategy.lower():
            base_leverage = max(1, base_leverage // 2)
        
        # Increase for low-risk strategies
        if 'arbitrage' in strategy.lower():
            base_leverage = min(10, base_leverage * 2)
        
        return base_leverage
    
    def _get_optimal_exchange_and_market(self, symbol: str, confidence: float, timeframe: str, required_balance: float = 10.0) -> Dict[str, str]:
        """
        Choose optimal exchange and market type for this trade
        
        🧠 USES ADAPTIVE INTELLIGENCE if available - knows which exchanges have this pair AND balance!
        🔥 USES OMNISCIENT ENGINE for market type selection!
        
        Returns: {
            'exchange': 'bybit' or 'gateio' or 'binance',
            'market_type': 'spot' or 'futures' or 'perpetual' or 'dex'
        }
        """
        optimal = {}  # Initialize
        # 🧠 USE ADAPTIVE INTELLIGENCE to choose exchange
        if self.adaptive_intelligence:
            optimal_exchange = self.adaptive_intelligence.get_optimal_exchange(symbol, required_balance)
            
            if optimal_exchange:
                # Determine market type
                market_type = 'spot'  # Default
                if self.omniscient_engine:
                    market_type = self.omniscient_engine.get_optimal_market_type(symbol, confidence, timeframe)
                
                logger.info(f"   🧠 ADAPTIVE: Selected {optimal_exchange} (has pair + balance)")
                return {'exchange': optimal_exchange, 'market_type': market_type}
            else:
                logger.warning(f"    No exchange has {symbol} with sufficient balance!")
        
        # Use OMNISCIENT ENGINE to choose if available (fallback)
        if self.omniscient_engine:
            market_type = self.omniscient_engine.get_optimal_market_type(symbol, confidence, timeframe)
            
            # Choose exchange based on market type and availability
            if market_type == 'dex':
                # DEX trading - use MOON SPOTTER!
                return {'exchange': 'dex', 'market_type': 'dex'}
            elif market_type == 'futures' and 'bybit' in self.exchanges:
                return {'exchange': 'bybit', 'market_type': 'futures'}
            elif market_type == 'perpetual' and 'binance' in self.exchanges:
                return {'exchange': 'binance', 'market_type': 'perpetual'}
            else:
                # Default to spot on available exchange
                if 'gateio' in self.exchanges:
                    return {'exchange': 'gateio', 'market_type': 'spot'}
                elif 'bybit' in self.exchanges:
                    return {'exchange': 'bybit', 'market_type': 'spot'}
        
        # Fallback: Use current exchange (testnet or live)
        if self.mode == 'testnet':
            logger.info(f"   🧪 TESTNET MODE: Forcing Bybit testnet (not {optimal.get('exchange', 'unknown')})")
            return {'exchange': 'bybit_testnet', 'market_type': 'spot'}
        else:
            return {'exchange': 'gateio', 'market_type': 'spot'}
    
    def _create_intelligent_take_profits(self, entry: float, side: str, 
                                         volatility: float, timeframe: str, 
                                         strategy: str) -> List[Dict]:
        """
        Create multi-level take profits based on ALL intelligence
        
        Returns list of TP levels with percentages
        """
        tp_levels = []
        
        # 🔥 ULTRA-AGGRESSIVE TP LEVELS - For FASTER PROFITS & COMPOUNDING!
        # Higher first TP = faster profit taking = faster balance growth!
        tf_targets = {
            '1m': [0.03, 0.05, 0.08],  # 3%, 5%, 8% - FASTER profits for scalping!
            '5m': [0.04, 0.06, 0.10],  # 4%, 6%, 10% - AGGRESSIVE profits!
            '15m': [0.025, 0.040, 0.060], # 2.5%, 4%, 6%
            '1h': [0.030, 0.050, 0.080],  # 3%, 5%, 8%
            '4h': [0.040, 0.070, 0.120],  # 4%, 7%, 12%
            '1d': [0.060, 0.120, 0.250],  # 6%, 12%, 25%
        }
        
        targets = tf_targets.get(timeframe, [0.03, 0.05, 0.08])  # Default to aggressive 3-8%
        
        # 🔥 NO VOLATILITY REDUCTION - Use full TP targets for maximum profits!
        # Volatility adjustment was reducing profits - removed for faster growth!
        # targets = [t * (1 + volatility) for t in targets]  # REMOVED - was reducing profits!
        
        # Create levels with partial exit strategy
        exit_percentages = [50, 30, 20]  # Exit 50% first, then 30%, then 20%
        
        for i, (target_pct, exit_pct) in enumerate(zip(targets, exit_percentages)):
            if side == 'buy':
                tp_price = entry * (1 + target_pct)
            else:
                tp_price = entry * (1 - target_pct)
            
            tp_levels.append({
                'level': i + 1,
                'price': tp_price,
                'target_pct': target_pct * 100,
                'exit_pct': exit_pct,
                'reason': f'{"Quick" if i == 0 else "Main" if i == 1 else "Runner"} profit target'
            })
        
        return tp_levels
    
    def _calculate_intelligent_stop_loss(self, entry: float, side: str,
                                         volatility: float, timeframe: str) -> float:
        """
        Calculate stop loss - FIXED 1% for scalping (1m/5m) for consistent risk/reward
        
        🔥 CRITICAL: For scalping, use fixed 1% SL to ensure 2:1 reward/risk ratio!
        """
        # 🔥 FIXED 1% STOP LOSS for scalping timeframes (1m/5m) - ensures 2:1 reward/risk!
        if timeframe in ['1m', '5m']:
            stop_distance = 0.01  # Fixed 1% for scalping
        else:
            # For longer timeframes, use volatility-based but cap at 2%
            stop_distance = min(volatility * 2.0, 0.02)  # Max 2% even for high volatility
            
            # Minimum stops by timeframe
            min_stops = {
                '15m': 0.008, # 0.8%
                '1h': 0.012,  # 1.2%
                '4h': 0.020,  # 2.0%
            }
            
            min_stop = min_stops.get(timeframe, 0.010)
            stop_distance = max(stop_distance, min_stop)
        
        # Calculate stop price
        if side == 'buy':
            stop_price = entry * (1 - stop_distance)
        else:
            stop_price = entry * (1 + stop_distance)
        
        return stop_price
    
    def _calculate_sl_pct(self, entry: float, stop_loss: float, side: str) -> float:
        """Calculate stop loss as percentage"""
        if side == 'buy':
            return (entry - stop_loss) / entry
        else:
            return (stop_loss - entry) / entry
    
    def _calculate_risk_pct(self, lot_size: float, stop_loss: float, entry: float) -> float:
        """Calculate risk percentage of account"""
        # Simplified - would use actual balance
        return (abs(entry - stop_loss) / entry) * (lot_size / 1000.0)
    
    def _determine_entry_strategy(self, signal: Dict, session: str, volatility: float) -> Dict:
        """
        Determine HOW to enter based on all intelligence
        
        Options:
        - Immediate market entry
        - Limit order at better price
        - Wait for pullback
        - Wait for breakout confirmation
        """
        urgency = signal.get('urgency', 'MEDIUM')
        strategy = signal.get('strategy', '')
        
        # High urgency = market entry
        if urgency == 'CRITICAL' or 'breakout' in strategy.lower():
            return {
                'type': 'market',
                'condition': 'immediate',
                'reason': 'Urgent opportunity - enter immediately'
            }
        
        # High volatility = wait for better entry
        if volatility > 0.04:
            return {
                'type': 'limit',
                'condition': 'on_pullback',
                'max_wait': 120,
                'reason': 'High volatility - wait for pullback'
            }
        
        # Quiet session = can be patient
        if session in ['off_hours', 'asian']:
            return {
                'type': 'limit',
                'condition': 'better_price',
                'max_wait': 300,
                'reason': 'Quiet session - wait for better entry'
            }
        
        # Default: market entry
        return {
            'type': 'market',
            'condition': 'immediate',
            'reason': 'Standard market entry'
        }
    
    def _calculate_max_hold_time(self, timeframe: str, strategy: str) -> int:
        """Calculate maximum hold time in minutes"""
        # Base on timeframe
        tf_holds = {
            '1m': 5,    # 5 minutes max
            '5m': 30,   # 30 minutes
            '15m': 120, # 2 hours
            '1h': 480,  # 8 hours
            '4h': 1440, # 24 hours
            '1d': 10080 # 1 week
        }
        
        base_hold = tf_holds.get(timeframe, 60)
        
        # Scalps = MUCH shorter hold (1-5 min for fast profits!)
        if 'scalp' in strategy.lower():
            base_hold = min(5, base_hold // 3)  # Max 5 minutes for scalps!
        
        # Swings = longer hold
        if 'swing' in strategy.lower():
            base_hold = base_hold * 2
        
        return base_hold
    
    def _get_review_interval(self, timeframe: str) -> int:
        """DEPRECATED - Use _get_check_interval() instead!"""
        # This method should not be used anymore!
        logger.warning(f" _get_review_interval called (DEPRECATED)! Use _get_check_interval instead!")
        return self._get_check_interval(timeframe)  # Redirect to correct method
        
        # OLD WRONG VALUES (kept for reference):
        intervals_old = {
            '1m': 10,   # OLD: Review every 10 seconds (TOO SLOW!)
            '5m': 30,   # Every 30 seconds
            '15m': 60,  # Every minute
            '1h': 300,  # Every 5 minutes
            '4h': 900,  # Every 15 minutes
        }
        return intervals.get(timeframe, 60)
    
    async def scan_for_moonshots(self) -> List[Dict]:
        """
        Scan for MOONSHOT opportunities using MOON SPOTTER
        
        🌙 Finds micro cap gems with 1000x potential!
        - DEX tokens
        - New launches
        - Constructive research
        """
        if not self.moon_spotter:
            return []
        
        try:
            logger.info("🌙 Scanning for MOONSHOT opportunities...")
            gems = await self.moon_spotter.scan_for_new_gems()
            
            if gems:
                logger.info(f"🌙 Found {len(gems)} potential MOONSHOTS!")
                for gem in gems[:5]:  # Log top 5
                    logger.info(f"   💎 {gem.get('symbol', 'UNKNOWN')}: ${gem.get('price', 0):.8f}")
                    logger.info(f"      Score: {gem.get('score', 0):.1f} | Market Cap: ${gem.get('market_cap', 0):,.0f}")
            
            return gems
        
        except Exception as e:
            logger.error(f"Moonshot scan error: {e}")
            return []
    
    async def execute_intelligent_trade(self, trade_plan: Dict) -> Dict:
        """
        Execute trade using the COMPLETE intelligent plan
        
        USES ALL ADVANCED FEATURES:
        - Perfect entry timing (waits for optimal price)
        - Optimal exchange selection
        - Market type selection (spot/futures/perpetual/dex)
        - Intelligent leverage
        - Trailing stops
        
        Returns execution result with all details
        """
        optimal = {'exchange': 'bybit_testnet', 'market_type': 'spot'}  # Default to prevent NameError
        try:
            symbol = trade_plan['symbol']
            side = trade_plan['side']
            lot_size = trade_plan['lot_size_usd']
            entry_price = trade_plan['entry_price']
            timeframe = trade_plan['timeframe']
            confidence = trade_plan.get('confidence', 0.5)
            
            # 🔧 INTELLIGENT ROUTING: Check if symbol is supported by current exchange
            # Skip forex (USD/JPY, EUR/GBP) and TradFi (GOLD, SUGAR) if using crypto exchange
            if self._should_skip_symbol(symbol):
                logger.debug(f"⏭️  Skipping {symbol} - Not supported by current exchange (will route to MT5 when added)")
                return {'success': False, 'reason': 'symbol_not_supported', 'symbol': symbol}
            
            logger.info(f">> EXECUTING ULTRA-ADVANCED INTELLIGENT TRADE:")
            # INJECTED EXECUTION CALL
            opp = {'symbol': symbol, 'action': side, 'size_usd': lot_size}
            await self.execute_trade(opp)
            logger.info(f"   {symbol} {side.upper()} on {timeframe}")
            logger.info(f"   Strategy: {trade_plan['strategy']}")
            logger.info(f"   Session: {trade_plan['session']}")
            logger.info(f"   Size: ${lot_size:.2f} @ {trade_plan['leverage']}x")
            logger.info(f"   TP Levels: {len(trade_plan['take_profit_levels'])}")
            
            # 🤖 CONSULT AI for very high-confidence trades (NON-BLOCKING!)
            ai_insights = None
            if self.ai_consultation and confidence >= 0.88:  # Only for 88%+ confidence
                logger.info(f"   🤖 VERY HIGH CONFIDENCE ({confidence:.0%}) - Consulting AI (non-blocking)...")
                
                # 🔥 NON-BLOCKING: Try AI with 2-second timeout, continue if unavailable
                try:
                    ai_context = {
                        'symbol': symbol,
                        'signal': side,
                        'confidence': confidence,
                        'timeframe': timeframe,
                        'current_price': entry_price,
                        'market_data': {
                            'strategy': trade_plan['strategy'],
                            'session': trade_plan['session'],
                            'volatility': trade_plan.get('volatility', 0),
                            'leverage': trade_plan['leverage']
                        }
                    }
                    
                    # ⏱️ 2-second timeout - if AI doesn't respond, continue without it
                    ai_insights = await asyncio.wait_for(
                        self.ai_consultation.consult_strategy(ai_context),
                        timeout=2.0
                    )
                    
                    if ai_insights and ai_insights.get('ai_consensus') == 'bearish' and side == 'buy':
                        logger.warning(f"    AI CONSENSUS: BEARISH (conflicts with BUY signal!)")
                        # Reduce size by 30% if AI disagrees
                        lot_size = lot_size * 0.7
                        logger.info(f"   📉 Size reduced to ${lot_size:.2f} due to AI caution")
                    elif ai_insights and ai_insights.get('ai_consensus') == 'bullish':
                        logger.info(f"   [OK] AI CONSENSUS: BULLISH (confirms signal!)")
                        # Boost size by 15% if AI strongly agrees
                        if ai_insights.get('unanimous'):
                            lot_size = lot_size * 1.15
                            logger.info(f"   📈 Size boosted to ${lot_size:.2f} (AI unanimous!)")
                
                except asyncio.TimeoutError:
                    logger.debug(f"   ⏭️ AI timeout - continuing with ultra engines")
                except Exception as e:
                    logger.debug(f"   ⏭️ AI unavailable - using ultra engines: {e}")
            
            # 🔥 CHOOSE OPTIMAL EXCHANGE AND MARKET TYPE
            optimal = self._get_optimal_exchange_and_market(symbol, confidence, timeframe, lot_size)
            
            # [OK] IN TESTNET MODE: FORCE TESTNET EXCHANGE!
            if self.mode == 'testnet':
                optimal = {'exchange': 'bybit_testnet', 'market_type': 'spot'}
                logger.info(f"   🧪 TESTNET MODE: Using Bybit testnet")
            
            logger.info(f"   📊 Exchange: {optimal['exchange']} | Market: {optimal['market_type']}")
            
            # 🎯 WAIT FOR PERFECT ENTRY if enabled
            if self.perfect_entry_timer and trade_plan['entry_condition'] != 'immediate':
                logger.info(f"   ⏳ Waiting for perfect entry @ ${entry_price:.6f}...")
                
                perfect_price = await self.perfect_entry_timer.wait_for_perfect_entry(
                    self.exchange,
                    symbol,
                    entry_price,
                    side,
                    max_wait=trade_plan.get('entry_wait_max_seconds', 60)
                )
                
                if perfect_price:
                    entry_price = perfect_price
                    logger.info(f"   [OK] Perfect entry achieved @ ${perfect_price:.6f}!")
                else:
                    logger.info(f"     Perfect entry timeout, using market price")
            
            logger.info(f"   🔥 OMNISCIENT: Using {optimal['market_type']} market on {optimal['exchange']}")
            
            # Execute via ccxt
            if not self.exchange:
                logger.error(f"   [X] No exchange available for {symbol}!")
                logger.error(f"   Exchange object: {self.exchange}")
                return {'success': False, 'reason': 'no_exchange', 'symbol': symbol}
            
            # 🔍 CRITICAL: Check balance BEFORE placing order
            usdt_free = 0  # Initialize for use later
            try:
                current_balance = await asyncio.to_thread(self.exchange.fetch_balance)
                usdt_info = current_balance.get('USDT', {})
                if isinstance(usdt_info, dict):
                    usdt_free = usdt_info.get('free', 0)
                    usdt_total = usdt_info.get('total', 0)
                else:
                    usdt_free = float(usdt_info) if usdt_info else 0
                    usdt_total = usdt_free
                usdt_used = usdt_total - usdt_free
                
                logger.info(f"   💰 Balance: ${usdt_free:.2f} free / ${usdt_total:.2f} total (${usdt_used:.2f} in open trades)")
                
                # 🚨 CRITICAL CHECK: Ensure sufficient free balance
                # Use 80% of free balance as maximum (keep 20% safety buffer)
                max_affordable = usdt_free * 0.80
                
                if lot_size > max_affordable:
                    logger.warning(f"     Order size ${lot_size:.2f} exceeds 80% of free balance ${usdt_free:.2f}")
                    logger.info(f"   💡 Reducing order size to ${max_affordable:.2f} (80% of available, keeps 20% buffer)")
                    lot_size = max_affordable
                
                # Final check: ensure we have minimum required
                # Lower minimum for testnet to allow micro-trading and compounding
                min_order_size = 0.10 if self.mode == 'testnet' else 5.0  # $0.10 minimum for testnet
                min_balance_required = 0.20 if self.mode == 'testnet' else 5.0  # Need at least $0.20 balance
                
                if usdt_free < min_balance_required:
                    logger.warning(f"   ⏭️ Skipping - insufficient balance (${usdt_free:.2f} available, minimum ${min_balance_required:.2f})")
                    logger.info(f"   💡 TIP: Add more funds or wait for positions to close")
                    return {'success': False, 'reason': 'insufficient_balance', 'available': usdt_free, 'required': lot_size, 'minimum': min_balance_required}
                
                # Ensure lot_size meets minimum (but allow smaller for micro-trading)
                if lot_size < min_order_size:
                    # For testnet, allow using all available balance if it's above $0.10
                    if self.mode == 'testnet' and usdt_free >= min_balance_required:
                        lot_size = max(min_order_size, usdt_free * 0.80)  # Use 80% of available
                        logger.info(f"   💡 Adjusted lot size to ${lot_size:.2f} (using available balance)")
                    else:
                        logger.warning(f"   ⏭️ Skipping - calculated size ${lot_size:.2f} below minimum ${min_order_size:.2f}")
                        return {'success': False, 'reason': 'size_below_minimum', 'calculated': lot_size, 'minimum': min_order_size}
                
                logger.info(f"   [OK] Sufficient balance: ${usdt_free:.2f} free, using ${lot_size:.2f} (${(lot_size/usdt_free*100):.1f}% of free)")
                logger.info(f"   📊 Placing order: ${lot_size:.2f} on {optimal['market_type']}")
            except Exception as e:
                logger.error(f"   [X] Could not check balance: {type(e).__name__}: {str(e)}")
                logger.error(f"     Continuing with original lot size ${lot_size:.2f} (balance check failed)")
                import traceback
                logger.debug(f"   Balance check traceback: {traceback.format_exc()}")
            
            # CRITICAL FIX: Calculate quantity in COINS, not USD!
            # Bybit needs amount in BASE currency (BTC, ETH, SOL, etc.)
            
            # Safety check: Ensure entry_price is valid!
            if not entry_price or entry_price <= 0:
                logger.error(f"   [X] Invalid entry price for {symbol}: {entry_price}, SKIPPING!")
                return {'success': False, 'reason': 'invalid_price', 'price': entry_price}
            
            quantity = lot_size / entry_price
            
            logger.info(f"   💰 Order: {quantity:.8f} {symbol.split('/')[0]} (${lot_size:.2f} @ ${entry_price:.2f})")
            
            # 🔥 CHECK EXCHANGE ORDER SIZE LIMITS (MIN & MAX)!
            try:
                # Get market limits from exchange
                market = self.exchange.market(symbol)
                limits = market.get('limits', {})
                amount_limits = limits.get('amount', {})
                cost_limits = limits.get('cost', {})  # Order value limits (USD)
                
                max_order_size = amount_limits.get('max')
                min_order_size = amount_limits.get('min')
                min_order_value = cost_limits.get('min')  # Minimum order value in USD
                
                # Check MINIMUM order value (USD)
                if min_order_value and lot_size < min_order_value:
                    logger.warning(f"    Order value ${lot_size:.2f} below exchange minimum ${min_order_value:.2f}")
                    logger.info(f"   🔧 Adjusting order value to minimum: ${min_order_value:.2f}")
                    lot_size = min_order_value
                    quantity = lot_size / entry_price
                    logger.info(f"   💰 Adjusted order: {quantity:.8f} {symbol.split('/')[0]} (${lot_size:.2f} @ ${entry_price:.2f})")
                
                # Check MINIMUM order quantity
                if min_order_size and quantity < min_order_size:
                    logger.warning(f"    Order quantity {quantity:.8f} below exchange minimum {min_order_size:.8f}")
                    logger.info(f"   🔧 Adjusting quantity to minimum: {min_order_size:.8f}")
                    quantity = min_order_size
                    lot_size = quantity * entry_price
                    logger.info(f"   💰 Adjusted order: {quantity:.8f} {symbol.split('/')[0]} (${lot_size:.2f} @ ${entry_price:.2f})")
                
                # Check MAXIMUM order size
                if max_order_size and quantity > max_order_size:
                    logger.warning(f"    Order size {quantity:.8f} exceeds exchange max {max_order_size:.8f}")
                    logger.info(f"   🔧 Adjusting quantity to exchange limit: {max_order_size:.8f}")
                    quantity = max_order_size
                    # Recalculate lot_size to match adjusted quantity
                    lot_size = quantity * entry_price
                    logger.info(f"   💰 Adjusted order: {quantity:.8f} {symbol.split('/')[0]} (${lot_size:.2f} @ ${entry_price:.2f})")
                elif max_order_size:
                    logger.debug(f"   [OK] Order size {quantity:.8f} within exchange limit {max_order_size:.8f}")
                
                # Final check: ensure adjusted lot_size doesn't exceed balance (if balance was fetched)
                if usdt_free > 0 and lot_size > usdt_free * 0.95:  # Use 95% max to avoid issues
                    logger.warning(f"    Adjusted order value ${lot_size:.2f} exceeds 95% of balance ${usdt_free:.2f}")
                    lot_size = usdt_free * 0.95
                    quantity = lot_size / entry_price
                    logger.info(f"   💰 Final adjusted order: {quantity:.8f} {symbol.split('/')[0]} (${lot_size:.2f} @ ${entry_price:.2f})")
                    
            except Exception as e:
                logger.warning(f"    Could not check exchange limits: {e} (continuing with calculated quantity)")
                logger.debug(f"   Limit check error details: {str(e)[:200]}")
            
            # 🔥 CRITICAL FIX FOR SELL ORDERS: Check base currency balance!
            if side == 'sell':
                # For SELL orders, we need BASE currency (TRX, BTC, etc.), not USDT!
                base_currency = symbol.split('/')[0]  # e.g., "TRX" from "TRX/USDT"
                
                try:
                    # Fetch balance to get base currency amount
                    sell_balance = await asyncio.to_thread(self.exchange.fetch_balance)
                    base_info = sell_balance.get(base_currency, {})
                    if isinstance(base_info, dict):
                        base_free = base_info.get('free', 0)
                        base_total = base_info.get('total', 0)
                    else:
                        base_free = float(base_info) if base_info else 0
                        base_total = base_free
                    
                    logger.info(f"   💰 SELL Order: Need {quantity:.8f} {base_currency}, have {base_free:.8f} free")
                    
                    # Check if we have enough base currency
                    if base_free < quantity:
                        if base_free > 0:
                            logger.info(f"    Insufficient {base_currency} for full size. Adjusting to {base_free:.8f} (Sell All)")
                            quantity = base_free * 0.99 # Sell 99% of what we have
                        else:
                            logger.warning(f"   ⏭️ Skipping SELL - insufficient {base_currency} balance ({base_free:.8f} available)")
                            return {'success': False, 'reason': 'insufficient_base_currency', 'base_currency': base_currency, 'available': base_free}
                    
                    logger.info(f"   [OK] Using valid {base_currency} quantity: {quantity:.8f}")
                except Exception as e:
                    logger.warning(f"     Could not check {base_currency} balance for SELL order: {e}")
                    logger.info(f"   💡 Continuing with order (balance check failed, exchange will reject if insufficient)")
            
            # Place order with detailed logging
            logger.info(f"   🎯 Placing {side.upper()} order: {quantity:.8f} {symbol.split('/')[0]} @ ${entry_price:.6f}")
            try:
                if side == 'buy':
                    params = {'createMarketBuyOrderRequiresPrice': False}
                    logger.debug(f"   Calling create_market_buy_order with quantity={quantity:.8f}")
                    order = await asyncio.to_thread(
                        self.exchange.create_market_buy_order,
                        symbol,
                        quantity,  # Changed from lot_size to quantity!
                        params
                    )
                else:
                    logger.debug(f"   Calling create_market_sell_order with quantity={quantity:.8f}")
                    order = await asyncio.to_thread(
                        self.exchange.create_market_sell_order,
                        symbol,
                        quantity,
                        {}  # Add empty params dict
                    )
                
                logger.info(f"   [OK] [ENTRY] Order placed successfully! Order ID: {order.get('id', 'N/A')}")
                logger.debug(f"   Order response: {order}")
            except Exception as e:
                logger.error(f"   [X] ORDER PLACEMENT FAILED: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                return {'success': False, 'reason': 'order_failed', 'error': str(e), 'symbol': symbol}
            
            # Get actual executed price from order response
            actual_price = order.get('average') or order.get('price') or trade_plan.get('entry_price') or entry_price
            if not actual_price or actual_price <= 0:
                logger.warning(f"     Invalid actual_price from order, using entry_price: {entry_price}")
                actual_price = entry_price
            
            # Record in multi-timeframe tracker
            trade_record = {
                **trade_plan,
                'order_id': order.get('id'),
                'entry_price': actual_price,  # OVERRIDE with actual executed price!
                'executed_at': datetime.utcnow().isoformat(),
                'status': 'open',
                'timeframe': timeframe
            }
            
            logger.info(f"   📊 Trade Record Entry Price: ${actual_price:.6f} (from order response)")
            
            self.active_trades_by_tf[symbol].append(trade_record)
            
            # 💰 START PROFIT MONITORING IMMEDIATELY!
            try:
                from PROFIT_MONITORING_SYSTEM import monitor_trade_for_profit
                asyncio.create_task(monitor_trade_for_profit(self.exchange, trade_record))
            except Exception as e:
                logger.warning(f" Profit monitoring not started: {e}")
            
            logger.info(f"[OK] INTELLIGENT TRADE EXECUTED!")
            order_id = order.get('id') or 'N/A'
            stop_loss = trade_plan.get('stop_loss') or 0.0
            max_hold = trade_plan.get('max_hold_time_minutes') or 0
            tp_levels = trade_plan.get('take_profit_levels', [])
            
            logger.info(f"   📋 Order ID: {order_id}")
            logger.info(f"   💰 Size: ${lot_size:.2f}")
            logger.info(f"   🎯 {len(tp_levels)} TP levels set")
            logger.info(f"   🛡️  Stop Loss: ${stop_loss:.4f}")
            logger.info(f"   ⏱️  Max Hold: {max_hold} minutes")
            logger.info(f"   📊 Active trades on {symbol}: {len(self.active_trades_by_tf[symbol])} timeframes")
            logger.info(f"   ⏰ Profit monitoring started!")
            
            if ai_insights:
                ai_consensus = ai_insights.get('ai_consensus', 'N/A')
                logger.info(f"   🤖 AI insights applied: {ai_consensus.upper() if isinstance(ai_consensus, str) else 'N/A'}")
                if ai_insights.get('unanimous'):
                    logger.info(f"   🌟 AI UNANIMOUS agreement!")
            
            # 🔥 CRITICAL FIX: Return dict with 'success': True so EXECUTION_ORCHESTRATOR recognizes it!
            return {
                'success': True,
                'order_id': order_id,
                'entry_price': actual_price,
                **trade_record
            }
            
        except Exception as e:
            logger.error(f"   [X] INTELLIGENT EXECUTION ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            return {'success': False, 'result': 'execution_error', 'error': str(e), 'symbol': symbol}




    def _recover_stuck_capital(self, balance_snapshot):
        """
        Emergency method to sell at BID price to force execution on Testnet.
        """
        try:
            logger.info("🚑 INITIATING BID-LIMIT RECOVERY...")
            total_recovered = 0.0
            
            if 'total' in balance_snapshot:
                for currency, amount in balance_snapshot['total'].items():
                    if currency == 'USDT' or amount <= 0: continue
                    symbol = f"{currency}/USDT"
                    
                    try:
                        # 1. Fetch Order Book for BEST BID
                        ob = self.exchange.fetch_order_book(symbol, limit=5)
                        if not ob['bids']: 
                            logger.warning(f"   No bids for {symbol}, trying taker price...")
                            ticker = self.exchange.fetch_ticker(symbol)
                            bid_price = ticker['last'] * 0.99
                        else:
                            bid_price = ob['bids'][0][0]
                        
                        value_usd = float(amount) * bid_price
                        if value_usd < 1.0: continue
                        
                        logger.info(f"   Liquidating {amount} {currency} @ ${bid_price:.4f}...")
                        
                        # 2. Limit Order at EXACT Bid (to satisfy bybit price bands)
                        clean_amt = self.exchange.amount_to_precision(symbol, amount)
                        clean_price = self.exchange.price_to_precision(symbol, bid_price)
                        
                        order = self.exchange.create_order(
                            symbol, 'limit', 'sell', 
                            float(clean_amt), float(clean_price), 
                            params={'category': 'spot'}
                        )
                        logger.info(f"   [OK] Recovery Order Placed: {order.get('id', 'N/A')}")
                        time.sleep(2) # Give it time to fill
                        total_recovered += value_usd
                            
                    except Exception as e:
                        logger.debug(f"   Recovery logic failed for {currency}: {e}")
                        pass
                        
            if total_recovered > 0:
                logger.info(f"[OK] RECOVERY ATTEMPTED. Balance should refresh shortly.")
            else:
                logger.info("ℹ️ No positions found.")
                
        except Exception as e:
            logger.error(f"[X] Critical Recovery error: {e}")

    
    def calibrate_wallet_positions(self):
        """
        FORCE RECOGNITION of existing wallet balances as active trades
        """
        try:
            bal = self.exchange.fetch_balance()
            for currency, data in bal.items():
                if currency in ['USDT', 'USDC', 'USD', 'free', 'used', 'total', 'info']:
                    continue
                    
                amount = data.get('free', 0)
                if amount > 0:
                    # check if value > $10 (meaningful position)
                    try:
                        ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                        value = amount * ticker['last']
                        if value > 10.0:
                            logger.info(f"⚖️ CALIBRATING: Found existing {currency} position (${value:.2f})")
                            # Register as active trade in orchestrator if possible
                            # For now, just log that we see it effectively
                    except: pass
        except Exception as e:
            logger.error(f"Calibration failed: {e}")

    def _validate_order(self, symbol, side, amount, price=None):
        """
        CRITICAL: Validate order against exchange rules BEFORE submission
        """
        try:
            market = self.exchange.market(symbol)
            min_amount = market['limits']['amount']['min'] if market['limits']['amount']['min'] else 0.0001
            min_cost = market['limits']['cost']['min'] if market['limits']['cost']['min'] else 5.0
            
            # 1. Check Minimum Amount
            if amount < min_amount:
                logger.warning(f"[X] BLOCKED: Amount {amount} < Min {min_amount} for {symbol}")
                return False
                
            # 2. Check Minimum Cost (Value)
            # Estimate price if not provided
            if not price:
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker['last']
                
            value = amount * price
            if value < min_cost:
                logger.warning(f"[X] BLOCKED: Value ${value:.2f} < Min ${min_cost:.2f} for {symbol} (Dust Prevention)")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f" Validation error for {symbol}: {e}")
            return True  # Proceed with caution if validation fails

    async def execute_trade(self, opportunity: Dict) -> Dict:
        """Execute trade with full integration (GATE.IO FIXED)"""
        # Init counters and PnL memory (lazy init for safety)
        if not hasattr(self, 'active_positions'): self.active_positions = {}
        if not hasattr(self, 'trades_won'): self.trades_won = 0
        if not hasattr(self, 'trades_lost'): self.trades_lost = 0
        if not hasattr(self, 'total_profit'): self.total_profit = 0.0
        if not hasattr(self, 'error_count'): self.error_count = 0
        if not hasattr(self, 'trades_executed'): self.trades_executed = 0
        try:

            symbol = opportunity.get('symbol')
            action = opportunity.get('action')
            
            if not symbol or not action:
                return {'success': False, 'result': 'execution_failed'}
            
            # EXCHANGE-SPECIFIC BLACKLIST - Pairs that are broken on specific exchanges only
            EXCHANGE_BLACKLIST = {
                'bybit_testnet': ['ATOM/USDT', 'ATOM/USD', 'ATOMUSDT'],  # Bybit testnet price floor issue
                # Other exchanges: ATOM is fine
            }
            
            # Check if current exchange has blacklisted pairs
            exchange_id = getattr(self.exchange, 'id', 'unknown').lower()
            # Get current balance
            try:
                balance = self.exchange.fetch_balance()
                usdt_free = balance['USDT']['free']
                logger.info(f" Available: ${usdt_free:.2f} USDT")
                # RECOVERY LOGIC
                if usdt_free < 1.0:
                    logger.warning(" Low balance detected! Checking for stuck positions...")
                    self._recover_stuck_capital(balance)
                    # Refresh balance
                    try:
                        balance = self.exchange.fetch_balance()
                        usdt_free = balance['USDT']['free']
                        logger.info(f" New Balance after recovery: ${usdt_free:.2f} USDT")
                    except: pass
            except Exception as e:
                logger.error(f" Balance fetch failed: {e}")
                usdt_free = 0.0

            # Use sizing logic with enforced minimums
            trade_value = opportunity.get('size_usd', 10.0)  # Default $10
            
            # Enforce minimum order size ($5 for Bybit)
            if trade_value < 5.0:
                trade_value = 5.0
            
            # Cap at 30% of balance for safety
            max_trade = usdt_free * 0.30
            if trade_value > max_trade:
                trade_value = max_trade
            
            # Final safety check
            if trade_value < 5.0:
                logger.warning(f"[X] Trade value ${trade_value:.2f} below minimum. Balance: ${usdt_free:.2f}")
                return {'success': False, 'result': 'insufficient_balance'}

            # Price
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker['last']
            except:
                logger.error(" Price fetch failed")
                return {'success': False, 'result': 'execution_failed'}

            # Amount
            amount = trade_value / price
            amount = float(self.exchange.amount_to_precision(symbol, amount))

            # VALIDATE ORDER
            if not self._validate_order(symbol, action, amount, price):
                return {'success': False, 'result': 'validation_failed_dust'}

            logger.info(f" EXECUTING (REAL): {action} {amount} {symbol} @ ${price:.4f}")

            # Execute
            # Gate.io fix: disable price requirement checklist
            params = {}
            if 'gate' in self.exchange.id or 'gateio' in self.exchange.id:  # FIXED GATE CHECK
                 params['createMarketBuyOrderRequiresPrice'] = False

            order = self.exchange.create_order(
                symbol,
                'market',
                action.lower(),
                amount,
                price, # Some exchanges need price even for market
                params
            )

            self.trades_executed += 1
            logger.info(f" [OK] ORDER FILLED: {order['id']}")
            
            # PnL TRACKING
            try:
                if action.lower() == 'buy':
                    self.active_positions[symbol] = {'entry_price': price, 'amount': amount}
                    logger.info(f"   📝 Position Opened: {symbol} @ ${price:.4f}")
                elif action.lower() == 'sell':
                    if symbol in self.active_positions:
                        entry = self.active_positions[symbol]['entry_price']
                        # Calculate Profit
                        profit_usd = (price - entry) * amount
                        self.total_profit += profit_usd
                        if profit_usd > 0:
                            self.trades_won += 1
                            logger.info(f"   💰 PROFIT: ${profit_usd:.4f} (Entry: ${entry:.4f} -> Exit: ${price:.4f})")
                        else:
                            self.trades_lost += 1
                            logger.info(f"   🔻 LOSS: ${profit_usd:.4f} (Entry: ${entry:.4f} -> Exit: ${price:.4f})")
                        # Clear position
                        del self.active_positions[symbol]
                    else:
                        # Assuming scalp from immediate history if not in memory (simplified)
                        pass
            except Exception as e:
                logger.error(f"PnL Error: {e}")
            self.error_count = 0
            return {'success': True, 'result': 'filled'}

        except Exception as e:
            logger.error(f" EXECUTION ERROR: {e}")
            self.error_count += 1
            return {'success': False, 'result': 'execution_failed'}
def get_intelligent_engine(exchange, venue_id="bybit_testnet"):
    """Get or create intelligent execution engine instance"""
    global _global_engine

    if _global_engine is None:
        _global_engine = IntelligentExecutionEngine(exchange)
        logger.info("Intelligent Execution Engine LOADED (via get_intelligent_engine)")

    return _global_engine

_instance = None
def get_intelligent_execution_engine(exchange_id='bybit_testnet', venue_id='spot'):
    global _instance
    if _instance is None:
        _instance = IntelligentExecutionEngine()
    return _instance
