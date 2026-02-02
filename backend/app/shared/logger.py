"""Logging configuration for the document generation application"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Setup a logger with console and optional file handlers

    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            # If we can't write to the log file, just use console logging
            print(f"Warning: Could not create log file {log_file}: {e}. Using console logging only.")

    return logger


# Create default logger (file logging is optional, will fall back to console)
default_logger = setup_logger(
    'docgen',
    log_file='logs/docgen.log'
)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (if None, returns default logger)

    Returns:
        Logger instance
    """
    if name:
        # Try to create file logger, will fall back to console if permission denied
        return setup_logger(name, log_file=f'logs/{name}.log')
    return default_logger
