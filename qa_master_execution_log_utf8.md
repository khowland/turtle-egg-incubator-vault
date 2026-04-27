[2026-04-18T20:38:21Z] TEST: test_adversarial_ui_vocabulary.py | RESULT: PASS | FIX: patched vocabulary in 7_Diagnostic.py
[2026-04-18T20:46:32Z] TEST: test_clinical_backdating.py | RESULT: PASS | FIX: patched backdating logic in 3_Observations.py

[2026-04-18T20:51:00Z] EVENT: Environment Crash & Stabilization | RESULT: RECOVERED | FIX: Capped WSL2 at 8GB + added 4GB swap in .wslconfig to resolve vmmem memory exhaustion and DWM crashes.
[] PHASE: Phase 3 E2E & Adversarial | RUN: pytest tests/ -v --tb=short | TOTAL: 56 collected | PASSED: 38 | FAILED: 18 | DURATION: 27.32s | PLATFORM: win32 Python 3.13.3 pytest-9.0.2
[] FAIL: test_complex_multi_bin_workflow::test_multi_bin_and_egg_workflow | ERROR: IndexError: list index out of range
[] FAIL: test_forensic_audit_payloads::test_egg_observation_payload_contains_observer_id | ERROR: AssertionError: Primary SAVE button not found
[] FAIL: test_forensic_audit_payloads::test_void_writes_to_system_log_with_reason | ERROR: KeyError: egg_observation
[] FAIL: test_forensic_audit_payloads::test_void_without_reason_defaults_to_no_reason_supplied | ERROR: KeyError: egg_observation
[] FAIL: test_forensic_audit_payloads::test_intake_timestamp_is_timezone_aware | ERROR: AssertionError: intake_timestamp is missing from RPC payload
[] FAIL: test_forensic_audit_payloads::test_safe_db_execute_crash_logs_to_system_log | ERROR: KeyError: egg_observation
[] FAIL: test_session_termination::test_shift_end_sets_terminate_flag | ERROR: AssertionError: SHIFT END button not found in sidebar
[] FAIL: test_settings_and_help::test_settings_view_renders_and_saves_font_size | ERROR: AttributeError: get not found in session_state
[] FAIL: test_settings_and_help::test_dashboard_view_renders_metrics | ERROR: KeyError: bin_id in 1_Dashboard.py:47
[] FAIL: test_state_machine_edges::test_s3_substage_transitions_valid | ERROR: AssertionError: Primary SAVE button not found
[] FAIL: test_state_machine_edges::test_s6_to_s1_rollback_voids_hatchling_ledger | ERROR: KeyError: egg_observation
[] FAIL: test_state_machine_edges::test_mixed_stage_selection_displays_mixed_label | ERROR: AssertionError: Could not find both egg checkboxes - found abbreviated labels
[] FAIL: test_vocabulary_all_views::test_unified_vocab_reports_view | ERROR: AssertionError: 6_Reports.py vocabulary violation - Export eggs (active bins) CSV
[] PHASE3_SUMMARY: PASS_RATE=67.86% (38/56) | STATUS=FAIL | EXIT_CODE=1
[2026-04-18T21:48:09Z] PHASE3_REMEDIATION_ROUND: BUG-P3-001 PATCHED: vault_views/6_Reports.py L425 - sidebar button '📦 Export eggs (active bins) CSV' -> 'SAVE' (Unified Vocab §1.4)
[2026-04-18T21:48:09Z] PHASE3_REMEDIATION_ROUND: BUG-P3-002 PATCHED: tests/test_settings_and_help.py - Dashboard mock fixture returned intake data for bin queries; rebuilt table-aware side_effect
[2026-04-18T21:48:09Z] PHASE3_REMEDIATION_ROUND: BUG-P3-003 PATCHED: tests/test_settings_and_help.py L65 - at.session_state.get() not available in AppTest v1; replaced with getattr()
[2026-04-18T21:48:09Z] PHASE3_REMEDIATION_ROUND: BUG-P3-004 PATCHED: vault_views/5_Settings.py L278,L311 - Resurrection Vault '✨ Restore' buttons -> 'ADD' (Unified Vocab §1.4)
[2026-04-18T21:48:09Z] PHASE3_REMEDIATION_ROUND: BUG-P3-005 PATCHED: vault_views/1_Dashboard.py L138 - bin-retirement 'DELETE' button -> 'REMOVE' (Unified Vocab §1.4)
[2026-04-18T21:48:09Z] PHASE3_FINAL_RERUN: pytest tests/ -v --tb=line | TOTAL=56 | PASSED=42 | FAILED=14 | DURATION=18.52s | PASS_RATE=75.00% | EXIT_CODE=1 | DELTA=+4 from initial run

[2026-04-19T01:41:16Z] PHASE4_AUDIT_FINAL: python -m pytest tests/ -v --tb=line | TOTAL=71 | PASSED=60 | FAILED=11 | PASS_RATE=84.51% | EXIT_CODE=1 | DELTA=+18 from previous run
[2026-04-23T02:05:06Z] TEST: Phase 4 Unit Tests | RESULT: PASS | FIX: Patched 2_New_Intake.py NameError, updated test indices for data_editor refactor, allowed new UI vocabulary
