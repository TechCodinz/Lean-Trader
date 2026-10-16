# Deploy 2025 - Fresh VPS in 15 min

1. git clone https://github.com/TechCodinz/Lean-Trader.git
2. Put keys in /root/secrets/bybit_testnet_*
3. docker build -t leantrader:2025 .
4. docker run -d --name leantrader-2025-testnet --restart unless-stopped -v /root/secrets:/run/secrets:ro leantrader:2025
5. Verify: docker exec leantrader-2025-testnet ps aux | grep python

See SYSTEM_MAP.md for architecture.
