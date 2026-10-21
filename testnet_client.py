"""Shared Bybit testnet client for the LeanTrader being.

Raw urllib signed client (the container image's TLS fingerprint is WAF-blocked
by Bybit testnet's CloudFront; when TESTNET_RELAY is set, requests are signed
and forwarded by the host-side relay instead). Used by the zoo trader's money
path design and the continuous propagation service.
"""
import hashlib
import hmac
import json
import os
import time
import urllib.request


class TestnetClient:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.base = 'https://api-testnet.bybit.com'
        self.relay = os.environ.get('TESTNET_RELAY', '')

    def _req(self, method, path, params=None, signed=True):
        params = params or {}
        if getattr(self, 'relay', None):
            data = json.dumps({'method': method, 'path': path, 'params': params}).encode()
            rq = urllib.request.Request(self.relay + '/relay', data=data,
                                         headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(rq, timeout=20) as r:
                j = json.loads(r.read().decode())
            if j.get('retCode') != 0:
                raise Exception(f"bybit {j.get('retCode')}: {j.get('retMsg')}")
            return j['result']
        ts = str(int(time.time() * 1000))
        recv = '5000'
        if method == 'GET':
            qs = '&'.join(f'{k}={v}' for k, v in params.items())
            body = ''
            payload = ts + self.key + recv + qs
        else:
            qs = ''
            body = json.dumps(params)
            payload = ts + self.key + recv + body
        headers = {'Content-Type': 'application/json'}
        if signed:
            headers['X-BAPI-API-KEY'] = self.key
            headers['X-BAPI-SIGN'] = hmac.new(self.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
            headers['X-BAPI-TIMESTAMP'] = ts
            headers['X-BAPI-RECV-WINDOW'] = recv
        url = self.base + path + (('?' + qs) if qs else '')
        req = urllib.request.Request(url, data=(body.encode() if method != 'GET' else None),
                                     headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode())
        if j.get('retCode') != 0:
            raise Exception(f"bybit {j.get('retCode')}: {j.get('retMsg')}")
        return j['result']

    def wallet_free_usdt(self):
        # TRUE spendable balance. The old read returned walletBalance
        # ($24.15) while totalAvailableBalance was $0.67 - the whole
        # fleet (and the governor's $15 gate) sized and gated on
        # money that was already margin for open positions, and new
        # orders died 110007. (2026-10-19 excavation.)
        res = self._req('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
        acct = res['list'][0]
        avail = acct.get('totalAvailableBalance')
        if avail not in (None, ''):
            return float(avail)
        coins = acct.get('coin', [])
        u = next((c for c in coins if c.get('coin') == 'USDT'), {})
        return float(u.get('availableToWithdraw') or u.get('walletBalance') or 0)

    def wallet_equity_usdt(self):
        res = self._req('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
        acct = res['list'][0]
        eq = acct.get('totalEquity')
        if eq not in (None, ''):
            return float(eq)
        return self.wallet_free_usdt()

    def positions(self):
        res = self._req('GET', '/v5/position/list', {'category': 'linear', 'settleCoin': 'USDT'})
        return res.get('list', [])

    def set_leverage(self, symbol, lev=10):
        return self._req('POST', '/v5/position/set-leverage',
                         {'category': 'linear', 'symbol': symbol,
                          'buyLeverage': str(lev), 'sellLeverage': str(lev)})

    def create_market_buy(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'linear', 'symbol': symbol, 'side': 'Buy',
                          'orderType': 'Market', 'qty': str(qty)})

    def create_market_sell_reduce(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'linear', 'symbol': symbol, 'side': 'Sell',
                          'orderType': 'Market', 'qty': str(qty), 'reduceOnly': True})

    def create_market_sell_open(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'linear', 'symbol': symbol, 'side': 'Sell',
                          'orderType': 'Market', 'qty': str(qty)})

    def create_market_buy_reduce(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'linear', 'symbol': symbol, 'side': 'Buy',
                          'orderType': 'Market', 'qty': str(qty), 'reduceOnly': True})

    def create_limit_postonly(self, symbol, side, qty, price):
        return self._req('POST', '/v5/order/create',
                         {'category': 'linear', 'symbol': symbol, 'side': side,
                          'orderType': 'Limit', 'qty': qty_str(qty),
                          'price': str(price), 'timeInForce': 'PostOnly'})

    def cancel_order(self, symbol, order_id):
        return self._req('POST', '/v5/order/cancel',
                         {'category': 'linear', 'symbol': symbol,
                          'orderId': order_id})

    def order_status(self, symbol, order_id):
        res = self._req('GET', '/v5/order/realtime',
                        {'category': 'linear', 'symbol': symbol,
                         'orderId': order_id})
        lst = res.get('list', []) if isinstance(res, dict) else []
        return lst[0] if lst else {}


# ---- Execution routing (2026-10-21, Princewill: resolve the way
# ---- they trade and route it properly). The forensic read of the
# ---- exchange record showed ~$0.02 per round trip of spread +
# ---- taker fees eating the fleet on $5-12 notionals, while the
# ---- maker-first orchestrator was the only arm whose per-close
# ---- expectancy (+$0.28) beat the friction. These two helpers
# ---- give every being that shape through the shared client.

