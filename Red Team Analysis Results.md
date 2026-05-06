## 🔴 Red Team Analysis Results

The red team software engineer completed a comprehensive analysis of the 12-test failure. Key findings:

---

### 1. Root Cause — START Button Not Found

**The Streamlit app was in an error state, not serving the login page.**

When Playwright loaded `http://127.0.0.1:8599`, the app was displaying Streamlit's generic error page (from schema drift cascading errors), not the login page with the START button. The selector `get_by_role("button", name="START", exact=True)` is correct — the button simply wasn't rendered because the app crashed on load.

**Causal chain:**
1. Stale session auto-resumes → encounters missing schema columns
2. `obs_id` / `observer_id` RPC failures → Streamlit error boundary catches exception
3. Generic error page served → no START button → all 12 tests timeout

**Fix:** The `obs_id` column you just added likely resolves the schema drift. Restart the Streamlit process to clear the stale session state.

---

### 2. Conftest.py Column Name Mismatch

**File:** `tests/e2e_playwright/conftest.py`, line 61

```python
# BROKEN — references `.id` but all tables use `*_id`
resp = supabase.table(table).update({"is_deleted": True}).neq('id', 0).execute()
```

Schema uses: `intake_id`, `bin_id`, `egg_id`, `egg_observation_id`, `bin_observation_id`, `hatchling_ledger_id`.

**Impact:** Cleanup silently fails. Test data accumulates across runs. Medium severity.

**Fix:** Replace with a column name map (5-minute change).

---

### 3. TSK-04 Strike 3 Verdict

**Recommendation: DO NOT hard-lock TSK-04.**

| Factor | Finding |
| :--- | :--- |
| Failure type | Infrastructure/environment (app crash) |
| Affected scope | All 12 tests identically — not TSK-04 specific |
| Test logic | Previously validated, unchanged |
| 3-strike intent | Governs test-specific regressions, not system outages |

**Verdict:** TSK-04 remains at **Strike 2** with failure classified as `ENV_BLOCK`. If we Strike-3'd TSK-04, we'd have to do the same to TSK-03 and TSK-07 — locking 16 test cases for an infrastructure glitch.

---

### Red Team's Prioritized Action Plan

| # | Action | Effort |
| :--- | :--- | :--- |
| 1 | Restart Streamlit app (clear stale session) | 5 sec |
| 2 | Fix conftest.py: replace `.neq('id', 0)` with table-specific PK names | 5 min |
| 3 | Add login fixture resilience — detect error page, auto-recovery | 10 min |
| 4 | Re-run TSK-03, TSK-04, TSK-07 | — |

---

Want me to apply fix #2 (conftest column names) and then re-run the 3 test suites?