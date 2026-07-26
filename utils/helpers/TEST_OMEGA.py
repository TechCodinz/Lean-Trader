
import asyncio
from OMEGA_SINGULARITY_ENGINE import initialize_omega_engine
import logging

logging.basicConfig(level=logging.INFO)

class MockDataHub:
    pass

async def test():
    print("🧪 Testing Omega Singularity Engine...")
    hub = MockDataHub()
    engine = initialize_omega_engine(hub)
    
    # Test Data: Low Entropy, High Volatility, High Volume (Singularity Conditions)
    data = {
        'closes': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119], # Super consistent trend = Low Entropy
        'momentum': 0.5,
        'volume_spike': True,
        'volatility': 0.05,
        'volume_ratio': 2.0,
        'divergence_pct': 0.01
    }
    
    print("📊 Analyzer Input:", data)
    result = await engine.analyze("BTC/USDT", data)
    
    if result:
        print("[OK] SIGNAL GENERATED!")
        print(result)
    else:
        print("[X] No signal (Singularity score too low?)")

if __name__ == "__main__":
    asyncio.run(test())
