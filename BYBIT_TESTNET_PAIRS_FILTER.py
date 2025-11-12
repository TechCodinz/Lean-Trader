#!/usr/bin/env python3
"""
BYBIT TESTNET PAIRS FILTER

Only allows trading pairs that actually exist on Bybit testnet!
Prevents "symbol not found" errors.
"""

# Pairs that exist on Bybit TESTNET (verified list)
BYBIT_TESTNET_PAIRS = {
    # Major pairs
    'BTC/USDT', 'BTCUSDT',
    'ETH/USDT', 'ETHUSDT',
    'BNB/USDT', 'BNBUSDT',
    'SOL/USDT', 'SOLUSDT',
    'XRP/USDT', 'XRPUSDT',
    'ADA/USDT', 'ADAUSDT',
    'DOGE/USDT', 'DOGEUSDT',
    'DOT/USDT', 'DOTUSDT',
    'MATIC/USDT', 'MATICUSDT',
    'LTC/USDT', 'LTCUSDT',
    'AVAX/USDT', 'AVAXUSDT',
    'LINK/USDT', 'LINKUSDT',
    'UNI/USDT', 'UNIUSDT',
    'ATOM/USDT', 'ATOMUSDT',
    'ETC/USDT', 'ETCUSDT',
    'FIL/USDT', 'FILUSDT',
    'TRX/USDT', 'TRXUSDT',
    'APT/USDT', 'APTUSDT',
    'ARB/USDT', 'ARBUSDT',
    'OP/USDT', 'OPUSDT',
    'NEAR/USDT', 'NEARUSDT',
    'SUI/USDT', 'SUIUSDT',
    '1000PEPE/USDT', '1000PEPEUSDT',
    '1000SHIB/USDT', '1000SHIBUSDT',
}

def is_testnet_pair(symbol: str) -> bool:
    """Check if pair exists on Bybit testnet"""
    # Normalize symbol
    normalized = symbol.replace('/', '').upper()
    
    # Check both formats
    return symbol.upper() in BYBIT_TESTNET_PAIRS or normalized in BYBIT_TESTNET_PAIRS

def filter_testnet_signals(signals: list) -> list:
    """Filter signals to only testnet-compatible pairs"""
    filtered = []
    
    for signal in signals:
        symbol = signal.get('symbol') or signal.get('pair', '')
        
        if is_testnet_pair(symbol):
            filtered.append(signal)
    
    return filtered

def get_testnet_pairs() -> set:
    """Get set of all testnet pairs"""
    return BYBIT_TESTNET_PAIRS
