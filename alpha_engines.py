# alpha_engines.py

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

MEMO = Path("reports/alpha_memory.json")
MEMO.parent.mkdir(parents=True, exist_ok=True)

# ----------------- small utils -----------------
def _clip(x, lo, hi):
    return max(lo, min(hi, x))

def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def _softmax(xs: List[float]) -> List[float]:
    a = np.array(xs, dtype=float)
    a = a - np.max(a)
    e = np.exp(a)
    p = e / (np.sum(e) + 1e-12)
    return p.tolist()

def _load_memo() -> Dict[str, Any]:
    if MEMO.exists():
        try:
            return json.loads(MEMO.read_text())
        except Exception:
            pass
    return {"reliability": {}, "explore_eps": 0.08}

def _save_memo(obj: Dict[str, Any]):
    try:
        MEMO.write_text(json.dumps(obj, indent=2))
    except Exception:
        pass

# ----------------- Decision object -----------------
@dataclass
class Decision:
    side: Optional[str]  # 'buy' or None (flat)
    prob: float  # calibrated probability 0..1
    size_mult: float  # 0.5 .. 2.0 (use to scale stake/lots)
    sleep_secs: int  # adaptive loop pacing
    reasons: List[str]  # bullets/news/strategy cues
    notes: str  # short text about which strategies voted what
    votes: Dict[str, float]  # strategy->score
    features: Dict[str, float]  # useful for logging

# ----------------- Base class -----------------
class BaseStrategy:
    name = "base"

    def compute(self, df: pd.DataFrame, **kw) -> Dict[str, Any]:
        raise NotImplementedError

    # helpers
    @staticmethod
    def _ema(s: pd.Series, n: int) -> pd.Series:
        return s.ewm(span=n, adjust=False).mean()

    @staticmethod
    def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
        h, low, c = df["high"], df["low"], df["close"]
        pc = c.shift(1)
        tr = pd.concat([(h - low), (h - pc).abs(), (low - pc).abs()], axis=1).max(axis=1)
        return tr.rolling(n).mean()

    @staticmethod
    def _rsi(s: pd.Series, n: int) -> pd.Series:
        d = s.diff()
        up = (d.clip(lower=0)).ewm(alpha=1 / n, adjust=False).mean()
        dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
        rs = up / (dn + 1e-12)
        return 100 - (100 / (1 + rs))

# ----------------- “Naked” & Oscillator engines -----------------
class OscillatorConfluence(BaseStrategy):
    name = "osc_confluence"

    def __init__(
        self,
        rsi_len=10,
        stoch_k=9,
        stoch_d=3,
        stoch_smooth=3,
        macd_fast=6,
        macd_slow=13,
        macd_signal=9,
    ):
        self.rsi_len = rsi_len
        self.stoch_k = stoch_k
        self.stoch_d = stoch_d
        self.stoch_smooth = stoch_smooth
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def _stoch(self, h, low, c):
        ll = low.rolling(self.stoch_k).min()
        hh = h.rolling(self.stoch_k).max()
        k = 100 * (c - ll) / (hh - ll + 1e-12)
        k = k.rolling(self.stoch_smooth).mean()
        d = k.rolling(self.stoch_d).mean()
        return k, d

    def _macd(self, s):
        f = self._ema(s, self.macd_fast)
        sl = self._ema(s, self.macd_slow)
        m = f - sl
        sig = self._ema(m, self.macd_signal)
        return m, sig, (m - sig)

    def compute(self, df: pd.DataFrame, **kw):
        d = df
        rsi = self._rsi(d["close"], self.rsi_len)
        k, q = self._stoch(d["high"], d["low"], d["close"])
        macd, sig, hist = self._macd(d["close"])
        kx = (k > q) & (k.shift(1) <= q.shift(1))
        stoch_low = (k < 80) & (q < 80)
        rsi_ok = (rsi > 50) | ((rsi >= 48) & (rsi.diff() > 0))
        macd_up = hist.diff() > 0
        raw = float((kx & stoch_low & rsi_ok & macd_up).astype(int).iloc[-1])
        s = (
            0.40 * raw
            + 0.25 * _sigmoid((rsi.iloc[-1] - 50) / 5)
            + 0.35 * _sigmoid(hist.iloc[-1] * 6)
        )
        s = _clip(2 * s - 1, -1, 1)
        reasons = [f"Stoch K∧D, RSI={rsi.iloc[-1]:.1f}, MACDΔ={hist.iloc[-1]:.3f}"]
        feats = {
            "rsi": float(rsi.iloc[-1]),
            "macd_hist": float(hist.iloc[-1]),
            "k": float(k.iloc[-1]),
            "d": float(q.iloc[-1]),
        }
        return {"score": s, "reasons": reasons, "features": feats}

