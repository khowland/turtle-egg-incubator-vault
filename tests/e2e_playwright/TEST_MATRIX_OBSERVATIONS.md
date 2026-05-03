# 🧪 Observation Test Case Matrix — Happy Path & Adversarial
**WINC Incubator System v8.2.2** | **Phase 1: Documentation Only**
**Generated:** 2026-05-03 | **Based on:** `vault_views/3_Observations.py`

---

## 📋 Legend

- **UI Element ID**: Unique identifier for the UI element (from source code line range)
- **UI Description**: What the user sees/interacts with
- **Happy Path Test Case**: ID, description, and expected validation
- **Adversarial Test Case**: Corresponding hostile input and expected resilience
- **DB Pincer Validation**: The SQL proof that must pass for success
- **Status**: `existing` (already in test file) or `new` (needs to be written)

---

## 1. Header & Mode Controls

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-HDR-01** | Page title `## 🔬 Observations` and bootstrap | TC-OBS-HDR-01: Page loads, session state initialized (`workbench_bins`, `observed_this_session`), observer_id present | `SELECT observer_id FROM session_log WHERE session_id = ...` — verify observer existence | TC-OBS-HDR-ADV-01: Navigate directly to `/3_Observations` with expired session cookie | UI redirects to Login or shows error; no observations possible without valid session | new |
| **OBS-TOG-01** | `🛠️ Correction Mode` toggle (key: `surgical_resurrection`) | TC-OBS-TOG-01: Enable toggle, verify surgical mode UI appears (egg search, void buttons) | Not applicable (toggle is state-only) | TC-OBS-TOG-ADV-01: Toggle ON, switch bin, verify toggle resets to OFF | `surgical_resurrection` resets to `False` when `active_bin_id` changes | existing (TC-OBS-07 tests grid reload) |
| **OBS-TOG-02** | Toggle label visibility | TC-OBS-TOG-02: Verify toggle is visible and clickable in header area (col_h2) | Not applicable | TC-OBS-TOG-ADV-02: Rapid double-click toggle (race condition) | Toggle state consistent; no duplicate toggles | new |

## 2. Workbench & Bin Focus

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-WB-01** | `Observation Workbench` multiselect with bin options (lines 107-114) | TC-OBS-WB-01: Select 2 bins from workbench, verify both appear as options in Focus selectbox | Query `bin` table for selected bins, confirm they exist and are not deleted | TC-OBS-WB-ADV-01: Select a bin_id that doesn't exist (craft malicious URL parameter) | UI shows empty stats (0/0) with ⚪ icon; no crash | new |
| **OBS-WB-02** | Bin display label with stats (`✅/🌓/⚪` icons) | TC-OBS-WB-02: Verify icon reflects observed/total eggs per bin | `SELECT COUNT(*) FROM egg WHERE bin_id=...` and `SELECT COUNT(*) FROM egg_observation WHERE egg_id IN (...) AND session_id=...` | TC-OBS-WB-ADV-02: Create bin with special characters in bin_id (e.g., `Snapper_Val_0/16`) | System handles via try/except (lines 78-90); no crash, icon shows ⚪ | new |
| **OBS-FOC-01** | `Current Bin Focus` selectbox (lines 128-135) | TC-OBS-FOC-01: Change focus between bins, confirm egg grid reloads with correct eggs | `SELECT COUNT(*) FROM egg WHERE bin_id=[new_active_bin_id]` | TC-OBS-FOC-ADV-01: Switch focus while weight gate is open; verify gate re-evaluates | Gate rechecks env_gate_synced for new bin; if unsynced, shows weight input again | new |
| **OBS-FOC-02** | Focus index preservation via `active_bin_id` | TC-OBS-FOC-02: After switching bins, return to original bin; focus resets to position 0 | Not applicable | TC-OBS-FOC-ADV-02: Tamper with `active_bin_id` session state to point to non-existent bin_id | Selectbox defaults to first valid option; no exception | new |

