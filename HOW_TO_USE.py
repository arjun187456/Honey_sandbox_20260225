"""
HOW TO RUN & USE THE 10 AM BREAKOUT ALGORITHM
==============================================

Quick Start Guide for Trading Bot in VS Code
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              10 AM BREAKOUT TRADING BOT - QUICK START GUIDE                   ║
║                                                                               ║
║ This guide helps you understand and run the algorithm in VS Code             ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

print("""

STEP 1: VERIFY YOUR SETUP
═════════════════════════

Before running the bot, ensure you have:

✓ Python 3.12+ installed
  Check: Open Terminal → Type: python3 --version
  Expected: Python 3.12.x or higher

✓ Required libraries installed
  Run this command:
  >>> pip install requests pandas python-dotenv

✓ .env file with API credentials
  Location: /workspaces/Honey/.env
  Content should have:
  UPSTOX_ACCESS_TOKEN=your_token_here
  
✓ Time synchronized with IST (Indian Standard Time)
  The algorithm uses AM/PM logic, so ensure your system is correct


STEP 2: UNDERSTAND THE STRUCTURE
═════════════════════════════════

File: breakout_algo_bot.py
├─ TradingState class: Tracks all positions & cash
├─ TradePosition class: Manages individual trades
├─ Morning monitoring functions: Track pre-10 AM highs
├─ Entry logic: Breakout detection
├─ Reversal logic: Counter-trade execution
├─ Main loop: Continuous position monitoring


STEP 3: RUN THE ALGORITHM
══════════════════════════

OPTION A: Live Trading (Real Money)
────────────────────────────────────

COMMAND:
>>> python3 breakout_algo_bot.py

WHAT THIS DOES:
• Connects to Upstox API in real-time
• Monitors option prices from 9:15 AM
• Records pre-10 AM highs/lows
• After 10 AM, watches for breakouts
• Auto-executes trades when signals trigger
• Monitors positions until 3:30 PM market close
• Exits all trades at market close

⚠️  WARNING: This will use REAL MONEY. Test first!


OPTION B: Test Mode (Simulated Trading)
────────────────────────────────────────

COMMAND:
>>> python3 breakout_algo_bot.py --test --duration 30

PARAMETERS:
--test : Run in simulation mode (no real trades)
--duration 30 : Run for 30 minutes (then stop)

WHAT THIS DOES:
• Fetches REAL market data from Upstox
• Simulates entry/exit logic
• Tracks P&L as if real trades happened
• Perfect for testing strategy without money risk!


STEP 4: MONITOR THE OUTPUT
═══════════════════════════

While running, you'll see OUTPUT like this:

═════════════════════════════════════════════════════════════════════
📈 PRE-10 AM MONITORING PHASE
═════════════════════════════════════════════════════════════════════
Call High (10AM): ₹135.50
Call Low (10AM):  ₹128.00
Put High (10AM):  ₹50.75
Put Low (10AM):   ₹45.30
═════════════════════════════════════════════════════════════════════

After 10 AM, when a breakout is detected:

═════════════════════════════════════════════════════════════════════
🔵 ENTRY SIGNAL EXECUTED - Trade #1
═════════════════════════════════════════════════════════════════════
Type:        CALL
Reason:      CALL breakout above 135.50
Entry Price: ₹140.25
Quantity:    28.57 contracts
Entry Time:  2026-02-16 10:15:32
SL:          ₹126.23 (-10%)
TP:          ₹154.28 (+10%)
Capital Left: ₹6000.00
═════════════════════════════════════════════════════════════════════

When a position exits:

═════════════════════════════════════════════════════════════════════
📊 TRADE EXIT - TAKE PROFIT HIT
═════════════════════════════════════════════════════════════════════
Trade ID:        #1
Type:            CALL
Entry:           ₹140.25 @ 10:15:32
Exit:            ₹154.28 @ 11:45:22
P&L:             ₹393.99
P&L %:           10.00%
Duration:        90 minutes
═════════════════════════════════════════════════════════════════════


STEP 5: UNDERSTAND THE LOGIC
═════════════════════════════

MORNING PHASE (9:15 AM - 10:00 AM)
────────────────────────────────────
1. Algorithm fetches 25500 ATM Call & Put options
2. Records the HIGHEST price each option reaches
   26500 CE: High = ₹135 ← This becomes the breakout level
   25500 PE: High = ₹50