class NakedPriceAction(BaseStrategy):
    name = "naked_price"

    def __init__(self, body_mult=1.2):
        self.body_mult = body_mult

    def compute(self, df: pd.DataFrame, **kw):
        d = df.tail(5).copy()
        o, h, low, c = d["open"], d["high"], d["low"], d["close"]
        rng = (h - low).iloc[-1]
        body = abs(c - o).iloc[-1]
        # determine lower wick size
        _ = (h - c).iloc[-1] if c.iloc[-1] >= o.iloc[-1] else (h - o).iloc[-1]
        lower_wick = (o - low).iloc[-1] if c.iloc[-1] >= o.iloc[-1] else (c - low).iloc[-1]
        score = 0.0
        why = []
        if (
            c.iloc[-2] < o.iloc[-2]
            and c.iloc[-1] > o.iloc[-1]
            and c.iloc[-1] > o.iloc[-2]
            and o.iloc[-1] < c.iloc[-2]
        ):
            score += 0.6
            why.append("Bullish engulfing")
        if lower_wick > self.body_mult * body and lower_wick > 0.6 * rng:
            score += 0.5
            why.append("Bullish pin bar")
        score = _clip(score, 0, 1)
        score = 2 * score - 1
        feats = {"rng": float(rng), "body": float(body), "lw": float(lower_wick)}
        return {"score": score, "reasons": why, "features": feats}

# ----------------- Trend / Breakout engines -----------------
class TrendSqueeze(BaseStrategy):
    name = "trend_squeeze"

    def __init__(self, ema_fast=50, ema_slow=200, bb_period=20, bb_std=2.0):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.bb_period = bb_period
        self.bb_std = bb_std

    def compute(self, df: pd.DataFrame, **kw):
        c = df["close"]
        ema_f = self._ema(c, self.ema_fast)
        ema_s = self._ema(c, self.ema_slow)
        ma = c.rolling(self.bb_period).mean()
        sd = c.rolling(self.bb_period).std(ddof=0)
        upper = ma + self.bb_std * sd
        lower = ma - self.bb_std * sd
        bw = (upper - lower) / (ma.replace(0, np.nan))
        squeeze = bw <= bw.rolling(120).quantile(0.5, interpolation="nearest")
        breakout = (c > upper.shift(1)) & squeeze.fillna(False)
        trend = ema_f > ema_s
        raw = float((breakout & trend).astype(int).iloc[-1])
        slope = float((ema_f - ema_s).iloc[-1])
        s = 0.6 * raw + 0.4 * _sigmoid(50 * slope / (abs(c.iloc[-1]) + 1e-9))
        s = _clip(2 * s - 1, -1, 1)
        reasons = [f"EMA {self.ema_fast}/{self.ema_slow} up, BB breakout"]
        feats = {
            "ema_spread": float(ema_f.iloc[-1] - ema_s.iloc[-1]),
            "bb_bw": float(bw.iloc[-1]) if pd.notna(bw.iloc[-1]) else 0.0,
        }
        return {"score": s, "reasons": reasons, "features": feats}

class DonchianBreakout(BaseStrategy):
    name = "donchian"

    def __init__(self, lookback=55):
        self.lookback = lookback

    def compute(self, df: pd.DataFrame, **kw):
        hh = df["high"].rolling(self.lookback).max()
        ll = df["low"].rolling(self.lookback).min()
        c = df["close"]
        raw = float((c.iloc[-1] >= hh.iloc[-2]).astype(int))
        mid = (hh + ll) / 2
        z = (c - mid) / ((hh - ll) / 2 + 1e-12)
        s = 0.6 * raw + 0.4 * _sigmoid(float(z.iloc[-1]))
        s = _clip(2 * s - 1, -1, 1)
        return {
            "score": s,
            "reasons": [f"Donchian {self.lookback} breakout"],
            "features": {"z": float(z.iloc[-1])},
        }

