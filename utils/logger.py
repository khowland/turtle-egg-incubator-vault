"""
=============================================================================
Module:        utils/logger.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      utils/audit.py, utils/db.py, utils/session.py, vault_views/2_New_Intake.py
Downstream:    logging
Use Cases:     [Pending - Describe practical usage here]
Inputs:        None
Outputs:       logging.Logger
Description:   Standardized Python logging configuration for terminal/cloud logs.
=============================================================================
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("WINC-Vault")