def _tick_size(client, symbol):
    cache = getattr(client, '_tick_cache', None)
    if cache is None:
        cache = client._tick_cache = {}
    if symbol not in cache:
        try:
            ii = client._req('GET', '/v5/market/instruments-info',
                             {'category': 'linear', 'symbol': symbol})
            pf = ((ii.get('list') or [{}])[0]).get(
                'priceFilter') or {}
            cache[symbol] = float(pf.get('tickSize') or 0)
        except Exception:
            cache[symbol] = 0.0
    return cache[symbol]


def _fmt_tick(price, tick):
    import math
    if not tick:
        return str(price)
    p = round(price / tick) * tick
    dec = max(0, -int(math.floor(math.log10(tick)))) \
        if tick < 1 else 0
    return f'{p:.{dec}f}'


def maker_open(client, symbol, is_short, qty, fuse_s=6):
    """Maker-first entry: post-only at the touch for a short
    fuse. Returns {'orderId', 'filled_qty', 'avg_price'} on a
    full or standing partial fill, else None (the caller falls
    back to its market path). Never leaves a resting order."""
    import time as _t
    try:
        tk = client._req('GET', '/v5/market/tickers',
                         {'category': 'linear', 'symbol': symbol})
        row = (tk.get('list') or [{}])[0]
        bid = float(row.get('bid1Price') or 0)
        ask = float(row.get('ask1Price') or 0)
        if not bid or not ask:
            return None
        price = _fmt_tick(ask if is_short else bid,
                          _tick_size(client, symbol))
        res = client.create_limit_postonly(
            symbol, 'Sell' if is_short else 'Buy', qty, price)
        oid = (res or {}).get('orderId')
        if not oid:
            return None
        deadline = _t.time() + fuse_s
        filled, avg = 0.0, 0.0
        while _t.time() < deadline:
            _t.sleep(1.2)
            st = client.order_status(symbol, oid)
            filled = float(st.get('cumExecQty') or 0)
            avg = float(st.get('avgPrice') or 0)
            if st.get('orderStatus') in (
                    'Filled', 'Cancelled', 'Rejected',
                    'PartiallyFilledCanceled'):
                break
        try:
            client.cancel_order(symbol, oid)
        except Exception:
            pass
        _t.sleep(0.4)
        try:
            st = client.order_status(symbol, oid)
            filled = float(st.get('cumExecQty') or filled)
            avg = float(st.get('avgPrice') or avg)
        except Exception:
            pass
        if filled > 0:
            return {'orderId': oid, 'filled_qty': filled,
                    'avg_price': avg, 'maker': True}
        return None
    except Exception:
        return None


def smart_close(client, symbol, is_long, qty, wait_s=25):
    """Touch-priced reduce-only close: rests a limit at the
    touch to catch the depth flickers that cancel market closes
    on thin testnet books (the stale-book lesson). Returns True
    when the limit fully closed the quantity; False when
    unfilled or partial - the caller then falls back to its
    market close for the remainder. Never leaves a resting
    order behind."""
    import time as _t
    try:
        tk = client._req('GET', '/v5/market/tickers',
                         {'category': 'linear', 'symbol': symbol})
        row = (tk.get('list') or [{}])[0]
        bid = float(row.get('bid1Price') or 0)
        ask = float(row.get('ask1Price') or 0)
        last = float(row.get('lastPrice') or 0)
        if is_long:
            px, side = (bid or last), 'Sell'
        else:
            px, side = (ask or last), 'Buy'
        if not px:
            return False
        res = client._req(
            'POST', '/v5/order/create',
            {'category': 'linear', 'symbol': symbol, 'side': side,
             'orderType': 'Limit', 'qty': qty_str(qty),
             'price': _fmt_tick(px, _tick_size(client, symbol)),
             'timeInForce': 'GTC', 'reduceOnly': True})
        oid = (res or {}).get('orderId')
        if not oid:
            return False
        deadline = _t.time() + wait_s
        while _t.time() < deadline:
            _t.sleep(2)
            st = client.order_status(symbol, oid)
            if st.get('orderStatus') == 'Filled':
                return True
            if st.get('orderStatus') in ('Cancelled', 'Rejected'):
                break
        try:
            client.cancel_order(symbol, oid)
        except Exception:
            pass
        _t.sleep(0.4)
        try:
            st = client.order_status(symbol, oid)
            return float(st.get('cumExecQty') or 0) >= float(qty)
        except Exception:
            return False
    except Exception:
        return False


def ccxt_to_raw(sym):
    # 'BTC/USDT:USDT' -> 'BTCUSDT'; dated/odd symbols -> None (paper-only)
    if sym.endswith('/USDT:USDT'):
        return sym.split('/')[0] + 'USDT'
    return None


def qty_str(q):
    t = ('%.6f' % float(q)).rstrip('0').rstrip('.')
    return t if t else '0'


def step_decimals(step):
    ds = str(step)
    return len(ds.split('.')[1].rstrip('0')) if '.' in ds else 0


def quantize(qty, step):
    if not step:
        return qty
    return round(int(qty / step) * step, step_decimals(step))


def make_client():
    key = sec = None
    for base in ('/run/secrets', '/root/secrets'):
        kp = os.path.join(base, 'bybit_testnet_api_key')
        sp = os.path.join(base, 'bybit_testnet_api_secret')
        if os.path.exists(kp) and os.path.exists(sp):
            key = open(kp).read().strip()
            sec = open(sp).read().strip()
            break
    if not key:
        raise Exception('testnet secret files not found')
    return TestnetClient(key, sec)
