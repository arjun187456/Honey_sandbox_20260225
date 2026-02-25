"""
10 AM BREAKOUT ALGORITHMIC TRADING STRATEGY FOR NIFTY 50 OPTIONS
================================================================
Strategy Overview:
- Monitor option prices until 10 AM for highs/lows
- After 10 AM, wait for breakout (price crossing pre-10 AM high)
- Buy when breakout occurs
- Initial SL: -10%, Initial TP: +10%
- Lock-step Trailing SL: Once 10% profit hit, maintain 6% gap (4% buffer)
- Reversal: If SL hit, trade opposite CE/PE
- Capital: ₹10k total (₹4k per trade, ₹2k buffer)

Author: Arjun Trading Bot
Created: 2026-02-16
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, time as dt_time
from urllib.parse import quote, quote_plus
from dotenv import load_dotenv
import json

# Configuration
load_dotenv()
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")

BASE_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# ============ STRATEGY CONFIGURATION ============
TOTAL_CAPITAL = 10000  # ₹10,000
FIRST_TRADE_CAPITAL = 4000  # ₹4,000 for first trade
REVERSAL_CAPITAL = 4000  # ₹4,000 for reversal trade
BUFFER_CAPITAL = 2000  # ₹2,000 emergency buffer

INITIAL_SL_PERCENT = -0.10  # Stop-Loss at -10%
INITIAL_TP_PERCENT = 0.10  # Take-Profit at +10%
TRAILING_SL_PERCENT = -0.04  # Trail SL at -4% (6% gap maintained)
TRAIL_ACTIVATION_PROFIT = 0.10  # Activate trail at +10%

MORNING_MONITORING_HOUR = 10  # Monitor until 10 AM
NIFTY_SYMBOL = "NSE_INDEX|Nifty 50"
OPTION_SYMBOL = "NSE_INDEX|Nifty 50"  # For option chain
EXPIRY_DATE = "2026-02-17"

# ============ MARKET HOURS ============
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)
MONITORING_CUTOFF = dt_time(10, 0)

# ============ TRADING STATE ============
class TradingState:
    """Maintains the state of all active trades"""
    
    def __init__(self):
        self.pre_10am_call_high = None
        self.pre_10am_call_low = None
        self.pre_10am_put_high = None
        self.pre_10am_put_low = None
        
        self.active_trades = []  # List of active trade positions
        self.closed_trades = []  # History of closed trades
        self.cash_available = TOTAL_CAPITAL
        self.total_pnl = 0
        
        self.morning_phase = True  # True until 10 AM
        self.monitoring_complete = False
        
    def to_dict(self):
        """Convert state to JSON-serializable format"""
        return {
            'pre_10am_call_high': self.pre_10am_call_high,
            'pre_10am_call_low': self.pre_10am_call_low,
            'pre_10am_put_high': self.pre_10am_put_high,
            'pre_10am_put_low': self.pre_10am_put_low,
            'active_trades': len(self.active_trades),
            'closed_trades': len(self.closed_trades),
            'cash_available': self.cash_available,
            'total_pnl': self.total_pnl,
            'morning_phase': self.morning_phase,
        }

state = TradingState()

# ============ API FUNCTIONS ============

def get_option_chain(expiry_date=EXPIRY_DATE):
    """Fetch option chain data"""
    url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(OPTION_SYMBOL, safe='|')}&expiry_date={quote_plus(str(expiry_date))}"
    url = url.replace(' ', '')
    
    try:
        resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data', [])
        else:
            print(f"❌ Error fetching option chain: Status {resp.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception fetching option chain: {e}")
        return []

def get_spot_price():
    """Get current Nifty 50 spot price"""
    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={quote(NIFTY_SYMBOL, safe='|,:')}"
    
    try:
        resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            # API may return key with ':' or '|' - try both formats
            price = data.get(NIFTY_SYMBOL, {}).get('last_price', 0)
            if price == 0:
                # Try with colon format
                alt_key = NIFTY_SYMBOL.replace('|', ':')
                price = data.get(alt_key, {}).get('last_price', 0)
            return price
        return 0
    except Exception as e:
        print(f"❌ Exception fetching spot price: {e}")
        return 0

def find_atm_strikes(spot_price, chain):
    """Find ATM calls and puts"""
    atm_range = 100  # Look for strikes within ±100 of spot
    
    call_options = []
    put_options = []
    
    for strike_data in chain:
        strike = strike_data.get('strike_price', 0)
        
        # Filter ATM range
        if abs(strike - spot_price) <= atm_range:
            ce = strike_data.get('call_options', {})
            pe = strike_data.get('put_options', {})
            
            if ce and pe:
                call_options.append({
                    'strike': strike,
                    'data': ce
                })
                put_options.append({
                    'strike': strike,
                    'data': pe
                })
    
    return call_options, put_options

# ============ MORNING MONITORING (Until 10 AM) ============

def update_morning_highs_lows(chain, spot_price):
    """Record pre-10 AM highs and lows"""
    call_options, put_options = find_atm_strikes(spot_price, chain)
    
    for call in call_options:
        ltp = call['data'].get('market_data', {}).get('ltp', 0)
        if state.pre_10am_call_high is None or ltp > state.pre_10am_call_high:
            state.pre_10am_call_high = ltp
        if state.pre_10am_call_low is None or ltp < state.pre_10am_call_low:
            state.pre_10am_call_low = ltp
    
    for put in put_options:
        ltp = put['data'].get('market_data', {}).get('ltp', 0)
        if state.pre_10am_put_high is None or ltp > state.pre_10am_put_high:
            state.pre_10am_put_high = ltp
        if state.pre_10am_put_low is None or ltp < state.pre_10am_put_low:
            state.pre_10am_put_low = ltp

# ============ ENTRY LOGIC ============

class TradePosition:
    """Represents a single active trade"""
    
    def __init__(self, trade_id, option_type, entry_price, entry_time, capital_used):
        self.trade_id = trade_id
        self.option_type = option_type  # 'CALL' or 'PUT'
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.capital_used = capital_used
        self.quantity = capital_used / entry_price
        
        # Stop-Loss & Take-Profit
        self.stop_loss = entry_price * (1 + INITIAL_SL_PERCENT)  # -10%
        self.take_profit = entry_price * (1 + INITIAL_TP_PERCENT)  # +10%
        
        self.highest_price = entry_price  # For trailing SL
        self.current_price = entry_price
        self.trail_activated = False
        
        self.status = "OPEN"  # OPEN, CLOSED, SL_HIT, TP_HIT
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0
        self.pnl_percent = 0
    
    def update_price(self, current_price):
        """Update current price and check for exit conditions"""
        self.current_price = current_price
        
        # Track highest price for trailing SL
        if current_price > self.highest_price:
            self.highest_price = current_price
        
        # Calculate P&L
        self.pnl = (current_price - self.entry_price) * self.quantity
        self.pnl_percent = (current_price - self.entry_price) / self.entry_price
        
        # Check if trail should be activated
        if self.pnl_percent >= TRAIL_ACTIVATION_PROFIT:
            self.trail_activated = True
        
        # Update trailing SL if activated
        if self.trail_activated:
            # Maintain 6% gap (4% SL + 6% buffer = 10%)
            calculated_sl = self.highest_price * (1 + TRAILING_SL_PERCENT)  # -4%
            if calculated_sl > self.stop_loss:
                self.stop_loss = calculated_sl
        
        # Check for exit
        if current_price <= self.stop_loss:
            self.status = "SL_HIT"
            self.exit_price = self.stop_loss
            return "SL_HIT"
        
        if current_price >= self.take_profit and not self.trail_activated:
            self.status = "TP_HIT"
            self.exit_price = self.take_profit
            return "TP_HIT"
        
        # If trailing activated, check against current TP (highest price - 4%)
        if self.trail_activated and current_price < self.stop_loss:
            self.status = "SL_HIT"
            self.exit_price = current_price
            return "SL_HIT"
        
        return "OPEN"
    
    def close_trade(self, exit_price, exit_time, reason):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.status = reason
        self.pnl = (exit_price - self.entry_price) * self.quantity
        self.pnl_percent = (exit_price - self.entry_price) / self.entry_price

def check_breakout_and_enter(chain, spot_price, current_time):
    """Check if breakout occurred and execute entry"""
    
    # Only enter trades if past 10 AM and in market hours
    if current_time.time() < MONITORING_CUTOFF or current_time.time() > MARKET_CLOSE:
        return None
    
    if not state.monitoring_complete:
        state.monitoring_complete = True
        state.morning_phase = False
    
    # Get current option data
    call_options, put_options = find_atm_strikes(spot_price, chain)
    
    entry_signal = None
    
    # Check CALL breakout
    if state.pre_10am_call_high:
        for call in call_options:
            ltp = call['data'].get('market_data', {}).get('ltp', 0)
            
            # Breakout condition: Price crosses pre-10 AM high
            if ltp > state.pre_10am_call_high:
                # Check if we already have an open CALL trade
                existing_call = any(t.option_type == 'CALL' and t.status == 'OPEN' for t in state.active_trades)
                
                if not existing_call and state.cash_available >= FIRST_TRADE_CAPITAL:
                    entry_signal = {
                        'type': 'CALL',
                        'strike': call['strike'],
                        'entry_price': ltp,
                        'reason': f'CALL breakout above {state.pre_10am_call_high:.2f}'
                    }
                    break
    
    # Check PUT breakout
    if state.pre_10am_put_high and not entry_signal:
        for put in put_options:
            ltp = put['data'].get('market_data', {}).get('ltp', 0)
            
            # Breakout condition: Price crosses pre-10 AM high
            if ltp > state.pre_10am_put_high:
                # Check if we already have an open PUT trade
                existing_put = any(t.option_type == 'PUT' and t.status == 'OPEN' for t in state.active_trades)
                
                if not existing_put and state.cash_available >= FIRST_TRADE_CAPITAL:
                    entry_signal = {
                        'type': 'PUT',
                        'strike': put['strike'],
                        'entry_price': ltp,
                        'reason': f'PUT breakout above {state.pre_10am_put_high:.2f}'
                    }
                    break
    
    return entry_signal

def execute_entry(entry_signal, current_time):
    """Execute the entry trade"""
    
    if not entry_signal:
        return None
    
    trade_id = len(state.active_trades) + 1
    
    trade = TradePosition(
        trade_id=trade_id,
        option_type=entry_signal['type'],
        entry_price=entry_signal['entry_price'],
        entry_time=current_time,
        capital_used=FIRST_TRADE_CAPITAL
    )
    
    state.active_trades.append(trade)
    state.cash_available -= FIRST_TRADE_CAPITAL
    
    print(f"\n{'='*80}")
    print(f"🔵 ENTRY SIGNAL EXECUTED - Trade #{trade_id}")
    print(f"{'='*80}")
    print(f"Type:        {trade.option_type}")
    print(f"Reason:      {entry_signal['reason']}")
    print(f"Entry Price: ₹{trade.entry_price:.2f}")
    print(f"Quantity:    {trade.quantity:.2f}")
    print(f"Entry Time:  {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"SL:          ₹{trade.stop_loss:.2f} ({INITIAL_SL_PERCENT*100}%)")
    print(f"TP:          ₹{trade.take_profit:.2f} ({INITIAL_TP_PERCENT*100}%)")
    print(f"Capital Left: ₹{state.cash_available:.2f}")
    print(f"{'='*80}\n")
    
    return trade

# ============ REVERSAL LOGIC ============

def execute_reversal(sl_hit_trade, chain, spot_price, current_time):
    """Execute reversal trade when SL is hit"""
    
    # Determine opposite option type
    opposite_type = 'PUT' if sl_hit_trade.option_type == 'CALL' else 'CALL'
    
    # Get opposite option data
    call_options, put_options = find_atm_strikes(spot_price, chain)
    
    # Select the opposite option at same strike range
    if opposite_type == 'PUT':
        candidates = put_options
    else:
        candidates = call_options
    
    if not candidates:
        print(f"⚠️  No {opposite_type} options available for reversal")
        return None
    
    # Pick the one closest to the hit trade's strike
    best_option = min(candidates, key=lambda x: abs(x['strike'] - sl_hit_trade.entry_price))
    entry_price = best_option['data'].get('market_data', {}).get('ltp', 0)
    
    if state.cash_available < REVERSAL_CAPITAL:
        print(f"⚠️  Insufficient funds for reversal (Need ₹{REVERSAL_CAPITAL}, Have ₹{state.cash_available})")
        return None
    
    # Create reversal trade
    trade_id = len(state.active_trades) + 1
    reversal_trade = TradePosition(
        trade_id=trade_id,
        option_type=opposite_type,
        entry_price=entry_price,
        entry_time=current_time,
        capital_used=REVERSAL_CAPITAL
    )
    
    state.active_trades.append(reversal_trade)
    state.cash_available -= REVERSAL_CAPITAL
    
    print(f"\n{'='*80}")
    print(f"🔄 REVERSAL TRADE EXECUTED")
    print(f"{'='*80}")
    print(f"Previous Trade: #{sl_hit_trade.trade_id} {sl_hit_trade.option_type} SL HIT at ₹{sl_hit_trade.exit_price:.2f}")
    print(f"Loss on Previous: ₹{sl_hit_trade.pnl:.2f} ({sl_hit_trade.pnl_percent*100:.2f}%)")
    print(f"\nReversal Trade ID: #{reversal_trade.trade_id}")
    print(f"Type:             {opposite_type}")
    print(f"Entry Price:      ₹{reversal_trade.entry_price:.2f}")
    print(f"SL:               ₹{reversal_trade.stop_loss:.2f}")
    print(f"TP:               ₹{reversal_trade.take_profit:.2f}")
    print(f"Capital Left:     ₹{state.cash_available:.2f}")
    print(f"{'='*80}\n")
    
    return reversal_trade

# ============ POSITION MONITORING ============

def update_all_positions(chain, spot_price, current_time):
    """Update all active positions and check for exits"""
    
    call_options, put_options = find_atm_strikes(spot_price, chain)
    
    for trade in state.active_trades:
        if trade.status == "OPEN":
            # Get current price
            if trade.option_type == 'CALL':
                candidates = call_options
            else:
                candidates = put_options
            
            # Find closest strike
            if candidates:
                best_option = min(candidates, key=lambda x: abs(x['strike'] - trade.entry_price))
                current_price = best_option['data'].get('market_data', {}).get('ltp', 0)
                
                exit_signal = trade.update_price(current_price)
                
                if exit_signal == "SL_HIT":
                    # Close the trade
                    trade.close_trade(trade.stop_loss, current_time, "SL_HIT")
                    state.cash_available += FIRST_TRADE_CAPITAL if trade.capital_used == FIRST_TRADE_CAPITAL else REVERSAL_CAPITAL
                    state.total_pnl += trade.pnl
                    state.closed_trades.append(trade)
                    
                    print_trade_exit(trade, "STOP LOSS HIT")
                    
                    # Execute reversal if it was first trade
                    if trade.capital_used == FIRST_TRADE_CAPITAL:
                        reversal = execute_reversal(trade, chain, spot_price, current_time)
                
                elif exit_signal == "TP_HIT":
                    # Close the trade
                    trade.close_trade(trade.take_profit, current_time, "TP_HIT")
                    state.cash_available += FIRST_TRADE_CAPITAL if trade.capital_used == FIRST_TRADE_CAPITAL else REVERSAL_CAPITAL
                    state.total_pnl += trade.pnl
                    state.closed_trades.append(trade)
                    
                    print_trade_exit(trade, "TAKE PROFIT HIT")

def print_trade_exit(trade, reason):
    """Print trade exit details"""
    print(f"\n{'='*80}")
    print(f"📊 TRADE EXIT - {reason}")
    print(f"{'='*80}")
    print(f"Trade ID:        #{trade.trade_id}")
    print(f"Type:            {trade.option_type}")
    print(f"Entry:           ₹{trade.entry_price:.2f} @ {trade.entry_time.strftime('%H:%M:%S')}")
    print(f"Exit:            ₹{trade.exit_price:.2f} @ {trade.exit_time.strftime('%H:%M:%S')}")
    print(f"P&L:             ₹{trade.pnl:.2f}")
    print(f"P&L %:           {trade.pnl_percent*100:.2f}%")
    print(f"Duration:        {(trade.exit_time - trade.entry_time).total_seconds():.0f} seconds")
    print(f"{'='*80}\n")

# ============ MAIN TRADING LOOP ============

def print_morning_status():
    """Print morning monitoring status"""
    print(f"\n{'='*80}")
    print(f"📈 PRE-10 AM MONITORING PHASE")
    print(f"{'='*80}")
    print(f"Call High (10AM): ₹{state.pre_10am_call_high:.2f if state.pre_10am_call_high else 'N/A'}")
    print(f"Call Low (10AM):  ₹{state.pre_10am_call_low:.2f if state.pre_10am_call_low else 'N/A'}")
    print(f"Put High (10AM):  ₹{state.pre_10am_put_high:.2f if state.pre_10am_put_high else 'N/A'}")
    print(f"Put Low (10AM):   ₹{state.pre_10am_put_low:.2f if state.pre_10am_put_low else 'N/A'}")
    print(f"{'='*80}\n")

def print_account_status():
    """Print current account status"""
    print(f"\n{'─'*80}")
    print(f"💰 ACCOUNT STATUS")
    print(f"{'─'*80}")
    print(f"Total Capital:      ₹{TOTAL_CAPITAL}")
    print(f"Cash Available:     ₹{state.cash_available:.2f}")
    print(f"In Active Trades:   ₹{TOTAL_CAPITAL - state.cash_available - BUFFER_CAPITAL:.2f}")
    print(f"Buffer (Locked):    ₹{BUFFER_CAPITAL}")
    print(f"Total P&L:          ₹{state.total_pnl:.2f}")
    print(f"P&L %:              {(state.total_pnl / TOTAL_CAPITAL * 100):.2f}%")
    print(f"Active Trades:      {len([t for t in state.active_trades if t.status == 'OPEN'])}")
    print(f"Closed Trades:      {len(state.closed_trades)}")
    print(f"{'─'*80}\n")

def run_trading_bot(test_mode=False, duration_minutes=30):
    """Main trading bot loop"""
    
    print(f"\n{'#'*80}")
    print(f"#{'10 AM BREAKOUT ALGORITHMIC TRADING BOT FOR NIFTY 50':^78}#")
    print(f"{'#'*80}\n")
    
    print(f"Configuration:")
    print(f"  Total Capital: ₹{TOTAL_CAPITAL}")
    print(f"  First Trade: ₹{FIRST_TRADE_CAPITAL}")
    print(f"  Reversal: ₹{REVERSAL_CAPITAL}")
    print(f"  SL: {INITIAL_SL_PERCENT*100}% | TP: {INITIAL_TP_PERCENT*100}% | Trail: {TRAILING_SL_PERCENT*100}%")
    print(f"  Monitoring until: {MONITORING_CUTOFF.strftime('%H:%M')}")
    print(f"  Test Mode: {test_mode} | Duration: {duration_minutes} min")
    print(f"\n")
    
    start_time = datetime.now()
    last_status_print = start_time
    
    while True:
        now = datetime.now()
        
        # Check if trading should stop
        if not test_mode:
            if now.time() > MARKET_CLOSE:
                print("\n⛔ Market closed. Stopping bot.")
                break
        else:
            if (now - start_time).total_seconds() > duration_minutes * 60:
                print(f"\n⏱️  Test duration ({duration_minutes} min) completed.")
                break
        
        try:
            # Fetch current data
            chain = get_option_chain()
            spot = get_spot_price()
            
            if not chain or spot == 0:
                print(f"⚠️  Could not fetch data at {now.strftime('%H:%M:%S')}")
                time.sleep(2)
                continue
            
            # MORNING PHASE (Until 10 AM): Record highs/lows
            if state.morning_phase and now.time() < MONITORING_CUTOFF:
                update_morning_highs_lows(chain, spot)
            
            # TRADING PHASE (After 10 AM)
            if now.time() >= MONITORING_CUTOFF and not state.monitoring_complete:
                print_morning_status()
                state.monitoring_complete = True
                state.morning_phase = False
            
            # Check for entry
            if now.time() >= MONITORING_CUTOFF:
                entry_signal = check_breakout_and_enter(chain, spot, now)
                if entry_signal:
                    execute_entry(entry_signal, now)
            
            # Update all active positions
            update_all_positions(chain, spot, now)
            
            # Print status every minute
            if (now - last_status_print).total_seconds() >= 60:
                print_account_status()
                last_status_print = now
                
                # Print active trades snapshot
                for trade in state.active_trades:
                    if trade.status == "OPEN":
                        print(f"  Trade #{trade.trade_id}: {trade.option_type} @ ₹{trade.entry_price:.2f} → ₹{trade.current_price:.2f} ({trade.pnl_percent*100:.2f}%)")
            
            time.sleep(2)  # Check every 2 seconds
        
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
    
    # Final report
    print_final_report()

def print_final_report():
    """Print final trading report"""
    print(f"\n{'='*80}")
    print(f"📋 FINAL TRADING REPORT")
    print(f"{'='*80}\n")
    
    print(f"ACCOUNT SUMMARY:")
    print(f"  Initial Capital:    ₹{TOTAL_CAPITAL}")
    print(f"  Final Capital:      ₹{TOTAL_CAPITAL + state.total_pnl}")
    print(f"  Total P&L:          ₹{state.total_pnl:.2f}")
    print(f"  P&L %:              {(state.total_pnl / TOTAL_CAPITAL * 100):.2f}%")
    print(f"  Cash Available:     ₹{state.cash_available:.2f}\n")
    
    print(f"TRADES SUMMARY:")
    print(f"  Total Trades:       {len(state.closed_trades)}")
    winning_trades = [t for t in state.closed_trades if t.pnl > 0]
    losing_trades = [t for t in state.closed_trades if t.pnl < 0]
    print(f"  Winning Trades:     {len(winning_trades)}")
    print(f"  Losing Trades:      {len(losing_trades)}")
    if len(state.closed_trades) > 0:
        win_rate = (len(winning_trades) / len(state.closed_trades)) * 100
        print(f"  Win Rate:           {win_rate:.1f}%\n")
    
    if state.closed_trades:
        print(f"TRADE HISTORY:")
        print(f"{'Trade':<8} {'Type':<7} {'Entry':<10} {'Exit':<10} {'P&L':<12} {'P&L %':<10}")
        print(f"{'─'*57}")
        for trade in state.closed_trades:
            pnl_str = f"₹{trade.pnl:.2f}"
            pnl_pct_str = f"{trade.pnl_percent*100:.2f}%"
            print(f"#{trade.trade_id:<7} {trade.option_type:<7} ₹{trade.entry_price:<9.2f} ₹{trade.exit_price:<9.2f} {pnl_str:<12} {pnl_pct_str:<10}")
    
    print(f"\n{'='*80}\n")

# ============ RUN BOT ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nifty 50 10 AM Breakout Trading Bot")
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in minutes')
    
    args = parser.parse_args()
    
    try:
        run_trading_bot(test_mode=args.test, duration_minutes=args.duration)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
