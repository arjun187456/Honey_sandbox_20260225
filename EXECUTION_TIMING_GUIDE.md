# 🕒 Bot Execution Timing & Data Flow Guide

## Overview

Your bot uses a **Hybrid Approach**: Historical Data (Phase 1) + Live Data (Phase 2) with a **Strict 10:00 AM Time Gate**.

---

## 📊 Two-Phase Architecture

### **Phase 1: Historical Data Synchronization** ⏱️ ~2-5 seconds
**When:** Bot startup (any time between 9:15 AM - 3:30 PM)  
**What:** Scans past market data from 9:15 AM to current time  
**Why:** Captures the high/low of the day even if you start late  
**Data Source:** `fetch_historical_high()` function

#### Example:
```
Start Time        Market Data Scanned       High Identified
9:30 AM           9:15-9:30 (15 min)       Call: ₹85.60, Put: ₹68.20
10:45 AM          9:15-10:45 (90 min)      Call: ₹87.25, Put: ₹70.50
2:00 PM           9:15-2:00 (285 min)      Call: ₹89.10, Put: ₹71.80
```

### **Phase 2: Live Monitoring** ⏱️ Continuous (every 2 seconds)
**When:** After Phase 1 completes until 3:30 PM  
**What:** Real-time price tracking and breakout detection  
**Data Source:** Live LTP (Last Traded Price) from Upstox API  
**Frequency:** Updates every 2 seconds  

---

## 🚨 **NEW: 10:00 AM Time Gate**

### What is the Time Gate?
The bot **will NOT execute any trades before 10:00 AM IST**, regardless of breakouts.

### Why?
- Ensures you follow the "10 AM Breakout Strategy" strictly
- Avoids morning volatility and false breakouts (9:15-10:00 AM)
- Aligns with the original algorithm design
- Gives the market 45 minutes to establish direction

### How It Works

```python
if 10:00:00 AM <= current_time <= 3:10:00 PM:
    TRADES ALLOWED ✅
else:
    TRADES BLOCKED ❌
    Status: "Waiting for 10:00 AM Time Gate..."
```

### Execution Timeline Examples

#### **Scenario 1: Start at 9:30 AM**
```
Time        Action                              Data Used
9:30:02     Bot starts                          -
9:30:05     Phase 1: Scan 9:15-9:30 (15 min)   Historical
9:30:07     Phase 1 Complete ✅                 Historical
9:30:08     Detect breakout in CALL option      Live (but blocked!)
9:30:09     Status: "Waiting for 10:00 AM..."   -
...
10:00:01    🚨 Time Gate Opens! ✅               Live
10:00:05    Execute entry trade immediately    Live (with slippage buffer)
```

#### **Scenario 2: Start at 11:30 AM**
```
Time        Action                              Data Used
11:30:02    Bot starts                          -
11:30:05    Phase 1: Scan 9:15-11:30 (135 min) Historical (includes 10 AM high!)
11:30:10    Phase 1 Complete ✅                 Historical
11:30:12    CALL high already identified        Historical
11:30:15    Check if already broken since 10AM Live (from Phase 1 snapshots)
11:30:20    Detect new breakout above 11 AM    Live (Gate open because it's 11:30)
11:30:22    Execute entry immediately! ✅      Live (with slippage buffer)
```

#### **Scenario 3: Start at 2:45 PM**
```
Time        Action                              Data Used
14:45:02    Bot starts                          -
14:45:05    Phase 1: Scan 9:15-2:45 (345 min)  Historical
14:45:10    Phase 1 Complete ✅                 Historical
14:45:15    Identify day high from 9:15-2:45   Historical
14:45:20    Check: Has price already broken?   Historical data
14:45:25    If NOT broken: Wait for breakout   Live (Gate open)
14:45:30    ALERT: Only 45 min until market close (3:30 PM)
```

---

## 🎯 Data Sources Breakdown

### Historical Data (Phase 1 Only)
| Component | Source | Frequency | Why |
|-----------|--------|-----------|-----|
| Option Chain | Upstox `/option/chain` | Once at startup | Get all strikes available |
| Spot Price History | Upstox market history | Once at startup | Identify ATM strike |
| Call High (9:15-Now) | Scan all CALL LTPs | Once at startup | Trigger level for Call breakout |
| Put High (9:15-Now) | Scan all PUT LTPs | Once at startup | Trigger level for Put breakout |

### Live Data (Phase 2 Only)
| Component | Source | Frequency | Why |
|-----------|--------|-----------|-----|
| Spot LTP | Upstox `/market-quote/ltp` | Every 2 seconds | Current Nifty price |
| Call LTP | Upstox option chain | Every 2 seconds | Real-time option prices |
| Put LTP | Upstox option chain | Every 2 seconds | Real-time option prices |
| P&L Tracking | Live prices | Every 2 seconds | Monitor stops/profits |

---

## 💰 Slippage Buffer (NEW: 0.05%)

### What is Slippage?
Slippage = Difference between quoted price and actual execution price

### Implementation
When you get a breakout signal at **₹70.22**, the bot adds a **0.05% cushion**:
```
Quoted Price:  ₹70.22
Slippage Buffer: ₹70.22 × 1.0005 = ₹70.255
Actual Order: BUY at ₹70.26 (unfavorable but ensures fill)
```

### Why This Matters
- **Ensures your order gets filled** at breakout moment
- **Small cost** (₹0.03 per ₹70 option = 0.04%)
- **Prevents missed trades** due to price gaps
- **Standard in professional trading**

