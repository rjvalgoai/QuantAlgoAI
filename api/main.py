from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from ws import SmartWebSocket, WebSocketManager
from core.logger import logger
# ... rest of imports

# Initialize FastAPI app
app = FastAPI(title="QuantAlgoAI API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Socket.IO setup
sio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create ASGI app
socket_app = socketio.ASGIApp(
    socketio_server=sio_server,
    other_asgi_app=app
)

# Socket.IO event handlers
@sio_server.event
async def connect(sid, environ):
    logger.info(f"[CONNECT] Client connected: {sid}")
    return True

@sio_server.event
async def disconnect(sid):
    logger.info(f"[DISCONNECT] Client disconnected: {sid}")

@sio_server.event
async def subscribe_market_data(sid, data):
    logger.info(f"[MARKET] Client {sid} subscribed to market data: {data}")
    # Add client to symbol-specific rooms
    for symbol in data:
        await sio_server.enter_room(sid, f"market_data_{symbol}")

# API routes
@app.get("/")
async def root():
    return {"message": "QuantAlgoAI API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "websocket": websocket_manager.connected
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize WebSocket connection
        await websocket_manager.connect()
        
        # Subscribe to default symbols
        default_symbols = ["NIFTY", "BANKNIFTY"]
        await websocket_manager.subscribe(default_symbols)
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    if websocket_manager.connected:
        await websocket_manager.stop() 