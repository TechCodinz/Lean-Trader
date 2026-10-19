"""ML retrain v2 (2026-10-19 excavation): the live veto model was
trained by train_ml.py on 2000 UNBOUNDED 5m candles = the OLDEST
page = ~7 days of 2020 BTC. Same recipe, real era: paginated
since-bounded fetch of the last 120 days, then the system's own
UltraTrainer.train_full_system, saved to runtime/models/."""
import os
import sys
import time

os.chdir('/app')
sys.path.insert(0, '/app')

import ccxt
import pandas as pd

ex = ccxt.bybit({'enableRateLimit': True})
DAYS = 120
since = int((time.time() - DAYS * 86400) * 1000)
rows = []
while True:
    batch = ex.fetch_ohlcv('BTC/USDT', '5m', since, 1000)
    if not batch:
        break
    rows.extend(batch)
    last = batch[-1][0]
    if len(batch) < 1000 or last >= int(time.time() * 1000) - 300000:
        break
    since = last + 1
    time.sleep(0.25)
df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
print(f'data rows: {len(df)} from {df.timestamp.min()} to {df.timestamp.max()}', flush=True)
csv_path = 'runtime/train_BTCUSDT_v2.csv'
df.to_csv(csv_path, index=False)

from tools.ultra_trainer import UltraTrainer
tr = UltraTrainer()
res = tr.train_full_system(data_path=csv_path, symbol='BTC/USDT', task='classification')
print('ENSEMBLE:', res.get('ensemble'), flush=True)
print('MODEL_ID:', res.get('model_id'), flush=True)
print('ensemble_model set:', tr.ensemble_model is not None, flush=True)
print('TRAINING DONE', flush=True)
