"""
Logging Configuration for JARVIS
"""

import logging
import os
from datetime import datetime


def setup_logging():
    """Set up logging configuration for JARVIS"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler for persistent logging
            logging.FileHandler(
                os.path.join(log_dir, 'jarvis.log'),
                encoding='utf-8'
            ),
            # Console handler for immediate feedback
            logging.StreamHandler()
        ]
    )
    
    # Create logger for JARVIS
    logger = logging.getLogger('JARVIS')
    logger.info("Logging system initialized")
    
    return logger


def get_logger(name: str = 'JARVIS'):
    """Get a logger instance"""
    return logging.getLogger(name)


# Initialize logging when module is imported
logger = setup_logging()
