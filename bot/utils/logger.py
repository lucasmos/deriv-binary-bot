import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(config):
    """Configure application logging"""
    log_dir = config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create main logger
    logger = logging.getLogger()
    logger.setLevel(config.get('LOG_LEVEL', 'INFO'))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger