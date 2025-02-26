import os

class Settings:
    API_PORT = 8000
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN="7836552815:AAHuWTVdtz_vYInRH_f9SDLJBc8MkHoog0o"
    TELEGRAM_CHAT_ID="7836552815"

    
    # Email Settings
    SMTP_SERVER = None
    SMTP_PORT = 587
    SENDER_EMAIL = None
    EMAIL_PASSWORD = None
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://quantalgo:quantum123@localhost/trading_bot_db")
    
    # Angel One API Settings
    ANGEL_ONE_API_KEY = "lB9qx6Rm"
    ANGEL_ONE_CLIENT_ID = "R182159"
    ANGEL_ONE_PASSWORD = "1010"
    ANGEL_ONE_TOKEN = "NRXMU4SVMHCEW3H2KQ65IZKDGI"
    ANGEL_TOTP_KEY = "NRXMU4SVMHCEW3H2KQ65IZKDGI"
    
    # For backward compatibility
    ANGEL_API_KEY = "lB9qx6Rm"
    ANGEL_CLIENT_ID = "R182159"
    ANGEL_PASSWORD = "1010"
    ANGEL_TOKEN ="NRXMU4SVMHCEW3H2KQ65IZKDGI"

    
    # Paths and Directories
    LOG_DIR = "logs"
    MODEL_PATH = "ai_strategy/models"
    DATA_PATH = "ai_strategy/data"
    
    # Logging Settings
    LOG_LEVEL = "INFO"
    
    # WebSocket Settings
    WS_RECONNECT_ATTEMPTS = 3
    WS_RECONNECT_DELAY = 5
    WS_HEARTBEAT_INTERVAL = 30
    
    # Market Data Settings
    ALPHA_VANTAGE_API_KEY = None  # Set in .env
    
    # System Settings
    MAX_WORKERS = 4
    DEBUG = True

settings = Settings()