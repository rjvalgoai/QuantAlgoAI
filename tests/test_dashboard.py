from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
import random
from datetime import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "QuantAlgoAI Dashboard API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # Simulate real-time data
        data = {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NIFTY",
            "price": random.uniform(19000, 20000),
            "prediction": random.choice(["BUY", "SELL"]),
            "confidence": random.uniform(0.5, 0.9),
            "features": {
                "rsi": random.uniform(30, 70),
                "macd": random.uniform(-10, 10),
                "volume": random.randint(100000, 500000)
            }
        }
        
        await websocket.send_json(data)
        await asyncio.sleep(1)

def run_dashboard():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_dashboard() 