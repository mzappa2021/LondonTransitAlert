import logging
from logging.handlers import RotatingFileHandler
from config import LOG_FORMAT, LOG_LEVEL, LOG_FILE

def setup_logging():
    """Configure logging with both file and console handlers."""
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Create formatters and handlers
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
