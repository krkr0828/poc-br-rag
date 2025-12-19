"""
Logging utility using AWS Lambda Powertools

Provides structured JSON logging for all Lambda functions with CloudWatch compatibility.
"""

import os
import logging
from aws_lambda_powertools import Logger

# Get log level from environment variable, default to INFO
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


def get_logger(name: str) -> Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Logger: Configured AWS Lambda Powertools logger with JSON formatting

    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", extra={"user_id": "123"})
    """
    logger = Logger(
        service=name,
        level=LOG_LEVEL,
        stream=None,  # Use default stdout
        log_uncaught_exceptions=True,
    )

    return logger
