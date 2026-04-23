---
component: vault_views/1_Dashboard.py,vault_views/5_Settings.py,tests/test_settings_and_help.py
issue_type: vocabulary_violation,test_fixture_error,api_mismatch
resolved: true
---
# Bug-P3-002 through P3-005: Phase 3 Remediation Bundle

## BUG-P3-002: Dashboard Test Mock — bin_id KeyError
- **File:** `tests/test_settings_and_help.py`
- **Fix:** Rebuilt `test_dashboard_view_renders_metrics` with table-aware `side_effect` returning bin-shaped data `{"bin_id": ...}` for bin table queries
- **Test:** `test_dashboard_view_renders_metrics` ✅

## BUG-P3-003: AppTest v1 session_state.get() AttributeError
- **File:** `tests/test_settings_and_help.py:65`
- **Fix:** `at.session_state.get()` → `getattr(at.session_state, key, default)`
- **Test:** `test_settings_view_renders_and_saves_font_size` ✅

## BUG-P3-004: 5_Settings.py Resurrection Vault Vocabulary Violation
- **File:** `vault_views/5_Settings.py:278, :311`
- **Fix:** `"✨ Restore"` → `"ADD"` (restore = additive op per §1.4)
- **Test:** `test_unified_vocab_settings_view` ✅

## BUG-P3-005: 1_Dashboard.py Bin Retirement Vocabulary Violation
- **File:** `vault_views/1_Dashboard.py:138`
- **Fix:** `"DELETE"` → `"REMOVE"` (destructive op per §1.4)
- **Test:** `test_dashboard_view_renders_metrics` ✅
