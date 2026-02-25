#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests
import json
from urllib.parse import quote

load_dotenv()
token = os.getenv("UPSTOX_ACCESS_TOKEN")

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {token}"
}

inst = "NSE_INDEX|Nifty 50"
url = f"https://api.upstox.com/v2/option/contract?instrument_key={quote(inst, safe='|')}"

print(f"Testing v2 endpoint for option contracts")
print(f"URL: {url}\n")

r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response:\n{json.dumps(r.json(), indent=2) if r.text else 'No response body'}")
