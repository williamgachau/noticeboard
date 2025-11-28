"""
Logging Configuration for SITDS Notice Board
=========================================

This module configures structured logging for the notice board system,
enabling comprehensive monitoring and debugging capabilities.
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger('sitds_noticeboard')
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# File handler for all logs
file_handler = logging.handlers.RotatingFileHandler(
    f'logs/noticeboard.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

# File handler for errors only
error_handler = logging.handlers.RotatingFileHandler(
    f'logs/noticeboard_errors.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Formatters
verbose_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
)
simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

# Apply formatters
file_handler.setFormatter(verbose_formatter)
error_handler.setFormatter(verbose_formatter)
console_handler.setFormatter(simple_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

def log_action(user, action, status, details=None):
    """
    Log user actions in the system.
    
    Args:
        user: The user performing the action
        action: Description of the action
        status: Success or failure status
        details: Additional context (optional)
    """
    message = f"User: {user.username} | Action: {action} | Status: {status}"
    if details:
        message += f" | Details: {details}"
    
    if status == 'SUCCESS':
        logger.info(message)
    elif status == 'FAILURE':
        logger.error(message)
    else:
        logger.warning(message)