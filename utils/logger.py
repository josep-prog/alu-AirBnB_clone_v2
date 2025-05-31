#!/usr/bin/python3
"""
Logging utility for AirBnB deployment
Handles all logging operations during deployment
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOGGING

def setup_logger():
    """Setup and configure the logger"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOGGING['log_file'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logger
    logger = logging.getLogger('airbnb_deploy')
    logger.setLevel(logging.INFO)

    # Create rotating file handler
    handler = RotatingFileHandler(
        LOGGING['log_file'],
        maxBytes=int(LOGGING['max_size'].replace('M', '000000')),
        backupCount=LOGGING['backup_count']
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

# Create logger instance
logger = setup_logger()

def log_deployment_start(server, version):
    """Log the start of a deployment"""
    logger.info(f"Starting deployment of version {version} to {server}")

def log_deployment_end(server, version, success):
    """Log the end of a deployment"""
    status = "successful" if success else "failed"
    logger.info(f"Deployment of version {version} to {server} {status}")

def log_error(message, error=None):
    """Log an error"""
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)

def log_info(message):
    """Log an info message"""
    logger.info(message)

def log_warning(message):
    """Log a warning message"""
    logger.warning(message) 