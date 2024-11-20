import logging
from config import LOG_FORMAT, LOG_LEVEL

def setup_logging():
    """Configure logging with console handler for GitHub Actions."""
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Create formatter and console handler
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler for GitHub Actions logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handler to the logger
    logger.addHandler(console_handler)
    
    return logger
