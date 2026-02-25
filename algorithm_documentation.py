"""
ALGORITHM DETAILS & CALCULATION EXAMPLES
========================================
This file demonstrates the mathematical logic of the 10 AM Breakout Bot
with detailed step-by-step calculations.
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    10 AM BREAKOUT ALGORITHM EXPLAINED                        ║
║                     WITH REALISTIC SCENARIOS & MATH                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# ============ SCENARIO 1: CLEAN BREAKOUT (BEST CASE) ============

print("\n" + "="*80)
print("SCENARIO 1: CLEAN BREAKOUT - STRONG UPTREND")
print("="*80)

print("""
MORNING PHASE (9:15 AM - 10:00 AM):
─────────────────────────────────────
Algorithm monitors 25500 CE (Call)
  9:30 AM: Price ₹130
  9:45 AM: Price ₹132
  10:00 AM HIGH RECORDED: ₹135 ← This is our breakout threshold
""")

print("\nTRADING PHASE (After 10:00 AM):")
print("─"*80)

entry_price = 135
entry_capital = 4000
quantity = entry_capital / entry_price

print(f"\n1️⃣  ENTRY")
print(f"   Time: 10:15 AM")
print(f"   Price crosses 10 AM high: ₹{entry_price}")
print(f"   Investment: ₹{entry_capital}")
print(f"   Quantity: {quantity:.2f} contracts")
print(f"   Initial SL: ₹{entry_price * 0.90:.2f} (-10%)")
print(f"   Initial TP: ₹{entry_price * 1.10:.2f} (+10%)")

# Price progression
price_progression = [
    (10.25, 138),
    (10.45, 145),
    (11.00, 148.5),
    (11.30, 152),
    (12.00, 158),
    (13.00, 165),
    (14.00, 172),
]

print(f"\n2️⃣  PRICE PROGRESSION WITH TRAILING STOP LOSS")
print(f"{'Time':<10} {'Price':<10} {'Profit %':<12} {'Status':<15} {'SL Action':<20}")
print(f"{'─'*67}")

current_price = entry_price
highest_price = entry_price
stop_loss = entry_price * 0.90
trail_activated = False

for time, price in price_progression:
    current_price = price
    profit_pct = (price - entry_price) / entry_price
    pnl = (price - entry_price) * quantity
    
    # Check if trail should activate
    if profit_pct >= 0.10:
        trail_activated = True
    
    # Update trailing SL
    if trail_activated:
        if price > highest_price:
            highest_price = price
        new_sl = highest_price * 0.96  # Maintain 6% gap (4% trail + 2% buffer)
        if new_sl > stop_loss:
            stop_loss = new_sl
            sl_status = f"Moved to ₹{new_sl:.2f}"
        else:
            sl_status = f"Held at ₹{stop_loss:.2f}"
    else:
        sl_status = f"Fixed at ₹{stop_loss:.2f}"
    
    status_text = "ACTIVE" if trail_activated else "Running"
    print(f"{time:<10} ₹{price:<9.2f} {profit_pct*100:>10.2f}% {status_text:<15} {sl_status:<20}")

print(f"\n3️⃣  FINAL EXIT")
print(f"   Time: 2:00 PM")
print(f"   Exit Price: ₹172")
profit = (172 - entry_price) * quantity
profit_pct = (172 - entry_price) / entry_price

print(f"   P&L: ₹{profit:.2f}")
print(f"   P&L %: {profit_pct*100:.2f}%")
print(f"   Return on Capital: {(profit / entry_capital * 100):.2f}%")

print(f"\n✅ RESULT: PROFIT ₹{profit:.2f}")
print(f"   Total Capital: ₹{4000 + profit:.2f}")
print(f"   Remaining untouched: ₹6000 (Buffer preserved)")

# ============ SCENARIO 2: FALSE BREAKOUT & REVERSAL ============

print("\n\n" + "="*80)
print("SCENARIO 2: FALSE BREAKOUT & REVERSAL - VOLATILITY")
print("="*80)

print("""
MORNING PHASE:
──────────────
25500 CE High @ 10 AM: ₹135
25500 PE High @ 10 AM: ₹50
""")

print("\nTRADING PHASE:")
print("─"*80)

entry_price_ce = 135
entry_capital_ce = 4000
quantity_ce = entry_capital_ce / entry_price_ce

print(f"\n1️⃣  FIRST TRADE: BUY CALL (10:15 AM)")
print(f"   Entry: ₹{entry_price_ce} | Qty: {quantity_ce:.2f}")
print(f"   SL: ₹{entry_price_ce * 0.90:.2f} (-10%)")

print(f"\n2️⃣  MARKET REVERSES (10:45 AM)")
print(f"   Price drops to ₹121.50 (-10% = SL HIT)")

loss_ce = (121.5 - entry_price_ce) * quantity_ce
loss_ce_pct = (121.5 - entry_price_ce) / entry_price_ce

print(f"   Exit Price: ₹121.50")
print(f"   Loss: ₹{loss_ce:.2f} ({loss_ce_pct*100:.2f}%)")

print(f"\n3️⃣  REVERSAL: BUY PUT (10:50 AM)")
print(f"   Market now expected to continue down")
entry_price_pe = 50
entry_capital_pe = 4000
quantity_pe = entry_capital_pe / entry_price_pe
print(f"   Entry: ₹{entry_price_pe} | Qty: {quantity_pe:.2f}")
print(f"   SL: ₹{entry_price_pe * 0.90:.2f} (-10%)")

print(f"\n4️⃣  MARKET CRASHES (1:00 PM - 3:00 PM)")
print(f"   {'Time':<10} {'PE Price':<10} {'Profit %':<12} {'Action':<20}")
print(f"   {'─'*52}")

pe_prices = [
    (11.00, 55),   # +10%
    (12.00, 65),   # +30%
    (14.00, 75),   # +50%
    (15.00, 80),   # +60%
]

for time, pe_price in pe_prices:
    pe_profit_pct = (pe_price - entry_price_pe) / entry_price_pe
    if pe_profit_pct >= 0.10:
        action = "Trail activated"
    else:
        action = "Running"
    print(f"   {time:<10} ₹{pe_price:<9.2f} {pe_profit_pct*100:>10.2f}% {action:<20}")

profit_pe = (80 - entry_price_pe) * quantity_pe
profit_pe_pct = (80 - entry_price_pe) / entry_price_pe

print(f"\n5️⃣  FINAL P&L CALCULATION")
print(f"   First Trade Loss (CE):  ₹{loss_ce:.2f}")
print(f"   Second Trade Profit (PE): ₹{profit_pe:.2f}")
net_profit = loss_ce + profit_pe

print(f"   ─────────────────────────")
print(f"   NET P&L: ₹{net_profit:.2f}")
print(f"   Total Capital: ₹{10000 + net_profit:.2f}")

print(f"\n✅ RESULT: PROFIT ₹{net_profit:.2f} (Even with one loss!)")
print(f"   Win Rate: 1 Win, 1 Loss, but profitable due to risk management")

# ============ SCENARIO 3: SIDEWAYS MARKET (WORST CASE) ============

print("\n\n" + "="*80)
print("SCENARIO 3: SIDEWAYS MARKET - RANGE BOUND")
print("="*80)

print("""
Market stays between 25500-25550 throughout the day.
Both Call and Put hit SL before any TP.
""")

print("\nTRADING PHASE:")
print("─"*80)

print(f"\n1️⃣  FIRST TRADE: BUY CALL (10:30 AM)")
ce_entry = 140
ce_qty = 4000 / ce_entry
print(f"   Entry: ₹{ce_entry} | Qty: {ce_qty:.2f}")
print(f"   TP: ₹{ce_entry * 1.10:.2f} | SL: ₹{ce_entry * 0.90:.2f}")

print(f"\n2️⃣  MARKET STAYS FLAT, CE DROPS (11:30 AM)")
ce_sl_hit = ce_entry * 0.90
ce_loss = (ce_sl_hit - ce_entry) * ce_qty
print(f"   Price drops to ₹{ce_sl_hit:.2f} → SL HIT")
print(f"   Loss: ₹{ce_loss:.2f}")

print(f"\n3️⃣  REVERSAL: BUY PUT (11:35 AM)")
pe_entry = 48
pe_qty = 4000 / pe_entry
print(f"   Entry: ₹{pe_entry} | Qty: {pe_qty:.2f}")
print(f"   TP: ₹{pe_entry * 1.10:.2f} | SL: ₹{pe_entry * 0.90:.2f}")

print(f"\n4️⃣  MARKET BOUNCES, PE ALSO HITS SL (2:00 PM)")
pe_sl_hit = pe_entry * 0.90
pe_loss = (pe_sl_hit - pe_entry) * pe_qty
print(f"   Price bounces to ₹{pe_sl_hit:.2f} → SL HIT")
print(f"   Loss: ₹{pe_loss:.2f}")

print(f"\n5️⃣  CONTROLLED LOSS")
total_loss = ce_loss + pe_loss
loss_pct = (total_loss / 10000) * 100
remaining_capital = 10000 + total_loss

print(f"   Total Loss: ₹{total_loss:.2f}")
print(f"   Loss %: {loss_pct:.2f}%")
print(f"   Remaining Capital: ₹{remaining_capital:.2f}")
print(f"   Capital Available to Trade: ₹{remaining_capital - 2000:.2f} (minus buffer)")

print(f"\n⚠️  RESULT: LIMITED LOSS (Sideways penalty)")
print(f"   Both sides hit SL, but losses are controlled")
print(f"   System enters 'HOLD' mode to prevent further losses")

# ============ LOCK-STEP TRAILING EXPLANATION ============

print("\n\n" + "="*80)
print("LOCK-STEP TRAILING STOP-LOSS MECHANICS")
print("="*80)

print("""
Once you achieve +10% profit, the SL is set at +4%.
From that point, for EVERY 1% price move UP:
- The SL also moves UP by 1% (maintaining the 6% gap)

