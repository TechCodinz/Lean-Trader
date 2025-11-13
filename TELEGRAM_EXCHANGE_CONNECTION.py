#!/usr/bin/env python3
"""
🔗 TELEGRAM EXCHANGE CONNECTION SYSTEM 🔗

Users connect their exchanges directly from Telegram:
- Secure API key collection
- Step-by-step guidance
- Connection verification
- Balance checking
- Test trade execution

MAKES IT EASY FOR USERS! ✨
"""

import asyncio
import logging
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import ccxt

logger = logging.getLogger(__name__)


class TelegramExchangeConnection:
    """
    EXCHANGE CONNECTION via TELEGRAM
    
    Features:
    - Guided API key setup
    - Secure storage
    - Connection testing
    - Balance verification
    - Exchange selection UI
    """
    
    def __init__(self, managed_trading_engine=None):
        self.managed_trading = managed_trading_engine
        
        # User connection states
        self.connection_states = {}  # {user_id: {'step': 1, 'exchange': 'bybit', ...}}
        
        # Supported exchanges
        self.supported_exchanges = {
            'bybit': {
                'name': 'Bybit',
                'icon': '🔷',
                'api_url': 'https://bybit.com/app/user/api-management',
                'guide': 'Go to Profile → API → Create New Key'
            },
            'binance': {
                'name': 'Binance',
                'icon': '🟡',
                'api_url': 'https://binance.com/en/my/settings/api-management',
                'guide': 'Go to Profile → API Management → Create API'
            },
            'gateio': {
                'name': 'Gate.io',
                'icon': '🔵',
                'api_url': 'https://gate.io/myaccount/apiv4keys',
                'guide': 'Go to Wallet → API Keys → Create New'
            },
            'okx': {
                'name': 'OKX',
                'icon': '⚫',
                'api_url': 'https://okx.com/account/my-api',
                'guide': 'Go to Profile → API → Create V5 API Key'
            }
        }
        
        logger.info("🔗 TELEGRAM EXCHANGE CONNECTION initialized!")
        logger.info(f"   Supported exchanges: {len(self.supported_exchanges)}")
    
    def create_exchange_selection_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard for exchange selection"""
        keyboard = []
        
        for ex_id, ex_data in self.supported_exchanges.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{ex_data['icon']} {ex_data['name']}", 
                    callback_data=f'connect_{ex_id}'
                )
            ])
        
        keyboard.append([InlineKeyboardButton("ℹ️ Why Connect?", callback_data='why_connect')])
        keyboard.append([InlineKeyboardButton("🔒 Security Info", callback_data='security_info')])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def start_connection(self, user_id: int, exchange: str) -> str:
        """
        Start exchange connection process
        
        Returns: Message with instructions
        """
        if exchange not in self.supported_exchanges:
            return "❌ Exchange not supported"
        
        ex_data = self.supported_exchanges[exchange]
        
        # Initialize connection state
        self.connection_states[user_id] = {
            'step': 1,
            'exchange': exchange,
            'started_at': datetime.now()
        }
        
        message = f"""
🔗 **CONNECT YOUR {ex_data['name'].upper()}**

Step 1: Get your API keys

1️⃣ Go to: {ex_data['api_url']}

2️⃣ Create new API key:
   {ex_data['guide']}

3️⃣ **IMPORTANT PERMISSIONS:**
   ✅ Enable: Read, Trade
   ❌ Disable: Withdraw (for security!)
   
4️⃣ **IP Whitelist (Optional but recommended):**
   Add our server IP for extra security

5️⃣ Copy your:
   • API Key
   • API Secret

📩 **When ready, send:**
`/api YOUR_API_KEY YOUR_API_SECRET`

Example:
`/api abcd1234... xyz9876...`

🔒 **Security:**
• Keys encrypted in storage
• No withdraw permissions needed
• You control your funds
• Disconnect anytime with /disconnect

Need help? /help_connect
"""
        
        return message
    
    async def process_api_keys(self, user_id: int, api_key: str, api_secret: str) -> Dict:
        """
        Process user's API keys
        
        Steps:
        1. Validate format
        2. Test connection
        3. Check balance
        4. Store securely
        5. Activate managed trading
        
        Returns: Connection result
        """
        if user_id not in self.connection_states:
            return {'success': False, 'error': 'Connection not started. Use /connect first'}
        
        state = self.connection_states[user_id]
        exchange_name = state['exchange']
        
        logger.info(f"🔗 Processing API keys for user {user_id}")
        logger.info(f"   Exchange: {exchange_name}")
        
        try:
            # Test connection
            if self.managed_trading:
                success = await self.managed_trading.connect_user_exchange(
                    user_id, exchange_name, api_key, api_secret
                )
                
                if success:
                    # Get user's balance
                    user_data = self.managed_trading.user_exchanges.get(user_id, {})
                    balance = user_data.get('balance', 0)
                    
                    return {
                        'success': True,
                        'exchange': exchange_name,
                        'balance': balance,
                        'message': f"""
✅ **CONNECTION SUCCESSFUL!**

Exchange: {self.supported_exchanges[exchange_name]['name']}
Balance: ${balance:.2f} USDT

🤖 **Managed Trading Active!**
• Bot will now trade on your account
• You keep 90% of profits
• We take 10% profit share
• Full transparency

📊 **Dashboard:** /dashboard
⚙️ **Settings:** /settings
📈 **Performance:** /performance
❌ **Disconnect:** /disconnect

Let the bot make money for you! 🚀
"""
                    }
                else:
                    return {'success': False, 'error': 'Connection test failed. Check your API keys.'}
            else:
                return {'success': False, 'error': 'Managed trading not available'}
        
        except Exception as e:
            logger.error(f"❌ Connection failed for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_user_dashboard_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        """Create keyboard for user dashboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Performance", callback_data='show_performance')],
            [InlineKeyboardButton("💰 Profit Report", callback_data='show_profits')],
            [InlineKeyboardButton("📈 Active Trades", callback_data='show_trades')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='show_settings')],
            [InlineKeyboardButton("❌ Disconnect Exchange", callback_data='disconnect_exchange')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def format_user_dashboard(self, user_id: int) -> str:
        """Format user dashboard"""
        if not self.managed_trading:
            return "Managed trading not available"
        
        stats = self.managed_trading.user_stats.get(user_id, {})
        
        return f"""
📊 **YOUR TRADING DASHBOARD**

💰 **Performance:**
Total Trades: {stats.get('trades', 0)}
Winning Trades: {stats.get('winning_trades', 0)}
Win Rate: {stats.get('win_rate', 0):.1%}

💎 **Profits:**
Total Profit: ${stats.get('total_profit', 0):.2f}
Your Share (90%): ${stats.get('user_profit', 0):.2f}
Service Fees (10%): ${stats.get('profit_share_paid', 0):.2f}

🚀 **Bot is working for you 24/7!**

📊 Detailed Report → /report
💰 Withdraw → /withdraw
⚙️ Settings → /settings
"""


# Singleton
_telegram_exchange_connection = None

def get_telegram_exchange_connection():
    """Get telegram exchange connection"""
    return _telegram_exchange_connection

def initialize_telegram_exchange_connection(managed_trading_engine=None):
    """Initialize telegram exchange connection"""
    global _telegram_exchange_connection
    _telegram_exchange_connection = TelegramExchangeConnection(managed_trading_engine)
    return _telegram_exchange_connection
