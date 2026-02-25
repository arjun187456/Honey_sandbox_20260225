# Honey_sandbox_20260225
trading new

## Trading Module

A simple Python trading portfolio module (`trading.py`) that supports:

- **Deposit** cash into your portfolio
- **Buy** shares of any symbol
- **Sell** shares from your holdings
- **Portfolio value** calculation given current market prices

### Example Usage

```python
from trading import TradingPortfolio

portfolio = TradingPortfolio()
portfolio.deposit(10000)
portfolio.buy("AAPL", 10, 150.0)
portfolio.sell("AAPL", 5, 160.0)
print(portfolio.portfolio_value({"AAPL": 160.0}))
```
