#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
token = os.getenv("UPSTOX_ACCESS_TOKEN")

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {token}"
}

from urllib.parse import quote

# Test 1: Spot Price with CORRECT format
print("=" * 60)
print("TEST 1: Get Nifty 50 Spot Price")
print("=" * 60)
symbol = "NSE_INDEX|Nifty 50"
url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={quote(symbol, safe='|,:')}"
print(f"URL: {url}\n")
r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
response = r.json()
print(f"Response: {json.dumps(response, indent=2)}")
if response.get('data'):
    ltp = response['data'].get(symbol, {}).get('last_price', 0)
    print(f"✅ Spot Price: ₹{ltp}")
else:
    print("❌ No data returned")

# Test 2: Option Chain
print("\n" + "=" * 60)
print("TEST 2: Get Option Chain for 2026-02-17")
print("=" * 60)
from urllib.parse import quote_plus
url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(symbol, safe='|')}&expiry_date={quote_plus('2026-02-17')}"
url = url.replace(' ', '')
print(f"URL: {url}\n")
r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
response = r.json()
if response.get('data'):
    data = response['data']
    print(f"✅ Got {len(data)} strikes")
    if data:
        first = data[0]
        print(f"   First strike: {first.get('strike_price')}")
        print(f"   Has CALL: {'call_options' in first}")
        print(f"   Has PUT: {'put_options' in first}")
else:
    print("❌ No data returned")
    print(f"Response: {json.dumps(response, indent=2)[:500]}")