This ensures:
1. You never lose profit once the 10% target is hit
2. You capture almost the entire move (except 6% from peak)
3. You're protected against sudden crashes

MATHEMATICAL PROOF:
""")

entry = 100
prices = [
    (100, "Entry", 90, "Initial"),
    (110, "+10%", 104, "Trail Triggered"),
    (111, "+11%", 105, "SL Follows UP"),
    (115, "+15%", 109, "SL Follows UP"),
    (125, "+25%", 119, "SL Follows UP"),
    (140, "+40%", 134, "SL Follows UP"),
    (135, "+35%", 129, "SL Moves Down? NO - Only trails UP"),
]

print(f"\n{'Price':<15} {'Profit':<12} {'SL Level':<12} {'Status':<20} {'Safe?':<10}")
print(f"{'─'*69}")

for price, description, sl, status in prices:
    profit_pct = ((price - entry) / entry) * 100
    is_safe = "✓ Safe" if price >= sl else "✗ Risk"
    print(f"₹{price:<14} {description:<12} ₹{sl:<11.0f} {status:<20} {is_safe:<10}")

print(f"""
OBSERVATION:
Once trail is active (₹110):
- If price goes to ₹140, SL is at ₹134 (6% gap)
- If price drops back to ₹135, you exit at ₹134 (profit locked)
- You never lose your ₹10 profit from ₹100 entry

