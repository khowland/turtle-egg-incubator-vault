"""
=============================================================================
File:     tests/test_vocabulary_all_views.py
Suite:    Phase 3 — P3-VOC-1, P3-VOC-2, P3-VOC-3, P3-VOC-4
Coverage: §1.4 Unified Vocabulary across ALL interactive vault_views
          Extends ADV-4 (7_Diagnostic only) to full sweep.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

ALLOWED_LABELS = {"SAVE", "CANCEL", "ADD", "REMOVE", "START", "SHIFT END"}
# Note: "SHIFT END" is the logout control defined in session.render_custom_sidebar()
# and is a purposeful extension of the Unified Vocabulary for shift management.


@pytest.fixture
def mock_client():
    m = MagicMock()
    m.table.return_value.select.return_value.execute.return_value.data = []
    m.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    m.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    return m


# ---------------------------------------------------------------------------
# P3-VOC-1: 2_New_Intake.py button vocab compliance
# ---------------------------------------------------------------------------
def test_unified_vocab_intake_view(mock_client):
    """
    P3-VOC-1: All buttons in 2_New_Intake.py must use the Unified Vocabulary.
    §1.4: SAVE, CANCEL, ADD, REMOVE, START.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_client):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "vocab-observer"
        at.session_state.session_id = "vocab-session"
        at.run(timeout=10)

        violations = [
            b.label for b in at.button if b.label not in ALLOWED_LABELS
        ]
        assert not violations, (
            f"[2_New_Intake.py] Unified Vocabulary violations found: {violations}"
        )


# ---------------------------------------------------------------------------
# P3-VOC-2: 6_Reports.py button vocab compliance
# ---------------------------------------------------------------------------
def test_unified_vocab_reports_view(mock_client):
    """
    P3-VOC-2: All buttons in 6_Reports.py must use the Unified Vocabulary.
    Expects 'START' to trigger report preview.
    """
    # Mock species for the filter multiselect
    mock_client.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}
    ]
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_client), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True):
        at = AppTest.from_file("vault_views/6_Reports.py")
        at.session_state.observer_id = "vocab-observer"
        at.session_state.session_id = "vocab-session"
        at.session_state.observer_name = "Vocab Tester"
        at.run(timeout=10)

        violations = [
            b.label for b in at.button if b.label not in ALLOWED_LABELS
        ]
        assert not violations, (
            f"[6_Reports.py] Unified Vocabulary violations found: {violations}"
        )


# ---------------------------------------------------------------------------
# P3-VOC-3: 5_Settings.py button vocab compliance
# ---------------------------------------------------------------------------
def test_unified_vocab_settings_view(mock_client):
    """
    P3-VOC-3: All buttons in 5_Settings.py must use the Unified Vocabulary.
    This is the first test ever executed against this view.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_client):
        at = AppTest.from_file("vault_views/5_Settings.py")
        at.session_state.observer_id = "vocab-observer"
        at.session_state.session_id = "vocab-session"
        at.session_state.observer_name = "Vocab Tester"
        at.run(timeout=10)

        if at.exception:
            raise at.exception[0]

        violations = [
            b.label for b in at.button if b.label not in ALLOWED_LABELS
        ]
        assert not violations, (
            f"[5_Settings.py] Unified Vocabulary violations found: {violations}"
        )


# ---------------------------------------------------------------------------
# P3-VOC-4: Static analysis — verify CSS color tokens in source
# (No AppTest; uses grep-style assertions on source code)
# ---------------------------------------------------------------------------
def test_button_color_token_in_source():
    """
    P3-VOC-4: AppTest cannot assert computed CSS. This test validates that
    the WINC design token colors from §1.4 are present somewhere in the
    project source (theme config or CSS injection).
      SAVE  -> Green  #10b981
      CANCEL-> Red    #ef4444
      ADD   -> Blue   #3b82f6
    """
    import os
    import glob

    # Files to search: .streamlit/config.toml + any .py with CSS injection
    search_roots = [
        os.path.join(".", ".streamlit"),
        os.path.join(".", "utils"),
        os.path.join(".", "vault_views"),
    ]
    color_tokens = {
        "SAVE (green)": "#10b981",
        "CANCEL (red)": "#ef4444",
        "ADD (blue)": "#3b82f6",
    }
    found_tokens = set()

    for root in search_roots:
        for filepath in glob.glob(os.path.join(root, "**", "*"), recursive=True):
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read().lower()
                for label, hex_val in color_tokens.items():
                    if hex_val.lower() in content:
                        found_tokens.add(label)
            except Exception:
                continue

    missing = set(color_tokens.keys()) - found_tokens
    assert not missing, (
        f"Design token color(s) from §1.4 not found in any source file: {missing}. "
        "Ensure SAVE=#10b981, CANCEL=#ef4444, ADD=#3b82f6 are present in theme config or CSS injection."
    )
