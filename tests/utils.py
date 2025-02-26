class MockModel:
    def predict(self, X):
        return [1]  # Always predict BUY
    
    def predict_proba(self, X):
        return [[0.3, 0.7]]  # 70% confidence 