"""
=============================================================================
Module:        utils/rbac.py
Description:   Role-based access decommissioned. All observers share clinical privileges.
=============================================================================
"""


def can_elevated_clinical_operations() -> bool:
    return True


def require_elevated_clinical(message=None) -> bool:
    return True
