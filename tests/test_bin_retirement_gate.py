"""
=============================================================================
File:     tests/test_bin_retirement_gate.py
Suite:    Phase 3.5 — Clinical Workflow: Bin Retirement Gate
Coverage: §2.2 Active egg gate, race condition double-check.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

def test_bin_with_active_eggs_not_retirable():
    """
    Verify that bins containing active eggs do not appear in the retirement target list.
    """
    mock_sb = MagicMock()
    bin_m = MagicMock()
    egg_m = MagicMock()
    
    def get_table(name):
        if name == "bin": return bin_m
        if name == "egg": return egg_m
        return MagicMock()

    bin_m.select.return_value.eq.return_value.execute.return_value.data = [{"bin_id": "ACTIVE-BIN"}]
    
    res = MagicMock()
    res.count = 5
    # The chain in Dashboard.py: table("egg").select("egg_id", count="exact").eq("bin_id", ...).eq("status", "Active").execute().count
    egg_m.select.return_value.eq.return_value.eq.return_value.execute.return_value = res

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=get_table):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_name = "Admin"
        at.run(timeout=15)

        retire_sel = next((s for s in at.selectbox if "Select Bin" in (s.label or "")), None)
        assert retire_sel is None, "Bin with 5 active eggs appeared in retirement list!"

def test_retire_bin_double_check_blocks_race_condition():
    """
    Verify that if eggs are added to a bin after the page loads, the 'REMOVE' 
    action is blocked by the clinical double-check gate.
    """
    mock_sb = MagicMock()
    bin_m = MagicMock()
    egg_m = MagicMock()
    
    def get_table(name):
        if name == "bin": return bin_m
        if name == "egg": return egg_m
        return MagicMock()

    bin_m.select.return_value.eq.return_value.execute.return_value.data = [{"bin_id": "RETIRE-ME"}]
    
    res0 = MagicMock(); res0.count = 0
    res1 = MagicMock(); res1.count = 1
    # Match EXACT chain length
    egg_m.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [res0, res1]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=get_table):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_name = "Admin"
        at.run(timeout=15)

        retire_sel = next((s for s in at.selectbox if "Select Bin" in (s.label or "")), None)
        assert retire_sel is not None, f"Retirement selectbox not found. Selectboxes: {[s.label for s in at.selectbox]}"
        
        toggle = next((t for t in at.toggle if "empty" in (t.label or "")), None)
        assert toggle is not None
        toggle.set_value(True).run(timeout=15)
        
        remove_btn = next((b for b in at.button if b.label == "REMOVE"), None)
        assert remove_btn is not None
        remove_btn.click().run(timeout=15)
        
        assert any("no longer empty" in err.value for err in at.error), "Race condition gate failed."
        assert not bin_m.update.called, "Bin was updated despite being non-empty!"
