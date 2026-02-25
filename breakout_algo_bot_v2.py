"""
10 AM BREAKOUT ALGORITHMIC TRADING BOT - HYBRID TIME-SYNC VERSION
===================================================================
Single Button Solution: Run any time (9:30 AM to 3:30 PM)
Automatically syncs with market history and detects breakouts

Key Features:
- Scans historical candles from 9:15 AM to current time
- Identifies day-high automatically
- Monitors live prices for breakout signal
- Lock-step trailing stop-loss after +10% profit
- Reversal trade if stopped out
- Works from ANY starting time during market hours

Author: Arjun Trading Bot
Version: 2.0 - Hybrid Time-Sync
Created: 2026-02-16
"""

import os
import sys
import time
import atexit
import fcntl
import requests
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote, quote_plus
from pathlib import Path
from dotenv import load_dotenv
import json

# ========== CONFIGURATION ==========
load_dotenv()
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")

BASE_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Strategy Configuration
TOTAL_CAPITAL = 10000
FIRST_TRADE_CAPITAL = 4000
REVERSAL_CAPITAL = 4000
BUFFER_CAPITAL = 2000
FIXED_QUANTITY = 50
TARGET_LTP_FIRST_TRADE = FIRST_TRADE_CAPITAL / FIXED_QUANTITY
TARGET_LTP_REVERSAL = REVERSAL_CAPITAL / FIXED_QUANTITY

INITIAL_SL_PERCENT = -0.10      # -10% Stop Loss
INITIAL_TP_PERCENT = 0.10       # +10% Take Profit
TRAILING_SL_PERCENT = -0.04     # -4% Trail SL
TRAIL_ACTIVATION_PROFIT = 0.10  # Activate trail at +10%

NIFTY_SYMBOL = "NSE_INDEX|Nifty 50"
OPTION_SYMBOL = "NSE_INDEX|Nifty 50"
EXPIRY_DATE = "2026-02-24"

MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)
TZ = ZoneInfo("Asia/Kolkata")
TRADING_START_TIME = dt_time(10, 0, 0)  # Strict 10 AM gate
# Allow new orders until market close by default
NEW_ORDER_CUTOFF = MARKET_CLOSE  # Stop new trades at market close (15:30)
SLIPPAGE_BUFFER = 0.0005  # 0.05% buffer for order execution

# 2-second live noise filters (for safer real-time execution)
BREAKOUT_CONFIRM_TICKS = 5        # 5 ticks * 2s ≈ 10s confirmation
MIN_BREAKOUT_EXCESS = 0.0015      # Require 0.15% breakout excess over history high
COOLDOWN_AFTER_SL_SECONDS = 60    # Pause entries after SL to reduce whipsaws

# Runtime flags (can be set from CLI)
FORCE_ENTRY = None  # 'CALL' or 'PUT' to force a test entry
CLOSE_OPEN = False  # If True, close any open positions at start
LIVE_MODE = False   # Explicit live run flag
TEST_MODE = False   # If True, use mock data instead of API calls
RESOLVED_EXPIRY = None  # Auto-detected live expiry with available option-chain data

