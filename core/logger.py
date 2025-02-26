import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from core.config import settings

# Create logs directory if it doesn't exist
log_dir = Path(settings.LOG_DIR)
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Format for our loglines
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    # File Handler
    file_handler = RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Create and export logger
logger = setup_logger()
