# Red Team Adversarial Audit Report

**Date:** 2026-04-18  
**Scope:** Turtle-DB Vault Views & Core Utilities  
**Auditor:** Red Team (Autonomous Adversarial Mode)

---

## 🚩 Critical Vulnerabilities Identified

### 1. RBAC Decommissioning (Auth Bypass by Design)
- **Component:** `utils/rbac.py`
- **Exposure:** Both `can_elevated_clinical_operations()` and `require_elevated_clinical()` return `True` unconditionally.
- **Risk:** Any authenticated observer can perform destructive or high-sensitivity operations (Bin retirement, Correction Mode, Voiding records). This breaks clinical governance §ISS-7.

### 2. Forensic Logging Gaps (Observer Anonymity)
- **Component:** `utils/bootstrap.py -> safe_db_execute`
- **Exposure:** The `system_log` payload only records `session_id`. It does NOT explicitly capture `observer_id` in the `system_log` record during automated logging.
- **Risk:** Audit trails for automated errors or standard operations cannot be definitively linked to a human observer if a session ID is shared or hijacked.

### 3. Session Adoption Risk (Unauthorized Persistence)
- **Component:** `utils/session.py`
- **Exposure:** Sessions are adopted automatically if < 4 hours old and not explicitly terminated.
- **Risk:** If a user fails to click "SHIFT END", the session remains "live" in the DB. Anyone opening the app on the same device (or potentially spoofing the handshake) adoptees the previous user's session without re-auth.

### 4. Unguarded Bin Retirement (Data Obfuscation)
- **Component:** `vault_views/1_Dashboard.py`
- **Exposure:** The `retire_bin` function updates `is_deleted = True` for a bin without verifying that all associated eggs are either `Hatched` or `Dead`.
- **Risk:** Active eggs can be removed from oversight mid-season, leading to biological loss and audit gaps.

---

## ⚠️ High-Risk Logic Flaws

### 5. Multi-Bin Sequence Injection
- **Component:** `vault_views/2_New_Intake.py`
- **Scenario:** The UI allows adding bins, but does not strictly prevent the creation of bins with duplicate `bin_num` or `bin_id` within the same intake session if the RPC logic allows it.
- **Risk:** Data collisions in the `egg` table if identifiers are not unique.

### 6. "Surgical Resurrection" UI State Leak
- **Component:** `vault_views/3_Observations.py`
- **Scenario:** `st.session_state.surgical_resurrection` is a simple boolean toggle. 
- **Risk:** If the UI crashes or redirects while this is `True`, the next egg selection might inadvertently be in "Correction Mode" without the user intending it, leading to accidental VOIDs.

---

## 🛠️ Recommended Hardening

1. **Re-activate RBAC:** Implement actual role checks in `utils/rbac.py` against the `observer` table's `role` column.
2. **Observer Attribution:** Update `safe_db_execute` to include `observer_id` in all `system_log` entries.
3. **Clinical Guardrails:** Add a server-side or UI-side check to block bin retirement if `active_eggs > 0`.
4. **Forced Termination:** Reduce the session adoption window to 1 hour and enforce a "Stale Session" redirect if `observer_id` is missing but `session_id` exists in the DB.
