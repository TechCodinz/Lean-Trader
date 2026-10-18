"""One-off ML training run: fetch BTC/USDT 5m data, train the UltraTrainer
ensemble via the system's own train_full_system (CSV path), save models to
runtime/models/ so the trader's pipeline loads them at startup."""
import os, sys
os.chdir('/app')
sys.path.insert(0, '/app')

import ccxt, pandas as pd

ex = ccxt.bybit()
rows = ex.fetch_ohlcv('BTC/USDT', '5m', limit=2000)
df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
os.makedirs('runtime', exist_ok=True)
csv_path = 'runtime/train_BTCUSDT.csv'
df.to_csv(csv_path, index=False)
print(f'data rows: {len(df)} -> {csv_path}', flush=True)

from tools.ultra_trainer import UltraTrainer
tr = UltraTrainer()
res = tr.train_full_system(data_path=csv_path, symbol='BTC/USDT', task='classification')
print('ENSEMBLE:', res.get('ensemble'), flush=True)
print('MODEL_ID:', res.get('model_id'), flush=True)
print('ensemble_model set:', tr.ensemble_model is not None, flush=True)
print('TRAINING DONE', flush=True)