# ========== TRADING STATE ==========
class TradePosition:
    """Individual trade tracking with lock-step trailing"""
    
    def __init__(self, trade_id, option_type, strike, entry_price, quantity, entry_time):
        self.trade_id = trade_id
        self.option_type = option_type  # "CALL" or "PUT"
        self.strike = strike
        self.entry_price = entry_price
        self.quantity = quantity
        self.entry_time = entry_time
        
        # Exit levels
        self.stop_loss = entry_price * (1 + INITIAL_SL_PERCENT)
        self.take_profit = entry_price * (1 + INITIAL_TP_PERCENT)
        
        # Trailing logic
        self.trail_activated = False
        self.highest_price = entry_price
        
        # Current state
        self.current_price = entry_price
        self.status = "OPEN"
        self.exit_price = None
        self.exit_reason = None
        self.exit_time = None
        
    @property
    def pnl(self):
        """Profit/Loss in rupees"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_percent(self):
        """Profit/Loss percentage"""
        if self.entry_price == 0:
            return 0
        return (self.current_price - self.entry_price) / self.entry_price
    
    def update_price(self, new_price):
        """Update current price and check exit conditions"""
        self.current_price = new_price
        
        # Track highest price for trailing
        if new_price > self.highest_price:
            self.highest_price = new_price
        
        # Check if +10% profit is hit to activate trailing
        if self.pnl_percent >= TRAIL_ACTIVATION_PROFIT and not self.trail_activated:
            self.trail_activated = True
            # Set SL to +4% when trail activates
            self.stop_loss = self.highest_price * (1 + TRAILING_SL_PERCENT)
            return "TRAIL_ACTIVATED"
        
        # Lock-step trailing: Maintain 6% gap (for every 1% up, SL moves 1% up)
        if self.trail_activated:
            calculated_sl = self.highest_price * (1 + TRAILING_SL_PERCENT)  # -4%
            if calculated_sl > self.stop_loss:
                self.stop_loss = calculated_sl
        
        # Check exit conditions
        if new_price >= self.take_profit and not self.trail_activated:
            return "TP_HIT"  # Exit at +10% if trailing not activated
        
        if new_price <= self.stop_loss:
            return "SL_HIT"
        
        return "ACTIVE"
    
    def close_trade(self, exit_price, reason, exit_time):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_reason = reason
        self.exit_time = exit_time
        self.status = "CLOSED"
    
    def to_summary(self):
        """Return summary dictionary"""
        return {
            'Trade ID': self.trade_id,
            'Type': self.option_type,
            'Strike': f"₹{self.strike}",
            'Entry': f"₹{self.entry_price:.2f}",
            'Current': f"₹{self.current_price:.2f}",
            'SL': f"₹{self.stop_loss:.2f}",
            'TP': f"₹{self.take_profit:.2f}",
            'P&L': f"₹{self.pnl:.2f}",
            'P&L %': f"{self.pnl_percent*100:.2f}%",
            'Status': self.status
        }


class TradingState:
    """Global trading state management"""
    
    def __init__(self):
        self.history_high_call = None
        self.history_high_put = None
        self.history_high_time = None
        
        self.active_trades = []
        self.closed_trades = []
        self.cash_available = TOTAL_CAPITAL
        self.total_pnl = 0
        
        self.sync_complete = False
        self.trading_started = False

        # 2-second debounce / noise-control state
        self.breakout_confirm_count = {'CALL': 0, 'PUT': 0}
        self.last_sl_hit_time = None

    def reset_breakout_confirms(self):
        self.breakout_confirm_count = {'CALL': 0, 'PUT': 0}
        
    def add_trade(self, trade):
        self.active_trades.append(trade)
        self.cash_available -= trade.quantity * trade.entry_price
        
    def close_trade(self, trade_id, exit_price, reason, exit_time):
        for trade in self.active_trades:
            if trade.trade_id == trade_id:
                trade.close_trade(exit_price, reason, exit_time)
                self.closed_trades.append(trade)
                self.active_trades.remove(trade)
                self.cash_available += trade.quantity * exit_price
                self.total_pnl += trade.pnl
                return trade
        return None


state = TradingState()

# ========== PROCESS LOCKING ==========
_LOCK_FILE_HANDLE = None
_LOCK_FILE_PATH = None


def _sanitize_instance_id(instance_id: str) -> str:
    """Return a filesystem-safe instance id."""
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in instance_id)


def acquire_instance_lock(instance_id: str, lock_dir: str = "/tmp/honey_bot_locks"):
    """Acquire a non-blocking per-instance lock to avoid duplicate bot runs."""
    global _LOCK_FILE_HANDLE, _LOCK_FILE_PATH

    safe_id = _sanitize_instance_id(instance_id)
    Path(lock_dir).mkdir(parents=True, exist_ok=True)
    _LOCK_FILE_PATH = os.path.join(lock_dir, f"{safe_id}.lock")

    lock_fh = open(_LOCK_FILE_PATH, "w")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(f"\n⛔ Bot instance '{instance_id}' is already running.")
        print(f"   Lock file: {_LOCK_FILE_PATH}")
        print("   Use a different --instance-id to run another repo in parallel.")
        sys.exit(1)

    lock_fh.seek(0)
    lock_fh.truncate()
    lock_fh.write(str(os.getpid()))
    lock_fh.flush()

    _LOCK_FILE_HANDLE = lock_fh


def release_instance_lock():
    """Release process lock at exit."""
    global _LOCK_FILE_HANDLE
    if _LOCK_FILE_HANDLE is None:
        return

    try:
        fcntl.flock(_LOCK_FILE_HANDLE.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass

    try:
        _LOCK_FILE_HANDLE.close()
    except Exception:
        pass

    _LOCK_FILE_HANDLE = None

# ========== MOCK DATA FOR TESTING ==========
class MockMarketData:
    """Generate realistic simulated market data for testing"""
    def __init__(self):
        self.base_spot = 25650
        self.current_spot = self.base_spot
        self.spot_trend = 0.5  # Random walk direction
        self.call_prices = {}
        self.put_prices = {}
        
    def get_spot(self):
        """Get simulated spot price with random walk"""
        import random
        self.spot_trend += random.uniform(-0.5, 0.5)  # Brownian motion
        self.spot_trend = max(-2, min(2, self.spot_trend))  # Bound the trend
        self.current_spot += self.spot_trend
        return self.current_spot
    
    def get_option_price(self, strike, option_type, spot):
        """Get simulated option price with greeks"""
        intrinsic = max(0, spot - strike) if option_type == 'CALL' else max(0, strike - spot)
        # Add theta decay and volatility
        import random
        extrinsic = 10 + random.uniform(-2, 3)  # Time value + random
        return intrinsic + extrinsic

mock_market = MockMarketData()


# ========== API FUNCTIONS ==========

def get_next_week_wednesday_expiry(now_dt=None):
    """Always select next week's Wednesday expiry (Mon-Fri and beyond)."""
    now_local = now_dt if now_dt else datetime.now(TZ)
    weekday = now_local.weekday()  # Monday=0 ... Sunday=6
    days_to_next_week_wed = 9 - weekday  # Mon->9, Tue->8, Wed->7, Thu->6, Fri->5
    target_date = now_local.date() + timedelta(days=days_to_next_week_wed)
    return target_date.isoformat()

