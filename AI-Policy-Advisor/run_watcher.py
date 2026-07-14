"""
run_watcher.py
==============
Command line runner for the automation watcher.
"""

from automation.watcher import start_watcher_loop
from utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting AI Policy Advisor Automation Watcher...")
    try:
        start_watcher_loop(interval_seconds=10)
    except Exception as e:
        logger.error("Watcher runner caught an exception: %s", e, exc_info=True)
