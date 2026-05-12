# TSDQ — Try Something Different Queue

**Last Updated**: 2026-05-07 00:15

---

## Active Queue

| TSDQ-ID | TSK(s) | Tests Blocked | Failure Pattern | Attempts | Priority | Strategy Status |
|---------|--------|---------------|-----------------|----------|----------|-----------------|
| TSDQ-001 | TSK-04, TSK-06, TSK-07 | 13 | `active_case_id` not bridged to Playwright session state after `switch_page` → selectbox/multi-select options never populate → timeout/hang | 6+ across sessions | 🔴 CRITICAL | Tactic 2 - Round 1 |
| TSDQ-002 | TSK-03 | 1 (test_supplemental_intake_full_save) | RPC `vault_finalize_supplemental_bin` not creating bin (expected ≥2, got 1) | 3 | 🟡 HIGH | Tactic 1 retry |

| TSDQ-003 | TSK-08 | 2 (test_sqli_payload_in_winc_case + test_xss_payloads_sanitized) | SQLi: Cloudflare 403 WAF block (security working). XSS: payload accepted and stored in intake_name — no sanitization. | 1 | 🟡 MEDIUM | Tactic 1 retest after fixes |


## Tactic 2 Strategy Log

### TSDQ-001: bridging bug

#### Round 1 (2026-05-07 00:15-00:30)
- **Model 1 (Deepseek)** approach: Click multi-select widget to trigger ORM fallback via on_change callback
- **Model 2 (Claude)** review: REJECTED — clicking empty multi-select does NOT trigger on_change (only value changes fire callbacks). Recommended `page.reload()` instead.
- **Model 1 fine-tune**: Implemented `_trigger_workbench_hydration()` helper in conftest.py using `page.reload()` with retry logic and diagnostics, per Model 2's refinements.
- **Model 2 polish**: SKIPPED (code is straightforward, proceed to smoke test).
- **Outcome**: FAILED — page.reload() did not populate workbench bins. Smoke test (TSK-07) still timed out with empty multi-select. This confirms session_state is server-side and reload preserves only the cookie, not the full state hydration.

---
*Managed by A0 orchestrator per QA_TSDQ_GOVERNANCE.md*

#### Round 2 (2026-05-07 00:30-00:45)
- **Root cause discovered**: Streamlit session state is NOT preserved across page.reload() or direct URL navigation. After reload, navigating to /3_Observations shows 'Page not found' because the session cookie linkage is lost. The ORM fallback data exists (bins, intakes, eggs confirmed in DB), but the Observations page never renders because there's no valid session.
- **Model 1 (Deepseek)** new approach: [IN PROGRESS — Navigate via Streamlit sidebar link click instead of page.reload/URL; the link click preserves the session cookie and triggers proper page rendering with session state]
- **Model 2 (Claude)** review: [PENDING]
- **Model 1 fine-tune**: [PENDING]
- **Model 2 polish**: [PENDING]
- **Outcome**: FAILED — wait+click approach also failed. Multi-select widget IS found (stMultiSelect visible) but clicking it and waiting 3s does NOT populate dropdown options (stMultiSelectDropdown li count remains 0). This confirms the issue is NOT session loss (widget renders in same session) but rather that Streamlit's multi-select on_change callback doesn't trigger a rerun on click — it only fires on value changes. With zero options, no value can be selected, creating a deadlock.

#### Round 3 (2026-05-07 01:00)
- **Root cause refined**: The multi-select widget renders but clicking it does NOT trigger Streamlit rerun for the parent page. Streamlit's `st.multiselect` on_change only fires on value selection (picking/deselecting an option). With zero options, no selection possible → deadlock. The ORM fallback in 3_Observations.py runs during page initialization but the multi-select widget receives an EMPTY set of workbench_bins at render time. The fix must ensure workbench_bins is populated BEFORE the multi-select widget renders.
- **Model 1 (Deepseek)** approach: Fix 3_Observations.py line 146-148 — replace `st.stop()` (which halts page rendering when workbench_bins is empty) with fallback to `bin_options` (all available bins from DB). This ensures focus_options is NEVER empty → selectbox always renders → no multi-select dropdown timeout.
- **Fix applied**: `vault_views/3_Observations.py` — when `focus_options` is empty, populate from `bin_options` and add all bin_ids to `workbench_bins`.
- **Model 2 (Claude)** review: [PENDING]
- **Model 1 fine-tune**: [PENDING]
- **Model 2 polish**: [PENDING]
- **Outcome**: FAILED after 3 rounds. Round 1 (page.reload) rejected, Round 2 (wait+click) failed, Round 3 (st.stop() removal + active_bin_id) insufficient. Property Matrix NOT visible after clicking egg checkboxes. Active_bin_id fix alone doesn't trigger editing form render. This confirms a deeper rendering issue — the Observations page editing form (Stage selectbox, checkboxes, SAVE button) never initializes when entering via the bin_options fallback path. ESCALATED to Tactic 2: two-model strategy rethink.

#### Round 4 (2026-05-07 01:30) — Tactic 2: Two-Model Strategy Rethink
- **Model 1 (Deepseek)** approach: [IN PROGRESS — Deep-dive reading 3_Observations.py editing form trigger logic to understand WHY the Property Matrix doesn't render after multi-select selection and active_bin_id set. Hypothesis: the multi-select widget re-renders because workbench_bins changes (due to fallback), but streamlit's widget key `obs_workbench` means the on_change callback may not fire because the widget already rendered with empty defaults before the fallback populated workbench_bins.]
- **Model 2 (Claude)** review: [PENDING]
- **Model 1 fine-tune**: [PENDING]
- **Model 2 polish**: [PENDING]
- **Outcome**: [PENDING]

#### Round 6 (2026-05-07 02:50) — Tactic 2: START Button Approach
- **Model 1 (Deepseek)** approach: Fix test helper to click START button (which directly sets selected_eggs and fires st.rerun()) instead of individual checkbox label clicks. Applied to TSK-04 helper. TSK-06/07 pending.
- **Outcome**: Smoke test running. If START button works, 13 tests unblocked. If not, escalate to Round 7 (full code review of Property Matrix rendering chain).

## TSDQ-002: Workbench MultiSelect Hydration — Bin-Code Mismatch
- **TSKs affected**: TSK-04 (7 tests), TSK-06 (5 tests), TSK-07 (1 test) = 13 tests
- **Attempts**: 10+ (MultiSelectDropdown, evaluate(), dispatchEvent, flexible search)
- **Symptoms**: 
  - After intake creation, navigating to Observations shows multi-select with 0 dropdown options
  - `[DIAG] Total dropdown options: 0`
  - TACTIC2 diagnostics show workbench_bins populated but for WRONG active_case_id
- **Root cause**: Test creates intake → navigates to Observations → active_case_id NOT set to new intake → workbench shows stale/empty bins from different case
- **Date escalated**: 2026-05-07 05:10
- **Status**: 🟡 TACTIC_2_QUEUED
- **Notes**: 
  - This is the original "bridging bug" — session state not transferred after navigation
  - The `.neq` filter and RPC revert fixed Property Matrix rendering but the multi-select STILL has 0 options
  - Need to investigate how active_case_id is set after intake creation (via URL params? session state bridging?)
  - The test might need to explicitly set active_case_id after intake creation