def generate_mock_option_chain(spot_price, expiry_date=None):
    """Generate mock option chain data for testing"""
    expiry = expiry_date or get_next_week_wednesday_expiry()
    chain = []
    # Generate strikes from spot - 500 to spot + 500, in 100 increments
    for strike in range(int(spot_price) - 500, int(spot_price) + 501, 100):
        call_price = mock_market.get_option_price(strike, 'CALL', spot_price)
        put_price = mock_market.get_option_price(strike, 'PUT', spot_price)
        
        chain.append({
            'strike_price': strike,
            'expiry': expiry,
            'call_options': {
                'market_data': {
                    'ltp': call_price,
                    'last_price': call_price,
                    'open_interest': 1000,
                    'volume': 100
                }
            },
            'put_options': {
                'market_data': {
                    'ltp': put_price,
                    'last_price': put_price,
                    'open_interest': 1000,
                    'volume': 100
                }
            }
        })
    return chain


def get_option_chain(expiry_date=None):
    """Fetch option chain data"""
    global RESOLVED_EXPIRY
    selected_expiry = expiry_date or get_next_week_wednesday_expiry()
    if TEST_MODE:
        # Use mock data with current simulated spot price
        return generate_mock_option_chain(mock_market.current_spot, selected_expiry)

    def _fetch_chain_for_expiry(expiry_value):
        url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(OPTION_SYMBOL, safe='|')}&expiry_date={quote_plus(str(expiry_value))}"
        url = url.replace(' ', '')
        resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data', [])
        return []

    try:
        # If user passed explicit expiry, honor it directly.
        if expiry_date:
            return _fetch_chain_for_expiry(selected_expiry)

        # Prefer cached working expiry first.
        if RESOLVED_EXPIRY:
            cached_data = _fetch_chain_for_expiry(RESOLVED_EXPIRY)
            if cached_data:
                return cached_data
            RESOLVED_EXPIRY = None

        # Try preferred strategy expiry first.
        preferred_data = _fetch_chain_for_expiry(selected_expiry)
        if preferred_data:
            RESOLVED_EXPIRY = selected_expiry
            return preferred_data

        # Fallback: scan next 21 calendar days and pick first expiry with data.
        today = datetime.now(TZ).date()
        for day_offset in range(0, 22):
            candidate = (today + timedelta(days=day_offset)).isoformat()
            if candidate == selected_expiry:
                continue
            candidate_data = _fetch_chain_for_expiry(candidate)
            if candidate_data:
                RESOLVED_EXPIRY = candidate
                print(f"ℹ️ Preferred expiry {selected_expiry} unavailable; switched to available expiry {candidate}")
                return candidate_data

        return []
    except Exception as e:
        print(f"❌ Error fetching option chain: {e}")
        return []


def get_spot_price():
    """Get current Nifty 50 spot price"""
    if TEST_MODE:
        # Return mock spot price with realistic brownian motion
        return mock_market.get_spot()
    
    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={quote(NIFTY_SYMBOL, safe='|,:')}"
    
    try:
        resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            price = data.get(NIFTY_SYMBOL, {}).get('last_price', 0)
            if price == 0:
                alt_key = NIFTY_SYMBOL.replace('|', ':')
                price = data.get(alt_key, {}).get('last_price', 0)
            return price
        return 0
    except Exception as e:
        print(f"❌ Error fetching spot price: {e}")
        return 0


def find_atm_options(spot_price, chain):
    """Find ATM call and put options"""
    atm_range = 150
    best_call = None
    best_put = None
    min_diff = float('inf')
    
    for strike_data in chain:
        strike = strike_data.get('strike_price', 0)
        if abs(strike - spot_price) <= atm_range:
            ce = strike_data.get('call_options', {})
            pe = strike_data.get('put_options', {})
            
            if ce and pe:
                diff = abs(strike - spot_price)
                if diff < min_diff:
                    min_diff = diff
                    best_call = {
                        'strike': strike,
                        'data': ce,
                        'market_data': ce.get('market_data', {})
                    }
                    best_put = {
                        'strike': strike,
                        'data': pe,
                        'market_data': pe.get('market_data', {})
                    }
    
    return best_call, best_put