3. This is stored in TradingState.pre_10am_call_high, etc.

TRADING PHASE (After 10:00 AM)
─────────────────────────────────
1. Algorithm monitors current prices vs. pre-10 AM highs
2. IF current price > pre_10am_high → BREAKOUT DETECTED
3. Execute BUY order at current market price
4. Set SL at -10% and TP at +10%
5. Monitor position in real-time

TRAILING LOGIC (After +10% profit achieved)
───────────────────────────────────────────────
Original SL: ₹126.23
Price moves to ₹148.28 (+10%):
  Trail activated! New SL: ₹142.36 (locked +4%)
Price moves to ₹155.26 (+15%):
  Price is higher, SL follows: ₹149.05 (locked +9%)
Price moves to ₹165.28 (+25%):
  Price climbs more, SL climbs: ₹159.07 (locked +19%)

If price then crashes to ₹159.50, you exit at ₹159.05
PROFIT LOCKED IN! 💰


STEP 6: SAMPLE SCENARIOS YOU'LL SEE
═══════════════════════════════════

SCENARIO A: Strong Uptrend
──────────────────────────
10:15 AM: Buy CALL at ₹140
11:00 AM: Price hits ₹154 (+10% TP) → EXIT
Result: ✓ PROFIT ₹393.99

SCENARIO B: Sudden Reversal → Reversal Trade
──────────────────────────────────────────────
10:15 AM: Buy CALL at ₹140
10:45 AM: Price drops to ₹126 (-10% SL) → EXIT LOSS (₹393.99)
10:50 AM: Buy PUT at ₹50 (reversal)
1:00 PM: Market crashes, PUT rises to ₹75 (+50%) → EXIT PROFIT (₹1,250)
Result: ✓ NET PROFIT despite first losing trade

SCENARIO C: Sideways Market
──────────────────────────
10:15 AM: Buy CALL at ₹140
       → Price stays 135-145, eventually hits SL at -10%
       → Loss: ₹393.99
10:50 AM: Buy PUT at ₹50 (reversal)
       → Price bounces around 50-52, hits SL
       → Loss: ₹50
Result: ⚠️ LIMITED LOSS (₹443.99 total, 4.4% of capital)


STEP 7: CONFIGURE FOR YOUR NEEDS
═════════════════════════════════

Edit breakout_algo_bot.py to change these settings:

# Capital Allocation
TOTAL_CAPITAL = 10000  # Change to your budget
FIRST_TRADE_CAPITAL = 4000  # First trade size
REVERSAL_CAPITAL = 4000  # Reversal trade size

# Risk/Reward
INITIAL_SL_PERCENT = -0.10  # -10% stop-loss
INITIAL_TP_PERCENT = 0.10  # +10% take-profit
TRAILING_SL_PERCENT = -0.04  # -4% trailing after TP hit

# Strategy Timing
MONITORING_CUTOFF = dt_time(10, 0)  # Monitor until 10 AM
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)


STEP 8: ANALYZING RESULTS
══════════════════════════

After bot finishes, you'll see FINAL REPORT:

═════════════════════════════════════════════════════
📋 FINAL TRADING REPORT
═════════════════════════════════════════════════════

ACCOUNT SUMMARY:
  Initial Capital:    ₹10000
  Final Capital:      ₹10950
  Total P&L:          ₹950
  P&L %:              9.50%
  Cash Available:     ₹3200

TRADES SUMMARY:
  Total Trades:       3
  Winning Trades:     2
  Losing Trades:      1
  Win Rate:           66.7%

TRADE HISTORY:
Trade  Type  Entry    Exit    P&L     P&L %
────────────────────────────────────────
#1     CALL  ₹140.25  ₹154.28  ₹393.99  +10.00%
#2     PUT   ₹50.00   ₹75.00   ₹1250.00 +50.00%
#3     CALL  ₹135.00  ₹121.50  -₹540.00 -10.00%

═════════════════════════════════════════════════════

