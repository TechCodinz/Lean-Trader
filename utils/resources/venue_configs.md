# Pitch-Bent System Configuration Examples

## CEX Configuration (Bitcoin/Ethereum Perpetuals)

```python
from pitch_bent.models import VenueConfig, VenueType, StrategyWeight

cex_btc_config = VenueConfig(
    venue_type=VenueType.CEX,
    symbol_class="BTC_majors",
    feature_weights={
        # Common features
        'volatility_level': 1.5,
        'volatility_slope': 1.0,
        'momentum_acceleration': 0.8,
        'range_expansion': 1.2,
        'microstructure_noise': 0.9,
        # CEX-specific
        'spread_pressure': 0.7,
        'orderbook_imbalance': 1.0,
        'depth_to_spread_ratio': 0.8,
        'funding_pressure': 1.3  # Important for perps
    },
    pitch_curve_params={
        'lot_min': 0.4,      # Don't go below 40% size
        'lot_curve': 1.8,
        'sl_max': 1.8,
        'tp_max': 1.3
    }
)
```

## FOREX Configuration (XAUUSD Scalping)

```python
forex_xauusd_config = VenueConfig(
    venue_type=VenueType.FOREX,
    symbol_class="forex_metals",
    feature_weights={
        # Common features  
        'volatility_level': 1.8,  # Vol very important for gold
        'volatility_slope': 1.5,
        'momentum_acceleration': 1.0,
        'range_expansion': 1.3,
        'microstructure_noise': 1.1,
        # Forex-specific
        'spread_pressure': 1.0,
        'session_energy': 1.4,  # Session timing critical
        'spike_guard_score': 2.0  # News spikes common
    },
    pitch_curve_params={
        'lot_min': 0.3,      # More defensive on gold
        'lot_curve': 2.0,
        'sl_max': 2.2,       # Wider stops for volatility
        'tp_max': 1.2,
        'entry_delay_max': 4.0  # Longer cooldown
    }
)
```

## DEX Configuration (Low-Liquidity Altcoins)

```python
dex_lowliq_config = VenueConfig(
    venue_type=VenueType.DEX,
    symbol_class="dex_lowliq",
    feature_weights={
        # Common features
        'volatility_level': 1.0,
        'volatility_slope': 0.9,
        'momentum_acceleration': 0.7,
        'range_expansion': 1.0,
        'microstructure_noise': 0.8,
        # DEX-specific
        'pool_liquidity_score': 2.5,  # CRITICAL for low liq
        'price_impact_estimate': 2.0,
        'gas_stress_score': 1.5,
        'mev_risk_proxy': 2.0
    },
    pitch_curve_params={
        'lot_min': 0.2,      # Very conservative
        'lot_curve': 2.5,
        'sl_max': 3.0,       # Very wide stops for slippage
        'tp_max': 1.5,
        'entry_delay_max': 5.0
    }
)
```

## Usage Example

```python
from pitch_bent.integration import initialize_pitch_system, get_pitch_system
from pitch_bent.models import MarketState, VenueType

# Initialize system (do once at startup)
pitch_system = initialize_pitch_system(enable=True)

# In your trading loop:
market_state = MarketState(
    symbol="BTC/USDT",
    venue_type=VenueType.CEX,
    timeframe="5m",
    price_series=[50000, 50100, 50050, 50200, 50150],  # Recent closes
    spread=10.0,  # Optional
    funding_rate=0.0001  # Optional for perps
)

base_params = {
    'lot_size': 100,  # USD
    'sl_pct': 0.01,    # 1% stop
    'tp_pct': 0.02     # 2% target
}

# Get bent parameters
bent_params = pitch_system.get_bent_params(
    market_state,
    base_params,
    symbol_class="BTC_majors",
    feature_weights=cex_btc_config.feature_weights
)

# Apply bending
actual_lot = base_params['lot_size'] * bent_params.lot_multiplier
actual_sl = base_params['sl_pct'] * bent_params.sl_multiplier
actual_tp = base_params['tp_pct'] * bent_params.tp_multiplier

print(f"Pitch: {bent_params.pitch_value:.2f}")
print(f"Lot: ${base_params['lot_size']} -> ${actual_lot:.2f}")
print(f"SL: {base_params['sl_pct']*100}% -> {actual_sl*100:.2f}%")
print(f"TP: {base_params['tp_pct']*100}% -> {actual_tp*100:.2f}%")
```
