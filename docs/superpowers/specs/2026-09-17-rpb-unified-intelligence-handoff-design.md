# RPB Unified Intelligence and Execution Handoff Design

Date: 2026-09-17
Repository source of truth: `TechCodinz/Lean-Trader`
Implementation branch: `restore/rpb-unified-20260917`

## Purpose

Make `REAL_PROFIT_BOT` (RPB) the single order-producing LeanTrader engine while preserving and channeling the useful intelligence, research, evolution, learning, routing, universe, and position-management systems already present in the Lean-Trader repository.

`TechCodinz/LeanTrader-Bot` is legacy/archive material only and is not the implementation target for this handoff.

## Non-negotiable constraints

- `TechCodinz/Lean-Trader` is the source of truth.
- `REAL_PROFIT_BOT` remains the final execution owner.
- Only one process may submit orders for the selected wallet after cutover.
- Testnet remains the execution environment until the operator explicitly selects live mode; no automatic promotion to live.
- Existing Telegram admin/VIP/free routing is preserved.
- Existing evolution/research state is preserved; no reset or retraining-from-zero step.
- Existing authenticated position/cost-basis state is reconciled before execution authority changes.
- Research, evolution, councils, specialists, scouts, world models, and training components may advise RPB but may not independently place orders.
- No fabricated fills, prices, PnL, signals, or exchange evidence.
- Authoritative profit means authenticated realized net PnL after actual exchange costs.

## Target architecture

Public/real market data
→ existing Lean-Trader intelligence/evolution/research
→ bounded advisory evidence into RPB
→ REAL_PROFIT_BOT as single execution owner
→ authenticated order/fill
→ owned position lifecycle
→ authenticated close
→ actual fees + realized net PnL
→ wallet refresh
→ next size/compound
→ outcome feedback to persistent learners/evolution.

## Implementation rules

1. Reuse the current Lean-Trader universal router, preflight, universe registry, and runtime contracts rather than reintroducing duplicate exchange clients.
2. RPB consumes intelligence from existing production/evolution components without starting a second execution lane.
3. Missing or stale advisory intelligence fails open with diagnostics; it must not silently starve the original RPB loop.
4. ACK is not a fill. Position ownership is created only after authenticated/reconciled fill evidence.
5. SELL quantity is bounded by reconciled owned inventory.
6. Settled outcomes update learning only after actual realized PnL is known.
7. Current production-owned positions are adopted through an idempotent reconciliation step; ambiguous material inventory blocks cutover.
8. Cutover verifies a single execution authority before RPB is started.

## Acceptance criteria

- RPB is the only order-producing process for the selected Testnet wallet.
- Full useful Lean-Trader intelligence remains connected to RPB.
- Dynamic universe and current routing remain active.
- Authenticated BUY → fill → owned position → monitored exit → authenticated SELL → actual fees → realized net PnL is evidenced.
- Wallet balance is refreshed and subsequent sizing uses the authenticated balance.
- Telegram receives authenticated entry/settlement events without being able to interrupt trading.
- Restart restores RPB-owned positions and learner state.
- No live real-money authority is enabled automatically.

## Rollback

If any acceptance check fails, stop RPB before restoring any previous execution process. Never run the old and new executors simultaneously.
