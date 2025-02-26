import requests
import json
import time
from core.angel_api import AngelOneAPI

class TradeExecution:
    def __init__(self):
        """Initialize with Angel One API credentials and trading parameters."""
        self.api = AngelOneAPI()  # API authentication & token handling
        self.api.login()
        self.max_risk_per_trade = 5000  # Maximum loss per trade in INR
        self.stop_loss_pct = 0.02  # 2% Stop Loss
        self.target_profit_pct = 0.05  # 5% Profit Booking

    def fetch_market_price(self, symbol):
        """
        Fetch **real-time** market price for a given symbol.
        :param symbol: Trading symbol (e.g., 'NIFTY25FEBCE')
        :return: Last traded price (LTP)
        """
        url = f"https://smartapi.angelbroking.com/marketdata/instruments?symbol={symbol}"
        headers = {"Authorization": f"Bearer {self.api.access_token}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("ltp", None)  # Extract Last Traded Price

    def calculate_trade_quantity(self, capital, price):
        """
        **Dynamically** determine trade quantity based on available capital.
        :param capital: Available funds
        :param price: Current market price
        :return: Number of lots
        """
        lot_size = 50  # Nifty options lot size
        max_lots = int(capital / (price * lot_size))
        return max(1, max_lots)  # Ensure minimum 1 lot

    def place_order(self, tradingsymbol, transaction_type, quantity):
        """
        Execute an **order** using Angel One API.
        :param tradingsymbol: Symbol (e.g., 'NIFTY25FEBCE')
        :param transaction_type: 'BUY' or 'SELL'
        :param quantity: Number of lots
        :return: Order response
        """
        order_payload = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": self.api.get_symbol_token(tradingsymbol),
            "transactiontype": transaction_type,
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": self.fetch_market_price(tradingsymbol),
            "quantity": quantity
        }

        response = self.api.place_order(order_payload)
        return response

    def execute_trade(self, symbol, signal, capital=100000):
        """
        Execute trade based on **AI signal**.
        :param symbol: Trading symbol (e.g., 'NIFTY25FEBCE')
        :param signal: 'BUY' or 'SELL'
        :param capital: Available trading capital
        :return: Order status
        """
        price = self.fetch_market_price(symbol)
        if not price:
            return {"status": "Error", "message": "Failed to fetch market price"}

        quantity = self.calculate_trade_quantity(capital, price)

        if signal == "BUY":
            order_response = self.place_order(symbol, "BUY", quantity)
        elif signal == "SELL":
            order_response = self.place_order(symbol, "SELL", quantity)
        else:
            return {"status": "Error", "message": "Invalid trade signal"}

        return order_response

# Example Usage
if __name__ == "__main__":
    trader = TradeExecution()
    ai_signal = "BUY"  # Assume AI model predicts 'BUY'
    symbol = "NIFTY25FEBCE"
    
    trade_result = trader.execute_trade(symbol, ai_signal)
    print(trade_result)
