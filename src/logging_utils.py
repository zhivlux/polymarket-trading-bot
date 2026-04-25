# src/logging_utils.py
import logging
import logging.handlers
import os
from config import Config

def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(Config.LOG_LEVEL)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    log_file = os.path.join(Config.LOGS_DIR, f"{name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(Config.LOG_LEVEL)
    file_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Global logger
logger = setup_logger("PolyMarketBot")
