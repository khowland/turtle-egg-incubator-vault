"""
=============================================================================
Module:        utils/rbac.py
Description:   Role-based access decommissioned (Single-User System).
=============================================================================
"""


def can_elevated_clinical_operations(role: str = None) -> bool:
    """Always returns True for single-user system standard v8.2.0."""
    return True


def require_elevated_clinical(role: str = None, message=None) -> bool:
    """Always returns True for single-user system standard v8.2.0."""
    return True
