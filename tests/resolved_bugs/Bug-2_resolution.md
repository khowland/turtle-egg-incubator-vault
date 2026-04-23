---
component: "3_Observations.py"
issue_type: "Clinical Logic / Audit Failure"
resolved: true
---
# Bug-2: Clinical Backdating Ignored
**Issue**: In `3_Observations.py`, the user could select an "Observation Date (Backdating)", but this value was ignored during the `commit_batch` operation. All clinical observations were recording the system execution time, violating §4 requirements for forensic audit accuracy when entering historical field data.
**Resolution**: Patched `3_Observations.py` to check for `st.session_state.backdate_obs`. If present, its isoformat string is passed as the `timestamp` column in the `egg_observation` insert payload.
**Verification**: `test_clinical_backdating.py` successfully validates that the historical date is correctly passed to the database mock. `test_report_forensics.py` verifies that reporting bundles include necessary observer and session metadata.
