#!/usr/bin/env python3
"""
Improved Nifty option-chain LTP dashboard for Upstox API.
- Reads ACCESS_TOKEN from env var UPSTOX_ACCESS_TOKEN or prompts user to set it.
- Properly URL-encodes instrument keys.
- Batch LTP fetch supports mixed separators returned by API.
- Better error handling and small retry/backoff.
"""
import os
import sys
import time
import logging
from datetime import datetime
from urllib.parse import quote, quote_plus

try:
    import requests
    import pandas as pd
    from dotenv import load_dotenv
except ImportError:
    print("\n[!] Missing Libraries: Please run 'pip install requests pandas python-dotenv' in your terminal.\n")
    sys.exit(1)

# Load credentials from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN") or "YOUR_ACCESS_TOKEN_HERE"
BASE_HEADERS = {"Accept": "application/json"}

if ACCESS_TOKEN and ACCESS_TOKEN != "YOUR_ACCESS_TOKEN_HERE":
    BASE_HEADERS["Authorization"] = f"Bearer {ACCESS_TOKEN}"


def _safe_get_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}


def get_market_quote(instrument_key):
    """Fetch LTP for a single instrument (handles both '|' and ':' keys)."""
    encoded = quote(instrument_key, safe='|,:')
    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={encoded}"
    try:
        r = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if r.status_code == 200:
            data = _safe_get_json(r).get("data", {})
            # API may return keys with either '|' or ':' - normalize
            return data.get(instrument_key) or data.get(instrument_key.replace("|", ":")) or {}
        logging.warning("get_market_quote returned status %s", r.status_code)
    except requests.RequestException as e:
        logging.warning("get_market_quote error: %s", e)
    return {}


def get_nifty_expiry_dates():
    """Return sorted list of expiries for Nifty 50."""
    inst = "NSE_INDEX|Nifty 50"
    url = f"https://api.upstox.com/v2/option/contract?instrument_key={quote(inst, safe='|') }"
    try:
        r = requests.get(url, headers=BASE_HEADERS, timeout=10)
        if r.status_code == 200:
            data = _safe_get_json(r).get("data", [])
            expiries = sorted({item.get("expiry") for item in data if item.get("expiry")})
            return expiries
        logging.warning("get_nifty_expiry_dates status %s", r.status_code)
    except requests.RequestException as e:
        logging.warning("get_nifty_expiry_dates error: %s", e)
    return []


def get_option_chain_data(expiry_date):
    """Fetch option chain for given expiry_date (string)."""
    inst = "NSE_INDEX|Nifty 50"
    url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(inst, safe='|')} &expiry_date={quote_plus(str(expiry_date))}"
    # remove accidental space around & if present
    url = url.replace(' ', '')
    try:
        r = requests.get(url, headers=BASE_HEADERS, timeout=15)
        if r.status_code == 200:
            return _safe_get_json(r).get("data", [])
        logging.warning("get_option_chain_data status %s", r.status_code)
    except requests.RequestException as e:
        logging.warning("get_option_chain_data error: %s", e)
    return []


def get_ltp_batch(instrument_keys):
    """Fetch LTP for list of instruments. Returns normalized keys with '|' separator."""
    if not instrument_keys:
        return {}
    # Quote each key preserving '|' and ':' so API accepts them
    quoted = ",".join(quote(k, safe='|:') for k in instrument_keys)
    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={quoted}"
    try:
        r = requests.get(url, headers=BASE_HEADERS, timeout=15)
        if r.status_code == 200:
            data = _safe_get_json(r).get("data", {})
            # Normalize returned keys (NSE_FO:12345 -> NSE_FO|12345)
            normalized = {k.replace(":", "|"): v for k, v in data.items()}
            return normalized
        logging.warning("get_ltp_batch status %s", r.status_code)
    except requests.RequestException as e:
        logging.warning("get_ltp_batch error: %s", e)
    return {}


def display_ltp_dashboard():
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("\n[!] Error: Please set UPSTOX_ACCESS_TOKEN environment variable before running.\n")
        return

    spot_info = get_market_quote("NSE_INDEX|Nifty 50")
    spot_price = spot_info.get("last_price") or 0

    expiries = get_nifty_expiry_dates()
    if not expiries:
        logging.error("No expiry dates found. Check token or API availability.")
        return
    nearest_expiry = expiries[0]

    chain_struct = get_option_chain_data(nearest_expiry)
    if not chain_struct:
        logging.error("Option chain empty for expiry %s", nearest_expiry)
        return

    # Ensure we have a list of dicts with strike_price
    chain_struct = [c for c in chain_struct if "strike_price" in c]
    chain_struct.sort(key=lambda x: x["strike_price"])

    lookup_price = spot_price if spot_price > 0 else chain_struct[len(chain_struct) // 2]["strike_price"]
    atm_index = 0
    for i, s in enumerate(chain_struct):
        if s["strike_price"] >= lookup_price:
            atm_index = i
            break

    visible_range = chain_struct[max(0, atm_index - 7): min(len(chain_struct), atm_index + 7)]

    rows = []
    for s in visible_range:
        strike = s["strike_price"]
        ce = s.get("call_options", {}) or {}
        pe = s.get("put_options", {}) or {}
        
        # Call data
        ce_market = ce.get("market_data", {}) or {}
        ce_ltp = ce_market.get("ltp", 0)
        ce_oi = ce_market.get("oi", 0)
        ce_bid = ce_market.get("bid_price", 0)
        ce_ask = ce_market.get("ask_price", 0)
        
        # Put data
        pe_market = pe.get("market_data", {}) or {}
        pe_ltp = pe_market.get("ltp", 0)
        pe_oi = pe_market.get("oi", 0)
        pe_bid = pe_market.get("bid_price", 0)
        pe_ask = pe_market.get("ask_price", 0)
        
        # PCR (Put-Call Ratio)
        pcr = pe_oi / ce_oi if ce_oi > 0 else 0
        
        rows.append({
            "C_OI": f"{ce_oi:,.0f}",
            "C_LTP": f"{ce_ltp:.2f}",
            "C_BID": f"{ce_bid:.2f}",
            "C_ASK": f"{ce_ask:.2f}",
            "STRIKE": int(strike),
            "P_BID": f"{pe_bid:.2f}",
            "P_ASK": f"{pe_ask:.2f}",
            "P_LTP": f"{pe_ltp:.2f}",
            "P_OI": f"{pe_oi:,.0f}",
            "PCR": f"{pcr:.2f}",
        })

    df = pd.DataFrame(rows)

    print(f"\n{'='*60}")
    print(f" NIFTY 50: {spot_price} | EXPIRY: {nearest_expiry}")
    print(f" TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    if not df.empty:
        print(df.to_string(index=False, justify='center'))
    else:
        print("Data is currently empty. Retrying...")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    try:
        while True:
            display_ltp_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped by user.")