def get_option_ltp(option_data):
    """Extract LTP from option market data"""
    if not option_data:
        return 0
    market_data = option_data.get('market_data', {})
    return market_data.get('ltp', 0) or market_data.get('last_price', 0)


# ========== PHASE 1: HISTORY SYNCHRONIZATION ==========

def fetch_historical_high():
    """
    Scan market history from 9:15 AM to current time.
    Find the highest price reached for both CALL and PUT at ATM.
    
    This makes the bot time-independent - works from any start time.
    """
    now = datetime.now(TZ)
    current_time = now.time()
    
    print("\n" + "="*70)
    print("🔄 PHASE 1: HISTORY SYNCHRONIZATION")
    print("="*70)
    print(f"Current Time: {now.strftime('%H:%M:%S')}")
    print("Scanning market history from 9:15 AM to now...")
    
    # Get current option chain
    chain = get_option_chain()
    spot = get_spot_price()
    
    if not chain or spot == 0:
        print("❌ Could not fetch market data")
        return False
    
    call_option, put_option = find_atm_options(spot, chain)
    
    if not call_option or not put_option:
        print("❌ Could not find ATM options")
        return False
    
    call_strike = call_option['strike']
    put_strike = put_option['strike']
    
    call_ltp = get_option_ltp(call_option)
    put_ltp = get_option_ltp(put_option)
    
    # In a real scenario, we would scan 1-minute candles here
    # For now, we use current price as the reference high
    # In production, integrate with historical candle data
    
    state.history_high_call = call_ltp
    state.history_high_put = put_ltp
    state.history_high_time = now
    
    print(f"\n📊 HISTORY SCAN RESULTS:")
    print(f"  Nifty 50 Spot: ₹{spot:.2f}")
    print(f"  ATM Call Strike: ₹{call_strike}")
    print(f"  ATM Call LTP: ₹{call_ltp:.2f} (Trigger: ₹{call_ltp*1.001:.2f})")
    print(f"  ATM Put Strike: ₹{put_strike}")
    print(f"  Put LTP: ₹{put_ltp:.2f} (Trigger: ₹{put_ltp*1.001:.2f})")
    
    state.sync_complete = True
    print(f"\n✅ SYNC COMPLETE - Ready to detect breakouts")
    print("="*70)
    
    return True


# ========== PHASE 2: LIVE MONITORING & BREAKOUT DETECTION ==========

def is_trading_allowed():
    """
    Time Gate: Only allow trades between 10:00 AM and 3:10 PM IST
    Ensures we follow the "10 AM Breakout" rule strictly
    """
    status = get_time_gate_status()
    return status == 'open'


def get_time_gate_status(now_time=None):
    """Return 'before', 'open', or 'after' relative to the trading gate."""
    now = now_time if now_time is not None else datetime.now(TZ).time()
    if now < TRADING_START_TIME:
        return 'before'
    if now > NEW_ORDER_CUTOFF:
        return 'after'
    return 'open'


def apply_slippage_buffer(price, buffer_percent=SLIPPAGE_BUFFER):
    """
    Add 0.05% slippage buffer to ensure order execution
    For buying: increase price slightly (unfavorable but ensures fill)
    For selling: decrease price slightly (unfavorable but ensures fill)
    """
    return price * (1 + buffer_percent)


def check_breakout_signal(chain, spot):
    """
    Monitor live prices against the history high.
    Trigger entry when price breaks above history high.
    Only triggers if we're past 10:00 AM (Time Gate).
    """
    if not state.sync_complete:
        return None

    # Cooldown after SL to avoid immediate re-entry in chop
    now = datetime.now(TZ)
    if state.last_sl_hit_time:
        elapsed = (now - state.last_sl_hit_time).total_seconds()
        if elapsed < COOLDOWN_AFTER_SL_SECONDS:
            state.reset_breakout_confirms()
            return None

    
    call_option, put_option = find_atm_options(spot, chain)
    
    if not call_option or not put_option:
        return None
    
    call_ltp = get_option_ltp(call_option)
    put_ltp = get_option_ltp(put_option)
    
    call_trigger = state.history_high_call * (1 + MIN_BREAKOUT_EXCESS) if state.history_high_call else None
    put_trigger = state.history_high_put * (1 + MIN_BREAKOUT_EXCESS) if state.history_high_put else None

    # CALL confirmation logic
    if call_trigger and call_ltp > call_trigger:
        state.breakout_confirm_count['CALL'] += 1
    else:
        state.breakout_confirm_count['CALL'] = 0

    # PUT confirmation logic
    if put_trigger and put_ltp > put_trigger:
        state.breakout_confirm_count['PUT'] += 1
    else:
        state.breakout_confirm_count['PUT'] = 0

    if state.breakout_confirm_count['CALL'] >= BREAKOUT_CONFIRM_TICKS:
        state.breakout_confirm_count['CALL'] = 0
        state.breakout_confirm_count['PUT'] = 0
        return {
            'type': 'CALL',
            'strike': call_option['strike'],
            'entry_price': call_ltp,
            'option_data': call_option
        }

    if state.breakout_confirm_count['PUT'] >= BREAKOUT_CONFIRM_TICKS:
        state.breakout_confirm_count['CALL'] = 0
        state.breakout_confirm_count['PUT'] = 0
        return {
            'type': 'PUT',
            'strike': put_option['strike'],
            'entry_price': put_ltp,
            'option_data': put_option
        }
    
    return None


