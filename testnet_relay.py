#!/usr/bin/env python3
"""LeanTrader testnet signing relay (HOST side).
The container's TLS fingerprint is WAF-blocked by Bybit testnet CloudFront;
the host's passes. This relay listens ONLY on the docker bridge IP, accepts
{method, path, params} from the trader container, signs with the host secret
files, forwards via urllib, and returns Bybit's JSON untouched.
Allowlisted paths only. Keys never leave the host."""
import hashlib, hmac, json, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = open('/root/secrets/bybit_testnet_api_key').read().strip()
SEC = open('/root/secrets/bybit_testnet_api_secret').read().strip()
BASE = 'https://api-testnet.bybit.com'
ALLOWED = {'/v5/account/wallet-balance', '/v5/order/create',
           '/v5/position/set-leverage', '/v5/position/list', '/v5/order/realtime'}

def forward(method, path, params):
    ts = str(int(time.time() * 1000)); recv = '5000'
    if method == 'GET':
        qs = '&'.join(f'{k}={v}' for k, v in params.items())
        body = None
        payload = ts + KEY + recv + qs
        url = BASE + path + (('?' + qs) if qs else '')
    else:
        body = json.dumps(params).encode()
        payload = ts + KEY + recv + body.decode()
        url = BASE + path
    sign = hmac.new(SEC.encode(), payload.encode(), hashlib.sha256).hexdigest()
    req = urllib.request.Request(url, data=body, method=method, headers={
        'Content-Type': 'application/json', 'X-BAPI-API-KEY': KEY,
        'X-BAPI-SIGN': sign, 'X-BAPI-TIMESTAMP': ts, 'X-BAPI-RECV-WINDOW': recv})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def _send(self, code, body):
        b = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        self._send(200, '{"ok": true}') if self.path == '/health' else self._send(404, '{}')
    def do_POST(self):
        try:
            n = int(self.headers.get('Content-Length', 0))
            j = json.loads(self.rfile.read(n) or b'{}')
            method, path, params = j.get('method', 'GET'), j.get('path', ''), j.get('params', {})
            if path not in ALLOWED:
                self._send(403, '{"error": "path not allowed"}')
                return
            st, body = forward(method, path, params)
            self._send(st, body)
        except Exception as e:
            self._send(500, json.dumps({'error': str(e)}))

if __name__ == '__main__':
    print('relay listening on 172.17.0.1:18099', flush=True)
    ThreadingHTTPServer(('172.17.0.1', 18099), H).serve_forever()