class KeltnerBreakout(BaseStrategy):
    name = "keltner"

    def __init__(self, ema_len=20, atr_mult=2.0):
        self.ema_len = ema_len
        self.atr_mult = atr_mult

    def compute(self, df: pd.DataFrame, **kw):
        ema = self._ema(df["close"], self.ema_len)
        atr = self._atr(df, 20)
        upper = ema + self.atr_mult * atr
        raw = float((df["close"].iloc[-1] > upper.iloc[-1]).astype(int))
        s = 0.7 * raw + 0.3 * _sigmoid(
            (df["close"].iloc[-1] - ema.iloc[-1]) / (atr.iloc[-1] + 1e-12)
        )
        s = _clip(2 * s - 1, -1, 1)
        return {
            "score": s,
            "reasons": [f"Keltner breakout {self.ema_len}/{self.atr_mult}"],
            "features": {"atr": float(atr.iloc[-1]) if pd.notna(atr.iloc[-1]) else 0.0},
        }

# ----------------- Reversion / Flow engines -----------------
class VWAPBounce(BaseStrategy):
    name = "vwap_revert"

    def compute(self, df: pd.DataFrame, **kw):
        p = df["close"]
        v = df["vol"]
        pv = (p * v).rolling(120).sum()
        vv = v.rolling(120).sum()
        vwap = pv / (vv + 1e-12)
        dist = (vwap - p) / (p + 1e-12)
        rising = p.diff().iloc[-1] > 0 and p.iloc[-1] < vwap.iloc[-1]
        s = 0.5 * _sigmoid(500 * float(dist.iloc[-1])) + (0.5 if rising else 0.0)
        s = _clip(2 * s - 1, -1, 1)
        return {
            "score": s,
            "reasons": [f"VWAP revert {float(dist.iloc[-1])*100:.2f}%"],
            "features": {"vwap_dist": float(dist.iloc[-1])},
        }

class VolumeSpike(BaseStrategy):
    name = "vol_spike"

    def compute(self, df: pd.DataFrame, **kw):
        vol = df["vol"]
        z = (vol - vol.rolling(50).mean()) / (vol.rolling(50).std(ddof=0) + 1e-9)
        # determine direction of last bar
        upbar = float((df["close"].iloc[-1] > df["open"].iloc[-1]).astype(int))
        s = _clip(2 * (_sigmoid(0.7 * z.iloc[-1]) * (0.6 * upbar + 0.4)) - 1, -1, 1)
        return {
            "score": s,
            "reasons": [f"Vol spike z={z.iloc[-1]:.2f}"],
            "features": {"vol_z": float(z.iloc[-1])},
        }

class MomentumThrust(BaseStrategy):
    """RPB transplant (2026-10-20): the Real Profit Bot's momentum
    brain - 24h price thrust confirmed by volume - as an ensemble
    voter. RPB fired alone with invented profit accounting and no
    exits; here its signal votes under the router's learned
    reliability and the fleet's real exit machinery."""
    name = "momentum_thrust"

    def compute(self, df: pd.DataFrame, **kw):
        try:
            close = df["close"]
            vol = df["vol"]
            if len(close) < 30:
                return {"score": 0.0, "reasons": ["thrust: short df"],
                        "features": {}}
            # bars spanning ~24h, inferred from the index spacing
            k = 24
            try:
                idx = df.index
                if len(idx) > 2:
                    step_h = (idx[-1] - idx[-2]).total_seconds() / 3600.0
                    if step_h > 0:
                        k = max(4, min(96, int(round(24.0 / step_h))))
            except Exception:
                pass
            k = min(k, len(close) - 1)
            thrust = float(close.iloc[-1] / close.iloc[-k] - 1.0)
            vmean = float(vol.rolling(50).mean().iloc[-1] or 0)
            vrecent = float(vol.iloc[-3:].mean() or 0)
            vratio = (vrecent / vmean) if vmean > 0 else 1.0
            # RPB tiers: 1.5% stirs, 3% fires, 5%+ is a moonshot
            mag = abs(thrust)
            if mag < 0.015:
                base = mag / 0.015 * 0.25
            elif mag < 0.03:
                base = 0.25 + (mag - 0.015) / 0.015 * 0.45
            elif mag < 0.05:
                base = 0.70 + (mag - 0.03) / 0.02 * 0.20
            else:
                base = 0.95
            score = base if thrust > 0 else -base
            if vratio < 0.8:  # no volume, no conviction (RPB's rule)
                score *= 0.5
            elif vratio > 1.5:
                score *= 1.1
            return {"score": _clip(score, -1, 1),
                    "reasons": [f"Thrust {thrust * 100:+.1f}%/24h "
                                f"volx{vratio:.1f}"],
                    "features": {"thrust": thrust, "vratio": vratio}}
        except Exception as e:
            return {"score": 0.0, "reasons": [f"thrust err {e}"],
                    "features": {}}