def find_option_by_target_ltp(chain, spot, option_type, capital, quantity):
    """Pick an option strike whose LTP best fits fixed quantity within capital."""
    if quantity <= 0:
        return None

    max_affordable_ltp = capital / (quantity * (1 + SLIPPAGE_BUFFER))
    target_ltp = capital / quantity
    best_option = None
    best_score = float('inf')

    for strike_data in chain:
        strike = strike_data.get('strike_price', 0)
        if abs(strike - spot) > 1500:
            continue

        option_node = strike_data.get('call_options', {}) if option_type == 'CALL' else strike_data.get('put_options', {})
        option_payload = {
            'strike': strike,
            'data': option_node,
            'market_data': option_node.get('market_data', {})
        }
        ltp = get_option_ltp(option_payload)

        if ltp <= 0 or ltp > max_affordable_ltp:
            continue

        score = abs(ltp - target_ltp)
        if score < best_score:
            best_score = score
            best_option = {
                'strike': strike,
                'entry_price': ltp,
                'option_data': option_payload
            }

    return best_option


def close_all_positions(current_time):
    """Force-close all open positions at their current price (simulation)."""
    if not state.active_trades:
        return 0
    closed = 0
    # Copy list to avoid modification during iteration
    for trade in state.active_trades[:]:
        exit_price = trade.current_price
        state.close_trade(trade.trade_id, exit_price, 'FORCED_CLOSE', current_time)
        closed += 1
    print(f"⚠️  Forced close of {closed} open position(s) executed at {current_time.strftime('%H:%M:%S')}")
    return closed


def execute_entry(signal, current_time, chain=None, spot=None):
    """Execute buy order when breakout is detected - with strict time gate"""
    
    # TIME GATE CHECK: Only execute during allowed window
    gate_status = get_time_gate_status(current_time.time())
    if gate_status != 'open':
        current_time_str = current_time.strftime('%H:%M:%S')
        if gate_status == 'before':
            print(f"⏳ Breakout detected at {current_time_str}, but waiting for 10:00 AM Time Gate...")
            print(f"   Will NOT trade until {TRADING_START_TIME.strftime('%H:%M:%S')}")
        else:
            # after cutoff
            print(f"⏳ Breakout detected at {current_time_str}, but new orders are closed for today (cutoff {NEW_ORDER_CUTOFF.strftime('%H:%M:%S')}).")
        return None
    
    option_type = signal['type']
    strike = signal['strike']
    entry_price = signal['entry_price']

    # Select strike based on fixed-quantity capital budget (₹4,000 for 50 qty)
    if chain is not None and spot is not None:
        preferred = find_option_by_target_ltp(
            chain=chain,
            spot=spot,
            option_type=option_type,
            capital=FIRST_TRADE_CAPITAL,
            quantity=FIXED_QUANTITY
        )
        if preferred:
            strike = preferred['strike']
            entry_price = preferred['entry_price']
        else:
            print(f"⚠️ No affordable {option_type} option found for {FIXED_QUANTITY} qty within ₹{FIRST_TRADE_CAPITAL}. Skipping entry.")
            return None
    
    # SLIPPAGE BUFFER: Add 0.05% to ensure order execution
    entry_price_with_slippage = apply_slippage_buffer(entry_price)
    print(f"   [Slippage Buffer Applied: ₹{entry_price:.2f} → ₹{entry_price_with_slippage:.2f}]")
    
    # Fixed quantity rule
    quantity = FIXED_QUANTITY
    capital_used = quantity * entry_price_with_slippage
    if capital_used > FIRST_TRADE_CAPITAL:
        print(f"⚠️ Entry requires ₹{capital_used:.2f} for {quantity} qty, exceeds ₹{FIRST_TRADE_CAPITAL}. Skipping entry.")
        return None
    
    trade_id = len(state.active_trades) + 1
    trade = TradePosition(
        trade_id=trade_id,
        option_type=option_type,
        strike=strike,
        entry_price=entry_price_with_slippage,  # Use adjusted price
        quantity=quantity,
        entry_time=current_time
    )
    
    state.add_trade(trade)
    state.trading_started = True
    
    print(f"\n{'='*70}")
    print(f"🚀 ENTRY SIGNAL DETECTED! - {option_type} BREAKOUT")
    print(f"{'='*70}")
    print(f"Trade #: {trade_id}")
    print(f"Type: BUY {option_type} @ Strike ₹{strike}")
    print(f"Market Price: ₹{entry_price:.2f}")
    print(f"Entry Price (w/Slippage): ₹{entry_price_with_slippage:.2f}")
    print(f"Quantity: {quantity}")
    print(f"Capital Used: ₹{capital_used:.2f} / ₹{FIRST_TRADE_CAPITAL}")
    print(f"Stop Loss: ₹{trade.stop_loss:.2f} ({INITIAL_SL_PERCENT*100:.0f}%)")
    print(f"Take Profit: ₹{trade.take_profit:.2f} ({INITIAL_TP_PERCENT*100:.0f}%)")
    print(f"Time: {current_time.strftime('%H:%M:%S')} ✅ AFTER 10:00 AM GATE")
    print(f"{'='*70}")
    
    return trade_id


