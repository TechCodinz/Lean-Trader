with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

# Find where order is executed and add logging BEFORE the result is used
old = """            # Get actual executed price from order response
            actual_price = order.get('average', order.get('price', trade_plan['entry_price']))"""

new = """            # Get actual executed price from order response
            logger.info(f"   🔍 ORDER RESPONSE KEYS: {list(order.keys())}")
            logger.info(f"   🔍 ORDER average={order.get('average')}, price={order.get('price')}")
            logger.info(f"   🔍 ORDER info={order.get('info', {})}")
            actual_price = order.get('average', order.get('price', trade_plan['entry_price']))
            logger.info(f"   🔍 EXTRACTED actual_price = {actual_price}")"""

if old in content:
    content = content.replace(old, new)
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
        f.write(content)
    print("[OK] Added ORDER RESPONSE logging")
else:
    print("[X] Could not find target code")
