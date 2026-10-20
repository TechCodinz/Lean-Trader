"""Shared Bybit MAINNET client (REAL MONEY) for the LeanTrader being.

Raw urllib signed client (the container image's TLS fingerprint is WAF-blocked
by api.bybit.com; when MAINNET_RELAY is set, requests are signed
and forwarded by the host-side relay instead). Used by the zoo trader's money
path design and the continuous propagation service.
"""
import hashlib
import hmac
import json
import os
import time
import urllib.request


class MainnetClient:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.base = 'https://api.bybit.com'
        self.relay = os.environ.get('MAINNET_RELAY', '')

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

    # --- Spot arm (triangular organ, staged 2026-10-20) ---
    # The relay forwards order/create params verbatim, so spot is
    # just category='spot'. Inert until the mainnet activation
    # rails exist (keys + kill-switch file); qty is passed at 6dp
    # which satisfies the majors' spot lot sizes.
    def spot_market_buy(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'spot', 'symbol': symbol,
                          'side': 'Buy', 'orderType': 'Market',
                          'qty': f'{float(qty):.6f}'})

    def spot_market_sell(self, symbol, qty):
        return self._req('POST', '/v5/order/create',
                         {'category': 'spot', 'symbol': symbol,
                          'side': 'Sell', 'orderType': 'Market',
                          'qty': f'{float(qty):.6f}'})

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
    # Relay mode (the deployment): the HOST relay holds the keys and
    # signs; the container never touches real-money credentials.
    if os.environ.get('MAINNET_RELAY'):
        return MainnetClient('', '')
    key = sec = None
    for base in ('/run/secrets', '/root/secrets'):
        kp = os.path.join(base, 'bybit_mainnet_api_key')
        sp = os.path.join(base, 'bybit_mainnet_api_secret')
        if os.path.exists(kp) and os.path.exists(sp):
            key = open(kp).read().strip()
            sec = open(sp).read().strip()
            break
    if not key:
        raise Exception('mainnet secret files not found (and no MAINNET_RELAY)')
    return MainnetClient(key, sec)