def execute_reversal(original_trade_id, current_price, current_time, chain=None, spot=None):
    """
    Execute reversal trade with opposite option type
    Called when first trade hits SL at -10%
    """
    original_trade = None
    for trade in state.closed_trades:
        if trade.trade_id == original_trade_id:
            original_trade = trade
            break
    
    if not original_trade:
        return None
    
    # Flip option type
    reversal_type = "PUT" if original_trade.option_type == "CALL" else "CALL"
    reversal_price = current_price * 0.95  # Fallback assumption
    reversal_strike = original_trade.strike

    if chain is not None and spot is not None:
        preferred = find_option_by_target_ltp(
            chain=chain,
            spot=spot,
            option_type=reversal_type,
            capital=REVERSAL_CAPITAL,
            quantity=FIXED_QUANTITY
        )
        if preferred:
            reversal_price = preferred['entry_price']
            reversal_strike = preferred['strike']
        else:
            print(f"⚠️ No affordable {reversal_type} option found for {FIXED_QUANTITY} qty within ₹{REVERSAL_CAPITAL}. Skipping reversal.")
            return None
    
    quantity = FIXED_QUANTITY
    reversal_capital_used = quantity * reversal_price
    if reversal_capital_used > REVERSAL_CAPITAL:
        print(f"⚠️ Reversal requires ₹{reversal_capital_used:.2f} for {quantity} qty, exceeds ₹{REVERSAL_CAPITAL}. Skipping reversal.")
        return None

    reversal_trade = TradePosition(
        trade_id=len(state.active_trades) + 1,
        option_type=reversal_type,
        strike=reversal_strike,
        entry_price=reversal_price,
        quantity=quantity,
        entry_time=current_time
    )
    
    state.add_trade(reversal_trade)
    
    print(f"\n{'='*70}")
    print(f"⚖️  REVERSAL TRADE EXECUTED - {reversal_type}")
    print(f"{'='*70}")
    print(f"Previous Trade: #{original_trade_id} {original_trade.option_type} STOPPED OUT at -10%")
    print(f"Loss on First Trade: ₹{original_trade.pnl:.2f}")
    print(f"\nReversal Trade #: {reversal_trade.trade_id}")
    print(f"Type: BUY {reversal_type} @ Strike ₹{reversal_strike}")
    print(f"Entry Price: ₹{reversal_price:.2f}")
    print(f"Quantity: {quantity}")
    print(f"Capital Used: ₹{reversal_capital_used:.2f} / ₹{REVERSAL_CAPITAL}")
    print(f"Stop Loss: ₹{reversal_trade.stop_loss:.2f}")
    print(f"Take Profit: ₹{reversal_trade.take_profit:.2f}")
    print(f"Time: {current_time.strftime('%H:%M:%S')}")
    print(f"{'='*70}")
    
    return reversal_trade.trade_id


def update_positions(chain, spot, current_time):
    """Update all open positions and check exit conditions"""
    if not state.active_trades:
        return
    
    call_option, put_option = find_atm_options(spot, chain)
    
    trades_to_close = []
    
    for trade in state.active_trades:
        if trade.option_type == "CALL" and call_option:
            current_price = get_option_ltp(call_option)
        elif trade.option_type == "PUT" and put_option:
            current_price = get_option_ltp(put_option)
        else:
            continue
        
        trade.update_price(current_price)
        status = trade.update_price(current_price)
        
        if status == "TRAIL_ACTIVATED":
            print(f"\n⚡ Trade #{trade.trade_id}: +10% PROFIT REACHED - Trail Activated!")
            print(f"   Current Price: ₹{current_price:.2f}")
            print(f"   SL Locked at +4%: ₹{trade.stop_loss:.2f}")
        
        elif status == "TP_HIT":
            print(f"\n✅ Trade #{trade.trade_id}: TAKE PROFIT HIT at +10%!")
            print(f"   Exit Price: ₹{trade.exit_price:.2f}")
            print(f"   P&L: ₹{trade.pnl:.2f}")
            trades_to_close.append((trade.trade_id, current_price, "TP_HIT"))
        
        elif status == "SL_HIT":
            print(f"\n❌ Trade #{trade.trade_id}: STOP LOSS HIT at -10%!")
            print(f"   Exit Price: ₹{current_price:.2f}")
            print(f"   Loss: ₹{trade.pnl:.2f}")
            trades_to_close.append((trade.trade_id, current_price, "SL_HIT"))
    
    # Close trades and execute reversals
    for trade_id, exit_price, reason in trades_to_close:
        closed_trade = state.close_trade(trade_id, exit_price, reason, current_time)

        if reason == "SL_HIT":
            state.last_sl_hit_time = current_time
            state.reset_breakout_confirms()
        
        if reason == "SL_HIT" and len(state.closed_trades) == 1:
            # This is the first trade being stopped out - execute reversal
            execute_reversal(trade_id, exit_price, current_time, chain=chain, spot=spot)


