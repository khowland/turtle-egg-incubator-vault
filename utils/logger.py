"""
=============================================================================
Module:     utils/logger.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Standardized Python logging configuration per Requirements §6.5.
            Outputs structured log lines to stdout for terminal and Docker
            log visibility. All modules import `logger` from this file.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Code Review: Completed enterprise header)
=============================================================================
"""

import logging
import sys

# =============================================================================
# SECTION: Logger Configuration
# Description: Single shared logger instance for the entire application.
#              Format: timestamp | LEVEL | module | message
#              Levels per §6.5:
#                INFO    → Startup, connections, session transitions
#                WARNING → Cache clears, missing optional data, retries
#                ERROR   → DB crashes, unhandled exceptions, schema issues
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Named logger — all modules use: from utils.logger import logger
logger = logging.getLogger("VaultElite")