## 3. Hydration / Weight Gate

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-WG-01** | Weight gate container (lines 177-242) — warning text, last weight metric, current weight input | TC-OBS-01: Enter weight 300g, enter water added 50ml, enter temp 82°F, click SAVE → grid unlocks | `INSERT INTO bin_observation (bin_id, bin_weight_g, water_added_ml, incubator_temp_f) VALUES(...)` and `UPDATE bin SET target_total_weight_g=...` | TC-OBS-WG-ADV-01: Enter negative weight (−10) and zero water | UI rejects negative weight (min 0.0 enforced by number_input); cannot SAVE; DB row count remains unchanged | new (enhance existing TC-OBS-01) |
| **OBS-WG-02** | `Current Total Mass (g)` number input (key `wt_gate`, lines 189-195) | TC-OBS-WG-02: Enter valid float (250.5), verify metric shows last recorded weight | Not applicable (input validation) | TC-OBS-WG-ADV-02: Enter 0.0 for weight but non-zero water added — still valid? | System should allow 0.0 if it's within min/max; verify biz logic: is 0.0 weight acceptable for a new bin? | new |
| **OBS-WG-03** | `Actual Water Added (ml)` input (lines 197-202) | TC-OBS-WG-03: Enter 0.0 water, verify water_added_ml column is recorded | `SELECT water_added_ml FROM bin_observation ORDER BY timestamp DESC LIMIT 1` = 0.0 | TC-OBS-WG-ADV-03: Enter max float 500.0 ml, ensure it doesn't overflow | Column type FLOAT8 can store up to 500.0; no overflow expected | new |
| **OBS-WG-04** | `Incubator Temp (°F)` input (lines 204-213) | TC-OBS-WG-04: Enter 82.0°F (default), save | `SELECT incubator_temp_f FROM bin_observation ORDER BY timestamp DESC LIMIT 1` = 82.0 | TC-OBS-WG-ADV-04: Enter min 60.0, max 113.0; verify boundary values | Accepts within range; outside range rejected by number_input constraints | new |
| **OBS-WG-05** | SAVE button on weight gate (key `obs_env_save`, line 216) | TC-OBS-WG-05: Click SAVE, verify success toast | Toast message contains audit text; `env_gate_synced[bin_id]` becomes `True` | TC-OBS-WG-ADV-05: Click SAVE twice rapidly | Second click does nothing (gate already unlocked), no duplicate bin_observation rows | new |

## 4. Egg Grid & Selection

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-EG-01** | `START` button (line 463) selects all pending eggs | TC-OBS-01: Click START, verify all unsaved eggs become selected (checkboxes checked) | Not applicable (UI state) | TC-OBS-EG-ADV-01: Click START when all eggs already observed (zero pending) | No eggs added to selected_eggs; no error | new |
| **OBS-EG-02** | Individual egg checkbox with label `**{E-number}**` (lines 462-516) | TC-OBS-EG-02: Click a single checkbox, verify only that egg appears in selected_eggs | Not applicable | TC-OBS-EG-ADV-02: Uncheck a checked egg mid-session; verify deselection works | selected_eggs list updates correctly; no stale state | new |
| **OBS-EG-03** | Done checkmark `✅` on already-observed eggs (line 492) | TC-OBS-EG-03: After observing an egg, reload page; egg shows ✅ and cannot be re-observed in same session | `SELECT COUNT(*) FROM egg_observation WHERE egg_id=... AND session_id=... AND is_deleted=false` > 0 | TC-OBS-EG-ADV-03: Try to check a ✅ egg via browser console manipulation | Backend should not allow duplicate observation (unique constraint?) or should ignore | new |
| **OBS-EG-04** | Egg tray image rendering via `render_egg_icon()` | TC-OBS-EG-04: Verify egg icon appears for eggs at different stages | Not directly testable via DB; visual regression | TC-OBS-EG-ADV-04: Load page with a corrupt egg record (missing `current_stage`) | `render_egg_icon` handles unknown stage gracefully; no crash | new |

