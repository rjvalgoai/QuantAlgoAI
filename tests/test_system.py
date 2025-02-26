import os
from pathlib import Path
import pandas as pd
import numpy as np

def test_system():
    print("🔍 Testing QuantAlgoAI System...")
    
    # 1. Test Data Pipeline
    print("\n1. Testing Data Pipeline...")
    try:
        from ai_strategy.feature_engineering import FeatureEngineer
        fe = FeatureEngineer()
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Open': np.random.randn(100) * 100 + 1000,
            'High': np.random.randn(100) * 100 + 1050,
            'Low': np.random.randn(100) * 100 + 950,
            'Close': np.random.randn(100) * 100 + 1000,
            'Volume': np.random.randint(1000, 10000, 100)
        })
        
        features = fe.calculate_technical_features(sample_data)
        print("✅ Feature Engineering: Working")
        print(f"Generated {len(fe.feature_names)} features")
        
    except Exception as e:
        print(f"❌ Feature Engineering Failed: {str(e)}")
        return False
    
    # 2. Test Model Training
    print("\n2. Testing Model Training...")
    try:
        from ai_strategy.model_training import ModelTrainer
        trainer = ModelTrainer("TEST")
        metrics = trainer.train(sample_data)
        print("✅ Model Training: Working")
        print(f"Training Metrics: {metrics}")
        
    except Exception as e:
        print(f"❌ Model Training Failed: {str(e)}")
        return False
    
    # 3. Test Model Inference
    print("\n3. Testing Model Inference...")
    try:
        from ai_strategy.model_inference import ModelInference
        model_path = "models/test_model.joblib"
        trainer.save_model(model_path)
        
        inference = ModelInference(model_path)
        prediction = inference.predict(sample_data.iloc[-1].to_dict())
        print("✅ Model Inference: Working")
        print(f"Sample Prediction: {prediction}")
        
    except Exception as e:
        print(f"❌ Model Inference Failed: {str(e)}")
        return False
    
    print("\n✅ All systems operational!")
    return True

if __name__ == "__main__":
    test_system() 