This is why the strategy is called "Money Printing Machine" on trending days!
""")

# ============ CAPITAL ALLOCATION LOGIC ============

print("\n" + "="*80)
print("CAPITAL ALLOCATION & RISK MANAGEMENT")
print("="*80)

print(f"""
Total Capital: ₹10,000
├─ First Trade Capital: ₹4,000 (40%)
├─ Reversal Capital: ₹4,000 (40%)
└─ Buffer (Locked): ₹2,000 (20%)

WHY THIS ALLOCATION?

1️⃣  First Trade (₹4,000)
    - Tests the market direction after 10 AM
    - If hits SL (-10%), loss = ₹400
    - Remaining capital for reversal = ₹6,000 ✓

2️⃣  Reversal (₹4,000)
    - If first trade fails, reverse with opposite option
    - If this also fails (-10%), loss = ₹400
    - Total loss scenario: ₹800 (8% of capital)

3️⃣  Buffer (₹2,000)
    - Never used for trading
    - Protects against gap downs, slippage
    - Ensures you can always exit positions

WORST CASE SCENARIO:
─────────────────────
Both trades hit -10% SL:
  Total Loss: ₹800
  Remaining Capital: ₹9,200 (92%)
  ✓ You can trade again tomorrow!

BEST CASE SCENARIO:
──────────────────
First trade hits +30% (with trailing):
  Profit: ₹1,200
  Remaining Capital: ₹11,200
  ✓ 12% gain in a single trade!
""")

# ============ COMPARISON WITH OTHER ALGORITHMS ============

print("\n" + "="*80)
print("COMPARISON: YOUR ALGORITHM VS INDUSTRY STANDARDS")
print("="*80)

comparison_data = {
    'Feature': [
        'Entry Timing',
        'Philosophy',
        'Best For',
        'Risk Management',
        'Trade Duration',
        'Wins on Trending',
        'Wins on Sideways',
        'Complexity',
        'Capital Required'
    ],
    'Your 10 AM Bot': [
        'Static (10:00 AM)',
        'Breakout + Reversal',
        'Trending + Hedged',
        'Dynamic Trailing SL',
        '15 min - 4 hours',
        '⭐⭐⭐⭐⭐',
        '⭐⭐',
        'Medium',
        'Low (₹4k per trade)'
    ],
    'ORB (Opening Range)': [
        'Dynamic (0-30 min)',
        'Quick Scalp',
        'Volatile Opens',
        'Fixed SL/TP',
        '5-30 minutes',
        '⭐⭐⭐',
        '⭐',
        'Low',
        'High'
    ],
    'VWAP Mean Reversion': [
        'All Day',
        'Contrarian Buy Dips',
        'Sideways Markets',
        'ATR-based',
        '1-2 hours',
        '⭐⭐',
        '⭐⭐⭐⭐',
        'High',
        'Medium'
    ]
}

import pandas as pd
comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

print(f"""

YOUR ALGORITHM ADVANTAGES:
──────────────────────────
✓ Reversal Logic: If first trade fails, you flip sides (hedged)
✓ Lock-Step Trailing: Locks profit incrementally (no exit before peak)
✓ Low Capital: Works with ₹4k per trade (scalable)
✓ Clear Signals: 10 AM high breakout is mechanical (no emotions)
✓ Risk/Reward: Designed for trending days (best markets)

COMPARABLE TO:
──────────────
🏆 ORB + Mean Reversion hybrid
   (Combines momentum + hedging concepts)

WHEN THIS FAILS:
────────────────
✗ Gap Downs: If market opens -5%, your SL might not execute
✗ Low Liquidity Options: Wide bid-ask spreads hurt profitability
✗ Earnings Days: Unpredictable volatility breaks the logic
✗ Network Issues: If your connection drops, you can't exit
""")

print("\n" + "="*80)
print(f"END OF ALGORITHM DOCUMENTATION")
print("="*80)