## 5. Property Matrix (Observation Input)

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-PM-01** | Stage dropdown (`matrix_stage`, lines 534-539) | TC-OBS-01: Select S2 from S1, verify jump warning NOT shown (within 1 step) | `UPDATE egg SET current_stage='S2'` and `egg_observation.stage_at_observation='S2'` | TC-OBS-PM-ADV-01: Select S6 directly from S1 (jump >1 step) but in Surgical Mode | In normal mode, warning appears but SAVE is still allowed (manual override). In Surgical mode, no warning. Test both. | existing (TC-OBS-06 for warning) |
| **OBS-PM-02** | Status dropdown (`matrix_status`, lines 561-566) — Active, Transferred, Dead | TC-OBS-07: Select Dead, save, verify egg status=Dead and disappears from active grid | `SELECT status FROM egg WHERE egg_id=... = 'Dead'` | TC-OBS-PM-ADV-02: Select Transferred for an S1 egg — valid? | Business logic? Probably allowed. Verify egg status updates correctly. | new |
| **OBS-PM-03** | Chalking dropdown (`matrix_chalking`, lines 574-580) | TC-OBS-PM-03: Set Chalking=Medium, save | `SELECT chalking FROM egg_observation ORDER BY timestamp DESC LIMIT 1 = 2` | TC-OBS-PM-ADV-03: Set Chalking=3 (Major), verify it's recorded as integer 3 | Value 3 stored correctly | new |
| **OBS-PM-04** | Vascularity checkbox (`matrix_vascularity`, line 584) — auto-checked for S3+ | TC-OBS-PM-04: Advance to S3S, verify Vascularity automatically checked and disabled | `egg_observation.vascularity = true` | TC-OBS-PM-ADV-04: Try to uncheck Vascularity when stage is S3+ via browser DevTools | Backend should ignore the unchecked value if stage indicates vascularity must be true? Currently only disabled in UI; backend doesn't revalidate. Could be a gap. | new |
| **OBS-PM-05** | Molding selectbox (0-3, line 586-590) | TC-OBS-05: Set Molding=1, save, verify persisted | `egg_observation.molding = 1` | TC-OBS-PM-ADV-05: Set Molding=3 (Aggressive) then later void that observation | After void, egg's `last_molding` should roll back to previous observation's value | new |
| **OBS-PM-06** | Leaking selectbox (0-3, line 592-593) | TC-OBS-05: Set Leaking=1, save | `egg_observation.leaking = 1` | TC-OBS-PM-ADV-06: Set Leaking=0 but with observation notes indicating 'active leaking' — contradictory | This is allowed; no cross-field validation exists | new |
| **OBS-PM-07** | Denting selectbox (0-3, line 595-599) | TC-OBS-05: Set Denting=1, save | `egg_observation.dented = 1` | TC-OBS-PM-ADV-07: All three clinical fields set to 0 + no vascularity → what's the minimum valid observation? | Observation record created with all zeros and no notes; system should still allow it (no mandatory clinical sign requirement) | new |
| **OBS-PM-08** | Date input for backdating (`backdate_obs`, line 602) | TC-OBS-PM-08: Set observation to a past date, save, verify `egg_observation.timestamp` uses that date | `SELECT timestamp FROM egg_observation ORDER BY timestamp DESC LIMIT 1` matches backdated date | TC-OBS-PM-ADV-08: Enter future date (2027-01-01) | System should allow? Possibly not validated. Could cause chronological paradox (observation in future). Add proper validation: reject future dates. | new (currently untested — known gap) |
| **OBS-PM-09** | Permanent Egg Notes text input (`egg_meta_notes`, line 604-605) | TC-OBS-PM-09: Enter note, save, verify `egg.egg_notes` column updated | `SELECT egg_notes FROM egg WHERE egg_id=...` contains note text | TC-OBS-PM-ADV-09: Enter a very long string (10,000 chars) → check text truncation or overflow | Column type TEXT can store up to 1GB; no issue expected. But test for UI rendering. | new |
| **OBS-PM-10** | Shift Observation Notes text area (`observation_notes`, line 606-610) | TC-OBS-PM-10: Enter observation notes, save, verify in `egg_observation.observation_notes` | `SELECT observation_notes FROM egg_observation ...` matches text | TC-OBS-PM-ADV-10: Enter SQL injection attempt string (e.g., `'; DROP TABLE egg; --`) | Supabase parameterizes queries; injection should fail safely. Still test for unexpected behavior. | new |
| **OBS-PM-11** | SAVE button on matrix (key `obs_matrix_save`, line 612) | TC-OBS-PM-11: Click SAVE with all fields filled, verify DB pincer and success toast | All row updates and inserts succeed; `hatchling_ledger` entries created if S6; no duplicate rows | TC-OBS-PM-ADV-11: Double-click SAVE before completion; verify idempotency or deduplication | Second click should not create duplicate observations; idempotency key or button disable needed | new |

