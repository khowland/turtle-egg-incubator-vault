# 🔬 Phase 4: Persistent Test Failure & RCA Report

This report summarizes the 10 remaining test failures as of April 19, 2026. These failures primarily stem from **Infrastructure Brittle-ness**, **Clinical Requirement Evolution**, and **Vocabulary Hardening**.

## 📊 Summary of Pass Rates
- **Initial (Phase 4 Start)**: 84.51% (60/71)
- **Current Status**: 86.49% (64/74)
- **Target**: 100.00%

## ❌ Remaining Failures & Root Cause Analysis

### 1. Session Resilience & Recovery (RES-1)
- **File**: `tests/test_session_resilience.py::test_session_recovery_boundary_valid`
- **Error**: `AssertionError: Security Error: Failed to re-adopt valid session 'old-active-session'...`
- **RCA**: This is the most persistent infrastructure issue. Despite standardizing on UTC and fixing client scopes in `utils/session.py`, the `AppTest` environment fails to adopt the mocked session ID.
- **Best Guess**: The `st.form_submit_button("START")` logic might be triggering a double-rerun that resets the `generated_uuid` before the recovery logic can finalize the state.
- **Attempted**: Standardized UTC, scope initialization, redundant patching.

### 2. Clinical Evolution (False Positives)
- **File**: `tests/test_audit_phase2_gaps.py::test_gap_intake_weight_bypass`
- **Error**: `AssertionError: Weight input found in Intake! Audit suggests it was missing.`
- **RCA**: This test was designed to **fail** if it found weight inputs (because Phase 2 audit said they were missing). Since we successfully hardened the Intake view with mandatory weight metrics, this test is now a "False Positive" failure—it correctly identifies the new feature but interprets it as a violation of the old "missing" state.
- **Resolution**: This test should be inverted to *require* the weight input.

### 3. Unified Vocabulary Mismatches
- **Files**: `test_bin_retirement_gate.py`, `test_branding_compliance.py`, `test_clinical_durability.py`
- **Error**: `Selectbox not found`, `button type mismatch`.
- **RCA**: During the §1.4 branding hardening, many labels changed (e.g., `DELETE` -> `REMOVE`).
    - The `Retirement` selectbox in `1_Dashboard.py` likely has a new label or emoji.
    - The `Surgery` selectbox in `3_Observations.py` has been refactored into the "Surgical Resurrection" section.
- **Explored**: Updated most labels, but some intermediate containers or button `type` attributes remain inconsistent with the test expected "None" or "primary".

### 4. Encoding & Metadata (Environment)
- **Files**: `test_audit_phase2_gaps.py` (multiple)
- **Error**: `UnicodeDecodeError: 'charmap' codec can't decode byte 0x90...`
- **RCA**: These tests likely attempt to read source code files containing emojis (🐢, 🔬, 🥚) without specifying `encoding='utf-8'` in the Python `open()` call.
- **Resolution**: Update test utility helpers to use UTF-8.

### 5. Atomic Continuity
- **File**: `tests/test_adversarial_persistence.py::test_atomic_transaction_resilience`
- **Error**: `Expected atomic RPC 'vault_finalize_intake' to be utilized`
- **RCA**: The test checks for an RPC call. Since we refactored the UI to call the RPC exactly as required, this might be a mock de-sync where the test is checking the `db.rpc` mock but the app is using a DIFFERENT instance of the Supabase client.

## 📍 Knowledge Base Reference
- **Location**: `tests/resolved_bugs/00_CENTRAL_HUB.md`
- **Detailed RCA**: `tests/resolved_bugs/RCA_Phase4.md`
- **Methodology**: `tests/resolved_bugs/QA_METHODOLOGY.md`

---
*End of Report.*
