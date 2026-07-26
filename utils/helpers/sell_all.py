import ccxt, os
from dotenv import load_dotenv
load_dotenv()
e = ccxt.bybit({"apiKey": os.getenv("BYBIT_TESTNET_API_KEY"), "secret": os.getenv("BYBIT_TESTNET_API_SECRET"), "enableRateLimit": True})
e.set_sandbox_mode(True)
b = e.fetch_balance()
for a,v in b.get("free",{}).items():
  if a not in ["USDT","USDC","USD"] and v>0.001:
    try:
      t=e.fetch_ticker(a+"/USDT")
      val = v*t.get("last",0)
      if val>1:
        print(f"Selling {a} (${val:.2f})...")
        e.create_market_sell_order(a+"/USDT",v)
        print(f"  SOLD!")
    except Exception as ex:
      print(f"  Skip {a}: {str(ex)[:50]}")
b2 = e.fetch_balance()
print(f"FINAL USDT: ${b2.get('free',{}).get('USDT',0):.2f}")
