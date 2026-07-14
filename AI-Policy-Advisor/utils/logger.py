"""
utils/logger.py
================
Centralized logging for the entire project.

WHY THIS FILE EXISTS
---------------------
Without centralized logging, developers scatter `print()` statements
everywhere. Those get left in production code, can't be turned off,
and give no context (which module? which line? what time?).

`get_logger(__name__)` gives every module its own named logger that
writes to both the console (for local dev) and a rotating log file
(for anything you'd need to debug later), using the LOG_LEVEL and
LOG_FILE from config.py.

USAGE (in any other file):
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
    logger.error("Something went wrong: %s", error)
"""

import logging
from logging.handlers import RotatingFileHandler

from config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    Safe to call multiple times for the same name — handlers are only
    attached once, so you won't get duplicate log lines.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (e.g. this module was imported more than once)
        return logger

    logger.setLevel(settings.log_level.upper())

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler — what you see while developing
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler — keeps the last 5 files of 1MB each,
    # so logs don't grow forever and eat disk space
    file_handler = RotatingFileHandler(
        settings.log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
