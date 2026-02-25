"""
Trading module - provides basic trading functionality including
buy/sell orders and portfolio tracking.
"""


class TradingPortfolio:
    """Manages a simple trading portfolio."""

    def __init__(self):
        self.holdings = {}
        self.cash = 0.0
        self.trade_history = []

    def deposit(self, amount):
        """Deposit cash into the portfolio."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.cash += amount

    def buy(self, symbol, quantity, price):
        """Buy shares of a given symbol."""
        symbol = symbol.upper()
        total_cost = quantity * price
        if total_cost > self.cash:
            raise ValueError("Insufficient funds")
        self.cash -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.trade_history.append({
            "action": "buy",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
        })

    def sell(self, symbol, quantity, price):
        """Sell shares of a given symbol."""
        symbol = symbol.upper()
        held = self.holdings.get(symbol, 0)
        if quantity > held:
            raise ValueError(f"Insufficient holdings for {symbol}")
        self.holdings[symbol] = held - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.cash += quantity * price
        self.trade_history.append({
            "action": "sell",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
        })

    def portfolio_value(self, prices):
        """Calculate total portfolio value given a dict of current prices."""
        value = self.cash
        for symbol, quantity in self.holdings.items():
            value += quantity * prices.get(symbol.upper(), 0)
        return value
