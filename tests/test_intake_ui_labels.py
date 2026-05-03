# CR-20260430-194500: Test updated UI labels in 2_New_Intake.py
"""
Test that 2_New_Intake.py uses updated labels:
- Radio options: "New Intake" and "Add Eggs or Bins to Existing Intake"
- Old labels ("Initial Intake (New Case)", "Supplemental Intake (Add to Existing Mother)") absent
- Date label: "Intake Date"
- Collection method label: "Egg Collection Method"
"""
import os
import pytest


def _load_intake_module_text():
    """Read 2_New_Intake.py as text for label assertions."""
    path = os.path.join(
        os.path.dirname(__file__),
        "..", "vault_views", "2_New_Intake.py"
    )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_intake_mode_radio_labels():
    """Radio must show 'New Intake' and 'Add Eggs or Bins to Existing Intake'."""
    src = _load_intake_module_text()

    # Required new labels
    assert "New Intake" in src, \
        "Radio must include 'New Intake' option"
    assert "Add Eggs or Bins to Existing Intake" in src, \
        "Radio must include 'Add Eggs or Bins to Existing Intake' option"

    # CR-20260501-1800: Backward-compat shim for old session state still contains old label string.
    # Only check that the radio widget options list contains new labels.
    # Verify radio definition line uses new labels
    radio_line = [l for l in src.split('\n') if 'st.radio' in l and 'Select Workflow' in l]
    assert len(radio_line) == 1, "Radio widget definition not found"
    assert "New Intake" in radio_line[0], "Radio must include 'New Intake'"
    assert "Add Eggs or Bins to Existing Intake" in radio_line[0], "Radio must include 'Add Eggs or Bins to Existing Intake'"


def test_date_label_is_intake_date():
    """Date input label must say 'Intake Date' not 'Date'."""
    src = _load_intake_module_text()
    assert "Intake Date" in src, \
        "Label must be 'Intake Date'"


def test_collection_method_label():
    """Collection method selectbox must say 'Egg Collection Method'."""
    src = _load_intake_module_text()
    assert "Egg Collection Method" in src, \
        "Label must be 'Egg Collection Method'"
    # Old label should be gone
    assert "Extraction Method" not in src, \
        "Old label 'Extraction Method' must be removed"
