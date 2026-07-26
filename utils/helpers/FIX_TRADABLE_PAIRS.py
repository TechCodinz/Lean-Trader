#!/usr/bin/env python3
"""Add missing _get_tradable_pairs method"""

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Check if method exists
if '_get_tradable_pairs' not in content:
    print("Adding _get_tradable_pairs method...")
    
    # Find a good place to add it (after __init__ or near other methods)
    # Add it in the class definition
    
    method_code = '''
    def _get_tradable_pairs(self):
        """Get list of tradable pairs for the exchange"""
        try:
            # Get markets from exchange
            if hasattr(self, 'exchange') and self.exchange:
                markets = self.exchange.load_markets()
                # Filter for USDT pairs that are active
                pairs = [symbol for symbol, market in markets.items() 
                        if market.get('quote') == 'USDT' 
                        and market.get('active', True)
                        and market.get('spot', True)]
                return pairs[:50]  # Limit to top 50 pairs
            else:
                # Fallback list
                return ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 
                       'DOGE/USDT', 'ADA/USDT', 'XRP/USDT', 'DOT/USDT']
        except Exception as e:
            logger.error(f"Error getting tradable pairs: {e}")
            return ['BTC/USDT', 'SOL/USDT', 'BNB/USDT']  # Minimal fallback
'''
    
    # Find the class definition
    import re
    
    # Look for the class and add method after __init__
    class_match = re.search(r'(class CompleteUltimateOrchestrator.*?:.*?def __init__.*?(?=\n    def [^_]|\n\nclass|\Z))', 
                           content, re.DOTALL)
    
    if class_match:
        # Insert after __init__
        init_end = class_match.end()
        content = content[:init_end] + method_code + content[init_end:]
        print("[OK] Added _get_tradable_pairs method after __init__")
    else:
        # Try simpler approach - add at end of file
        content += method_code
        print("[OK] Added _get_tradable_pairs method at end")
    
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
else:
    print("ℹ️  _get_tradable_pairs already exists")
