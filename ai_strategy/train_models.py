from .model_training import ModelTrainer
import pandas as pd
import yfinance as yf
import os

def train_models():
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Symbol mapping for NSE indices
    symbols = {
        "NIFTY": "^NSEI",  # Changed from ^NIFTY to ^NSEI
        "BANKNIFTY": "^NSEBANK"  # Changed from ^BANKNIFTY to ^NSEBANK
    }
    
    for name, symbol in symbols.items():
        print(f"Training model for {name}")
        
        try:
            # Download historical data
            print(f"Downloading data for {symbol}...")
            data = yf.download(
                symbol,
                start="2020-01-01",
                end="2024-02-19",
                progress=True,
                auto_adjust=True
            )
            
            if data.empty:
                print(f"No data found for {symbol}")
                continue
                
            print(f"Downloaded {len(data)} rows of data")
            print("Sample data:")
            print(data.head())
            
            # Initialize trainer
            trainer = ModelTrainer(name)
            
            # Train model
            print(f"Training model for {name}...")
            metrics = trainer.train(data)
            print(f"Training metrics for {name}:")
            print(metrics)
            
            # Save model
            model_path = f"models/{name.lower()}_model.joblib"
            trainer.save_model(model_path)
            print(f"Model saved to {model_path}")
            
        except Exception as e:
            print(f"Error training model for {name}: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    print("Starting model training...")
    train_models()
    print("Training complete!") 