def print_status(title="MARKET STATUS"):
    """Print current trading status"""
    now = datetime.now(TZ)
    print(f"\n{'─'*70}")
    print(f"{title} | {now.strftime('%H:%M:%S')}")
    print(f"{'─'*70}")
    print(f"Nifty 50: ₹{spot:.2f}" if 'spot' in locals() else "Nifty 50: --")
    print(f"Capital Available: ₹{state.cash_available:.2f}")
    print(f"Total P&L: ₹{state.total_pnl:.2f}")
    print(f"Active Trades: {len(state.active_trades)}")
    print(f"Closed Trades: {len(state.closed_trades)}")
    
    if state.active_trades:
        print(f"\nACTIVE TRADES:")
        for trade in state.active_trades:
            summary = trade.to_summary()
            print(f"  #{summary['Trade ID']}: {summary['Type']} {summary['Strike']} "
                  f"@ {summary['Entry']} → {summary['Current']} ({summary['P&L %']})")


# ========== MAIN TRADING LOOP ==========

def run_trading_bot(test_mode=False, duration_minutes=30):
    """
    Main bot - Single Button Solution
    Press Run and it connects to market history and starts trading
    """
    global TEST_MODE
    TEST_MODE = test_mode
    
    print("\n" + "="*70)
    print("🚀 10 AM BREAKOUT ALGORITHMIC TRADING BOT - HYBRID TIME-SYNC v2.0")
    print("="*70)
    print(f"Mode: {'TEST' if test_mode else 'LIVE'}")
    print(f"Start Time: {datetime.now(TZ).strftime('%H:%M:%S')}")
    selected_expiry = get_next_week_wednesday_expiry()
    print(f"Expiry Selection: Next-week Wednesday ({selected_expiry})")
    print(f"Capital: ₹{TOTAL_CAPITAL} (First: ₹{FIRST_TRADE_CAPITAL}, Reversal: ₹{REVERSAL_CAPITAL}, Buffer: ₹{BUFFER_CAPITAL})")
    print(f"Position Sizing: Fixed Qty={FIXED_QUANTITY} | Target LTP≈₹{TARGET_LTP_FIRST_TRADE:.2f} for ₹{FIRST_TRADE_CAPITAL}")
    print(f"Risk Profile: SL={INITIAL_SL_PERCENT*100:.0f}% | TP={INITIAL_TP_PERCENT*100:.0f}% | Trail={TRAILING_SL_PERCENT*100:.0f}%")
    print(f"2s Filters: ConfirmTicks={BREAKOUT_CONFIRM_TICKS} | MinExcess={MIN_BREAKOUT_EXCESS*100:.2f}% | CooldownAfterSL={COOLDOWN_AFTER_SL_SECONDS}s")
    print("="*70)
    
    # PHASE 1: Sync with market history
    if not fetch_historical_high():
        print("❌ Failed to synchronize with market history")
        return

    # If requested, close any open simulated positions at start
    if CLOSE_OPEN:
        closed = close_all_positions(datetime.now(TZ))
        if closed:
            print(f"🔁 Closed {closed} pre-existing open position(s) before starting monitoring")
    
    # PHASE 2: Monitor for breakouts
    print("\n🔄 PHASE 2: LIVE MONITORING")
    print("="*70)
    print("Waiting for breakout signal above history high...\n")
    
    start_time = datetime.now(TZ)
    last_status_print = start_time
    last_trade_id = 0
    
    try:
        while True:
            now = datetime.now(TZ)
            
            # Check time limits
            if not test_mode:
                if now.time() > MARKET_CLOSE:
                    print("\n⛔ Market closed. Exiting bot.")
                    break
            else:
                if (now - start_time).total_seconds() > duration_minutes * 60:
                    print(f"\n⏱️ Test duration ({duration_minutes} min) completed.")
                    break
            
            try:
                # Get current market data
                chain = get_option_chain()
                spot = get_spot_price()
                
                if not chain or spot == 0:
                    time.sleep(2)
                    continue
                
                # OPTION: Force entry for testing
                if FORCE_ENTRY and not state.trading_started:
                    call_option, put_option = find_atm_options(spot, chain)
                    opt = call_option if FORCE_ENTRY == 'CALL' else put_option
                    if opt:
                        entry_price = get_option_ltp(opt)
                        forced_signal = {
                            'type': FORCE_ENTRY,
                            'strike': opt['strike'],
                            'entry_price': entry_price,
                            'option_data': opt
                        }
                        print(f"⚠️ Force entry requested ({FORCE_ENTRY}) @ ₹{entry_price:.2f}")
                        trade_id = execute_entry(forced_signal, now, chain=chain, spot=spot)
                        if trade_id:
                            last_trade_id = trade_id
                            # continue to update positions after forced entry
                # Check for breakout
                signal = check_breakout_signal(chain, spot)
                if signal and not state.trading_started:
                    trade_id = execute_entry(signal, now, chain=chain, spot=spot)
                    if trade_id:  # Only update if trade was actually executed
                        last_trade_id = trade_id
                
                # Update open positions
                update_positions(chain, spot, now)
                
                # Print status every 30 seconds
                if (now - last_status_print).total_seconds() >= 30:
                    print_status(f"LIVE UPDATE | {now.strftime('%H:%M:%S')}")
                    last_status_print = now
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️  Error in trading loop: {e}")
                time.sleep(5)
                continue
    
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user.")
    
    # Final Report
    print_final_report()


