from backend.api.trade_execution import TradeExecution
from backend.ai_strategy.model_inference import ModelInference

class TradeManager:
    def __init__(self, api_key, client_id):
        self.trader = TradeExecution(api_key, client_id)
        self.ai_model = ModelInference()

    def execute_trade(self, market_data):
        """Decides and executes trades based on AI model."""
        prediction = self.ai_model.predict(market_data)

        if prediction == 1:
            self.trader.place_order("NIFTY25FEBCE", qty=1, transaction_type="BUY")
        elif prediction == -1:
            self.trader.place_order("NIFTY25FEBCE", qty=1, transaction_type="SELL")
        else:
            print("⚠️ No Trade Signal!")

# Example Usage
if __name__ == "__main__":
    manager = TradeManager(api_key="your_api_key", client_id="your_client_id")
    sample_data = {"Close": 18000, "Volume": 50000}
    manager.execute_trade(sample_data)
