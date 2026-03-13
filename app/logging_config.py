import logging
import sys

# Create a logger for the PDFToru app
logger = logging.getLogger("pdftoru")
logger.setLevel(logging.INFO)

# StreamHandler to stdout (Docker-friendly)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Log format: timestamp | level | message
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)