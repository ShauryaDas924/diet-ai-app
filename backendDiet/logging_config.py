# backend/logging_config.py
import logging
import sys


# -----------------------------
# Logging configuration
# -----------------------------

LOG_LEVEL = logging.INFO

logger = logging.getLogger("diet_ai")
logger.setLevel(LOG_LEVEL)

# Prevent duplicate handlers if reloaded
if not logger.handlers:

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Avoid double logging from root logger
    logger.propagate = False
