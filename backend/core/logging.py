"""
logging.py — Structured logging setup for ShelterAI API.
"""

import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("shelter_ai")

logger = setup_logging()