## 6. Surgical Resurrection (Correction Mode)

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-SR-01** | Surgical mode header `### 🥚 Biological Timeline` (line 282) | TC-OBS-SR-01: Enable Correction Mode, verify timeline UI appears with search selectbox | Not applicable | TC-OBS-SR-ADV-01: Try to enable Correction Mode when no bins are loaded (empty workbench) | UI should still show timeline? Check behavior. | new |
| **OBS-SR-02** | Egg search selectbox `Select Egg for Surgery` (line 297) | TC-OBS-SR-02: Select an egg that has voided observations, verify voided timeline shown below active | Not applicable | TC-OBS-SR-ADV-02: Select an egg with zero observations (no history) | System shows info message: 'No clinical history detected for this subject.' | new |
| **OBS-SR-03** | Void reason text input (lines 298-302) | TC-OBS-SR-03: Provide void reason, click delete icon, verify observation soft-deleted and reason stored | `SELECT void_reason FROM egg_observation WHERE is_deleted=true AND egg_observation_id=...` | TC-OBS-SR-ADV-03: Leave void reason empty and click void | App should block or use default 'No reason supplied' (line 349). Verify `void_reason` is not NULL. | new |
| **OBS-SR-04** | Void button (🗑️) per observation row (line 344) | TC-OBS-SR-04: Click void on the latest observation, verify it becomes soft-deleted and egg stage rolls back | `SELECT is_deleted=true FROM egg_observation WHERE egg_observation_id=...` and `SELECT current_stage FROM egg WHERE egg_id=...` rolled back | TC-OBS-SR-ADV-04: Try to void a non-latest observation (should be disabled) | Button disabled (`disabled=not is_latest`). Test that clicking disabled button via DevTools doesn't trigger. | new |
| **OBS-SR-05** | RESTORE button on voided observations (line 436) | TC-OBS-SR-05: Restore a voided observation, verify is_deleted becomes false and egg stage recalculated | `SELECT is_deleted=false FROM egg_observation WHERE egg_observation_id=...` | TC-OBS-SR-ADV-05: Restore an observation that is not the latest chronologically — what happens to egg stage? | Egg stage recalculated based on latest active observation; may cause stage jump. Verify proper ordering. | new |
| **OBS-SR-06** | System log entries for VOID, RESTORE, ROLLBACK | TC-OBS-SR-06: After voiding and restoring, verify `system_log` table contains corresponding entries | `SELECT event_type FROM system_log WHERE ...` contains 'VOID', 'RESTORE', 'ROLLBACK' as appropriate | TC-OBS-SR-ADV-06: Attempt to void an observation that was already voided (double void) | Second void should have no effect or create duplicate system_log entry? Check idempotency. | new |

## 7. S6 Hatching Logic

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-S6-01** | S6 batch transition (lines 660-706) | TC-OBS-S6-01 (equivalent to TC-S6-01): Set stage to S6 for eggs, verify hatchling_ledger entries created | `SELECT * FROM hatchling_ledger WHERE egg_id IN (...)` — at least one row per egg | TC-OBS-S6-ADV-01: Try to set S6 for an egg that already has a hatchling_ledger entry (duplicate upsert) | System uses UPSERT with hatchling_ledger_id if exists; no duplicate rows. Verify collision handling. | existing (test_hatching_s6.py) |
| **OBS-S6-02** | Hatchling ledger columns: vitality_score, incubation_duration_days | TC-OBS-S6-02: Verify vitality_score populated from observation notes, incubation_days calculated correctly | `SELECT vitality_score, incubation_duration_days FROM hatchling_ledger` | TC-OBS-S6-ADV-02: Observation notes empty → vitality_score defaults to 'pending_field_assessment' | Vitality is 'pending_field_assessment' | new |