KEY METRICS TO TRACK:
✓ Total P&L: Absolute profit/loss
✓ P&L %: Return as percentage
✓ Win Rate: % of trades that were profitable
✓ Average Win: Average profit on winning trades
✓ Average Loss: Average loss on losing trades
✓ Risk-Reward Ratio: Avg Win / Avg Loss (Higher is better)


STEP 9: TROUBLESHOOTING
═══════════════════════

Problem: "401 Unauthorized Error"
─────────────────────────────────
Cause: API token expired
Solution:
  1. Go to Upstox dashboard
  2. Generate new Access Token
  3. Update .env file with new token
  4. Restart bot

Problem: "No data available"
────────────────────────────
Cause: Market is closed or API not responding
Solution:
  1. Check time (9:15 AM - 3:30 PM IST)
  2. Verify internet connection
  3. Check if Upstox API is up: status.upstox.com

Problem: "Cannot import module X"
──────────────────────────────────
Cause: Library not installed
Solution:
  >>> pip install requests pandas python-dotenv

Problem: "Trades not executing"
───────────────────────────────
Cause: Algorithm logic not triggering
Solution:
  1. Check if pre-10 AM highs were recorded
  2. Verify current price > pre-10 AM high
  3. Check if cash available > trade capital
  4. Check logs for errors


STEP 10: BEST PRACTICES
═══════════════════════

✓ DO THIS:
  • Start in TEST mode first (--test --duration 30)
  • Paper trade for a week before real money
  • Monitor market conditions (not earnings day)
  • Keep system on during market hours
  • Check internet connectivity
  • Have backup power supply (UPS)
  • Review trade logic after each day
  • Gradually increase capital if profitable

✗ DON'T DO THIS:
  • Trade with money you can't afford to lose
  • Run multiple bots on same account
  • Change parameters during market hours
  • Trade earnings-related options
  • Use weak internet connection
  • Leave computer unattended
  • Use borrowed capital


ADVANCED CUSTOMIZATIONS
═══════════════════════

A) Change to a different expiry:
   Open breakout_algo_bot.py
   Line: EXPIRY_DATE = "2026-02-24"  # Change date


B) Trade different strikes:
   Change ATM range in find_atm_strikes()
   atm_range = 200  # Instead of 100


C) Different SL/TP percentages:
   INITIAL_SL_PERCENT = -0.08  # 8% instead of 10%
   INITIAL_TP_PERCENT = 0.15  # 15% instead of 10%


D) Add notification:
   Install: pip install twilio
   Send SMS/WhatsApp when trade exits


REAL TRADING CHECKLIST
═══════════════════════

Before going LIVE:
☐ API tokens working (test with data fetch)
☐ .env file configured correctly
☐ Capital ready and segregated
☐ Tested in --test mode for 5+ days
☐ Reviewed all code logic
☐ Backup internet connection ready
☐ Backup power supply (UPS) ready
☐ Set stop-loss hard limits in code
☐ Daily maximum loss limit set
☐ Notifications enabled
☐ Checked platform charges/brokerage

STARTUP COMMAND:
>>> python3 breakout_algo_bot.py

STOP COMMAND:
Press Ctrl+C (keyboard interrupt)


FINAL TIPS
═════════

1. Your algorithm is "Hedged Breakout Strategy"
   - Not pure momentum (has reversal)
   - Not pure contrarian (has breakout)
   - Balanced for trending AND sideways markets

2. Best used with:
   - Low slippage options (High OI, tight spreads)
   - ATM strikes (liquidity for exit)
   - Expiries with 3-5 days left (good liquidity)
   - Trending markets (NOT earnings days)

3. Capital growth strategy:
   Start: ₹10,000 (₹4k per trade)
   After 5 winning days: ₹15,000 (₹6k per trade)
   After 10 winning days: ₹25,000 (₹10k per trade)

4. Monitor daily:
   - Win rate (should be >40%)
   - Average win vs loss (win should be 1.5x+ loss)
   - Max consecutive losses (stop if >3)
   - Daily maximum loss (exit if >500 loss)

═════════════════════════════════════════════════════════════════════

READY TO START? 🚀

Test Mode:
>>> python3 breakout_algo_bot.py --test --duration 60

Live Trading:
>>> python3 breakout_algo_bot.py

Monitor the output. Good luck! 💰

═════════════════════════════════════════════════════════════════════
""")
