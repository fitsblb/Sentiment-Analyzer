"""
Logging configuration for the Sentiment Analyzer application.
Provides structured logging with different handlers and formatters.
"""
import logging
import logging.handlers
import os
import sys
from typing import Optional

from .config import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels for better readability in development."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'  # Reset color
    
    def format(self, record):
        """Format log record with colors if running in development."""
        if config.DEBUG and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            log_color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> logging.Logger:
    """
    Set up application logging with appropriate handlers and formatters.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('sentiment_analyzer')
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if config.DEBUG:
        formatter = ColoredFormatter(config.LOG_FORMAT)
    else:
        formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Console handler for all environments
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if LOG_FILE is specified
    if config.LOG_FILE:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(config.LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                config.LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
            logger.addHandler(file_handler)
            
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not create file handler for {config.LOG_FILE}: {e}")
    
    # Don't propagate to root logger to avoid duplicate messages
    logger.propagate = False
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module or component.
    
    Args:
        name: Optional name for the logger. If None, returns the main app logger.
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f'sentiment_analyzer.{name}')
    return logging.getLogger('sentiment_analyzer')


# Initialize the main logger
main_logger = setup_logging()