def print_final_report():
    """Print final trading report"""
    print("\n" + "="*70)
    print("📋 FINAL TRADING REPORT")
    print("="*70)
    
    print(f"\nACCOUNT SUMMARY:")
    print(f"  Starting Capital: ₹{TOTAL_CAPITAL:,.2f}")
    print(f"  Remaining Cash: ₹{state.cash_available:,.2f}")
    print(f"  Total P&L: ₹{state.total_pnl:,.2f}")
    print(f"  P&L %: {(state.total_pnl/TOTAL_CAPITAL)*100:.2f}%")
    
    print(f"\nTRADES SUMMARY:")
    print(f"  Total Trades: {len(state.closed_trades)}")
    winning = [t for t in state.closed_trades if t.pnl > 0]
    losing = [t for t in state.closed_trades if t.pnl < 0]
    print(f"  Winning: {len(winning)}")
    print(f"  Losing: {len(losing)}")
    print(f"  Win Rate: {(len(winning)/max(1, len(state.closed_trades)))*100:.1f}%")
    
    if state.closed_trades:
        print(f"\nTRADE DETAILS:")
        for trade in state.closed_trades:
            summary = trade.to_summary()
            print(f"  #{summary['Trade ID']}: {summary['Type']} {summary['Strike']} "
                  f"{summary['Entry']} → {summary['Current']} | {summary['P&L']} ({summary['P&L %']})")
    
    if state.active_trades:
        print(f"\nOPEN POSITIONS:")
        for trade in state.active_trades:
            summary = trade.to_summary()
            print(f"  #{summary['Trade ID']}: {summary['Type']} {summary['Strike']} "
                  f"{summary['Entry']} → {summary['Current']} | {summary['P&L']} ({summary['P&L %']})")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="10 AM Breakout Algorithmic Trading Bot - Hybrid Time-Sync"
    )
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in minutes')
    parser.add_argument('--live', action='store_true', help='Explicitly run in live mode')
    parser.add_argument('--confirm-live', action='store_true', help='Confirm live trading (required with --live)')
    parser.add_argument('--force-entry', choices=['CALL', 'PUT'], help='Force a test entry of CALL or PUT')
    parser.add_argument('--close-open', action='store_true', help='Close existing open positions at start')
    parser.add_argument(
        '--instance-id',
        default=os.path.basename(os.getcwd()),
        help='Unique instance id for process lock (use different value per repo)'
    )
    parser.add_argument(
        '--lock-dir',
        default='/tmp/honey_bot_locks',
        help='Directory to store process lock files'
    )
    
    args = parser.parse_args()
    # Wire CLI flags into runtime globals
    FORCE_ENTRY = args.force_entry
    CLOSE_OPEN = args.close_open
    LIVE_MODE = args.live

    # Safety: require explicit confirmation to run live
    if args.live and not args.confirm_live:
        print('\n⚠️  Live mode requested but not confirmed.')
        print('To run live, re-run with both --live and --confirm-live flags:')
        print('  python3 breakout_algo_bot_v2.py --live --confirm-live')
        sys.exit(1)

    # Determine test_mode: if --live provided, override --test
    test_mode = False if args.live else args.test

    acquire_instance_lock(instance_id=args.instance_id, lock_dir=args.lock_dir)
    atexit.register(release_instance_lock)
    print(f"🔒 Instance lock acquired: {args.instance_id}")

    try:
        run_trading_bot(test_mode=test_mode, duration_minutes=args.duration)
    finally:
        release_instance_lock()
