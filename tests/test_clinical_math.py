import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import datetime

def test_incubation_duration_math():
    """
    ADV-12: Validate that incubation_duration_days is accurate.
    """
    mock_supabase = MagicMock()
    table_mocks = {}
    
    intake_date = datetime.date.today() - datetime.timedelta(days=10)

    def mock_table(table_name):
        if table_name in table_mocks: return table_mocks[table_name]
        m = MagicMock()
        if table_name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [{"bin_id": "B1", "intake_id": "M1"}]
        elif table_name == "egg":
            # Grid select
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                {"egg_id": "CALC-1", "bin_id": "B1", "current_stage": "S5", "status": "Active", "intake_timestamp": intake_date.isoformat()}
            ]
            # Sidebar detail select
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"egg_id": "CALC-1", "bin_id": "B1", "intake_timestamp": intake_date.isoformat()}
            ]
        elif table_name == "species":
            m.select.return_value.execute.return_value.data = [{"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}]
        elif table_name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [{"intake_id": "M1", "intake_name": "MOTHER-1"}]
        elif table_name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [{"session_id": "math-session"}]
        
        table_mocks[table_name] = m
        return m

    mock_supabase.table.side_effect = mock_table

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "math-user"
        at.session_state.session_id = "math-session"
        at.session_state.observer_name = "Math Analyst"
        at.session_state.workbench_bins = {"B1"}
        at.session_state.env_gate_synced = {"B1": True}
        at.run(timeout=15)
        
        # Select the egg in checkbox
        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        assert egg_cb is not None, "Could not find egg checkbox"
        egg_cb.check().run(timeout=15)
        
        # Transition to S6 (Hatched)
        stage_sel = next(s for s in at.selectbox if "Stage" in s.label)
        stage_sel.set_value("S6").run(timeout=15)
        
        # Click SAVE
        save_btn = next(b for b in at.button if b.label == "SAVE")
        save_btn.click().run(timeout=15)
        
        # Check hatchling_ledger upsert payload
        upsert_calls = table_mocks["hatchling_ledger"].upsert.mock_calls
        assert len(upsert_calls) > 0, "Hatchling ledger upsert not called"
        
        payload = upsert_calls[0][1][0]
        # Expect 10 days duration
        assert payload[0]["incubation_duration_days"] == 10, f"Expected 10 days, got {payload[0]['incubation_duration_days']}"
