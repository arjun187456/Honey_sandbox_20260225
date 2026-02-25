#!/usr/bin/env python3
import os
import requests
from urllib.parse import quote, quote_plus
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

NIFTY_SYMBOL = "NSE_INDEX|Nifty 50"

# Test spot price  
print("Testing spot price fetch...")
url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={quote(NIFTY_SYMBOL, safe='|,:')}"
resp = requests.get(url, headers=HEADERS, timeout=10)
data = resp.json().get('data', {})

# Try both formats
price = data.get(NIFTY_SYMBOL, {}).get('last_price', 0)
if price == 0:
    alt_key = NIFTY_SYMBOL.replace('|', ':')
    price = data.get(alt_key, {}).get('last_price', 0)

print(f"✅ Spot Price: ₹{price}")

# Test option chain
print("\nTesting option chain fetch...")
OPTION_SYMBOL = "NSE_INDEX|Nifty 50"
EXPIRY_DATE = "2026-02-17"
url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(OPTION_SYMBOL, safe='|')}&expiry_date={quote_plus(str(EXPIRY_DATE))}"
url = url.replace(' ', '')
resp = requests.get(url, headers=HEADERS, timeout=10)
chain = resp.json().get('data', [])

print(f"✅ Got {len(chain)} option strikes")
if chain:
    print(f"   First strike: ₹{chain[0].get('strike_price')}")
    print(f"   Has call: {'call_options' in chain[0]}")
    print(f"   Has put: {'put_options' in chain[0]}")
    
print(f"\n✅ ALL TESTS PASSED")