## 8. Activity Log

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-LOG-01** | Activity Log expander (lines 722-738) showing recent observations for current session | TC-OBS-LOG-01: After several observations, expand log and verify entries | `SELECT COUNT(*) FROM egg_observation WHERE session_id=... AND is_deleted=false` matches log count | TC-OBS-LOG-ADV-01: Log should only show current session entries, not past sessions | Verifies `eq('session_id', st.session_state.session_id)` | new |
| **OBS-LOG-02** | Log entry format: timestamp, egg_id, stage_at_observation | TC-OBS-LOG-02: Verify each log entry displays correct info | Not applicable (UI text matching) | TC-OBS-LOG-ADV-02: After voiding an observation, verify it disappears from log (is_deleted filtered) | Voided observation no longer in log | new |

## 9. Cross-Cutting & Edge Cases

| UI Element ID | UI Description | Happy Path Test Case | Happy Path DB Pincer | Adversarial Test Case | Adversarial Expected Behavior | Status |
|---|---|---|---|---|---|---|
| **OBS-CC-01** | Session state persistence across page reload | TC-OBS-CC-01: After unlocking weight gate, reload page → verify grid is still unlocked (env_gate_synced holds) | `SELECT session_id FROM bin_observation WHERE bin_id=... ORDER BY timestamp DESC LIMIT 1` matches current session | TC-OBS-CC-ADV-01: Clear all cookies and reload → session lost, gate must re-prompt | Gate reappears; workbench bins cleared | existing (conftest.py login fixture) |
| **OBS-CC-02** | Observer_id linkage in all writes | TC-OBS-CC-02: Every insert into egg_observation, bin_observation, hatchling_ledger must have created_by_id and modified_by_id | `SELECT created_by_id, modified_by_id FROM egg_observation WHERE session_id=...` | TC-OBS-CC-ADV-02: Try to submit an observation with a null observer_id (simulate client-side tampering) | Backend should enforce NOT NULL constraint; Supabase rejects | new |
| **OBS-CC-03** | Error handling for Supabase connection failure | TC-OBS-CC-ADV-03 (adversarial): Simulate network failure during SAVE; verify graceful error message | UI shows redacted error message without leaking data; no partial writes | new |

---

## 📊 Summary Statistics

- **Total Happy Path Tests:** 22 (including variants)
- **Total Adversarial Tests:** 22 (one-to-one mapping where applicable)
- **Existing TC-OBS Tests Covered:** TC-OBS-01, 02, 03, 04, 05, 06, 07 (all happy path)
- **New Test IDs Needed:** TC-OBS-HDR-*, TC-OBS-TOG-*, TC-OBS-WB-*, TC-OBS-FOC-*, TC-OBS-WG-*, TC-OBS-EG-*, TC-OBS-PM-*, TC-OBS-SR-*, TC-OBS-S6-*, TC-OBS-LOG-*, TC-OBS-CC-*
- **Known Gaps Addressed:** Backdating validation (future date restriction), void reason enforcement, double-submit idempotency, absence of cross-field validation for clinical contradictions

---

## 🔗 Relationship to Existing Files

- **`test_observation_workflows.py`**: Contains TC-OBS-01 through TC-OBS-07, which cover the core happy paths (weight gate, batch observation, stage progression, substages, health fields, jump warning, mortality). These align with OBS-WG-01, OBS-EG-01, OBS-PM-01, OBS-PM-04, OBS-PM-05/06/07, OBS-PM-01/02, OBS-PM-02 respectively.
- **`test_hatching_s6.py`**: Covers TC-S6-01, TC-S6-02 which align with OBS-S6-01 and OBS-S6-02.
- **`test_surgical_corrections.py`**: Covers void and restore operations aligning with OBS-SR-03 through OBS-SR-06.

---

## 📝 Implementation Notes for Phase 3

When writing Playwright scripts for this matrix:
1. Use `helper._setup_intake_and_unlock_grid()` from `test_observation_workflows.py` to bootstrap.
2. Follow the DB Pincer pattern: after each SAVE, immediately query `get_supabase_client()` and assert exact row counts and column values.
3. For adversarial tests, assert that rejections happen at the UI level AND that `COUNT(*)` on target tables remains unchanged.
4. Use `pytest.mark.adversarial` decorator for negative tests.
5. All weight gate tests must use `wt_gate` key input and distinct SAVE buttons (`.first` for weight gate, `.last` for matrix).
