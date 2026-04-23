# 🎯 Implied System Objective: Turtle-DB (WINC)

## ⚖️ Final Agreed Objective
To provide a **forensic-grade biological ledger and analytical engine** where data integrity (S0-S6 lifecycle) and clinical transparency are paramount. The system must facilitate **seamless, high-frequency observation recording** to empower academic analysis of how environmental factors (mass, temperature, substrate) directly correlate to hatching success. It must maintain a **'5th-Grader Standard' UI** while enforcing **'Doctoral-Level' data constraints** via Atomic RPC transactions, ensuring no turtle egg is lost to a session crash or unauthorized modification.

---

## 🚩 Master Discrepancy & Root Cause Analysis

### 1. Clinical Intake Mass Bypass (Req §2)
- **Discrepancy:** Requirements mandate weight checks. The UI allows a value of `0.0` to pass initial setup.
- **Root Cause:** **UI/Logic Mismatch**. The `2_New_Intake.py` backend state expects a `mass` field, but the physical frontend loop lacks an `st.number_input` to collect it. Validation exists on the button but has no data to validate.
- **Resolution:** Add mandatory `st.number_input("Mass (g)")` to the bin setup loop in `2_New_Intake.py`.

### 2. Forensic Audit & RBAC Neutralization (Req §36)
- **Discrepancy:** Forensic tracking of 'Elevated' operations is hardcoded to `True`.
- **Root Cause:** **Decommissioned Security Layer**. The `role` column removal in v8.1.5 was not followed by a new identity-based authorization strategy, leaving `utils/rbac.py` as a dummy module.
- **Resolution:** Implement identity verification against the `observer` registry for critical writes.

### 3. Biological Lifecycle Gaps (S0-S1 Transition)
- **Discrepancy:** System allows non-sequential stage jumps (e.g., S0 to S5).
- **Root Cause:** **Missing State Machine Validator**. The application relies on user selection without backend enforcement of the biological progression sequence implied in `Requirements.md`.
- **Resolution:** Implement a transition validator in `3_Observations.py` ensuring eggs pass through S1 (Chalked) before advancing.

### 4. Workflow Handoff Failure (ID Desync)
- **Discrepancy:** Navigation from Intake to Observations often crashes or shows empty grids.
- **Root Cause:** **String Format Inconsistency**. Intake sets `active_bin_id` as a raw string (`SN-1-F-1`), but Observations expects a space-delimited display name (`Bin SN-1-F-1`) and attempts to `.split(" ")[1]`, causing index errors or data misses.
- **Resolution:** Standardize on raw IDs for session state; use helper functions for display formatting only.

### 5. Deterministic Testing Fragility
- **Discrepancy:** 74 tests exist, but 8 critical failures were detected only after manual audit.
- **Root Cause:** **Excessive Mocking**. 60%+ of assertions use static mocks. These verify that *Python calls a function*, but fail to verify that *Postgres accepts the payload*. This hid the `B-004` NameError and schema mismatches.
- **Resolution:** Transition to **Integration Testing** using a local Supabase container to verify actual DB constraints and RPC success.

---

## 📋 Academic Analysis Requirements
For WINC to identify factors affecting hatching success, the following data points must be hardened:
1. **Initial Mass Consistency**: Must be recorded at Intake to provide a true baseline.
2. **Observation Frequency**: The UI must be optimized for fast, repetitive checking to encourage detailed longitudinal data.
3. **Condition Correlations**: `bin_observation` and `egg_observation` must be explicitly linked in the schema to allow multi-variate analysis of incubator temperature vs. individual shell health.