# ----------------- Regime / Session filters -----------------
class VolumeProfile(BaseStrategy):
    """Transplant (2026-10-20): critical_features_addon's
    VolumeProfileAnalyzer as an ensemble voter. Where price sits
    against the volume profile's value area carries information
    the price-only strategies cannot see: above the value-area
    high, buyers have accepted higher prices (continuation lean);
    below the value-area low, acceptance sits lower (bearish
    lean); inside the area, price is near fair value - a mild
    pull toward the point of control. Distance is normalized by
    the value area's width and capped."""
    name = "volume_profile"
    _analyzer = None

    def compute(self, df: pd.DataFrame, **kw):
        try:
            if len(df) < 100:
                return {"score": 0.0, "reasons": ["vp: short df"],
                        "features": {}}
            if VolumeProfile._analyzer is None:
                from critical_features_addon import VolumeProfileAnalyzer
                VolumeProfile._analyzer = VolumeProfileAnalyzer()
            view = df.tail(110).copy()
            if 'volume' not in view.columns and 'vol' in view.columns:
                view['volume'] = view['vol']
            res = VolumeProfile._analyzer.analyze(view)
            if not res:
                return {"score": 0.0, "reasons": ["vp: no profile"],
                        "features": {}}
            close = float(view['close'].iloc[-1])
            vah = float(res['value_area_high'])
            val = float(res['value_area_low'])
            poc = float(res['poc'])
            width = max(vah - val, close * 0.0005)
            if close > vah:
                score = min(1.0, (close - vah) / width)
                why = f"vp: above value area (POC {poc:.4g})"
            elif close < val:
                score = -min(1.0, (val - close) / width)
                why = f"vp: below value area (POC {poc:.4g})"
            else:
                score = max(-0.4, min(0.4, (poc - close) / width * 0.5))
                why = f"vp: inside value area, POC pull (POC {poc:.4g})"
            return {"score": float(score), "reasons": [why],
                    "features": {"poc": poc, "vah": vah, "val": val}}
        except Exception as e:
            return {"score": 0.0, "reasons": [f"vp: {e}"],
                    "features": {}}


def _anis_lloyd(n):
    """E[R/S_n] for i.i.d. Gaussian of length n (Anis & Lloyd 1976).
    Opus fine-tune deliverable, verified 2026-10-20."""
    import math as _m
    if n < 3:
        return 1.0
    gamma_ratio = _m.exp(_m.lgamma((n - 1) / 2.0) - _m.lgamma(n / 2.0))
    tot = 0.0
    for i in range(1, n):
        tot += _m.sqrt((n - i) / i)
    return gamma_ratio * tot / _m.sqrt(_m.pi)


