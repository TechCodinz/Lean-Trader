# Whitelist of profitable pairs
PROFITABLE_PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT']
BLACKLIST = ['USDC/USDT', 'USDT/USD', 'DAI/USDT', 'MON/USDT', 'TAO/USDT', 'BNB/USDT', 'FTM/USDT']
MIN_POSITION_SIZE_USD = 10

def is_profitable_pair(symbol):
    if symbol in BLACKLIST:
        return False
    if symbol in PROFITABLE_PAIRS:
        return True
    return False

def get_min_position_size():
    return MIN_POSITION_SIZE_USD
