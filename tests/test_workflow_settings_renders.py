"""
=============================================================================
Layer 2: Happy-Path Workflow — Settings Renders
Verifies the Settings page loads without crash and that Ac-3 (hide audit
columns) is enforced — created_at/modified_at must not appear in the UI.
=============================================================================
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def _make_settings_mock():
    mock_sb = MagicMock()

    def get_table(name):
        m = MagicMock()
        if name == "observer":
            m.select.return_value.execute.return_value.data = [
                {"observer_id": "uuid-1", "display_name": "Kevin Howland", "is_active": True}
            ]
        elif name == "species":
            m.select.return_value.execute.return_value.data = [
                {
                    "species_id": "SN", "species_code": "SN",
                    "common_name": "Snapping Turtle",
                    "scientific_name": "Chelydra serpentina",
                    "vulnerability_status": "LC",
                    "intake_count": 1,
                }
            ]
        elif name == "intake":
            m.select.return_value.limit.return_value.execute.return_value.data = []
        elif name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        elif name == "egg":
            m.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        elif name == "system_log":
            m.select.return_value.order.return_value.execute.return_value.data = []
            m.insert.return_value.execute.return_value.data = []
        return m

    mock_sb.table.side_effect = get_table
    mock_sb.rpc.return_value.execute.return_value.data = {}
    return mock_sb


def test_settings_renders_without_exception():
    """
    The Settings page must load without raising any exception.
    A crashing Settings page locks out user management and backup operations.
    """
    mock_sb = _make_settings_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/5_Settings.py")
        at.session_state.observer_id = "settings-observer"
        at.session_state.session_id = "settings-session"
        at.session_state.observer_name = "Settings Tester"
        at.run(timeout=15)

        assert not at.exception, (
            f"Settings page raised an unhandled exception: {at.exception}. "
            "Clinical team cannot access user management or backup."
        )


def test_settings_audit_columns_hidden():
    """
    CR-20260426 Ac-3: created_at and modified_at must NOT appear as column
    headers in the Settings user/species data tables.
    These are internal audit columns, not clinical data.
    """
    import pathlib
    settings_src = pathlib.Path("vault_views/5_Settings.py").read_text(encoding="utf-8")

    # Verify the column_config hides these columns (None assignment)
    assert '"created_at": None' in settings_src or "'created_at': None" in settings_src, (
        "created_at is not hidden (None) in Settings column_config. "
        "CR-20260426 Ac-3 regression — audit column visible to clinical users."
    )
    assert '"modified_at": None' in settings_src or "'modified_at': None" in settings_src, (
        "modified_at is not hidden (None) in Settings column_config. "
        "CR-20260426 Ac-3 regression — audit column visible to clinical users."
    )


def test_settings_backup_gate_locks_without_backup():
    """
    §8.2.1: Destructive restore buttons must be locked until backup is downloaded.
    Verifies the backup gate logic is present in Settings source.
    """
    import pathlib
    settings_src = pathlib.Path("vault_views/5_Settings.py").read_text(encoding="utf-8")
    assert "backup_verified" in settings_src, (
        "backup_verified gate logic missing from 5_Settings.py. "
        "Destructive operations may be unlocked without a backup."
    )
    assert "OBLITERATE CURRENT DATA" in settings_src, (
        "Typed confirmation 'OBLITERATE CURRENT DATA' missing from Settings. "
        "§8.2.2 destructive confirmation requirement violated."
    )