def hurst_multiwindow(prices):
    """Multi-window R/S Hurst exponent with Anis-Lloyd correction
    (Opus fine-tune, 2026-10-20 - replaces the single-window R/S
    that was biased toward 0.5). Independent verification on a
    10-seed suite: persistent tapes 0.573, anti-persistent 0.424,
    pure walks centered 0.498 (old estimator: 0.576 / 0.468 /
    0.521 biased). ~0.3 ms at 160 prices, pure math."""
    import math as _m
    N = len(prices)
    if N < 40:
        return 0.5
    log_ret = []
    for i in range(1, N):
        if prices[i] <= 0 or prices[i - 1] <= 0:
            return 0.5
        log_ret.append(_m.log(prices[i] / prices[i - 1]))
    M = len(log_ret)
    if M < 20:
        return 0.5
    max_win = M // 2
    if max_win < 8:
        return 0.5
    windows = []
    n = 8
    while n <= max_win:
        windows.append(n)
        next_n = int(n * 1.3) + 1
        n = next_n if next_n > n else n + 1
    if len(windows) < 6:
        step = max(1, (max_win - 8) // 7)
        windows = list(range(8, max_win + 1, step))
    if len(windows) < 4:
        return 0.5
    log_n, log_rs = [], []
    for win in windows:
        num_subs = M // win
        if num_subs < 1:
            continue
        rs_sum, valid = 0.0, 0
        for s_idx in range(num_subs):
            chunk = log_ret[s_idx * win:(s_idx + 1) * win]
            mu = sum(chunk) / win
            cum = lo = hi = ss = 0.0
            for v in chunk:
                d = v - mu
                cum += d
                lo = min(lo, cum)
                hi = max(hi, cum)
                ss += d * d
            S = _m.sqrt(ss / win)
            if S < 1e-15:
                continue
            rs_sum += (hi - lo) / S
            valid += 1
        if valid == 0:
            continue
        avg_rs = rs_sum / valid
        e_al = _anis_lloyd(win)
        if avg_rs <= 0 or e_al <= 0:
            continue
        corrected = avg_rs / e_al
        if corrected <= 0:
            continue
        log_n.append(_m.log(win))
        log_rs.append(_m.log(corrected))
    if len(log_n) < 4:
        return 0.5
    k = len(log_n)
    sx = sum(log_n)
    sy = sum(log_rs)
    sxx = sum(x * x for x in log_n)
    sxy = sum(x * y for x, y in zip(log_n, log_rs))
    denom = k * sxx - sx * sx
    if abs(denom) < 1e-30:
        return 0.5
    H = 0.5 + (k * sxy - sx * sy) / denom
    return max(0.05, min(0.95, H))


class FractalRegime(BaseStrategy):
    """Excavated 2025 logic (DIVINE_INTELLIGENCE_FEATURES'
    FractalDimensionAnalyzer, wired 2026-10-20): a regime voter.
    The Hurst exponent on closes classifies the tape - trending
    (H > 0.55): vote WITH the recent direction; mean-reverting
    (H < 0.45): vote AGAINST it (fade); near 0.5 (random walk):
    abstain. The ensemble had no regime-conditional voter:
    momentum strategies fired in chop and reversion strategies
    fired in trends; this voter leans the other way in each."""
    name = "fractal_regime"
    _analyzer = None

    def compute(self, df: pd.DataFrame, **kw):
        try:
            close = df["close"]
            if len(close) < 40:
                return {"score": 0.0, "reasons": ["fractal: short df"],
                        "features": {}}
            prices = [float(x) for x in close.tolist()[-200:]]
            hurst = float(hurst_multiwindow(prices))
            look = min(20, len(prices) - 1)
            direction = 1.0 if prices[-1] > prices[-1 - look] else -1.0
            if hurst > 0.55:
                strength = max(0.0, min(1.0, (hurst - 0.55) / 0.20))
                score = direction * (0.3 + 0.7 * strength)
                why = f"fractal: H={hurst:.2f} trending, follow"
            elif hurst < 0.45:
                strength = max(0.0, min(1.0, (0.45 - hurst) / 0.20))
                score = -direction * (0.3 + 0.7 * strength)
                why = f"fractal: H={hurst:.2f} reverting, fade"
            else:
                score = 0.0
                why = f"fractal: H={hurst:.2f} random walk, abstain"
            return {"score": float(max(-1.0, min(1.0, score))),
                    "reasons": [why], "features": {"hurst": hurst}}
        except Exception as e:
            return {"score": 0.0, "reasons": [f"fractal: {e}"],
                    "features": {}}


class VolRegime(BaseStrategy):
    name = "regime"

    def compute(self, df: pd.DataFrame, **kw):
        atr = self._atr(df, 14)
        vol_norm = (atr / (df["close"] + 1e-12)).rolling(50).mean()
        s = _clip(_sigmoid(200 * float((vol_norm.iloc[-1] or 0))) - 0.5, -1, 1)  # prefer higher vol
        return {
            "score": s,
            "reasons": [f"Vol regime {(vol_norm.iloc[-1] or 0):.4f}"],
            "features": {"vol_norm": float(vol_norm.iloc[-1] or 0)},
        }

class SessionBias(BaseStrategy):
    name = "session_bias"

    def compute(self, df: pd.DataFrame, **kw):
        # approximate: use last 400 bars time drift to hour-of-day bias
        ts = pd.to_datetime(df["ts"], unit="ms")
        hour = ts.dt.hour.iloc[-1] if "ts" in df else 12
        # mild institutional bias: 13:00-17:00 UTC risk-on
        bias = 1.0 if 13 <= int(hour) <= 17 else 0.0
        s = 0.3 * bias
        return {
            "score": s,
            "reasons": [f"Session hour={hour} bias={bias:.1f}"],
            "features": {"hour": float(hour)},
        }

# ----------------- Alpha Router -----------------

_STUDY_CACHE = {'mtime': 0.0, 'data': {}}


def _study_tilt(symbol):
    """Fleet pair-study tilt for a symbol: the measured expectancy
    of EVERY being's real closes on this pair (pair_study.json),
    sample-scaled and capped - knowledge weight, never a veto."""
    import json as _j
    import os as _os
    path = '/app/runtime/pair_study.json'
    try:
        m = _os.path.getmtime(path)
    except Exception:
        return 0.0
    if m != _STUDY_CACHE['mtime']:
        try:
            with open(path) as f:
                _STUDY_CACHE['data'] = _j.load(f)
            _STUDY_CACHE['mtime'] = m
        except Exception:
            return 0.0
    e = _STUDY_CACHE['data'].get(symbol)
    if not e:
        return 0.0
    n = int(e.get('trades') or 0)
    if n < 5:
        return 0.0
    exp = float(e.get('expectancy') or 0.0)
    return max(-0.06, min(0.06, exp * 0.5)) * min(1.0, n / 25.0)


class AlphaRouter:
    """
    Fuses many strategies, calibrates to probability, adapts by (symbol,timeframe).
    Exploration via epsilon-greedy; reliability updated externally via update_reliability().
    """

    def __init__(self):
        self.strats: List[BaseStrategy] = [
            OscillatorConfluence(),
            TrendSqueeze(),
            NakedPriceAction(),
            DonchianBreakout(),
            KeltnerBreakout(),
            VWAPBounce(),
            VolumeSpike(),
            MomentumThrust(),
            FractalRegime(),
            VolumeProfile(),
            VolRegime(),
            SessionBias(),
        ]
        self.memo = _load_memo()

    def _key(self, symbol: str, timeframe: str) -> str:
        return f"{symbol}|{timeframe}"

    def _weights_for(self, symbol: str, timeframe: str) -> Dict[str, float]:
        r = self.memo.get("reliability", {})
        key = self._key(symbol, timeframe)
        return r.get(key, {})

    def pick(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        base_reasons: Optional[List[str]] = None,
    ) -> Decision:
        base_reasons = base_reasons or []
        votes: Dict[str, float] = {}
        notes = []
        feats: Dict[str, float] = {}

        for s in self.strats:
            try:
                out = s.compute(df)
                score = float(out.get("score", 0.0))
                votes[s.name] = _clip(score, -1, 1)
                for k, v in (out.get("features") or {}).items():
                    feats[f"{s.name}.{k}"] = float(v)
                if out.get("reasons"):
                    notes.append(f"{s.name}: " + "; ".join(out["reasons"][:2]))
            except Exception:
                votes[s.name] = 0.0

        # per-strategy probabilities
        probs = {k: _sigmoid(2.2 * v) for k, v in votes.items()}
        # reliability weights
        ws = self._weights_for(symbol, timeframe)
        weights = {k: max(0.2, ws.get(k, 1.0)) for k in votes.keys()}

        # ensemble probability
        p = sum(probs[k] * weights[k] for k in votes) / (sum(weights.values()) + 1e-12)

        # exploration: occasionally trust a strong voter
        if random.random() < float(self.memo.get("explore_eps", 0.08)):
            k_max = max(votes, key=lambda k: votes[k])
            p = 0.65 + 0.25 * votes[k_max]

        # PAIR STUDY tilt (Princewill's awareness design): the
        # fleet's lived record on this pair weighs the ensemble's
        # confidence before the side is called. A studied pair that
        # has hurt the fleet drags confidence a few points; a proven
        # pair lifts it. Capped and sample-scaled in _study_tilt -
        # it can shade a marginal call, never veto a strong one.
        try:
            _tilt = _study_tilt(symbol)
            if _tilt:
                p = _clip(p + _tilt, 0.01, 0.99)
                notes.append(f"study tilt {_tilt:+.3f} ({symbol})")
        except Exception:
            pass

        # Bidirectional (restored 2026-10-20, Opus audit Fix #1 -
        # verified live): the 2025 core, both execution arms and
        # the risk manager were always side-aware; only this line
        # had forgotten how to say "sell", so every downtrend was
        # dead time. Symmetric thresholds: p >= 0.58 long,
        # p <= 0.42 short, between them the ensemble abstains.
        _thr = self._adaptive_threshold()
        if p >= _thr:
            side = "buy"
        elif p <= 1.0 - _thr:
            side = "sell"
        else:
            side = None
        if abs(_thr - 0.58) > 1e-9:
            notes.append(f"adaptive thr {_thr:.2f} "
                         f"(calib n={len(self.memo.get('calib') or [])})")
        size_mult = _clip(0.5 + 1.5 * (p - 0.5) / 0.5, 0.5, 2.0)
        sleep = 5 if p > 0.7 else 8 if p > 0.6 else 12

        reasons = list(base_reasons)[:3]
        for n in notes[:2]:
            reasons.append("• " + n)

        note = " | ".join(notes[:3])
        return Decision(
            side=side,
            prob=float(p),
            size_mult=float(size_mult),
            sleep_secs=int(sleep),
            reasons=reasons,
            notes=note,
            votes=votes,
            features=feats,
        )

    def _save_merged(self):
        """Multi-writer safe save: the zoo (1h) and the orchestrator
        service (15m/1h) both teach this memo from separate
        processes; a blind overwrite would erase the other writer's
        learning on every save. Reload and merge instead:
        reliability cells merge per key (this writer wins the cells
        it touched), calibration rows merge as a multiset union
        (duplicates from distinct trades survive)."""
        try:
            cur = _load_memo()
            rel = dict(cur.get('rel') or {})
            rel.update(self.memo.get('rel') or {})
            from collections import Counter
            cur_rows = [tuple(r) for r in (cur.get('calib') or [])]
            my_rows = [tuple(r) for r in (self.memo.get('calib') or [])]
            extra = list((Counter(my_rows) - Counter(cur_rows)).elements())
            merged = dict(self.memo)
            merged['rel'] = rel
            merged['calib'] = [list(r) for r in (cur_rows + extra)][-300:]
            self.memo = merged
            _save_memo(merged)
        except Exception:
            try:
                _save_memo(self.memo)
            except Exception:
                pass

    def note_outcome(self, conviction: float, pnl: float):
        """Calibration feed: a router-attributed trade closed.
        Records (conviction, win) in the memo so the decision
        threshold can be set by evidence, not by hand."""
        try:
            c = self.memo.setdefault('calib', [])
            c.append([round(float(conviction), 3), 1 if pnl > 0 else 0])
            del c[:-300]
            self.memo['calib'] = c
            self._save_merged()
        except Exception:
            pass

    def _adaptive_threshold(self) -> float:
        """The intelligent threshold (Princewill, 2026-10-20:
        'make it intelligent, not manual'). The bar floats to the
        lowest conviction band whose realized record pays under
        the fleet's payoff math (+2% target / -1% stop: a band
        clears at ~45% win rate after fees at these notionals).
        Bands are 0.10 wide, sliding by 0.05, needing >= 8
        attributed closes. Bounded [0.52, 0.65]; until 30
        attributed closes exist at all, the designed 0.58 stands.
        If NO band pays, the bar rises to the 0.65 cap - the
        system trades only its best ideas until evidence earns
        it more room."""
        c = self.memo.get('calib') or []
        if len(c) < 30:
            return 0.58
        for lo in (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
            rows = [w for p, w in c if lo <= p < lo + 0.10]
            if len(rows) >= 8 and (sum(rows) / len(rows)) >= 0.45:
                return max(0.52, min(0.65, lo + 0.02))
        return 0.65

    def update_reliability(self, symbol: str, timeframe: str, strat_name: str, reward: float):
        r = self.memo.setdefault("reliability", {})
        key = self._key(symbol, timeframe)
        row = r.setdefault(key, {})
        w = float(row.get(strat_name, 1.0))
        # Recalibrated 2026-10-20 (Princewill approved): the
        # reward arriving here is bounded to +/-1 by the
        # callers, so tanh(reward/100) made every step
        # ~0.001 - after 500+ closes all weights still sat
        # at 1.000, i.e. the router was not learning. The
        # step is now 0.1*tanh(reward) (~0.076 at full
        # reward), same [0.2, 3.0] clip.
        w = _clip(w + 0.1 * np.tanh(reward), 0.2, 3.0)
        row[strat_name] = float(w)
        self._save_merged()
