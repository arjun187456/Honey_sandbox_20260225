# Upstox API Documentation for Algo Trading

## Table of Contents
1. [Setup & Authentication](#setup--authentication)
2. [Market Data APIs](#market-data-apis)
3. [Options Chain APIs](#options-chain-apis)
4. [Error Handling](#error-handling)
5. [Code Examples](#code-examples)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Setup & Authentication

### 1. Generate API Credentials

**Steps:**
1. Log in to your [Upstox Account](https://upstox.com/)
2. Go to **Dashboard → Settings → Connected Apps**
3. Click **Create App** or select existing app
4. Note down:
   - **API Key**: Used to authenticate app
   - **API Secret**: Keep secure, used for token generation
   - **Access Token**: JWT token for API calls

### 2. Environment Setup

Create a `.env` file in your project root:

```bash
# .env
UPSTOX_ACCESS_TOKEN=your_jwt_token_here
UPSTOX_API_KEY=your_api_key_here
UPSTOX_API_SECRET=your_api_secret_here  # Optional, for advanced features
```

### 3. Load Credentials in Python

```python
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")

BASE_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
```

### 4. Token Expiry & Refresh

- **Validity**: 1 hour by default
- **How to refresh**: Generate new token from Upstox dashboard when expired
- **Detection**: 401 Unauthorized status code indicates expired token

---

## Market Data APIs

### 1. Get LTP (Last Traded Price)

**Endpoint**: `GET /v3/market-quote/ltp`

**Purpose**: Fetch real-time last traded price for instruments

**Request**:
```bash
GET https://api.upstox.com/v3/market-quote/ltp?instrument_key=NSE_INDEX%7CNifty%2050

Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  Accept: application/json
```

**Python Example**:
```python
def get_ltp(instrument_key):
    from urllib.parse import quote
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    encoded_key = quote(instrument_key, safe='|,:')
    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={encoded_key}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return data['data'][instrument_key]['last_price']
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
nifty_ltp = get_ltp("NSE_INDEX|Nifty 50")
print(f"Nifty 50 LTP: {nifty_ltp}")
```

**Response Example**:
```json
{
  "status": "success",
  "data": {
    "NSE_INDEX:Nifty 50": {
      "last_price": 25527.15,
      "instrument_token": "NSE_INDEX|Nifty 50",
      "ltq": 0,
      "volume": 0,
      "cp": 25471.1
    }
  }
}
```

**Instrument Keys**:
- Nifty 50 Index: `NSE_INDEX|Nifty 50`
- Options: `NSE_FO|48063` (token) or `NSE_FO:NIFTY2621723100CE` (contract code)
- Stocks: `NSE_EQ|INE002A01018` (example: TCS)

---

## Options Chain APIs

### 1. Get Option Chain Contracts

**Endpoint**: `GET /v2/option/chain`

**Purpose**: Fetch all available option contracts for a symbol and expiry

**Request**:
```bash
GET https://api.upstox.com/v2/option/chain?instrument_key=NSE_INDEX%7CNifty%2050&expiry_date=2026-02-17

Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  Accept: application/json
```

**Python Example**:
```python
def get_option_chain(symbol="NSE_INDEX|Nifty 50", expiry_date="2026-02-17"):
    from urllib.parse import quote, quote_plus
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    url = f"https://api.upstox.com/v2/option/chain?instrument_key={quote(symbol, safe='|')}&expiry_date={quote_plus(str(expiry_date))}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error: {response.status_code}")
        return []

# Usage
chain = get_option_chain()
print(f"Total strikes: {len(chain)}")

for strike_data in chain[:3]:  # Print first 3 strikes
    print(f"Strike: {strike_data['strike_price']}")
    print(f"  Call LTP: {strike_data['call_options']['market_data']['ltp']}")
    print(f"  Put LTP: {strike_data['put_options']['market_data']['ltp']}")
```

**Response Structure**:
```json
{
  "status": "success",
  "data": [
    {
      "strike_price": 25200.0,
      "expiry": "2026-02-17",
      "call_options": {
        "instrument_key": "NSE_FO|48063",
        "market_data": {
          "ltp": 347.50,
          "bid_price": 345.00,
          "ask_price": 348.00,
          "oi": 380185,
          "volume": 1000
        },
        "option_greeks": {
          "delta": 0.95,
          "gamma": 0.001,
          "theta": -50.0,
          "vega": 2.5,
          "iv": 18.5,
          "pop": 94.5
        }
      },
      "put_options": {
        "instrument_key": "NSE_FO|48064",
        "market_data": {
          "ltp": 12.50,
          "bid_price": 12.25,
          "ask_price": 12.75,
          "oi": 7463820,
          "volume": 5000
        },
        "option_greeks": {
          "delta": -0.05,
          "gamma": 0.001,
          "theta": -5.0,
          "vega": 0.2,
          "iv": 68.5,
          "pop": 0.5
        }
      }
    }
  ]
}
```

### 2. Get Option Expiry Dates

**Endpoint**: `GET /v2/option/contract` (implicit via filtering)

**Python Example**:
```python
def get_expiry_dates(symbol="NSE_INDEX|Nifty 50"):
    from urllib.parse import quote
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    url = f"https://api.upstox.com/v2/option/contract?instrument_key={quote(symbol, safe='|')}"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()['data']
        expiries = sorted(set(item['expiry'] for item in data))
        return expiries
    return []

# Usage
expiries = get_expiry_dates()
print(f"Available expiries: {expiries}")
```

---

## Data Fields Explanation

### Market Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `ltp` | Float | Last Traded Price |
| `bid_price` | Float | Best Bid Price (buyers) |
| `ask_price` | Float | Best Ask Price (sellers) |
| `oi` | Integer | Open Interest (contracts outstanding) |
| `volume` | Integer | Trading volume today |
| `cp` | Float | Close price (previous day) |

### Option Greeks

| Greek | Range | Interpretation |
|-------|-------|-----------------|
| **Delta (Δ)** | -1 to +1 | Price sensitivity per rupee. Calls: 0 to 1, Puts: -1 to 0 |
| **Gamma (Γ)** | 0 to ∞ | Rate of delta change. Higher = faster price moves |
| **Theta (Θ)** | -∞ to ∞ | Time decay per day. Negative = losing value daily |
| **Vega (ν)** | -∞ to ∞ | Sensitivity to volatility. Higher = volatility impact |
| **IV** | % | Implied Volatility. Market's expectation of price movement |
| **POP** | % | Probability of Profit for the option |

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | Process data normally |
| 401 | Unauthorized | Token expired → Generate new token |
| 403 | Forbidden | Insufficient permissions → Check API scope |
| 404 | Not Found | Invalid instrument key → Verify key format |
| 429 | Rate Limited | Too many requests → Add delays (5 requests/sec limit) |
| 500 | Server Error | API issue → Retry with backoff |

### Error Handling Code

```python
import requests
import time

def safe_api_call(url, max_retries=3, backoff_factor=2):
    """Make API call with retry logic"""
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Error: Token expired. Please regenerate.")
                break
            elif response.status_code == 429:
                wait_time = backoff_factor ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"Error: {response.status_code} - {response.text}")
                break
                
        except requests.Timeout:
            print(f"Timeout on attempt {attempt + 1}. Retrying...")
            time.sleep(backoff_factor ** attempt)
        except Exception as e:
            print(f"Exception: {e}")
            break
    
    return None
```

---

## Code Examples

### Example 1: Real-time Option Chain Dashboard

```python
import time
import pandas as pd
from datetime import datetime

def live_option_dashboard(expiry="2026-02-17", update_interval=5):
    """Display live option chain data"""
    
    while True:
        chain = get_option_chain(expiry_date=expiry)
        spot = get_ltp("NSE_INDEX|Nifty 50")
        
        # Prepare data
        rows = []
        for strike in chain:
            ce = strike['call_options']['market_data']
            pe = strike['put_options']['market_data']
            
            rows.append({
                'Strike': int(strike['strike_price']),
                'Call_OI': ce['oi'],
                'Call_LTP': ce['ltp'],
                'Put_LTP': pe['ltp'],
                'Put_OI': pe['oi'],
                'PCR': pe['oi'] / ce['oi'] if ce['oi'] > 0 else 0
            })
        
        df = pd.DataFrame(rows).sort_values('Strike')
        
        # Display
        print(f"\n{'='*60}")
        print(f"Nifty 50: {spot} | Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print(df.to_string(index=False))
        
        time.sleep(update_interval)

# Run:
# live_option_dashboard()
```

### Example 2: PCR-Based Trading Signal

```python
def generate_pcr_signal(expiry="2026-02-17"):
    """Generate trading signal based on PCR"""
    
    chain = get_option_chain(expiry_date=expiry)
    
    total_ce_oi = sum(c['call_options']['market_data']['oi'] for c in chain)
    total_pe_oi = sum(c['put_options']['market_data']['oi'] for c in chain)
    
    pcr = total_pe_oi / total_ce_oi
    
    if pcr > 1.2:
        return "BULLISH", pcr
    elif pcr < 0.8:
        return "BEARISH", pcr
    else:
        return "NEUTRAL", pcr

# Usage:
signal, pcr_value = generate_pcr_signal()
print(f"Signal: {signal} (PCR: {pcr_value:.2f})")
```

### Example 3: Iron Condor Strategy Setup

```python
def find_iron_condor_strikes(expiry="2026-02-17", distance=200):
    """Find strikes for iron condor strategy"""
    
    chain = get_option_chain(expiry_date=expiry)
    spot = get_ltp("NSE_INDEX|Nifty 50")
    
    # Find strikes
    short_call_strike = spot + distance
    short_put_strike = spot - distance
    
    long_call_strike = spot + distance + 200
    long_put_strike = spot - distance - 200
    
    print(f"Iron Condor Setup (Spot: {spot})")
    print(f"  Long Call:   {long_call_strike:.0f}")
    print(f"  Short Call:  {short_call_strike:.0f}")
    print(f"  Short Put:   {short_put_strike:.0f}")
    print(f"  Long Put:    {long_put_strike:.0f}")
```

---

## Common Issues & Solutions

### Issue 1: 401 Unauthorized Error

**Cause**: Access token is expired or invalid

**Solution**:
```python
# 1. Generate new token from Upstox dashboard
# 2. Update .env file
# 3. Restart script

# Or automatically check:
if response.status_code == 401:
    print("Token invalid. Please generate new token from Upstox dashboard.")
```

### Issue 2: Rate Limiting (429 Error)

**Cause**: Too many API requests in short time

**Solution**:
```python
# Add delay between requests
time.sleep(0.2)  # 200ms between calls

# Or batch requests
# Instead of: 100 individual LTP calls
# Do: 1 batch call with 100 instrument keys
```

### Issue 3: Wrong Instrument Key Format

**Common Mistakes**:
```
❌ "Nifty 50"                    # Just the name
❌ "NSE_INDEX:Nifty 50"          # Colon instead of pipe
❌ "NSE_FO|NIFTY2621723100CE"   # Using contract code in LTP API

✅ "NSE_INDEX|Nifty 50"          # Correct for LTP
✅ "NSE_FO|48063"                # Correct for options
```

**Solution**:
```python
# Always use the key from API response
response = get_option_chain()
correct_key = response[0]['call_options']['instrument_key']
```

### Issue 4: Empty Data Response

**Cause**: 
- Market closed
- Invalid expiry date
- No permission for that instrument

**Solution**:
```python
# Check if data exists
if not chain:
    print("No data available. Check:")
    print("  - Market status (9:15 AM - 3:30 PM IST)")
    print("  - Expiry date is valid")
    print("  - Token has permissions")
```

---

## Best Practices

1. **Always validate API responses**
   ```python
   if response.status_code != 200:
       return None  # Don't process failed requests
   ```

2. **Implement rate limiting**
   ```python
   import time
   time.sleep(0.2)  # Respect API limits
   ```

3. **Use try-except blocks**
   ```python
   try:
       data = requests.get(url, timeout=10).json()
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Store tokens securely**
   ```python
   # Don't hardcode tokens
   # Use .env files or environment variables
   ```

5. **Monitor token expiry**
   ```python
   # Keep track of token generation time
   # Regenerate before expiry (1 hour)
   ```

---

## Useful Links

- **Upstox Developer Docs**: https://developer.upstox.com/
- **API Status**: https://status.upstox.com/
- **Support**: support@upstox.com
- **Community**: https://forum.upstox.com/

---

## Summary

| Task | Endpoint | Method |
|------|----------|--------|
| Get Spot Price | `/v3/market-quote/ltp` | GET |
| Get Option Chain | `/v2/option/chain` | GET |
| Get Expiries | `/v2/option/contract` | GET |
| Get Order Book | `/v2/portfolio/orders` | GET |
| Place Order | `/v2/order/place` | POST |

**Remember**: Always check API documentation for latest updates and changes.
