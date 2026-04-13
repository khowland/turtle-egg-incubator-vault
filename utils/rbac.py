"""
=============================================================================
Module:        utils/rbac.py
Description:   Role-based access removed for single-kiosk mode.
=============================================================================
"""


def can_elevated_clinical_operations() -> bool:
    return True


def require_elevated_clinical(message=None) -> bool:
    return True
