from .model_inference import ModelInference
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_model(symbol: str, model_path: str, test_data: pd.DataFrame):
    """Evaluate model performance"""
    inference = ModelInference(model_path)
    
    # Make predictions
    predictions = []
    for idx in range(len(test_data)):
        market_data = test_data.iloc[idx].to_dict()
        pred = inference.predict(market_data)
        predictions.append(pred["prediction"])
    
    # Calculate actual returns
    actual = (test_data['close'].shift(-1) > test_data['close']).astype(int)
    
    # Generate report
    print(f"\nModel Evaluation for {symbol}")
    print("\nClassification Report:")
    print(classification_report(actual[:-1], predictions[:-1]))
    
    # Plot confusion matrix
    cm = confusion_matrix(actual[:-1], predictions[:-1])
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {symbol}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig(f'models/{symbol.lower()}_confusion_matrix.png')
    plt.close()

if __name__ == "__main__":
    # Load test data and evaluate models
    for symbol in ["NIFTY", "BANKNIFTY"]:
        model_path = f"models/{symbol.lower()}_model.joblib"
        # Load your test data here
        test_data = pd.read_csv(f"data/{symbol.lower()}_test.csv")
        evaluate_model(symbol, model_path, test_data) 