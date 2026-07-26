with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

old = """            logger.info(f"   🔍 ORDER RESPONSE KEYS: {list(order.keys())}")
            logger.info(f"   🔍 ORDER average={order.get('average')}, price={order.get('price')}")
            logger.info(f"   🔍 ORDER info={order.get('info', {})}")
            actual_price = order.get('average', order.get('price', trade_plan['entry_price']))
            logger.info(f"   🔍 EXTRACTED actual_price = {actual_price}")"""

new = """            # Extract price - Bybit testnet quirk: average/price often None
            actual_price = None
            if order.get('average'):
                actual_price = order.get('average')
            elif order.get('price'):
                actual_price = order.get('price')
            elif order.get('cost') and order.get('filled') and order.get('filled') > 0:
                actual_price = order.get('cost') / order.get('filled')
                logger.info(f"   💡 Calculated from cost/filled: ${actual_price:.6f}")
            elif order.get('trades') and len(order.get('trades')) > 0:
                trades = order.get('trades')
                actual_price = sum(t.get('price', 0) for t in trades) / len(trades)
                logger.info(f"   💡 Calculated from trades: ${actual_price:.6f}")
            else:
                actual_price = entry_price
                logger.warning(f"    Using fallback: ${actual_price:.6f}")
            logger.info(f"   [OK] Final entry_price: ${actual_price:.6f}")"""

if old in content:
    content = content.replace(old, new)
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
        f.write(content)
    print("[OK] Fixed!")
else:
    print("[X] Not found")
