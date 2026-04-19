import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json

def test_report_bundle_includes_forensic_metadata():
    """
    ADV-9: Verify that the WormD export bundle includes forensic metadata (§4).
    """
    mock_supabase = MagicMock()
    # Mock data for reports
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}
    ]
    # Mock intake for multi-select
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"intake_id": "test-intake-id", "intake_name": "SN-001", "species_id": 1}
    ]
    # Mock bins and eggs
    mock_supabase.table.return_value.select.return_value.in_.return_value.eq.return_value.execute.return_value.data = []

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        # We need to mock can_elevated_clinical_operations to True
        with patch("utils.rbac.can_elevated_clinical_operations", return_value=True):
            at = AppTest.from_file("vault_views/6_Reports.py")
            at.session_state.observer_id = "forensic-observer"
            at.session_state.session_id = "forensic-session"
            at.session_state.observer_name = "Forensic Analyst"
            at.run(timeout=15)
            
            # Trigger 'START' button to build preview
            start_btn = next(b for b in at.button if b.label == "START")
            start_btn.click().run(timeout=15)
            
            # Check session state for JSON bundle
            # at.session_state is a Proxy, try attribute access
            json_bundle_str = None
            try:
                json_bundle_str = at.session_state._wormd_json
            except AttributeError:
                # Fallback to checking keys
                if "_wormd_json" in at.session_state:
                    json_bundle_str = at.session_state["_wormd_json"]
            
            assert json_bundle_str is not None, f"JSON bundle was not generated. State keys: {list(at.session_state.keys())}"
            
            json_bundle = json.loads(json_bundle_str)
            audit = json_bundle.get("audit_provenance", {})
            
            assert audit.get("exported_by_observer_id") == "forensic-observer"
            assert audit.get("session_id") == "forensic-session"

def test_empty_species_filter_resilience():
    """
    ADV-10: Resilience check - deselecting all species shouldn't crash metrics.
    """
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}
    ]
    # Mock analytical data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/6_Reports.py")
        at.run()
        
        # Deselect all in multiselect (index 0 is filters)
        at.multiselect[0].unselect("Snapping Turtle").run()
        
        # Should not crash and should show "No egg records detected"
        assert any("No egg records detected" in i.value for i in at.info)
