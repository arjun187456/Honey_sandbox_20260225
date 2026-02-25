# Live Parallel Run Report (10 Bots)

## Run Metadata
- Report Generated (UTC): 2026-02-25 08:06:47 UTC
- Mode: `--live --confirm-live` (paper execution logic with live market feed)
- Strategy File: `breakout_algo_bot_v2.py`
- Parallel Instances Targeted: 10
- Active Processes Verified: 10

## What Was Completed In This Run
1. Cleaned existing live instances to avoid duplicate process count.
2. Launched 10 bot instances in parallel.
3. Verified exact active process count = 10.
4. Collected terminal health/output snapshots for all 10 instances.
5. Consolidated per-instance P&L and aggregate metrics.

## Active Process List (Current)
- 44039
- 44579
- 45268
- 45864
- 46529
- 47108
- 47811
- 48538
- 49559
- 50613

## Per-Instance Snapshot
| Bot | Terminal ID | Status | Active Trades | Closed Trades | Total P&L (₹) |
|---|---|---|---:|---:|---:|
| 1 | 7b25f26b-ab69-47f8-97cc-7b8efc63469f | Running | 0 | 2 | 7038.36 |
| 2 | 39d42ad2-d2a3-433d-88a2-027a23957ecb | Running | 0 | 2 | 6775.50 |
| 3 | 63ef5e3a-b044-4876-b7dd-6a2d9165eb31 | Running | 0 | 2 | 8385.88 |
| 4 | 5e0cfbd1-30ee-4ff9-bccd-bc46fd9ac479 | Running | 0 | 2 | 7668.03 |
| 5 | 126e3871-a09f-4ca7-b8b6-12a6fb3c8eb2 | Running | 0 | 2 | 7620.71 |
| 6 | 0ef58978-b177-4725-a755-3fcabcc1b080 | Running | 0 | 2 | 8383.38 |
| 7 | 918cdc7c-256c-4df5-87ea-bdd8beec1cae | Running | 0 | 2 | 8328.38 |
| 8 | 4462815d-4af2-4a3d-9b33-06e6fe82f72d | Running | 0 | 2 | 7588.20 |
| 9 | 535333f4-3425-48c4-8914-dc89703150a0 | Running | 0 | 2 | 7135.58 |
| 10 | 1a1398fd-21eb-4348-9603-95ca4a0cb281 | Running | 0 | 2 | 7213.08 |

## Aggregate Metrics (Snapshot)
- Instance Count: 10
- Sum of Total P&L: ₹76137.10
- Average P&L per Bot: ₹7613.71
- Minimum Bot P&L: ₹6775.50
- Maximum Bot P&L: ₹8385.88

## Notes
- All 10 instances are currently alive and continuing to monitor market data.
- In this snapshot, each bot has completed 2 closed trades and currently has no open trades.
- Multiple identical bots in parallel can duplicate exposure and amplify risk/account-level variance.

## Capital Placement and Investment Detail

### Configured Amount Per Bot
- Starting capital per bot: ₹10,000
- First trade budget per bot: ₹4,000
- Reversal trade budget per bot: ₹4,000
- Buffer per bot: ₹2,000
- Maximum deployable at any time per bot: ₹8,000

### Portfolio-Level Configured Capital (10 Bots)
- Total starting capital: ₹100,000
- Total first-trade budget: ₹40,000
- Total reversal budget: ₹40,000
- Total buffer: ₹20,000
- Maximum deployable simultaneously: ₹80,000

### Observed Per-Bot Deployment and P&L (from terminal logs)
| Bot | First Trade Capital Used (₹) | Reversal Capital Used (₹) | Total Deployed in 2 Trades (₹) | Current Invested Now (₹) | Total P&L (₹) |
|---|---:|---:|---:|---:|---:|
| 1 | 3281.64 | 3550.00 | 6831.64 | 0.00 | 7038.36 |
| 2 | N/A* | 3210.00 | N/A* | 0.00 | 6775.50 |
| 3 | 3234.12 | 3675.00 | 6909.12 | 0.00 | 8385.88 |
| 4 | 3951.97 | 3675.00 | 7626.97 | 0.00 | 7668.03 |
| 5 | 3579.29 | 3850.00 | 7429.29 | 0.00 | 7620.71 |
| 6 | 3236.62 | 3675.00 | 6911.62 | 0.00 | 8383.38 |
| 7 | 3239.12 | 3692.50 | 6931.62 | 0.00 | 8328.38 |
| 8 | 3611.81 | 3850.00 | 7461.81 | 0.00 | 7588.20 |
| 9 | 3851.93 | 3845.00 | 7696.93 | 0.00 | 7135.58 |
| 10 | N/A* | 3867.50 | N/A* | 0.00 | 7213.08 |

### Investment Summary (Observed)
- Bots currently with open positions: 0 of 10
- Current invested capital now (all bots combined): ₹0.00
- Known first-trade deployed (8 bots with visible value): ₹27,986.50
- Reversal deployed (all 10 bots): ₹36,890.00
- Known deployed total from visible logs: ₹64,876.50
- Total P&L across all 10 bots: ₹76,137.10

### P&L Interpretation
- Average P&L per bot: ₹7,613.71
- Best bot P&L: ₹8,385.88
- Lowest bot P&L: ₹6,775.50

\* N/A means the initial first-trade capital-used line was not present in the retained terminal buffer at snapshot time, so exact first-leg deployed value could not be extracted for that bot.
