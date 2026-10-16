# LeanTrader System Map

## Stages
0. Boot: container + secrets + Bybit testnet
1. Scanner: DYNAMIC_MARKET_SCANNER.py, 851 pairs -> trending
2. Signals: REAL_PROFIT_BOT (signals only, buys DISABLED) + wire_scanner_extractor.py
3. Execution: STEADY_PROFIT_EXTRACTOR.py, 21 fast pairs, 0.8% SL / 1.2% TP
4. Positions: spot_closer.py (legacy) + position_manager.py (extractor)
5. Risk: sizer.py, 0.25% per trade
6. Memory: PatternMemory, BrainMemory, CoreMemory

## Invariants
- RPB never buys (grep DISABLED: RPB)
- Extractor is sole trader
- Testnet only