### Examples
```
Option Price    With Slippage (0.05%)    Cost of Slippage
₹50.00          ₹50.025                  ₹0.025 (0.05%)
₹100.00         ₹100.05                  ₹0.05 (0.05%)
₹200.00         ₹200.10                  ₹0.10 (0.05%)
```

---

## 📈 Real-Time P&L Calculation

### How Trailing Stop-Loss Works with Live Data

**Entry:** 10:05 AM → BUY CALL at ₹100  
**Initial SL:** ₹90 (-10%)  
**Initial TP:** ₹110 (+10%)

```
Time      Price    P&L %   Trail Active?  New SL      Status
10:05     100.00   0%      NO             90.00       Entry
10:15     102.50   +2.5%   NO             90.00       Open
10:25     110.00   +10%    YES ⭐        104.00      Trail Activated
10:35     111.50   +11.5%  YES            105.50      Moving with price
10:45     110.00   +10%    YES            105.50      Still protected
10:55     105.50   +5.5%   YES            105.50      STOP LOSS HIT! 🛑
11:00     -        -       -              -           EXIT (5% profit secured)
```

**Key Point:** Every ₹1 price increase = ₹1 SL increase (lock-step)

---

## ⏰ Important Time Rules

| Time | Status | Action |
|------|--------|--------|
| 9:15 AM | Market Opens | Bot can start anytime |
| 9:15 - 9:59 AM | No Trading | Phase 1 scans history, Phase 2 monitors but NO entries |
| 10:00 AM | 🟢 Gate Opens | First trade possible |
| 10:00 - 3:10 PM | 🟢 Trading Active | Can enter new trades |
| 3:10 - 3:30 PM | 🟡 Exit Only | No new trades, close existing positions |
| 3:30 PM | Market Closes | Bot auto-closes all positions |

---

## 🔧 Configuration You Can Modify

Open `breakout_algo_bot_v2.py` and adjust these:

```python
# Line ~49 - Change trading time gate
TRADING_START_TIME = dt_time(10, 0, 0)   # Change from 10:00 AM
NEW_ORDER_CUTOFF = dt_time(15, 10, 0)   # Change from 3:10 PM
SLIPPAGE_BUFFER = 0.0005                # Change from 0.05% to any %

# Example: Start trading at 9:45 AM instead
TRADING_START_TIME = dt_time(9, 45, 0)  # Breakout at 9:45 AM OK

# Example: Reduce slippage to 0.02%
SLIPPAGE_BUFFER = 0.0002
```

---

## 📋 Troubleshooting Timing Issues

### Problem: "Waiting for 10:00 AM Time Gate" message appears
**Solution:** This is CORRECT behavior if you start at 9:30-9:59 AM. Bot is designed to wait.

### Problem: No trades by 3:00 PM
**Solution:** Market was flat before 10:00 AM and hasn't broken high yet. Market drifts some days.

### Problem: Entry price different from displayed price
**Solution:** This is the slippage buffer (+0.05%). It ensures order fills. Check both prices in the log:
```
Market Price:             ₹70.22
Entry Price (w/Slippage): ₹70.26  ← This is actual execution
```

### Problem: Bot not starting
**Double check:**
```
1. Time between 9:15 AM - 3:30 PM? ✓
2. API token valid in .env file? ✓
3. Market is OPEN (Mon-Fri, not holidays)? ✓
```

---

## 📊 Testing the Timing

### Test During Market Hours
```bash
# Safe test mode - won't execute real trades
python3 breakout_algo_bot_v2.py --test --duration 10
```

### Expected Output (Test Mode)
```
✅ Phase 1: HISTORY SYNCHRONIZATION (09:30:15)
   Nifty 50 Spot: ₹25,564.10
   ATM Call Strike: ₹25,550.0
   ATM Call LTP: ₹85.60 (Trigger: ₹85.69)
   
✅ SYNC COMPLETE - Ready to detect breakouts

🔄 PHASE 2: LIVE MONITORING
Waiting for breakout signal...

⏰ [09:30:45] LIVE UPDATE
   No breakouts yet (waiting for 10:00 AM Gate to open)
   
🚀 [10:01:30] ENTRY SIGNAL DETECTED! - CALL BREAKOUT
   Market Price: ₹85.90
   Entry Price (w/Slippage): ₹85.91
   Status: TRADE OPEN ✅
```

---

## 🎯 Quick Execution Summary

| Feature | Details |
|---------|---------|
| **Phase 1** | Historical scan at startup (any time 9:15-3:30 PM) |
| **Phase 2** | Live monitoring with 2-second updates |
| **Time Gate** | 10:00 AM (strict) to 3:10 PM (new orders) |
| **Slippage** | +0.05% added to ensure order fills |
| **Data Quality** | Real-time LTP from official Upstox API |
| **Frequency** | Every 2 seconds for live data checks |
| **Best Results** | Start 9:15-10:00 AM for clean history scan |

---

## ✅ Your Bot Now Follows The Rules

1. ✅ **Historical Phase**: Scans from 9:15 AM automatically
2. ✅ **10 AM Gate**: Stops trading before 10:00 AM
3. ✅ **Live Data**: Real-time monitoring after 10:00 AM
4. ✅ **Slippage Buffer**: 0.05% added for reliable fills
5. ✅ **Lock-Step Trailing**: Activates at +10%
6. ✅ **Market Hours**: Auto-closes at 3:30 PM

**Status: Production Ready! 🚀**

---

*This guide was updated February 16, 2026 with 10 AM Time Gate and Slippage Buffer implementation.*
