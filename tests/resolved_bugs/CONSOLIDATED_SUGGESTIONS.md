---
title: Consolidated Audit Suggestions
tags:
  - suggestions
  - audit
---
# 📋 Consolidated System Suggestions: Turtle-DB

This report tracks all audit findings, potential bugs, and enterprise-grade enhancements for the WINC Incubator System. Findings are strictly appended to maintain historical context.

---

## 🐛 Potential Bugs & Logic Flaws

### [B-001] Missing Intake Weight Validation (Clinical Gap)
- **Component:** vault_views/2_New_Intake.py
- **Impact:** Requirement §2 mandates weight checks. Currently, bins can be created in Intake without any initial mass recording. This allows "weightless" bins to exist until the first observation.
- **Senior Recommendation:** Add a mandatory bin_mass_g field to the Intake form. Block the SAVE button if weight is 0 or null.

### [B-002] Silent Session Persistence Failures
- **Component:** utils/session.py
- **Impact:** Multiple pass statements in database interaction logic (show_splash_screen). If the Supabase session cannot be logged, the user is not notified, leading to fragmented audit trails.
- **Senior Recommendation:** Replace pass with st.toast or st.warning notifications for the biologist to signal degraded system state.

### [B-003] Weak Identity Validation
- **Component:** vault_views/2_New_Intake.py
- **Impact:** The finder name warning doesn't stop the submission. If special characters are used, it could break downstream analytics or label printing.
- **Senior Recommendation:** Ensure is_valid_finder boolean acts as a hard guard for the SAVE button's disabled state.

---

## 🚀 Enhancements & Mobile Optimizations

### [E-001] Mobile Form Layout (Kiosk/Cell Phone)
- **Context:** Streamlit on mobile tends to stack columns vertically. 
- **Suggestion:** Use st.container(border=True) sparingly for key groups and ensure labels are concise. Use use_container_width=True on all buttons (already partially implemented).

### [E-002] Use Case Documentation (Standard §35)
- **Context:** Many modules have [Pending] Use Case headers.
- **Suggestion:** Populate these headers to ensure the "5th-Grader Standard" for maintainability is met for future volunteer developers.


## 🐛 Potential Bugs & Logic Flaws (Phase 2 Append)

### [B-004] Undefined Variable supabase_client in utils/session.py
- **Component:** utils/session.py (Lines 163, 174)
- **Impact:** CRITICAL. During session recovery, the script attempts to use supabase_client before it is defined in the local scope. This causes the entire session logging and recovery logic to crash with a NameError, as verified by test_session_resilience.py.
- **Senior Recommendation:** Initialize supabase_client = get_supabase() at the start of the show_splash_screen submission logic block.

### [B-005] Missing "SHIFT END" Termination Button
- **Component:** app.py or Sidebar Utility
- **Impact:** Requirement §36/§4. The system needs a way to explicitly terminate a session to prevent accidental resumption beyond the 4-hour window. test_shift_end_sets_terminate_flag failed because the button is missing from the UI.
- **Senior Recommendation:** Add a "SHIFT END" button to the sidebar that inserts a 'TERMINATE' event into the system_log.

### [B-006] Multiselect State Mismatch (Streamlit Out-of-Sync)
- **Component:** vault_views/3_Observations.py
- **Impact:** test_complex_multi_bin_workflow failed with StreamlitAPIException. Default values for the workbench bins are not consistently present in the dynamically fetched options list.
- **Senior Recommendation:** Ensure the default list in st.multiselect is always a subset of the currently fetched bin_options to avoid internal Streamlit crashes.

---

## 🚀 Enhancements & Mobile Optimizations (Phase 2 Append)

### [E-003] Adaptive Column Layout for Mobile
- **Context:** Mobile users on cell phones experience cramped layouts in 3-column structures (2_New_Intake.py).
- **Suggestion:** Use a helper function to detect screen width (if possible via custom components) or default to 1-2 columns for critical data entry on mobile. Streamlit's native column stacking is a fallback, but explicit layouts for small screens are better.

### [E-004] Standardized Testing Harness
- **Context:** Several tests failed due to mocking inconsistencies (get_table vs get_resilient_table).
- **Suggestion:** Refactor the test utility mocks to ensure a consistent interface across all unit tests to avoid "false negative" failures.


## 📋 Phase 2 Test Suite Failures (Verified)

### [B-007] UI Branding Violation: SAVE Button Type
- **Test:** test_button_label_and_type_compliance
- **Impact:** Requirement §1. The SAVE button in some views is using default 'button' type instead of 'primary'. This violates the Green branding requirement for primary actions.
- **Senior Recommendation:** Change all primary SAVE buttons to type="primary".

### [B-008] Intake Handoff Failure
- **Test:** test_workflow_intake_to_observation_handoff
- **Impact:** CRITICAL. The active_bin_id is missing from session state after a successful save in Intake. This breaks the automated transition to the Observations workbench.
- **Senior Recommendation:** Verify state persistence in the _intake_success_ui helper function.

### [B-009] Streamlit Multiselect Desync
- **Test:** test_complex_multi_bin_workflow
- **Impact:** StreamlitAPIException. The system attempts to set a default value in the bin multiselect that is not yet in the options list. This happens during rapid navigation or auto-transitions.
- **Senior Recommendation:** Wrap multiselect defaults in a filter that ensures they exist in the current options list.

### [B-010] Mocking Interface Mismatch (Test Debt)
- **Test:** test_retire_bin_double_check_blocks_race_condition
- **Impact:** The test harness expects get_table() with 2 arguments, but the current mock only supports 1. This prevents race condition verification.
- **Senior Recommendation:** Refactor tests/mock_utils.py to match the current get_resilient_table signature.

