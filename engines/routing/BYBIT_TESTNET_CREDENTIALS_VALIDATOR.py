#!/usr/bin/env python3
"""
BYBIT_TESTNET_CREDENTIALS_VALIDATOR.py
Strict startup validation for Bybit testnet credentials
"""

import os
import sys
import logging
from dotenv import load_dotenv
import ccxt

logger = logging.getLogger(__name__)

class BybitTestnetValidator:
    """Validate Bybit testnet credentials and configuration"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('BYBIT_TESTNET_API_KEY')
        self.api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
        self.issues = []
    
    def validate_credentials(self) -> bool:
        """Validate API credentials exist"""
        logger.info("Validating Bybit testnet credentials...")
        
        if not self.api_key:
            self.issues.append("[X] MISSING BYBIT_TESTNET_API_KEY in .env")
        
        if not self.api_secret:
            self.issues.append("[X] MISSING BYBIT_TESTNET_API_SECRET in .env")
        
        if self.issues:
            return False
        
        logger.info("[OK] API credentials found")
        return True
    
    def validate_testnet_connection(self) -> bool:
        """Validate connection to Bybit testnet"""
        logger.info("Testing Bybit testnet connection...")
        
        try:
            exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            
            # Enable testnet/sandbox mode
            exchange.set_sandbox_mode(True)
            
            # Test connection by fetching balance
            balance = exchange.fetch_balance()
            
            logger.info(f"[OK] Connected to Bybit testnet")
            logger.info(f"   Endpoint: {exchange.urls['api']}")
            
            return True
            
        except Exception as e:
            self.issues.append(f"[X] Connection failed: {e}")
            return False
    
    def validate_balance(self) -> dict:
        """Validate account has sufficient balance"""
        logger.info("Checking testnet balance...")
        
        try:
            exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            exchange.set_sandbox_mode(True)
            
            balance = exchange.fetch_balance()
            
            usdt_free = balance.get('USDT', {}).get('free', 0)
            usdt_total = balance.get('USDT', {}).get('total', 0)
            
            logger.info(f"   USDT Free: ${usdt_free:.2f}")
            logger.info(f"   USDT Total: ${usdt_total:.2f}")
            
            if usdt_free < 10:
                self.issues.append(f" LOW BALANCE: ${usdt_free:.2f} USDT (recommend $100+ for trading)")
            else:
                logger.info(f"[OK] Sufficient balance for trading")
            
            return {
                'usdt_free': usdt_free,
                'usdt_total': usdt_total,
                'sufficient': usdt_free >= 10
            }
            
        except Exception as e:
            self.issues.append(f"[X] Balance check failed: {e}")
            return {'usdt_free': 0, 'usdt_total': 0, 'sufficient': False}
    
    def validate_wallet_type(self) -> dict:
        """Validate wallet type matches trading mode"""
        logger.info("Validating wallet configuration...")
        
        try:
            exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            exchange.set_sandbox_mode(True)
            
            # Get account type
            account_type = exchange.options.get('defaultType', 'unknown')
            
            logger.info(f"   Account type: {account_type}")
            logger.info(f"   Testnet mode: {exchange.sandbox}")
            
            return {
                'account_type': account_type,
                'is_testnet': exchange.sandbox,
                'endpoint': exchange.urls.get('api', 'unknown')
            }
            
        except Exception as e:
            self.issues.append(f"[X] Wallet validation failed: {e}")
            return {}
    
    def run_full_validation(self) -> bool:
        """Run all validations"""
        print("=" * 80)
        print("BYBIT TESTNET CREDENTIALS VALIDATION")
        print("=" * 80)
        print()
        
        # Step 1: Credentials
        if not self.validate_credentials():
            self.print_errors()
            return False
        
        # Step 2: Connection
        if not self.validate_testnet_connection():
            self.print_errors()
            return False
        
        # Step 3: Wallet type
        wallet_info = self.validate_wallet_type()
        
        # Step 4: Balance
        balance_info = self.validate_balance()
        
        # Summary
        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        if not self.issues:
            print("\n[OK] ALL VALIDATIONS PASSED")
            print(f"   Ready to trade with ${balance_info['usdt_free']:.2f} USDT")
            return True
        else:
            self.print_errors()
            return False
    
    def print_errors(self):
        """Print all validation errors"""
        print("\n" + "=" * 80)
        print("VALIDATION ERRORS")
        print("=" * 80)
        print()
        
        for issue in self.issues:
            print(issue)
        
        print()
        print("=" * 80)
        print("CANNOT START TRADING - FIX ERRORS ABOVE")
        print("=" * 80)
    
    def assert_valid_or_exit(self):
        """Assert valid or exit with error code"""
        if not self.run_full_validation():
            sys.exit(1)

def validate_bybit_testnet() -> bool:
    """Convenience function for validation"""
    validator = BybitTestnetValidator()
    return validator.run_full_validation()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    validator = BybitTestnetValidator()
    validator.assert_valid_or_exit()
    
    print("\n[OK] Bybit testnet is ready for trading")
