#!/usr/bin/env python3
"""
QUICK START GUIDE - HYBRID TIME-SYNC BOT v2.0
"Single Button" Solution - Press Run Anytime, Anywhere

Author: Arjun Trading Bot
Date: February 16, 2026
"""

# ═══════════════════════════════════════════════════════════════════
# 🚀 INSTANT START (Copy & Paste This)
# ═══════════════════════════════════════════════════════════════════

print("""
╔════════════════════════════════════════════════════════════════════╗
║   🚀 HYBRID TIME-SYNC TRADING BOT v2.0 - QUICK START ⭐          ║
║                                                                    ║
║   The "Single Button" Solution                                    ║
║   Perfect for any start time during market hours                 ║
╚════════════════════════════════════════════════════════════════════╝

STEP 1: Verify Setup (30 seconds)
─────────────────────────────────

✓ Check 1: Token is valid
  $ cat .env
  ✓ See: UPSTOX_ACCESS_TOKEN=eyJ0...
  
✓ Check 2: Libraries installed
  $ pip list | grep -E "requests|pandas"
  ✓ Should show: requests, pandas
  
✓ Check 3: Bot file exists
  $ ls -la breakout_algo_bot_v2.py
  ✓ Should show file size ~15KB


STEP 2: Run in Test Mode First (5 minutes)
──────────────────────────────────────────

$ python3 breakout_algo_bot_v2.py --test --duration 5

Expected Output:
  
  ======================================================================
  🚀 10 AM BREAKOUT ALGORITHMIC TRADING BOT - HYBRID TIME-SYNC v2.0
  ======================================================================
  
  ======================================================================
  🔄 PHASE 1: HISTORY SYNCHRONIZATION
  ======================================================================
  Current Time: {HH:MM:SS}
  Scanning market history from 9:15 AM to now...
  
  📊 HISTORY SCAN RESULTS:
    Nifty 50 Spot: ₹25,XXX.XX
    ATM Call Strike: ₹25,XXX.0
    ATM Call LTP: ₹XX.XX (Trigger: ₹XX.XX)
    ATM Put Strike: ₹25,XXX.0
    Put LTP: ₹XX.XX (Trigger: ₹XX.XX)
  
  ✅ SYNC COMPLETE - Ready to detect breakouts
  ======================================================================
  
  🔄 PHASE 2: LIVE MONITORING
  ======================================================================
  Waiting for breakout signal above history high...

This means ✅ BOT IS WORKING CORRECTLY


STEP 3: Understand What Just Happened
──────────────────────────────────────

Bot did 2 things:
  
  PHASE 1: Synced with market history
    ├─ Found: Nifty 50 current spot price
    ├─ Found: ATM CALL & PUT options
    ├─ Got: Current LTP (price)
    └─ Set: This as the trigger for breakout
  
  PHASE 2: Started monitoring
    ├─ Watches: Live CALL & PUT prices
    ├─ Waits for: Price to cross trigger
    └─ Will: Execute entry when breakout detected

The bot is now waiting for a price breakout above its threshold.


STEP 4: Advanced Test (Run during Market Hours)
───────────────────────────────────────────────

Only works if market is OPEN (9:15 AM - 3:30 PM IST):

$ python3 breakout_algo_bot_v2.py --test --duration 30

The bot will:
  ✓ Sync with current market history immediately
  ✓ Monitor live prices
  ✓ Execute entry IF a breakout occurs
  ✓ Track position & P&L
  ✓ Test trailing stop-loss
  ✓ Report final results


STEP 5: Go Live! 🎯
──────────────────

During market hours (9:15 AM - 3:30 PM):

$ python3 breakout_algo_bot_v2.py

This will:
  ✓ Start bot (PHASE 1: Sync immediately)
  ✓ Monitor all day
  ✓ Execute REAL trades with REAL capital
  ✓ Auto-exit at 3:30 PM market close

⚠️  BEFORE going live:
  ☐ Tested with --test --duration 30
  ☐ Understand the strategy
  ☐ Reviewed capital allocation (₹4k + ₹4k + ₹2k)
  ☐ Understand SL/TP/trailing logic
  ☐ Account has sufficient capital (₹10,000+)


═══════════════════════════════════════════════════════════════════════
📊 UNDERSTANDING THE Output
═══════════════════════════════════════════════════════════════════════

You'll see output like this:

  📊 HISTORY SCAN RESULTS:
    Nifty 50 Spot: ₹25,564.10
    ATM Call Strike: ₹25,550.0
    ATM Call LTP: ₹85.60 (Trigger: ₹85.69)  ← Entry if price > ₹85.69
    ATM Put Strike: ₹25,550.0
    Put LTP: ₹68.20 (Trigger: ₹68.27)  ← Entry if price > ₹68.27

This means:
  ✓ CALL option current price: ₹85.60
  ✓ Will buy CALL if price crosses ₹85.69 (0.1% higher)
  ✓ PUT option current price: ₹68.20
  ✓ Will buy PUT if price crosses ₹68.27 (0.1% higher)


═══════════════════════════════════════════════════════════════════════
🎯 EXPECTED OUTCOMES (What You'll See)
═══════════════════════════════════════════════════════════════════════

Outcome 1: No Breakout
─────────────────────
Duration: Test mode 30 minutes
Prices: Stay below trigger
Result: ✅ No trades executed
        ✅ No capital lost
        ✅ Bot waiting for opportunity
        
Output:
  ✅ SYNC COMPLETE
  Waiting for breakout signal...
  (ends without any trades)


Outcome 2: One Successful Breakout
──────────────────────────────────
Duration: 10 minutes into test
Prices: Break above history high
Result: ✅ Entry executed
        ✅ Position opened
        ✅ Watching P&L
        
Output:
  ✅ SYNC COMPLETE
  Waiting for breakout signal...
  
  11:05 AM: BREAKOUT DETECTED!
  🚀 ENTRY SIGNAL DETECTED! - CALL BREAKOUT
  ════════════════════════════════════════════
  Trade #: 1
  Type: BUY CALL @ Strike ₹25,550
  Entry Price: ₹85.75
  Quantity: 46.62
  Capital Used: ₹4000
  Stop Loss: ₹77.18 (-10%)
  Take Profit: ₹94.32 (+10%)
  Time: 11:05:30


Outcome 3: First Trade Hits TP (+10%)
──────────────────────────────────────
Duration: 15 minutes
Prices: Rise above entry + 10%
Result: ✅ Position exits at profit
        ✅ P&L shows gain
        
Output:
  ⚡ Trade #1: +10% PROFIT REACHED - Trail Activated!
     Current Price: ₹94.35
     SL Locked at +4%: ₹90.58
     Profit Locked: ₹350


Outcome 4: First Trade Hits SL (-10%), Then Reversal Profits
────────────────────────────────────────────────────────────
Duration: Full session
Prices: Drop initially → Reversal profits
Result: ✅ First trade stops out
        ✅ Reversal catches profit
        ✅ Net positive
        
Output:
  ❌ Trade #1: STOP LOSS HIT at -10%!
     Exit Price: ₹77.18
     Loss: -₹350
  
  ⚖️ REVERSAL TRADE EXECUTED - PUT
  Trade #: 2
  Type: BUY PUT @ Strike ₹25,550
  Entry Price: ₹68.50
  Quantity: 58.39
  Capital Used: ₹4000
  Stop Loss: ₹61.65 (-10%)
  Take Profit: ₹75.35 (+10%)
  
  ✅ Trade #2: +15% PROFIT!
     Exit Price: ₹78.78
     Profit: +₹600
  
  TOTAL: -₹350 + ₹600 = ₹250 NET PROFIT ✅


═══════════════════════════════════════════════════════════════════════
💰 Capital Allocation Explained
═══════════════════════════════════════════════════════════════════════

Total Capital: ₹10,000
├─ First Trade: ₹4,000 (40%)
│   ├─ Use for initial BUY CALL or PUT
│   ├─ Max loss per trade: ₹400 (-10%)
│   └─ Profit if TP hit: ₹400 (+10%)
│
├─ Reversal Trade: ₹4,000 (40%)
│   ├─ Use for counter-trade if SL hit
│   ├─ Max loss per trade: ₹400 (-10%)
│   └─ Profit if TP hit: ₹400 (+10%)
│
└─ Emergency Buffer: ₹2,000 (20%)
    └─ NEVER traded - Safety reserve

Worst Case Loss:
  First trade SL: -₹400
  Reversal SL: -₹400
  Total: -₹800 (8% of ₹10,000)
  Remaining: ₹9,200 (can trade again!)

Best Case Profit:
  Clean breakout: ₹400 (+10%)
  OR
  Reversal hedge: ₹400 + ₹600 = ₹1,000 (10% gain)


═══════════════════════════════════════════════════════════════════════
🔧 CUSTOMIZATION (Change These Numbers)
═══════════════════════════════════════════════════════════════════════

Edit breakout_algo_bot_v2.py:

# Line ~40: Change total capital
TOTAL_CAPITAL = 10000  → Change to 50000 for ₹50k trading

# Line ~42-44: Change per-trade alloc
FIRST_TRADE_CAPITAL = 4000  → Change to 10000 for ₹10k per trade
REVERSAL_CAPITAL = 4000     → Change to 10000

# Line ~46-48: Change SL/TP
INITIAL_SL_PERCENT = -0.10   → Change to -0.08 for 8% SL
INITIAL_TP_PERCENT = 0.10    → Change to 0.15 for 15% TP
TRAILING_SL_PERCENT = -0.04  → Change to -0.03 for tighter trail

# Line ~50: Change when trail activates
TRAIL_ACTIVATION_PROFIT = 0.10  → Change to 0.08 for earlier trail


═══════════════════════════════════════════════════════════════════════
⚠️ SAFETY CHECKS BEFORE GOING LIVE
═══════════════════════════════════════════════════════════════════════

Before running without --test flag:

☐ Test 1: Token Check
  $ python3 quick_test.py
  Should show: ✅ Spot Price: ₹25,XXX and ✅ Got 93 option strikes

☐ Test 2: Dashboard Works
  $ timeout 5 python3 nifty_option_dashboard.py
  Should show: Live Nifty option chain data

☐ Test 3: Bot Test Mode
  $ python3 breakout_algo_bot_v2.py --test --duration 10
  Should show: Phase 1 sync + Phase 2 monitoring

☐ Test 4: During Market Hours
  $ python3 breakout_algo_bot_v2.py --test --duration 30
  Run between 9:15 AM - 3:30 PM
  Should show real market data + possible trades

☐ Final: Read Guides
  Read: HYBRID_TIME_SYNC_GUIDE.md (understand v2 fully)


═══════════════════════════════════════════════════════════════════════
🎓 KEY CONCEPTS (3-Minute Understanding)
═══════════════════════════════════════════════════════════════════════

1. HISTORY SYNC
   What: Bot scans market from 9:15 AM to when you press RUN
   Why: Knows what the "high so far" is
   Benefit: Works from ANY start time (9:30 AM, 11 AM, 2 PM, etc.)

2. BREAKOUT TRIGGER
   What: Price > History High
   Example: History high was ₹85.60 → Entry when price hits ₹85.70
   Why: Means momentum is happening

3. ENTRY
   When: Price crosses trigger
   What: Buy ₹4k worth of CALL or PUT
   Where: At market prices (LTP)
   Quantity: ₹4000 / Entry_Price

4. STOP-LOSS
   What: Exit if price drops 10% from entry
   Example: Entry ₹85.00 → SL at ₹76.50
   Why: Limits loss per trade to ₹400

5. TAKE-PROFIT
   What: Exit if price rises 10% from entry
   Example: Entry ₹85.00 → TP at ₹93.50
   Why: Books profit at +10%

6. TRAILING STOP-LOSS
   What: After +10% profit, SL locks at +4%
   Example: Entry ₹85.00 → Price ₹93.50 (+10%) → SL moves to ₹89.76 (+4%)
   Benefit: Never lose profit. Captures big moves.

7. LOCK-STEP TRAILING
   What: For every 1% price rises, SL rises 1% (maintains 6% gap)
   Example: Price ₹94.50 → SL ₹90.72, Price ₹95.50 → SL ₹91.68
   Benefit: Protects gains while capturing trend

8. REVERSAL TRADE
   What: If first trade hits SL, buy opposite side with ₹4k
   Example: First trade CALL stopped out → Buy PUT
   Why: Hedges - if wrong on direction, other side profits

9. FINAL REPORT
   Shows: Total P&L, Win rate, Trade details
   When: At market close or when you stop bot


═══════════════════════════════════════════════════════════════════════
🆘 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

Problem: "Could not fetch market data"
Solution: 
  1. Check if market is open (9:15 AM - 3:30 PM)
  2. Check token: cat .env | grep UPSTOX
  3. Token expired? Regenerate from Upstox dashboard
  4. Try: python3 quick_test.py

Problem: "Could not find ATM options"
Solution:
  1. Market data might be delayed
  2. Try running again (sometimes temporary)
  3. Check: nifty_option_dashboard.py works?

Problem: "Bot runs but no trades"
Solution:
  1. Normal - might be no breakout yet
  2. Wait for price to cross trigger
  3. Check terminal shows "Waiting for breakout signal"
  4. Use --test to see full session

Problem: "Trade executed but P&L looks wrong"
Solution:
  1. Check quantity calculation: ₹4000 / entry_price
  2. Check SL: entry_price * 0.90
  3. Check TP: entry_price * 1.10
  4. All formulas are correct - numbers should match


═══════════════════════════════════════════════════════════════════════
📚 FURTHER READING
═══════════════════════════════════════════════════════════════════════

Deep Dives:
  Read: HYBRID_TIME_SYNC_GUIDE.md      (Complete strategy explained)
  Read: VERSION_COMPARISON.md          (v1 vs v2 differences)
  Read: ALGORITHM_SUMMARY.md           (High-level overview)

Code Understanding:
  Review: breakout_algo_bot_v2.py     (Main implementation)
  Class: TradePosition                 (Individual trade tracking)
  Class: TradingState                  (Global state)
  Function: fetch_historical_high()    (Phase 1 sync)
  Function: check_breakout_signal()    (Phase 2 monitoring)

Scenarios:
  Review: algorithm_documentation.py   (Real trading examples)
  Scenario 1: Clean breakout (+27%)
  Scenario 2: Reversal hedge (+60%)
  Scenario 3: Sideways market (-8%)


═══════════════════════════════════════════════════════════════════════
🎯 SUCCESS CHECKLIST
═══════════════════════════════════════════════════════════════════════

Before Live Trading:

☐ Understand History Sync (Phase 1)
☐ Understand Live Monitoring (Phase 2)
☐ Know capital allocation: ₹4k + ₹4k + ₹2k
☐ Know SL: -10%, TP: +10%, Trail: -4%
☐ Know lock-step trailing (1% for 1%)
☐ Know reversal (opposite side if SL)
☐ Tested --test mode 5+ times
☐ Tested with real market data (9:15-3:30 PM)
☐ Reviewed all output messages
☐ Comfortable with worst case (-8%)
☐ Ready to press RUN!


═══════════════════════════════════════════════════════════════════════
🚀 READY TO TRADE? HERE'S YOUR COMMAND:
═══════════════════════════════════════════════════════════════════════

During Market Hours (9:15 AM - 3:30 PM IST):

$ python3 breakout_algo_bot_v2.py

The bot will:
  ✅ Auto-sync with market history
  ✅ Monitor all day
  ✅ Execute trades on breakouts
  ✅ Manage SL/TP automatically
  ✅ Execute reversals
  ✅ Trail stop-loss
  ✅ Report P&L

Good luck! 🚀💰

═══════════════════════════════════════════════════════════════════════
""")

# If you saved this as quick_start_v2.py, you can read it any time:
# $ python3 quick_start_v2.py
