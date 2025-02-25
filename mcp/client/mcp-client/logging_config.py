import logging
from logging.handlers import RotatingFileHandler
from config import config

def setup_logging():
    """Configure logging with rotation based on configuration"""
    logging.basicConfig(
        level=getattr(logging, config.logging_config['level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                config.logging_config['file'],
                maxBytes=config.logging_config['max_bytes'],
                backupCount=config.logging_config['backup_count']
            )
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)