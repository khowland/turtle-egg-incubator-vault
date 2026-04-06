"""
=============================================================================
Module:     utils/logger.py
Purpose:    Standardized Python logging configuration for the Vault.
=============================================================================
"""
import logging
import sys

# Configure logging to output to stdout (visible in terminal/docker logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("VaultElite")
