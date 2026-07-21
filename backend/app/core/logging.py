"""Application logging configuration."""

import logging
from logging.config import dictConfig


def configure_logging(log_level: str) -> None:
    """Configure structured, process-wide logging once during application startup."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"handlers": ["console"], "level": log_level.upper()},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for a backend module."""
    return logging.getLogger(name)
