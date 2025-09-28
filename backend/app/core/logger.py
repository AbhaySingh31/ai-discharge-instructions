import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Configure logger
logger = logging.getLogger("ai-discharge")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# File handler (rotating)
if not os.path.exists("logs"):
    os.makedirs("logs")
    
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=1024 * 1024 * 5,  # 5MB
    backupCount=3
)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
