# Honey - Nifty 50 Algo Trading Dashboard

A complete algorithmic trading solution for NSE Nifty 50 options analysis and strategy execution using Upstox API.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Pandas](https://img.shields.io/badge/Pandas-Latest-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Latest-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

## 📊 Features

### ✅ Implemented
- **Real-time Option Chain Dashboard**: Live updates every 5 seconds
- **Market Data Integration**: Direct Upstox API connection
- **Data Analysis Tools**: Pandas-based data manipulation
- **Visualization**: Matplotlib charts and graphs
- **API Documentation**: Complete guide with examples
- **Jupyter Notebooks**: Interactive analysis tutorials
- **Version Control**: Git integration

### 🚀 Core Components

#### 1. **Live Dashboard** (`nifty_option_dashboard.py`)
```bash
python3 nifty_option_dashboard.py
```

Features:
- Real-time Nifty 50 spot price
- Option chain with 14 ATM strikes
- Open Interest (OI) for calls and puts
- Put-Call Ratio (PCR) analysis
- Bid-Ask spreads
- Auto-refresh every 5 seconds

**Sample Output**:
```
============================================================
 NIFTY 50: 25527.85 | EXPIRY: 2026-02-17
 TIME: 2026-02-16 11:36:43
============================================================
   C_OI    C_LTP  C_BID  C_ASK   STRIKE P_BID  P_ASK  P_LTP     P_OI     PCR 
   380,185 351.00 350.55 351.00  25200   12.00  12.05  12.05  7,463,820 19.63
   154,180 304.35 303.65 304.30  25250   14.95  15.00  14.95  4,372,225 28.36
   ...
============================================================
```

#### 2. **Data Analysis Notebook** (`data_analysis_tutorial.ipynb`)

10-step tutorial including:
1. Library imports and setup
2. API connection configuration
3. Data fetching and preparation
4. Metrics calculation
5. Open Interest visualization
6. PCR analysis charts
7. Greeks analysis (Delta, Gamma, Theta, Vega)
8. Trading signal generation
9. Performance metrics
10. Practice exercises

#### 3. **API Documentation** (`API_DOCUMENTATION.md`)

Complete reference with:
- Setup & authentication guide
- Market data API endpoints
- Options chain API usage
- Error handling
- 10+ code examples
- Troubleshooting guide

---

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Git

### Step 1: Clone Repository
```bash
cd /workspaces
git clone <your-repo-url>
cd Honey
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests pandas python-dotenv matplotlib numpy
```

### Step 3: Get Upstox API Credentials
1. Log in to [Upstox Dashboard](https://upstox.com/)
2. Go to **Settings → Connected Apps**
3. Create new app or use existing
4. Copy **Access Token**

### Step 4: Set Up Environment
Create `.env` file:
```bash
UPSTOX_ACCESS_TOKEN=eyJ0eXAibJ3...your_token_here
UPSTOX_API_KEY=your_api_key_here
```

### Step 5: Run Dashboard
```bash
python3 nifty_option_dashboard.py
```

---

## 📚 Quick Start

### 1. View Live Option Chain
```bash
# Terminal 1: Run dashboard
python3 nifty_option_dashboard.py

# Output updates every 5 seconds with live prices
```

### 2. Analyze Data in Jupyter
```bash
# Terminal: Open notebook
jupyter notebook data_analysis_tutorial.ipynb

# Run cells to fetch and visualize option chain data
```

### 3. Generate Trading Signals
```python
# In Python/Notebook
from upstox_connection import get_option_chain, get_spot_price

chain = get_option_chain()
spot = get_spot_price()

# PCR Analysis
total_put_oi = sum(c['put_options']['market_data']['oi'] for c in chain)
total_call_oi = sum(c['call_options']['market_data']['oi'] for c in chain)
pcr = total_put_oi / total_call_oi

print(f"Market PCR: {pcr:.2f}")
if pcr > 1.2:
    print("🟢 BULLISH sentiment")
elif pcr < 0.8:
    print("🔴 BEARISH sentiment")
```

---

## 📖 File Structure

```
Honey/
├── nifty_option_dashboard.py    # Live dashboard script
├── data_analysis_tutorial.ipynb # Interactive Jupyter notebook
├── API_DOCUMENTATION.md         # Complete API reference
├── README.md                    # This file
├── .env                         # API credentials (git-ignored)
├── .gitignore                   # Git ignore rules
└── zephyer_testcode.py         # Test examples
```

---

## 🔑 Key Concepts

### Open Interest (OI)
- **Definition**: Number of outstanding option contracts
- **Interpretation**: Higher OI = More liquidity
- **Usage**: Identify popular strikes

### Put-Call Ratio (PCR)
```
PCR = Total Put OI / Total Call OI

PCR > 1.2  → BULLISH (More puts = protective buying)
PCR = 1.0  → NEUTRAL (Balanced)
PCR < 0.8  → BEARISH (More calls = upside betting)
```

### Greeks Explained

| Greek | Meaning | Trading Use |
|-------|---------|-------------|
| **Delta** | Rate of price change | Probability of ITM |
| **Gamma** | Acceleration (delta change) | Accelerated P&L |
| **Theta** | Time decay | Daily profit/loss |
| **Vega** | Volatility sensitivity | Volatility trades |
| **IV** | Implied Volatility | Premium levels |

### Max Pain
- Strike with highest Open Interest
- Market tends to gravitate here at expiry
- Acts as natural support/resistance

---

## 💡 Example Strategies

### 1. PCR-Based Direction Trading
```python
# If PCR > 1.2, market is bullish
# Buy call options or go long
if market_pcr > 1.2:
    action = "BUY_CALL"
```

### 2. Iron Condor Setup
```python
# Simultaneously sell OTM call and put
short_call = atm + 200
short_put = atm - 200
# Target: Premium collection from both sides
```

### 3. OI-Based Strike Selection
```python
# Trade at strike with highest OI
# Best liquidity and tight spreads
max_oi_strike = df[df['Total_OI'].idxmax()]['Strike']
```

---

## 🔐 Security Best Practices

1. **Never hardcode tokens**
   ```python
   # ❌ Wrong
   token = "eyJ0eXAi..."
   
   # ✅ Right
   token = os.getenv("UPSTOX_ACCESS_TOKEN")
   ```

2. **Keep `.env` in `.gitignore`**
   ```
   # .gitignore
   .env
   .env.local
   ```

3. **Regenerate tokens regularly**
   - Tokens expire after 1 hour
   - Keep track of generation time
   - Automate refresh process

4. **Use HTTPS only**
   - All Upstox APIs use HTTPS
   - Verify SSL certificates

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Token expired or invalid

**Solution**:
```bash
# 1. Generate new token from Upstox dashboard
# 2. Update .env file:
UPSTOX_ACCESS_TOKEN=new_token_here
# 3. Restart script
```

### Issue: No Data Showing

**Cause**: Market closed or invalid instrument key

**Solution**:
```
✓ Check market hours (9:15 AM - 3:30 PM IST)
✓ Verify API token is valid
✓ Check expiry date is correct
✓ Ensure app has market data permission
```

### Issue: Slow Response

**Cause**: Network latency or rate limiting

**Solution**:
```python
# Increase timeout
response = requests.get(url, timeout=15)

# Add delays between calls
time.sleep(0.5)
```

---

## 📊 Workflow

```
1. Start Dashboard
   ↓
2. Monitor Live Prices
   ↓
3. Analyze in Jupyter Notebook
   ↓
4. Identify Opportunities (PCR, OI, Greeks)
   ↓
5. Generate Signals
   ↓
6. Execute Orders (future feature)
   ↓
7. Track P&L
```

---

## 📈 Data Points Tracked

Per Strike:
- Call LTP (Last Traded Price)
- Call OI (Open Interest)
- Call Greeks (Delta, Gamma, Vega, Theta)
- Call IV (Implied Volatility)
- Put LTP
- Put OI
- Put Greeks
- Put IV
- Put-Call Ratio
- Bid-Ask Spreads

---

## 🎯 Next Steps

- [ ] Implement order placement
- [ ] Add notification system
- [ ] Create strategy backtesting
- [ ] Build performance dashboard
- [ ] Add database for historical data
- [ ] Develop mobile app integration
- [ ] Create automated trading bot

---

## 📚 Learning Resources

1. **Upstox API**: https://developer.upstox.com/
2. **Options Trading**: https://www.investopedia.com/options-basics/
3. **Pandas Guide**: https://pandas.pydata.org/docs/
4. **Matplotlib Tutorial**: https://matplotlib.org/
5. **Python for Finance**: https://www.py4finance.com/

---

## 🤝 Contributing

Found a bug or have a suggestion?

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## ⚠️ Disclaimer

```
This is an educational tool for learning algorithmic trading.
Not financial advice. Past performance ≠ future results.
Use at your own risk. Always test strategies thoroughly.
Follow all regulatory requirements in your country.
```

---

## 📞 Support

- **Email**: support@upstox.com
- **Forum**: https://forum.upstox.com/
- **Documentation**: https://developer.upstox.com/docs/

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎓 About the Author

Built as a learning project for Upstox Algo Trading Crash Course.

**Course Topics Covered**:
- ✅ Python & VS Code setup
- ✅ Required libraries (Pandas, Matplotlib, Requests)
- ✅ Virtual environments
- ✅ Upstox API integration
- ✅ Option chain data analysis
- ✅ Trading signal generation
- ✅ Git & GitHub basics

---

## 🚀 Latest Updates

**v1.0.0** (2026-02-16)
- ✅ Live option chain dashboard
- ✅ Real-time data visualization
- ✅ API documentation complete
- ✅ Jupyter tutorial notebook
- ✅ Git version control

---

**Happy Trading! 📈💰**

Remember: "With great data comes great profits!" 🎯

