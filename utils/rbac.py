"""
=============================================================================
Module:        utils/rbac.py
Project:       Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36] — Elevated clinical operations gating
Dependencies:  streamlit
Inputs:        st.session_state.observer_role
Outputs:       Boolean capability checks for UI gates
Description:   Role-based access for surgical void, resurrection, retirement,
               diagnostics navigation, and WormD export (staff-grade actions).
=============================================================================
"""

import streamlit as st

# Roles granted elevated clinical / archival operations (ISS-7).
_TRUSTED_CLINICAL_ROLES = frozenset({"Admin", "Staff", "Biologist"})


def observer_role() -> str:
    """Returns current observer role string; defaults to Guest if unset."""
    return st.session_state.get("observer_role") or "Guest"


def can_elevated_clinical_operations() -> bool:
    """
    Surgical Resurrection (void observations), Resurrection Vault, bin retirement,
    Diagnostics nav, and WormD bundle export require a trusted clinical role.
    """
    return observer_role() in _TRUSTED_CLINICAL_ROLES


def require_elevated_clinical(message: str | None = None) -> bool:
    """
    If the current user lacks elevation, show a warning and return False.
    Callers should st.stop() when False.
    """
    if can_elevated_clinical_operations():
        return True
    st.warning(
        message
        or "This action requires a trusted clinical role (Admin, Staff, or Biologist). "
        "Contact a vault administrator."
    )
    return False
